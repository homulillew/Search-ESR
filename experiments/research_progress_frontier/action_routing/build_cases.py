"""Verify frozen C handles against actually observed prefixes and build diagnosis set."""

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

from case_specs import SPECS, STAGE_D_PRESELECTION

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
A = json.loads((STUDY / "closure_probe/review_cases.json").read_text())
B_ALIASES = {x["case_id"].split("_")[1]: x["raw_to_view_doc_ref"] for x in
             json.loads((STUDY / "frontier_selection/source_aliases.json").read_text())}
PACKETS = json.loads((ROOT / "experiments/research_state_qualification/qualification_upper_bound/review_packets.json").read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def legacy_views(qid):
    windows = {}
    for case in A:
        if case["qid"] == qid:
            for view in case["visible_evidence"]:
                windows[(view["doc_ref"], view["ref"])] = view
    docs = B_ALIASES[qid]
    alias = {}
    for i, (raw_doc, raw_win) in enumerate(sorted(windows, key=lambda x: (docs[x[0]], x[1])), 1):
        alias[f"W{i}"] = {"raw_window_ref": raw_win, "raw_docid": raw_doc,
                          "view_doc_ref": docs[raw_doc], "excerpt": windows[(raw_doc, raw_win)]["excerpt"]}
    return alias


def packet_views(qid, seq):
    packet = next(x for x in PACKETS if x["qid"] == qid and x["seq"] == seq)
    views = {}
    for message in packet["prefix_messages"]:
        if message.get("role") != "tool":
            continue
        try:
            result = json.loads(message["content"])
        except (json.JSONDecodeError, TypeError):
            continue
        for item in result.get("results", []):
            views.setdefault(item["preview_ref"], {"doc_ref": item["doc_ref"],
                                                    "excerpt": item["preview"]})
    return packet, views


def main():
    if (HERE / "review_cases.json").exists():
        raise FileExistsError(HERE / "review_cases.json")
    rows, alias_map = [], {}
    for spec in SPECS:
        qid = spec["qid"]
        if spec["checkpoint"].startswith("R1:"):
            seq = int(spec["checkpoint"].split(":")[1])
            packet, views = packet_views(qid, seq)
            docs = {d["doc_ref"] for d in packet["observed_documents"]}
            prefix_hash = digest(packet["prefix_messages"])
            evidence = {ref: views[ref]["excerpt"] for ref in spec["current_evidence_refs"]}
            if spec["known_relevant_window"] != "none":
                assert spec["known_relevant_window"] in views
                assert views[spec["known_relevant_window"]]["doc_ref"] == spec["known_suitable_document"]
            if spec["known_suitable_document"] != "none":
                assert spec["known_suitable_document"] in docs
        else:
            # Stage B's new packet-local D# aliases are used only in the controlled C view.
            view_windows = legacy_views(qid)
            alias_map[qid] = {k: {f: v[f] for f in ("raw_window_ref", "raw_docid", "view_doc_ref")}
                              for k, v in view_windows.items()}
            docs = set(B_ALIASES[qid].values())
            evidence = {ref: view_windows[ref]["excerpt"] for ref in spec["current_evidence_refs"]}
            if spec["known_relevant_window"] != "none":
                assert view_windows[spec["known_relevant_window"]]["view_doc_ref"] == spec["known_suitable_document"]
            if spec["known_suitable_document"] != "none":
                assert spec["known_suitable_document"] in docs
            # Freeze the source event log and explicit checkpoint boundary rather than any later response.
            from experiments.research_progress_frontier.closure_probe.case_specs import SOURCES
            path = ROOT / SOURCES[qid]
            seq = int(spec["checkpoint"].split(":")[1])
            prior = [json.loads(line) for line in path.open() if json.loads(line)["seq"] <= seq]
            prefix_hash = digest(prior)
        row = dict(spec)
        row["prefix_sha256"] = prefix_hash
        row["visible_evidence_sha256"] = digest(evidence)
        rows.append(row)
    counts = Counter(r["uncertainty_type_private"] for r in rows)
    if len(rows) != 25 or counts != Counter({x: 5 for x in ("source", "location", "context", "closure", "complete")}):
        raise ValueError(counts)
    selected = [r for r in rows if r["case_id"] in STAGE_D_PRESELECTION]
    if len(selected) != 8 or Counter(r["expected_action"] for r in selected) != \
       Counter({x: 2 for x in ("search", "find", "open", "verify")}):
        raise ValueError("Stage D preselection not balanced")
    (HERE / "review_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    (HERE / "source_aliases.json").write_text(json.dumps(alias_map, ensure_ascii=False, indent=2) + "\n")
    (HERE / "stage_d_preselection.json").write_text(json.dumps(STAGE_D_PRESELECTION, indent=2) + "\n")
    print("Stage C cases", len(rows), dict(counts), "D preselection", len(selected))


if __name__ == "__main__":
    main()
