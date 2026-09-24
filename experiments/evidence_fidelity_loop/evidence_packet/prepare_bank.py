"""Materialize E1 from frozen historical observations; never create source text."""

import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PRIOR = ROOT / "experiments/gap_evidence_claim_loop"
F1 = json.loads((PRIOR / "finding_extraction/BANK.json").read_text())
F3 = json.loads((PRIOR / "single_gap_rollout/REVIEW_PACKETS.json").read_text())
DB = sqlite3.connect(ROOT / "BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite")


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def source_identity(historical_id, text, historical_title):
    if historical_id.isdigit():
        row = DB.execute("SELECT text,url FROM documents WHERE docid=?", (historical_id,)).fetchone()
        assert row, historical_id
        body, url = row
        match = re.search(r"(?m)^title: (.+)$", body[:500])
        title = historical_title or (match.group(1) if match else "")
        return title, url, historical_id
    # The legacy D# namespace is checkpoint local. Match the observed title to
    # corpus metadata once, without reading future trajectories or gold answers.
    if historical_title:
        rows = DB.execute("SELECT docid,text,url FROM documents WHERE instr(substr(text,1,400),?)>0",
                          ("title: " + historical_title,)).fetchall()
    else:
        needle = "Ding Junhui (; born 1 April 1987)"
        assert needle in text
        rows = DB.execute("SELECT docid,text,url FROM documents WHERE instr(text,?)>0", (needle,)).fetchall()
    assert len(rows) == 1, (historical_id, historical_title, len(rows))
    docid, body, url = rows[0]
    match = re.search(r"(?m)^title: (.+)$", body[:500])
    return historical_title or (match.group(1) if match else ""), url, docid


excluded = {"T2_546", "T2_1094", "T2_580", "T2_387"}
bank = []
for x in F1:
    if x["case_id"] in excluded:
        continue
    w, p = x["new_observation"], x["source_checkpoint"]
    title, url, corpus_id = source_identity(p["historical_doc_ref"], w["text"], w["title"])
    no_gain = x["review"]["no_gain"] or x["review"]["type"] in ("E3", "E8")
    bank.append({
        "case_id": "F1_" + x["case_id"], "qid": x["qid"],
        "historical_origin": {"path": "experiments/gap_evidence_claim_loop/finding_extraction/BANK.json",
                              "case_id": x["case_id"], "checkpoint": p,
                              "metadata_corpus_docid": corpus_id},
        "raw_question": x["raw_question"], "active_gap": x["active_gap"],
        "relevant_committed_claims": x["existing_claims"],
        "observation": {"doc_ref": w["doc_ref"], "title": title, "url": url,
                        "window_ref": w["ref"], "text": w["text"]},
        "category": "M4" if no_gain else "M1",
        "required_findings": x["review"]["required_findings"],
        "forbidden_inferences": x["review"]["forbidden_inferences"],
        "metadata_required": False,
    })


specs = [
    ("P10", "W9", "M3", "What exact album count did the May 2017 Forbes Africa feature report for Oliver Mtukudzi?",
     ["The May 2017 Forbes Africa feature reports that Oliver Mtukudzi had 65 albums."],
     ["The feature reports 67 albums."]),
    ("P05", "W6", "M4", "What exact album count did the May 2017 Forbes Africa feature report for Oliver Mtukudzi?",
     ["Afrikanza reports that Oliver Mtukudzi had produced 65 albums."],
     ["Forbes Africa itself reported 65 albums in this source.", "The 2016 Forbes Africa interview reported 67 albums."]),
    ("P05", "W7", "M4", "What exact album count did the May 2017 Forbes Africa feature report for Oliver Mtukudzi?",
     ["A retrospective article says '67 albums later' while separately quoting Mtukudzi's 2016 Forbes Africa interview."],
     ["Mtukudzi had 67 albums at the time of the 2016 Forbes Africa interview.",
      "The May 2017 Forbes Africa feature reports 67 albums."]),
    ("P07", "W17", "M3", "In the 2014 Nigeria Professional Football League, what were Enugu Rangers' position, points and goal difference?",
     ["The 2014 NPFL table places Enugu Rangers eighth with 58 points and +8 goal difference."],
     ["The table shows Rangers eighth in 2016."]),
    ("P03", "W21", "M2", "What exact credited role did actor Peter King Nzioki play in The Constant Gardener?",
     ["Peter King Nzioki was credited as Policeman 1 in The Constant Gardener (2005)."],
     ["Peter King played Policeman 1 in The Fifth Estate."]),
    ("P12", "W2", "M1", "Which season-one episode shows Jimmy being convinced by Gretchen's friends to take her on a date?",
     ["Insouciance, season 1 episode 2 of You're the Worst, has Jimmy convinced by Gretchen's friends to take her on a date."],
     ["This source establishes the season-three sacrifice."]),
    ("P12", "W4", "M1", "Which season-three finale includes Edgar's sacrifice?",
     ["No Longer Just Us, season 3 episode 13 of You're the Worst, mentions Edgar's sacrifice."],
     ["This source establishes the season-one date scene."]),
]

for rid, ref, category, gap, required, forbidden in specs:
    packet = next(x for x in F3 if x["review_id"] == rid)
    all_results = [z for a in packet["actions"] if a["name"] == "search"
                   for z in a["result"].get("results", [])]
    found = None
    for a in packet["actions"]:
        r = a["result"]
        collection = r.get("results", []) if a["name"] == "search" else r.get("matches", [])
        for z in collection:
            if z.get("preview_ref", z.get("window_ref")) == ref and (z.get("preview") or z.get("text")):
                found = (a, z)
                break
        if found:
            break
    assert found, (rid, ref)
    action, z = found
    doc_ref = z.get("doc_ref", action["result"].get("doc_ref"))
    identity = next((s for s in all_results if s["doc_ref"] == doc_ref and s.get("url")), None)
    assert identity, (rid, ref, doc_ref)
    bank.append({
        "case_id": f"F3_{rid}_{ref}", "qid": packet["qid"],
        "historical_origin": {"path": "experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json",
                              "review_id": rid, "window_ref": ref,
                              "text_sha256": sha(z.get("preview") or z.get("text"))},
        "raw_question": packet["raw_question"], "active_gap": gap,
        "relevant_committed_claims": [],
        "observation": {"doc_ref": doc_ref, "title": identity.get("title", ""),
                        "url": identity["url"], "window_ref": ref,
                        "text": z.get("preview") or z.get("text")},
        "category": category, "required_findings": required,
        "forbidden_inferences": forbidden,
        "metadata_required": category in ("M2", "M3"),
    })

assert len(bank) == 44 and len({x["qid"] for x in bank}) == 12
assert {x["category"] for x in bank} == {"M1", "M2", "M3", "M4"}
assert all(x["observation"]["url"] and x["observation"]["text"] for x in bank)
(HERE / "BANK.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
print("cases", len(bank), "qids", len({x["qid"] for x in bank}))
