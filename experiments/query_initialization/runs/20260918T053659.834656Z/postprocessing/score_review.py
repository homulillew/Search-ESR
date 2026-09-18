"""Summarize manually verified positive entries; this is not complete relevance judging."""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


def main():
    run = Path(sys.argv[1]).resolve()
    root = Path(__file__).resolve().parents[2]
    annotations = json.loads((run / "evidence_annotations.json").read_text())["annotations"]
    reviewed = json.loads((run / "query_review.json").read_text())["directions"]
    audit = json.loads((run / "audit.json").read_text())
    index = {(a["qid"], a["docid"]): a for a in annotations}
    db = sqlite3.connect(f"file:{root}/BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite?mode=ro", uri=True)
    for a in annotations:
        text = db.execute("select text from documents where docid=?", (a["docid"],)).fetchone()[0]
        assert hashlib.sha256(text.encode()).hexdigest() == a["document_sha256"]
        for alternative in a["proof_alternatives"]:
            for proof in alternative:
                assert proof["source_spans"]
                assert all(text[start:end] == proof["quote"] for start, end in proof["source_spans"])

    rows = []
    for s in audit["sessions"]:
        bundle = json.loads((run / s["session"] / "bundle.json").read_text())
        hits = []
        for direction in bundle["directions"]:
            for w in direction["result"]:
                a = index.get((s["qid"], w["docid"]))
                if a is None:
                    continue
                # Match real source intervals, including the separate title; never concatenated text.
                visible = [[w["offset"], w["end_char"]]]
                if w["title_span"]:
                    visible.append(w["title_span"])
                supported = any(all(any(any(lo <= start and end <= hi for lo, hi in visible)
                                            for start, end in proof["source_spans"])
                                    for proof in alternative)
                                for alternative in a["proof_alternatives"])
                hits.append(dict(docid=w["docid"], direction=direction["direction"],
                                 window_ref=w["window_ref"], kind=a["kind"], clue=a["clue"],
                                 reference_visible=supported))
        row = dict(session=s["session"], qid=s["qid"], arm=s["arm"], repeat=s["repeat"],
                   status=s["status"], confirmed_document=bool(hits),
                   confirmed_target_document=any(h["kind"] == "target_linked" for h in hits),
                   reference_visible=any(h["reference_visible"] for h in hits),
                   target_reference_visible=any(h["reference_visible"] and h["kind"] == "target_linked" for h in hits),
                   hits=hits)
        first = {h["clue"] for h in hits if h["direction"] == 1 and h["reference_visible"]}
        second = {h["clue"] for h in hits if h["direction"] == 2 and h["reference_visible"]}
        row["second_adds_verified_clue"] = bool(second - first)
        row["second_only_verified_entry"] = bool(second) and not first
        rows.append(row)
    aggregates = {}
    for arm in "ABC":
        rs = [r for r in rows if r["arm"] == arm]
        drs = [r for r in reviewed if f"__{arm}__" in r["session"]]
        aggregates[arm] = dict(attempts=len(rs), **{key: sum(r[key] for r in rs) for key in [
            "confirmed_document", "confirmed_target_document", "reference_visible", "target_reference_visible",
            "second_adds_verified_clue", "second_only_verified_entry"]},
            reviewed_directions=len(drs), flagged_directions=sum(bool(r["flags"]) for r in drs),
            flagged_sessions=len({r["session"] for r in drs if r["flags"]}))
    paired = {}
    for left, right in [("A", "B"), ("B", "C"), ("A", "C")]:
        for metric in ["confirmed_document", "reference_visible", "target_reference_visible"]:
            pairs = []
            for qid in sorted({r["qid"] for r in rows}, key=int):
                l = sum(r[metric] for r in rows if r["qid"] == qid and r["arm"] == left)
                r = sum(r[metric] for r in rows if r["qid"] == qid and r["arm"] == right)
                pairs.append(dict(qid=qid, left=l, right=r))
            paired[f"{right}_vs_{left}__{metric}"] = dict(
                wins=sum(r["right"] > r["left"] for r in pairs),
                ties=sum(r["right"] == r["left"] for r in pairs),
                losses=sum(r["right"] < r["left"] for r in pairs), questions=pairs)
    result = dict(caveat="Confirmed-positive lower bounds in a manually reviewed pool; unverified is not irrelevant. Reference coverage is narrower than all possible useful windows. No full-corpus recall or final answer accuracy.",
                  aggregates=aggregates, paired=paired, sessions=rows)
    (run / "review_metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps(aggregates, ensure_ascii=False, indent=2))
    print(json.dumps({k: {x: v[x] for x in ["wins", "ties", "losses"]} for k, v in paired.items()}, indent=2))


if __name__ == "__main__":
    main()
