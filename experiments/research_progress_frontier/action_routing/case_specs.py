"""Frozen low-ambiguity Stage C progress-state diagnoses.

Five cases per uncertainty class. Complete cases are explicitly local diagnostic
subtasks with all claims in that local scope verified; they are not claims that
the original multi-hop BrowseComp question was solved.
"""


def c(cid, qid, kind, checkpoint, gap, claim, source_type, doc="none", window="none",
      refs=(), verification="not_applicable", action=None, scope="current research gap"):
    expected = action or {"source": "search", "location": "find", "context": "open",
                          "closure": "verify", "complete": "submit"}[kind]
    return {"case_id": cid, "qid": qid, "uncertainty_type_private": kind,
            "checkpoint": checkpoint, "diagnostic_scope": scope,
            "active_gap": gap, "claim_ref": "C1", "current_claim_status": claim,
            "expected_source_type": source_type, "known_suitable_document": doc,
            "known_relevant_window": window, "current_evidence_refs": list(refs),
            "verification_status": verification, "expected_action": expected}


SPECS = [
    # Source missing: no currently observed suitable document for the active gap.
    c("C_source_546", "546", "source", "R1:25", "Find the linked 2023 decider, later 4-3, 4-0 and loss sequence for one player.",
      "C1: open — only Ding's opening 4-3 win is observed.", "dated round-by-round snooker tournament results"),
    c("C_source_1094", "1094", "source", "R1:45", "Find Lille founding/name history to test the PSG–Lille club-identity hypothesis.",
      "C1: open — PSG–Lille's club histories have not been linked to the question.", "club founding and name-history source"),
    c("C_source_580", "580", "source", "event:2", "Test the proposed series against the season-one date scene.",
      "C1: open — only a season-four episode is observed.", "season-one episode guide"),
    c("C_source_177", "177", "source", "event:2", "Locate the 2011–2016 league table with tied points, position and goal difference.",
      "C1: open — signing-count article has no such standings.", "dated historical league standings"),
    c("C_source_1034", "1034", "source", "event:2", "Test Heart Evangelista's university study and her child's birthplace.",
      "C1: open — observed profile lacks both conditions.", "biography or family interview"),

    # Suitable document already known; desired location is not known.
    c("C_location_546_bio", "546", "location", "R1:33", "Locate Ding Junhui's professional-start year and career break totals inside his biography.",
      "C1: open — D17 is a player biography, but the relevant statistics are not at the observed W31 passage.",
      "player career biography", doc="D17"),
    c("C_location_546_results", "546", "location", "R1:17", "Locate a 2023 British Open 4-0 match result elsewhere in the observed tournament table.",
      "C1: open — D11 is a tournament-results document; the observed W14 rows do not show this requested match.",
      "round-by-round tournament results", doc="D11"),
    c("C_location_517", "517", "location", "event:16", "Locate Peter Nzioki's specific Constant Gardener character in his biography.",
      "C1: open — D1 names the film, but the observed window does not give the character.", "actor biography/filmography", doc="D1"),
    c("C_location_435", "435", "location", "event:12", "Locate Oliver Mtukudzi's first-album period and exact album total in his observed profile.",
      "C1: open — D2 discusses his career but the local excerpt says only over 60 albums.", "artist biography", doc="D2"),
    c("C_location_387", "387", "location", "event:2", "Locate the 8x11-inch paper passage within Dean Dodrill's observed interview.",
      "C1: open — D1 is his setup interview, but the current window ends at the animation light table.",
      "animator interview", doc="D1"),

    # Relevant current window known, but adjacent context is needed.
    c("C_context_1094", "1094", "context", "R1:45", "Read what follows W38's opening PSG–Lille goal description to assess later scoring chronology.",
      "C1: open — W38 is the relevant fixture article but its visible span ends during the goal narrative.",
      "fixture report", doc="D34", window="W38", refs=("W38",)),
    c("C_context_546", "546", "context", "R1:17", "Read adjacent rows around W14 to identify the neighboring dated match in this tournament table.",
      "C1: open — W14 contains a partial result table and adjacent entries are needed.",
      "tournament results table", doc="D11", window="W14", refs=("W14",)),
    c("C_context_517", "517", "context", "event:16", "Read the biography continuation immediately after the current Peter Nzioki career paragraph.",
      "C1: open — the relevant W1 biography passage ends during early career details.",
      "actor biography", doc="D1", window="W1", refs=("W1",)),
    c("C_context_387", "387", "context", "event:2", "Read the interview continuation after the animation light-table paragraph.",
      "C1: open — W1 ends immediately after introducing Dean's animation work area.",
      "animator interview", doc="D1", window="W1", refs=("W1",)),
    c("C_context_580", "580", "context", "event:2", "Read adjacent episode synopsis context for why the friend says Jimmy left Gretchen.",
      "C1: open — W1 says the friend reveals why, but the observed span does not state the reason.",
      "episode synopsis", doc="D1", window="W1", refs=("W1",)),

    # Exact evidence is present; closure decision awaits semantic verification.
    c("C_closure_546", "546", "closure", "R1:25", "Decide whether Ding beat Ma Hailong 4-3 in the 2023 English Open opener.",
      "C1: open pending verification — W13 is visible and directly discusses the result.",
      "currently observed evidence", doc="D10", window="W13", refs=("W13",), verification="not_verified"),
    c("C_closure_1094", "1094", "closure", "R1:45", "Decide whether a 1908 AC Milan split formed Internazionale.",
      "C1: open pending verification — W42 is visible and directly discusses the split.",
      "currently observed evidence", doc="D37", window="W42", refs=("W42",), verification="not_verified"),
    c("C_closure_517", "517", "closure", "event:16", "Decide whether Peter Nzioki was born in 1978 to an army father and hospital-worker mother.",
      "C1: open pending verification — W1 contains the candidate biography.",
      "currently observed evidence", doc="D1", window="W1", refs=("W1",), verification="not_verified"),
    c("C_closure_435", "435", "closure", "event:12", "Decide whether Oliver Mtukudzi died at age 66.",
      "C1: open pending verification — W2 is a relevant obituary.",
      "currently observed evidence", doc="D2", window="W2", refs=("W2",), verification="not_verified"),
    c("C_closure_177", "177", "closure", "event:2", "Decide whether Rangers signed 13 players ahead of 2022/23.",
      "C1: open pending verification — W1 is the observed signing article.",
      "currently observed evidence", doc="D1", window="W1", refs=("W1",), verification="not_verified"),

    # Synthetic complete *local* tasks, explicitly not full original-question completion.
    c("C_complete_546", "546", "complete", "R1:25", "none — local opening-result subtask is complete",
      "C1: supported and verified — Ding beat Ma Hailong 4-3; no local open claim remains.",
      "none", refs=("W13",), verification="verified", scope="local opening-result subtask"),
    c("C_complete_1094", "1094", "complete", "R1:45", "none — local club-origin subtask is complete",
      "C1: supported and verified — Internazionale formed after the 1908 Milan split; no local open claim remains.",
      "none", refs=("W42",), verification="verified", scope="local club-origin subtask"),
    c("C_complete_517", "517", "complete", "event:16", "none — local birth-year subtask is complete",
      "C1: supported and verified — Peter Nzioki was born in 1978; no local open claim remains.",
      "none", refs=("W1",), verification="verified", scope="local birth-year subtask"),
    c("C_complete_435", "435", "complete", "event:12", "none — local age-at-death subtask is complete",
      "C1: supported and verified — Oliver Mtukudzi died at 66; no local open claim remains.",
      "none", refs=("W2",), verification="verified", scope="local age-at-death subtask"),
    c("C_complete_580", "580", "complete", "event:2", "none — local season-four plot subtask is complete",
      "C1: supported and verified — Gretchen returned for her brother's baby's birth; no local open claim remains.",
      "none", refs=("W1",), verification="verified", scope="local season-four plot subtask"),
]

# Fixed before any C model call; Stage D selection ignores observed C performance.
STAGE_D_PRESELECTION = [
    "C_source_546", "C_source_1094",
    "C_location_546_bio", "C_location_546_results",
    "C_context_1094", "C_context_546",
    "C_closure_546", "C_closure_1094",
]
