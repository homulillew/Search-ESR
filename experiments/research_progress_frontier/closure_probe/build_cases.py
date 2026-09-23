"""Copy only already-visible historical excerpts into frozen Stage A packets."""

import hashlib
import json
from pathlib import Path

from case_specs import SOURCES, SPECS

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def find_packet(qid, checkpoint, wanted):
    seq = int(checkpoint.split(":")[1])
    packets = json.loads((ROOT / SOURCES[qid]).read_text())
    packet = next(p for p in packets if p["qid"] == qid and p["seq"] == seq)
    matches = []
    for message in packet["prefix_messages"]:
        if message.get("role") != "tool":
            continue
        try:
            result = json.loads(message["content"])
        except (json.JSONDecodeError, TypeError):
            continue
        for item in result.get("results", []):
            if item.get("preview_ref") == wanted:
                matches.append(item)
    if not matches:
        raise ValueError(f"Observed W ref missing: {qid} {checkpoint} {wanted}")
    first = matches[0]
    if any(m["preview"] != first["preview"] or m["doc_ref"] != first["doc_ref"] for m in matches):
        raise ValueError(f"Conflicting W ref: {qid} {wanted}")
    return {"ref": wanted, "doc_ref": first["doc_ref"], "title": first["title"],
            "excerpt": first["preview"], "raw_protocol": "orthogonal_DW",
            "source_event": checkpoint, "source_path": SOURCES[qid]}


def find_events(qid, checkpoint, wanted):
    limit = int(checkpoint.split(":")[1])
    events = [json.loads(line) for line in (ROOT / SOURCES[qid]).open()]
    matches = []
    for event in events:
        if event["seq"] > limit:
            break
        rows = []
        if event["kind"] == "tool_result":
            result = event.get("result")
            rows = result if isinstance(result, list) else []
        elif event["kind"] == "api_request":
            for message in event["request"].get("messages", []):
                if message.get("role") != "tool":
                    continue
                try:
                    result = json.loads(message["content"])
                except (json.JSONDecodeError, TypeError):
                    continue
                if isinstance(result, list):
                    rows.extend(result)
        for item in rows:
            if str(item.get("docid")) == wanted and item.get("window_ref") and item.get("text"):
                matches.append((event["seq"], item))
    if not matches:
        raise ValueError(f"Observed doc missing: {qid} {checkpoint} {wanted}")
    seq, first = matches[0]
    return {"ref": first["window_ref"], "doc_ref": str(first["docid"]),
            "title": first.get("title", ""), "excerpt": first["text"],
            "raw_protocol": "legacy_docid_window_ref", "source_event": f"event:{seq}",
            "source_path": SOURCES[qid]}


def main():
    if (HERE / "review_cases.json").exists():
        raise FileExistsError(HERE / "review_cases.json")
    rows, provenance = [], []
    for spec in SPECS:
        qid = spec["qid"]
        evidence = []
        for checkpoint, wanted in spec["source_selectors"]:
            item = (find_packet(qid, checkpoint, wanted) if checkpoint.startswith("R1:")
                    else find_events(qid, checkpoint, wanted))
            evidence.append(item)
        row = {k: spec[k] for k in ("case_id", "qid", "checkpoint", "question_constraint", "claim",
                                    "candidate", "review_label", "review_missing", "ambiguity", "case_type",
                                    "review_reason")}
        row["visible_evidence"] = [dict(ref=e["ref"], doc_ref=e["doc_ref"],
                                        title=e["title"], excerpt=e["excerpt"]) for e in evidence]
        row["visible_evidence_sha256"] = sha_text(json.dumps(row["visible_evidence"], ensure_ascii=False, sort_keys=True))
        rows.append(row)
        provenance.append({"case_id": spec["case_id"], "source_selectors": spec["source_selectors"],
                           "source_items": [{k: e[k] for k in ("ref", "doc_ref", "raw_protocol",
                                                            "source_event", "source_path")} for e in evidence],
                           "stale_action_private": spec["stale_action_private"]})
    if len(rows) != 29 or len({r["case_id"] for r in rows}) != len(rows):
        raise ValueError("Expected 29 distinct cases")
    if len({r["qid"] for r in rows}) != 8 or sum(r["case_type"] == "stale_gap" for r in rows) != 5:
        raise ValueError("Qid or stale quota failed")
    (HERE / "review_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    (HERE / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + "\n")
    from collections import Counter
    print("cases", len(rows), "qids", len({r["qid"] for r in rows}),
          "labels", dict(Counter(r["review_label"] for r in rows)),
          "types", dict(Counter(r["case_type"] for r in rows)))


if __name__ == "__main__":
    main()
