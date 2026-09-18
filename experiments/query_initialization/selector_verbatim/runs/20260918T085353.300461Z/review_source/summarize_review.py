"""Post-run qualitative scoring; no model or retrieval calls.

Review labels are coding-agent judgments, not human gold or complete qrels.
Validate every positive quote against the immutable corpus, then determine
visibility separately for each actual returned window (including its title).
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
import sys


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def contained(span, regions):
    start, end = span
    for left, right in sorted(regions):
        if left > start:
            return False
        if right > start:
            start = right
        if start >= end:
            return True
    return False


def summarize(run):
    run = Path(run)
    reviews = [read(p) for p in sorted(run.glob("review_part_*.json"))]
    audit = read(run / "audit.json")
    cards = read(run / "semantic_cards.json")
    mapping = read(run / "semantic_card_mapping.json")
    pool = read(run / "review_pool.json")
    semantic = [x for r in reviews for x in r["semantic"]]
    source_review = [x for r in reviews for x in r["source_review"]]
    annotations = [x for r in reviews for x in r["annotations"]]
    assert len(semantic) == len(cards) == 60
    assert {s["card_id"] for s in semantic} == {c["card_id"] for c in cards}
    assert all(s["qid"] == mapping[s["card_id"]]["qid"] for s in semantic)
    assert len(source_review) == len(pool)
    assert {(s["qid"], s["docid"]) for s in source_review} == {(s["qid"], s["docid"]) for s in pool}
    by_doc = {(a["qid"], a["docid"]): a for a in annotations}
    assert len(by_doc) == len(annotations)
    assert set(by_doc) <= {(s["qid"], s["docid"]) for s in pool}
    db = sqlite3.connect("file:/data/WSH/Search-ESR/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro", uri=True)
    quote_count = 0
    for annotation in annotations:
        text, url = db.execute("SELECT text,url FROM documents WHERE docid=?", (annotation["docid"],)).fetchone()
        assert digest(text) == annotation["document_sha256"]
        assert url == annotation["url"]
        assert annotation["proof_alternatives"]
        for alternative in annotation["proof_alternatives"]:
            assert alternative
            for proof in alternative:
                assert proof["source_spans"]
                for start, end in proof["source_spans"]:
                    assert 0 <= start < end <= len(text)
                    assert text[start:end] == proof["quote"], (annotation["qid"], annotation["docid"], proof)
                    quote_count += 1
    db.close()
    sessions = {s["session"]: dict(session=s["session"], qid=s["qid"], arm=s["arm"], repeat=s["repeat"],
                 useful_source=0, visible_evidence=0, useful_docs=[], visible_docs=[], source_ranks=[], visible_ranks=[])
                for s in audit["sessions"]}
    for item in pool:
        annotation = by_doc.get((item["qid"], item["docid"]))
        if annotation is None:
            continue
        windows = {w["window_ref"]: w for w in item["windows"]}
        for occurrence in item["occurrences"]:
            window = windows[occurrence["window_ref"]]
            assert window["document_sha256"] == annotation["document_sha256"]
            regions = [[window["offset"], window["end_char"]]]
            if window.get("title_span"):
                regions.append(window["title_span"])
            visible = any(all(any(contained(span, regions) for span in proof["source_spans"])
                              for proof in alternative) for alternative in annotation["proof_alternatives"])
            row = sessions[occurrence["session"]]
            row["useful_source"] = 1
            row["useful_docs"].append(item["docid"])
            row["source_ranks"].append(occurrence["rank"])
            if visible:
                row["visible_evidence"] = 1
                row["visible_docs"].append(item["docid"])
                row["visible_ranks"].append(occurrence["rank"])
    for row in sessions.values():
        row["first_source_rank"] = min(row["source_ranks"], default=None)
        row["first_visible_rank"] = min(row["visible_ranks"], default=None)
    qids = [str(t["qid"]) for t in read(run / "tasks.json")]
    paired = []
    for qid in qids:
        base = sessions[f"qid_{qid}__full_question__r1"]
        repeats = [sessions[f"qid_{qid}__selector__r{i}"] for i in (1, 2)]
        row = {"qid": qid, "full_question": base, "selector": repeats}
        for metric in ("useful_source", "visible_evidence"):
            mean = statistics.mean(s[metric] for s in repeats)
            delta = mean - base[metric]
            row[metric] = dict(full_question=base[metric], selector_mean=mean, delta=delta,
                direction="win" if delta > 0 else "loss" if delta < 0 else "tie",
                repeatable_win=base[metric] == 0 and all(s[metric] == 1 for s in repeats),
                repeatable_loss=base[metric] == 1 and all(s[metric] == 0 for s in repeats))
        paired.append(row)
    metrics = {}
    for metric in ("useful_source", "visible_evidence"):
        rows = [p[metric] for p in paired]
        base = statistics.mean(r["full_question"] for r in rows)
        selected = statistics.mean(r["selector_mean"] for r in rows)
        metrics[metric] = dict(full_question=base, selector=selected, delta=selected-base,
            full_question_hits=sum(r["full_question"] for r in rows),
            selector_hits=sum(s[metric] for s in sessions.values() if s["arm"] == "selector"),
            paired_wins=sum(r["direction"] == "win" for r in rows),
            paired_losses=sum(r["direction"] == "loss" for r in rows),
            paired_ties=sum(r["direction"] == "tie" for r in rows),
            repeatable_wins=[p["qid"] for p in paired if p[metric]["repeatable_win"]],
            repeatable_losses=[p["qid"] for p in paired if p[metric]["repeatable_loss"]])
    selector_semantic = [s for s in semantic if mapping[s["card_id"]]["arm"] == "selector"]
    acceptable = sum(s["acceptable"] for s in selector_semantic)
    engineering = audit["aggregates"]["selector"]
    gates = dict(mechanical=audit["mechanical_checks"] == "passed",
        initial_legitimate=engineering["initial_valid"] >= 38,
        executable=engineering["complete"] == 40,
        understandable_packets=acceptable >= 36,
        utility_noninferior=all(m["delta"] >= 0 for m in metrics.values()),
        net_gain_with_repeatable_win=any(m["delta"] > 0 and m["repeatable_wins"] for m in metrics.values()))
    output = dict(method="Coding-agent qualitative review, partially unblinded; not independent human gold or complete qrels. All pooled returned windows screened, only recorded full-source portions additionally read. Unconfirmed is not proof of irrelevance. No extra API judge. Strict no-LLM-judge preregistration was not satisfied by this review method.",
        qids=qids, review_files=[p.name for p in sorted(run.glob("review_part_*.json"))],
        review_coverage=dict(questions=len(qids), semantic_cards=len(semantic), pooled_sources=len(pool),
                            unique_windows=len(read(run / "utility_cards.json")), positive_sources=len(annotations),
                            verified_quote_spans=quote_count),
        selector_semantics=dict(acceptable=acceptable, total=len(selector_semantic),
            issues=[s for s in selector_semantic if not s["acceptable"] or s.get("issues")]),
        metrics=metrics, gates=gates, numeric_gates_passed=all(gates.values()),
        default_promoted=False, promotion_note="Numerical gates alone do not authorize promotion; repeated regressions, small-sample uncertainty and review-method deviation require explicit interpretation.",
        aggregates=audit["aggregates"], concurrency={k:v for k,v in audit["concurrency"].items() if "records" not in k},
        paired=paired)
    # Compare actual selected refs, not packet metadata or attempt identifiers.
    audited={s["session"]:s for s in audit["sessions"]}
    output["selector_repeat_selection_changed"] = sum(audited[f"qid_{q}__selector__r1"]["input_refs"] != audited[f"qid_{q}__selector__r2"]["input_refs"] for q in qids)
    (run / "review_summary.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:output[k] for k in ("review_coverage", "selector_semantics", "metrics", "gates", "numeric_gates_passed", "selector_repeat_selection_changed")}, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    summarize(sys.argv[1])
