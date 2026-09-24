"""Transcribe prefix-only single-reviewer labels before any V1 Verify call."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATES = json.loads((HERE / "CANDIDATES.json").read_text())

# All 55 statements were read with their current W, metadata, Gap and Claims.
# These are the only exceptions to directly supported, new, Gap-material facts.
SOURCE_UNSUPPORTED = {
    "E1_F3_P05_W7:F0": "A 2019 retrospective places '67 albums later' beside a 2016 interview quote; it does not establish that the count belonged to the interview time.",
    "E1_F3_P12_W4:F0": "The observed title says season 3 episode 13 and the body mentions Edgar's sacrifice, but neither states that this episode was the season finale.",
}
GAP_IRRELEVANT = {
    "E1_F1_T3_177:F2": "A fifth-place finish in an unspecified prior season does not establish the requested historical tied-points table clue.",
    "E1_F1_T1_387:F2": "PC storage capacity does not advance the gaming-PC and wireless-keyboard Gap.",
    "E1_F1_T6_546:F0": "The opening 4-3 result is already committed; a forfeited opening frame does not establish a subsequent match in the required sequence.",
    "E1_F1_T6_546:F1": "Opening-match comeback breaks do not establish any later linked match result.",
    "E1_F3_P05_W7:F0": "A retrospective 67-album phrase and 2016 quote do not answer the May 2017 Forbes Africa feature-count Gap.",
    "F3_P12_W3:F1": "Series creator and generic genre do not verify either season-specific plot clue.",
    "F3_P12_W5:F0": "Being a main character does not verify the season-three roommate sacrifice; the Reader omitted the source's roommate relation.",
}
NOVELTY_DUPLICATE = {}

ids = {c["candidate_id"] for c in CANDIDATES}
assert set(SOURCE_UNSUPPORTED) <= ids and set(GAP_IRRELEVANT) <= ids
labels = []
for c in CANDIDATES:
    cid = c["candidate_id"]
    supported = cid not in SOURCE_UNSUPPORTED
    relevant = cid not in GAP_IRRELEVANT
    novel = cid not in NOVELTY_DUPLICATE
    labels.append({"candidate_id": cid, "source_supported": supported,
                   "gap_relevant": relevant, "novel": novel,
                   "claim_eligible": supported and relevant and novel,
                   "source_reason": SOURCE_UNSUPPORTED.get(cid, "All substantive factual parts are directly supported by this W and authentic source metadata."),
                   "relevance_reason": GAP_IRRELEVANT.get(cid, "Material to the current Active Gap."),
                   "novelty_reason": NOVELTY_DUPLICATE.get(cid, "Not adequately represented by existing committed Claims."),
                   "reviewer": "Codex single-reviewer prefix-only semantic audit"})
assert len(labels) == 55
(HERE / "ANNOTATIONS.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2) + "\n")
print("supported", sum(x["source_supported"] for x in labels), "/55",
      "eligible", sum(x["claim_eligible"] for x in labels), "/55")
