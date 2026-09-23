"""Single-reviewer, arm-blind A1 annotations against frozen packets and rubric.

Each entry is review_id: (failure-codes per proposed Claim, coverage booleans, reason).
A task anchor; G active-gap relevance; T concrete testability; P no unsupported
specific commitment; R nonredundancy; M minimality. An absent code passes.
The reviewer sees only REVIEW_PACKETS.json; no PRIVATE_MAPPING.json is used here.
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = json.loads((HERE / "REVIEW_PACKETS.json").read_text())
FAILURE = {
    "A": "The cited near-verbatim anchor does not cover this proposition.",
    "G": "This proposition does not advance the active Gap.",
    "T": "The wording is not a concrete falsifiable candidate proposition.",
    "P": "It commits to an exact entity, date, score, or relation absent from the visible prefix and question.",
    "R": "An adequate existing Claim already registers this proposition.",
    "M": "It adds state without a necessary new verification condition.",
}

# The order of entries inside each case is the packet's original proposal order.
DECISIONS = {
    # 546: W1 reports only the opening Ma Hailong match; later opponents/dates are unseen.
    "R4e362417a800": (["GMR"], [False], "Opening-match restatement adds no later-sequence check."),
    "Rdff4fceeb14d": (["GM", "GM"], [False], "Two observed opening-match details leave later results unregistered."),
    "R2e1a96ce6f1c": (["P"], [False], "Exact later opponents and dates are absent from the prefix."),
    "Re42f7ca30349": (["P", "P", "P"], [False], "All three precise later matches are unsupported by W1 or the question."),
    "Raabaf174b683": (["P"], [False], "The detailed later sequence is an unsupported commitment."),
    "R5ecdb552591a": (["GMR", "GMR"], [False], "The already registered opener is copied into extra Claims."),

    # 1094: T1/T2 W1 is PSG–Lille; T3 W1 is an AC Milan history excerpt.
    "Rfb2177bb06a9": (["P", "P"], [False, False], "The specific founding/merger examples have no visible support."),
    "Re0bb6369be1d": (["GM", "", ""], [True, True], "One fixture summary is extra; the two open club-history tests fit G2."),
    "R41b0352b0356": (["GM", "GM"], [False, False], "Free-kick and fixture facts are local W1 facts, not club-history checks."),
    "R4671da93592a": (["", ""], [True, True], "Two bounded open club-history propositions map to the two anchors."),
    "Rdfae38452612": (["", ""], [True, True], "Two club-history propositions are testable without asserting a verified result."),
    "R72451a079ca3": (["GTM", "GTPM"], [False, False], "Alternative 'may be' entities belong in hypotheses; the single spelling note cannot establish several identity iterations."),

    # 517: W1 has a film-debut mention but no exact cast character.
    "Rd90773e2ee57": (["GM", "GTM", "AGM"], [True], "Existing C1 already registers the exact role; extra W1 biography is not G2 admission."),
    "R9b0741331d22": ([], [False], "Output failed anchor validation; no Claim was admitted."),
    "Rdde971ed85ae": ([""], [True], "The question supplies the policeman clue and W1 links the candidate to the film."),
    "Rd1783c68c345": ([""], [True], "Exact cast credit is the active testable condition."),
    "Rf0f308772f8c": (["R"], [True], "The same policeman-role proposition already exists as C1."),
    "R581f023e9d1a": (["AGM", "GM", "AGM"], [False], "Observed name and other film facts do not specify the missing character."),

    # 435: W1 supplies only >60 albums and career span, not the exact feature count/debut.
    "R00ab550ec97a": (["GM", "GM"], [False, False], "Observed lower bound and career span cannot register the exact G2 conditions."),
    "Rdf11aa7bd7c7": (["", ""], [True, True], "Question-stated 67 albums and 1970s debut are bounded open tests."),
    "Rca701b147aab": (["GPM", "P", "P"], [False, False], "Oliver identity and exact 1978/May-2015 count are absent from this Miriam packet."),
    "R6aaca8f875a6": (["GM", "GM"], [False, False], "W1 caveats are source notes, not exact album/debut Claims."),
    "Rbc7a4040e059": (["GM"], [False, False], "Excluding Miriam by age does not test her album/debut G2 conditions."),
    "Rf2c15a80b49c": (["P", "P"], [False, False], "Neither exact Forbes count nor 1975 debut is visible."),

    # 580: W1 contains only the season-four episode; proposed season-one episode IDs are unseen.
    "Rf404c6ad4b40": (["GM", "GM"], [False], "Season-four summary/cast does not test the season-one scene."),
    "Ra722e09ab35a": (["P"], [False], "Exact season-one title and number are unsupported."),
    "R4f8bcec1db29": ([], [False], "Output failed anchor validation; no Claim was admitted."),
    "R4c03a629272d": (["P"], [False], "Exact season-one title and number are unsupported."),
    "Rdc3abce40664": (["GM", "GMR", "GM"], [False], "All three Claims repackage season-four observations outside G2."),
    "R4cde2e0b3093": (["P"], [False], "The asserted season-one episode title is absent from W1."),

    # 177: W1 is a 2022/23 signing article, not the historical standings table.
    "R16396ffef8ab": (["TM"], [False, False], "Circular whole-question conjunction lacks a named team and dated row to test."),
    "R5f70586c5154": ([], [False, False], "Output failed anchor validation; no Claim was admitted."),
    "R65927669a046": (["GM", "GM", "GMR"], [False, False], "State expands around local city/recent season facts without a historical table check."),
    "Rb7c11c5e9029": (["GP"], [False, False], "Uganda/Express standings are unsupported and unrelated to registered Rangers lead."),
    "R88e497723378": (["P"], [False, False], "The exact 2015 NPFL row is not present in W1."),
    "R5b46fa5d8333": ([], [False, False], "Output failed anchor validation; no Claim was admitted."),

    # 1034: W1 concerns Heart's early career, with no education or child evidence.
    "Rc1455a300b3c": (["", ""], [True, True], "Separating the two question conditions yields individually testable open Claims."),
    "Ra397a5db273d": (["TM", "TM"], [False, False], "Unnamed target restatements do not test the observed candidate."),
    "R948c64a5256d": (["TM", "TM"], [False, False], "Unnamed target restatements do not test the observed candidate."),
    "R27b2b4b39c6c": ([], [False, False], "Output failed anchor validation; no Claim was admitted."),
    "Rfba33d12acc4": (["GTM"], [False, False], "Candidate rejection is a working-hypothesis update, not education/child Claim Admission."),
    "R498192e5f129": ([], [False, False], "Output failed anchor validation; no Claim was admitted."),

    # 387: W1 supplies gaming PC/storage; Game B animation and paper are not in it.
    "Rad62fbf05300": (["GM", "AGM"], [False, False], "Equipment and answer-size facts do not resolve the animation/paper Gap."),
    "R1778221990eb": (["AGM"], [False, False], "Storage is a final-answer fact outside the active animation/paper Gap."),
    "Rcb241f3647ef": ([], [False, False], "No new Claim covers the still-open animation/paper checks."),
    "Rbdeae76230d5": (["", ""], [True, True], "Two question-stated, candidate-specific verification conditions cover G2."),
    "R81a32b3b2a42": (["AGM", "GMR"], [False, False], "Observed storage and keyboard facts bypass the missing Game B link."),
    "R5a6be6c24278": (["P", ""], [False, True], "Jazz Jackrabbit 2 identification is unseen; the paper-size test is question anchored."),
}


def main():
    if set(DECISIONS) != {p["review_id"] for p in PACKETS}:
        missing = {p["review_id"] for p in PACKETS} - set(DECISIONS)
        extra = set(DECISIONS) - {p["review_id"] for p in PACKETS}
        raise ValueError((missing, extra))
    reviews = {}
    for p in PACKETS:
        rid = p["review_id"]
        failures, coverage, reason = DECISIONS[rid]
        if len(failures) != len(p["proposed_claims"]) or len(coverage) != len(p["coverage_requirements"]):
            raise ValueError(rid)
        claim_reviews = []
        for codes in failures:
            if set(codes) - set(FAILURE):
                raise ValueError((rid, codes))
            claim_reviews.append({
                "task_anchored": "A" not in codes,
                "gap_relevant": "G" not in codes,
                "testable": "T" not in codes,
                "no_premature_commitment": "P" not in codes,
                "nonredundant": "R" not in codes,
                "minimal": "M" not in codes,
                "semantically_plausible": True,
                "reason": " ".join(FAILURE[k] for k in codes) if codes else "A bounded, testable condition for the active Gap.",
            })
        reviews[rid] = {"claim_reviews": claim_reviews, "coverage": coverage, "reason": reason}
    (HERE / "REVIEWS.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
