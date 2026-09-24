"""Freeze 24 distinct real corpus-window prefixes for multi-Gap F1."""

import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
E1 = {x["case_id"]: x for x in json.loads((ROOT / "experiments/evidence_fidelity_loop/evidence_packet/BANK.json").read_text())}
V1 = {x["candidate_id"]: x for x in json.loads((ROOT / "experiments/minimal_research_loop/verify_necessity/CANDIDATES.json").read_text())}
LABELS = {x["candidate_id"]: x for x in json.loads((ROOT / "experiments/minimal_research_loop/verify_necessity/ANNOTATIONS.json").read_text())}
SQLITE = ROOT / "BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite"

SELECTED = [
    "F1_T1_546", "F1_T4_546", "F1_T5_546",
    "F1_T1_1094", "F1_T3_1094", "F1_T4_1094",
    "F1_T1_517", "F1_T4_517",
    "F1_T1_435", "F1_T2_435", "F3_P10_W9", "F3_P05_W6",
    "F1_T1_580", "F3_P12_W2", "F3_P12_W4",
    "F1_T1_177", "F1_T4_177", "F3_P07_W17",
    "F1_T1_1034", "F1_T4_186", "F1_T5_186",
    "F1_T4_311", "F1_T5_311", "F1_T1_387",
]

GAPS = {
    "546": ["Did the tentative player meet the professional-start, century and maximum-break conditions?", "What was the linked 2023 opening decider, later 4-3, 4-0, loss match sequence?", "Did the relevant opponents meet the question's century-count conditions?"],
    "1094": ["Which real fixture had the 95th-minute free kick, and who took it?", "Do the clubs in that fixture meet the split-founded and changing-identity history clues?", "Did the fixture's goal chronology match the question?"],
    "517": ["Which candidate matches the 1970s birth and parental-occupation clues?", "Did that candidate play a policeman in the specified 2005 film?", "Did the same actor appear in the specified 2013 thriller with the stated director?"],
    "435": ["Which musician matches the death-age and career clues?", "What exact album count did the May 2017 Forbes Africa feature report for that musician?", "Does the musician match the political song, activism and interview clues?"],
    "580": ["Which series and Season 1 episode match the early date scene?", "Which series and Season 3 episode establish the roommate sacrifice?", "Which series and Season 4 episode establish the birth return?", "Are all three plot events linked to the same series in the stated order?"],
    "177": ["Which team meets the historical tied-points position and goal-difference table clues?", "Does that team match the signing, city and trophy clues?", "What are that team's founding year and country?"],
    "1034": ["Which person matches the model and singer clue?", "What are that person's birth name, university study and child's birthplace?", "Did that person hold the specified coordinator and manager roles?"],
    "186": ["Which game matches the amphibian-named developer clue?", "Does that game meet the release, platform, player-mode and shareware clues?", "Who are the three credited people and which two share a surname?", "What was that developer's earlier company name?"],
    "311": ["Which television program meets the title, director and writer clues?", "Does it meet the broadcast, schedule, episode-count and duration clues?", "Does it match the educational, character and origin clues?"],
    "387": ["Who animated the named second game's intro and ending, and how is that game linked to the first game's company?", "What gaming PC, keyboard and storage did that animator have?", "Did that animator draw the intro and ending on ordinary 8x11-inch paper?"],
}

# Only a Claim-supported local subproblem is removed from the open-Gap list.
CLOSED = {
    "F1_T5_546": [1], "F1_T1_1094": [1], "F1_T1_517": [1],
    "F3_P10_W9": [2], "F1_T1_580": [3], "F3_P12_W2": [1], "F1_T1_1034": [1],
    "F1_T5_186": [2, 3], "F1_T1_387": [2],
}

PREFERRED = {
    "F1_T1_546": 2, "F1_T4_546": 2, "F1_T5_546": 2,
    "F1_T1_1094": 2, "F1_T3_1094": 1, "F1_T4_1094": 1,
    "F1_T1_517": 2, "F1_T4_517": 1,
    "F1_T1_435": 2, "F1_T2_435": 1, "F3_P10_W9": 3, "F3_P05_W6": 2,
    "F1_T1_580": 1, "F3_P12_W2": 2, "F3_P12_W4": 1,
    "F1_T1_177": 1, "F1_T4_177": 1, "F3_P07_W17": 3,
    "F1_T1_1034": 2, "F1_T4_186": 1, "F1_T5_186": 4,
    "F1_T4_311": 1, "F1_T5_311": 2, "F1_T1_387": 3,
}


def main():
    target = HERE / "BANK.json"
    if target.exists():
        raise FileExistsError(target)
    assert len(SELECTED) == 24 and len(set(SELECTED)) == 24
    rows, seen_docs = [], set()
    with sqlite3.connect(f"{SQLITE.as_uri()}?mode=ro", uri=True) as db:
        for sid in SELECTED:
            source = E1[sid]
            qid = source["qid"]
            old = source["observation"]
            docid = source["historical_origin"].get("metadata_corpus_docid")
            if docid is None:
                matches = db.execute("select docid from documents where url=?", (old["url"],)).fetchall()
                assert len(matches) == 1, sid
                docid = matches[0][0]
            text, url = db.execute("select text,url from documents where docid=?", (docid,)).fetchone()
            assert url == old["url"] and text.count(old["text"]) == 1, sid
            assert (qid, docid) not in seen_docs, sid
            seen_docs.add((qid, docid))
            observation = dict(old)
            observation["doc_ref"] = "D1"
            observation["window_ref"] = "W1"
            claims = []
            for candidate in V1.values():
                if candidate["case_id"] != "E1_" + sid:
                    continue
                if not LABELS[candidate["candidate_id"]]["source_supported"]:
                    continue
                if any(c["statement"] == candidate["finding"] for c in claims):
                    continue
                claims.append({"claim_id": "C" + str(len(claims)+1),
                               "statement": candidate["finding"], "evidence_refs": ["W1"]})
            gaps = [{"gap_id": f"G{i}", "question": question}
                    for i, question in enumerate(GAPS[qid], 1) if i not in CLOSED.get(sid, [])]
            assert 2 <= len(gaps) <= 4, sid
            assert f"G{PREFERRED[sid]}" in {g["gap_id"] for g in gaps}, sid
            rows.append({"case_id": "F1_" + sid, "qid": qid,
                         "raw_question": source["raw_question"],
                         "committed_claims": claims, "open_gaps": gaps,
                         "workspace": {"known_documents": [{"doc_ref": "D1", "title": old["title"],
                                                              "url": old["url"], "date": old.get("date", "")}],
                                       "observed_windows": [observation]},
                         "working_hypothesis": None,
                         "review": {"eligible_gaps": [g["gap_id"] for g in gaps],
                                    "preferred_next_gap": f"G{PREFERRED[sid]}",
                                    "reason": "The preferred Gap addresses an unresolved question constraint from the current prefix; every listed open Gap remains eligible."},
                         "provenance": {"historical_e1_case": sid, "corpus_docid": docid,
                                        "corpus_text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                                        "source_window_sha256": hashlib.sha256(old["text"].encode()).hexdigest(),
                                        "source_offset": text.index(old["text"]),
                                        "source_window_ref": old["window_ref"],
                                        "source_doc_ref": old["doc_ref"]}})
    assert len(rows) == 24 and len({x["qid"] for x in rows}) == 10
    target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
    print("F1 cases", len(rows), "qids", len({x["qid"] for x in rows}))


if __name__ == "__main__":
    main()
