"""Transcribe the single-reviewer E1 semantic audit against frozen packet truth."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = json.loads((HERE / "BANK.json").read_text())
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())

# Manually checked against the exact T/P request and the frozen full packet.
# Every other emitted finding in the 88-cell transcript is source-supported and
# materially Gap-relevant. The four listed findings are source-supported but
# fail the pre-registered novelty / Gap relevance requirement.
OFF_GAP = {
    ("F1_T3_1094", "P", 0): "AC Milan's split does not establish either PSG or Lille history.",
    ("F1_T4_311", "P", 0): "A children's song title does not answer the requested television-program title.",
    ("F1_T6_546", "P", 0): "The opening 4–3 result is already a committed Claim; the first-frame detail does not establish a later match.",
    ("F1_T6_546", "P", 1): "Opening-match breaks do not establish any later linked result.",
}

# Required-finding indices missed despite the full output being reviewed.
MISSED = {
    ("F1_T5_186", "P"): [1],  # single-player was said, shareware was not
    ("F3_P05_W7", "T"): [0],
    ("F3_P05_W7", "P"): [0],
    ("F3_P10_W9", "T"): [0],  # original Forbes Africa source unseen
    ("F3_P07_W17", "T"): [0],  # 2014 existed only in the unseen title
    ("F3_P03_W21", "T"): [0],  # Peter King identity existed only in unseen D title
}

reviews = {}
for case in BANK:
    cid = case["case_id"]
    for arm in ("T", "P"):
        cell = f"{cid}:{arm}"
        outcome = OUTCOMES[cell]
        findings = outcome["output"]["findings"]
        rows = []
        for i, finding in enumerate(findings):
            off_gap = OFF_GAP.get((cid, arm, i))
            rows.append({"finding_index": i, "statement": finding["statement"],
                         "source_supported": True, "gap_relevant_and_new": off_gap is None,
                         "metadata_overreach": False,
                         "reason": off_gap or "Checked against the supplied observation, its visible metadata, active Gap, and committed Claims."})
        missing = MISSED.get((cid, arm), [])
        assert all(0 <= i < len(case["required_findings"]) for i in missing), cell
        if not findings:
            assert set(missing) == set(range(len(case["required_findings"]))), cell
        reviews[cell] = {"case_id": cid, "arm": arm, "error": outcome["error"],
                         "findings": rows,
                         "required_finding_hits": [i not in missing for i in range(len(case["required_findings"]))],
                         "required_finding_text": case["required_findings"],
                         "reviewer": "Codex single-reviewer semantic audit"}

assert len(reviews) == 88
(HERE / "REVIEWS.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n")
