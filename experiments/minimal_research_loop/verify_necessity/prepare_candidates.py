"""Freeze every natural Reader Finding with Harness-owned source W."""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = json.loads((HERE / "OBSERVATIONS.json").read_text())
OUTCOMES = json.loads((HERE / "reader_outcomes.json").read_text())


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


assert len(PACKETS) == len(OUTCOMES) == 52
candidates = []
for p in PACKETS:
    cid = p["case_id"]
    out = OUTCOMES[cid]
    assert out["source_window"] == p["observation"]["window_ref"]
    for i, f in enumerate(out["output"]["findings"]):
        assert set(f) == {"statement"}
        candidates.append({"candidate_id": f"{cid}:F{i}", "case_id": cid, "qid": p["qid"],
                           "raw_question": p["raw_question"], "active_gap": p["active_gap"],
                           "relevant_committed_claims": p["relevant_committed_claims"],
                           "observation": p["observation"],
                           "finding": f["statement"],
                           "harness_source_window": out["source_window"],
                           "reader_response_hash": digest(out["output"])})
assert len(candidates) == 55 and len({c["candidate_id"] for c in candidates}) == 55
(HERE / "CANDIDATES.json").write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n")
print("candidates", len(candidates), "qids", len({c["qid"] for c in candidates}))
