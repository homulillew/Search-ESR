"""Validate qualitative annotations and score paired two-action observations.

No API calls. Coding-agent labels are not independent human gold. Source
usefulness and actually observed support are scored separately, with failures
retained and repeated trials averaged within each question.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
import sys

ROOT = Path(__file__).resolve().parents[3]
ARMS = ("current", "exploratory")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def views(step):
    value = step.get("result") or []
    return value if isinstance(value, list) else [value]


def covered(span, ranges):
    start, end = span
    for left, right in sorted(ranges):
        if left > start:
            return False
        start = max(start, right)
        if start >= end:
            return True
    return False


def visible(proof, ranges):
    return any(all(any(covered(span, ranges) for span in fact["source_spans"])
                   for fact in alternative) for alternative in proof)


def coverage(windows):
    output = {}
    for w in windows:
        key = (w["docid"], w["document_sha256"])
        output.setdefault(key, []).append([w["offset"], w["end_char"]])
        if w.get("title_span"):
            output[key].append(w["title_span"])
    return output


def score(run):
    run = Path(run)
    audit = read(run / "audit.json")
    cards = read(run / "behavior_cards.json")
    mapping = read(run / "behavior_card_mapping.json")
    pool = read(run / "review_pool.json")
    review_files = sorted(run.glob("review_part_*.json"))
    reviews = [read(p) for p in review_files]
    labels = [b for r in reviews for b in r["behavior"]]
    sources = [s for r in reviews for s in r["source_review"]]
    annotations = [a for r in reviews for a in r["annotations"]]
    assert len(labels) == len(cards) == 80
    assert {b["card_id"] for b in labels} == {c["card_id"] for c in cards}
    assert len(sources) == len(pool)
    assert {(s["qid"], s["docid"]) for s in sources} == {(s["qid"], s["docid"]) for s in pool}
    annotation_map = {(a["qid"], a["docid"]): a for a in annotations}
    assert len(annotation_map) == len(annotations)
    assert set(annotation_map) <= {(s["qid"], s["docid"]) for s in pool}
    db = sqlite3.connect("file:" + str(ROOT / "BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite") + "?mode=ro", uri=True)
    checked_spans = 0

    def validate(annotation):
        nonlocal checked_spans
        text, url = db.execute("SELECT text,url FROM documents WHERE docid=?", (annotation["docid"],)).fetchone()
        assert hashlib.sha256(text.encode()).hexdigest() == annotation["document_sha256"]
        if "url" in annotation:
            assert annotation["url"] == url
        assert annotation["proof_alternatives"]
        for alternative in annotation["proof_alternatives"]:
            assert alternative
            for fact in alternative:
                assert fact["source_spans"]
                for a, b in fact["source_spans"]:
                    assert 0 <= a < b <= len(text)
                    assert text[a:b] == fact["quote"], (annotation["docid"], fact)
                    checked_spans += 1

    for annotation in annotations:
        validate(annotation)
    sessions = []
    for label in labels:
        identity = mapping[label["card_id"]]
        assert identity["qid"] == label["qid"]
        if label.get("session"):
            assert label["session"] == identity["session"]
        result = read(run / identity["session"] / "result.json")
        first = next((s for s in result["steps"] if s["step"] == 1), {})
        second = next((s for s in result["steps"] if s["step"] == 2), {})
        first_views, second_views = views(first), views(second)
        first_ranges, second_ranges = coverage(first_views), coverage(second_views)
        cumulative_ranges = coverage(first_views + second_views)
        row = dict(**identity, status=result["status"],
            first_query_fidelity=label["first_query_fidelity"],
            second_action_grounding=label["second_action_grounding"],
            first_query_issues=label.get("first_query_issues", []),
            unsupported_claims=label.get("unsupported_claims", []),
            first_source=0, first_visible=0, cumulative_source=0, cumulative_visible=0,
            new_relevant_evidence=int(bool(label.get("new_evidence"))), new_evidence=label.get("new_evidence", []),
            first_useful_docs=[], first_visible_docs=[], cumulative_useful_docs=[], cumulative_visible_docs=[])
        for phase, ranges in (("first", first_ranges), ("cumulative", cumulative_ranges)):
            for (docid, source_hash), regions in ranges.items():
                annotation = annotation_map.get((identity["qid"], docid))
                if not annotation:
                    continue
                assert source_hash == annotation["document_sha256"]
                row[phase + "_source"] = 1
                row[phase + "_useful_docs"].append(docid)
                if visible(annotation["proof_alternatives"], regions):
                    row[phase + "_visible"] = 1
                    row[phase + "_visible_docs"].append(docid)
        for evidence in label.get("new_evidence", []):
            validate(evidence)
            key = evidence["docid"], evidence["document_sha256"]
            assert visible(evidence["proof_alternatives"], second_ranges.get(key, [])), (identity["session"], "new evidence not visible in step2", evidence)
            assert not visible(evidence["proof_alternatives"], first_ranges.get(key, [])), (identity["session"], "identical evidence already seen", evidence)
            # A follow-up fact can become useful only after this session has
            # identified its subject. Do not propagate that contextual label
            # to other sessions through a global document-positive pool.
            assert (identity["qid"], evidence["docid"]) in {(s["qid"],s["docid"]) for s in pool}
            row["cumulative_source"] = row["cumulative_visible"] = 1
            if evidence["docid"] not in row["cumulative_useful_docs"]:
                row["cumulative_useful_docs"].append(evidence["docid"])
            if evidence["docid"] not in row["cumulative_visible_docs"]:
                row["cumulative_visible_docs"].append(evidence["docid"])
        row["visible_gain_from_second"] = row["cumulative_visible"] - row["first_visible"]
        row["source_gain_from_second"] = row["cumulative_source"] - row["first_source"]
        sessions.append(row)
    db.close()
    qids = [str(t["qid"]) for t in read(run / "tasks.json")]
    by_session = {s["session"]: s for s in sessions}
    metric_names = ("first_source", "first_visible", "cumulative_source", "cumulative_visible", "new_relevant_evidence", "visible_gain_from_second", "source_gain_from_second")
    paired = []
    for qid in qids:
        group = {arm:[by_session[f"qid_{qid}__{arm}__r{r}"] for r in (1,2)] for arm in ARMS}
        row = dict(qid=qid, sessions=group, metrics={})
        for metric in metric_names:
            a, b = [[s[metric] for s in group[arm]] for arm in ARMS]
            av, bv = statistics.mean(a), statistics.mean(b)
            row["metrics"][metric] = dict(current=av, exploratory=bv, delta=bv-av,
                direction="win" if bv>av else "loss" if bv<av else "tie",
                repeatable_win=min(b)>max(a), repeatable_loss=max(b)<min(a))
        paired.append(row)
    metrics = {}
    for metric in metric_names:
        rows = [q["metrics"][metric] for q in paired]
        metrics[metric] = {arm:dict(hits=sum(s[metric] for s in sessions if s["arm"]==arm), attempts=40,
                                  question_mean=statistics.mean(r[arm] for r in rows)) for arm in ARMS}
        metrics[metric].update(delta=statistics.mean(r["delta"] for r in rows),
            paired_counts=dict(Counter(r["direction"] for r in rows)),
            repeatable_wins=[q["qid"] for q in paired if q["metrics"][metric]["repeatable_win"]],
            repeatable_losses=[q["qid"] for q in paired if q["metrics"][metric]["repeatable_loss"]])
    output = dict(method="Post-run coding-agent qualitative review, partly unblinded, incomplete pooled relevance labels; not independent human gold or full recall. Every pooled returned window screened. Mechanical source/quote/visible-range checks are deterministic. Semantic novelty additionally depends on reviewer comparison of facts, not just text intervals.",
        review_files=[p.name for p in review_files],
        coverage=dict(questions=len(qids), sessions=len(sessions), pooled_sources=len(pool),
            distinct_windows=len(read(run / "utility_cards.json")), positive_sources=len(annotations), verified_quote_spans=checked_spans),
        metrics=metrics,
        behavior={arm:dict(first_query_fidelity=dict(Counter(s["first_query_fidelity"] for s in sessions if s["arm"]==arm)),
                           second_action_grounding=dict(Counter(s["second_action_grounding"] for s in sessions if s["arm"]==arm)),
                           sessions_with_unsupported_claims=sum(bool(s["unsupported_claims"]) for s in sessions if s["arm"]==arm)) for arm in ARMS},
        aggregates=audit["aggregates"],
        concurrency={k:v for k,v in audit["concurrency"].items() if "records" not in k},
        net_and_repeatable_utility_gain=any(metrics[m]["delta"]>0 and metrics[m]["repeatable_wins"] for m in ("cumulative_visible", "new_relevant_evidence")),
        default_prompt_changed=False,
        decision_note="Utility criterion alone is not a promotion decision; interpret semantic issues, repeated losses and actual cost without adjusting the frozen prompts.",
        paired=paired)
    (run / "review_summary.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:output[k] for k in ("coverage","metrics","behavior","net_and_repeatable_utility_gain")},ensure_ascii=False,indent=2))
    return output


if __name__ == "__main__":
    score(sys.argv[1])
