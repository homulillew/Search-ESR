"""Create S1 Search requests from frozen V2 query text and reviewer labels."""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V2 = ROOT / "experiments/variable_preserving_state/query_bias"


def despeculate(query, values):
    result = query
    for value in values:
        if not value or value not in result:
            raise ValueError(f"Frozen leaking value is not an exact query substring: {value!r}")
        result = result.replace(value, "")
    result = result.replace('""', '').replace("''", '')
    result = re.sub(r'([,;:])\s*\1+', r'\1', result)
    result = " ".join(result.split()).strip(" ,;:")
    if not result or result == query:
        raise ValueError("Degenerate or unchanged D query")
    return result


def prepare():
    path = HERE / "BANK.json"
    if path.exists():
        raise FileExistsError(path)
    results = json.loads((V2 / "results.json").read_text())["rows"]
    cases = {c["case_id"]: c for c in json.loads((V2 / "V2_CASES.json").read_text())}
    assert len(results) == 48 and len(cases) == 16
    bank = []
    for row in results:
        cid, arm, query = row["case_id"], row["arm"], row["query"]
        assert arm in ("Q0", "Q1", "Q2") and isinstance(query, str) and query
        review = row["review"]
        values = review["leaking_values"]
        assert review["unsupported_binding_leakage"] == bool(values)
        common = {"source_cell": f"{cid}:{arm}", "case_id": cid, "qid": cases[cid]["qid"],
                  "v2_arm": arm, "frozen_leaking_values": values}
        bank.append({**common, "search_id": f"{cid}:{arm}:S", "variant": "S", "query": query})
        if values:
            bank.append({**common, "search_id": f"{cid}:{arm}:D", "variant": "D",
                         "query": despeculate(query, values)})
    assert len({b["search_id"] for b in bank}) == len(bank)
    assert len([b for b in bank if b["variant"] == "S"]) == 48
    assert len([b for b in bank if b["variant"] == "D"]) == sum(bool(r["review"]["leaking_values"]) for r in results)
    path.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    prepare()
