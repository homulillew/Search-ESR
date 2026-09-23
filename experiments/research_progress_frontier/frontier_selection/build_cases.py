"""Build clean Stage B Progress Views from frozen reviewer claims and observed titles."""

import json
from pathlib import Path

from case_specs import SPECS

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
A = ROOT / "experiments/research_progress_frontier/closure_probe"
CASES_A = json.loads((A / "review_cases.json").read_text())
PROV_A = json.loads((A / "provenance.json").read_text())
SOURCE_PATHS = {p["case_id"]: p["source_items"][0]["source_path"] for p in PROV_A if p["source_items"]}


def original_question(qid):
    if qid in ("546", "1094"):
        path = ROOT / "experiments/research_state_qualification/qualification_upper_bound/review_packets.json"
        return next(p["original_question"] for p in json.loads(path.read_text()) if p["qid"] == qid)
    example = next(c for c in CASES_A if c["qid"] == qid)
    events = [json.loads(x) for x in (ROOT / SOURCE_PATHS[example["case_id"]]).open()]
    for event in events:
        if event["kind"] == "api_request":
            for message in event["request"].get("messages", []):
                content = message.get("content")
                if message.get("role") == "user" and isinstance(content, str) and content and \
                   not content.startswith("Harness observation bookkeeping"):
                    return content
    raise ValueError(qid)


def main():
    if (HERE / "review_cases.json").exists():
        raise FileExistsError(HERE / "review_cases.json")
    rows, aliases = [], []
    for spec in SPECS:
        qid = spec["qid"]
        observed = {}
        for case in CASES_A:
            if case["qid"] != qid:
                continue
            for item in case["visible_evidence"]:
                observed.setdefault(item["doc_ref"], item["title"])
        if qid in ("546", "1094"):
            mapping = {doc: doc for doc in observed}
        else:
            mapping = {doc: f"D{i}" for i, doc in enumerate(sorted(observed), 1)}
        directory = [{"doc_ref": mapping[doc], "observed_title": title}
                     for doc, title in sorted(observed.items(), key=lambda x: mapping[x[0]])]
        row = {k: spec[k] for k in ("case_id", "qid", "candidate_hypotheses", "claims", "gap_options",
                                    "acceptable_active_gaps", "unacceptable_closed_gaps",
                                    "unsupported_hypothesis_gaps", "preferred_source_types",
                                    "review_reason", "ambiguity")}
        row["original_question"] = original_question(qid)
        row["source_directory"] = directory
        rows.append(row)
        aliases.append({"case_id": spec["case_id"], "raw_to_view_doc_ref": mapping,
                        "note": "Only the new Stage B Progress View uses D# aliases for legacy raw docids."})
    if len(rows) != 8 or len({r["qid"] for r in rows}) != 8:
        raise ValueError("Expected one Frontier case per qid")
    for row in rows:
        gap_ids = {g[0] for g in row["gap_options"]}
        if len(gap_ids) != 4 or not (set(row["acceptable_active_gaps"]) |
                                         set(row["unacceptable_closed_gaps"]) |
                                         set(row["unsupported_hypothesis_gaps"])) <= gap_ids:
            raise ValueError(row["case_id"])
    (HERE / "review_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    (HERE / "source_aliases.json").write_text(json.dumps(aliases, ensure_ascii=False, indent=2) + "\n")
    print("Stage B cases", len(rows), "qids", len({r["qid"] for r in rows}))


if __name__ == "__main__":
    main()
