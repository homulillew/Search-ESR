"""Transcribe single-reviewer semantic sufficiency of every V1 pointer."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK = json.loads((HERE / "BANK.json").read_text())
OUTCOMES = json.loads((HERE / "outcomes.json").read_text())

# The other mechanically valid supported V1 pointers were individually read
# against their exact text slices plus only their listed metadata fields.
INSUFFICIENT = {
    "S1_01": "The span juxtaposes '67 albums later' with a quotation from 2016 but does not date the 67-album count to that interview.",
    "A_F1_T5_517_2": "The pointed span says only 'Nzioki' and 'his mother'; neither pointer nor listed metadata establishes the full Peter King Nzioki identity.",
}
reviews = {}
for c in BANK:
    cell = c["case_id"] + ":V1"
    outcome = OUTCOMES[cell]
    value = outcome["output"]
    if value is None or value["verdict"] != "supported":
        reviews[cell] = {"pointer_sufficient": False, "reason": "No supported V1 verdict; no Claim can be committed."}
        continue
    if not outcome["mechanical_valid"]:
        reviews[cell] = {"pointer_sufficient": False,
                         "reason": "Mechanical pointer rejection: " + str(outcome["mechanical_error"])}
        continue
    slices = [c["observation"]["text"][s["start"]:s["end"]] for s in value["support"]]
    missing = INSUFFICIENT.get(c["case_id"])
    reviews[cell] = {"pointer_sufficient": missing is None,
                     "reason": missing or "The exact pointed text and explicitly listed metadata jointly establish all substantive parts of the Finding.",
                     "support_slices": slices,
                     "metadata_used": {m: c["observation"][m] for m in value["source_metadata_used"]}}

assert len(reviews) == 68
assert sum(not r["pointer_sufficient"] for r in reviews.values()
           if r.get("support_slices")) == len(INSUFFICIENT)
(HERE / "REVIEWS.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n")
