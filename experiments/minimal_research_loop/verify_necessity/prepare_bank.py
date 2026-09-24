"""Select 52 genuine historical W packets before any V1 Reader call."""

import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
E1 = json.loads((ROOT / "experiments/evidence_fidelity_loop/evidence_packet/BANK.json").read_text())
F3 = json.loads((ROOT / "experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json").read_text())


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def date_from(text):
    m = re.search(r"(?m)^date: ([^\n]+)$", text[:650])
    return m.group(1).strip() if m else ""


bank = []
for x in E1:
    w = x["observation"]
    bank.append({"case_id": "E1_" + x["case_id"], "qid": x["qid"],
                 "historical_origin": {"path": "experiments/evidence_fidelity_loop/evidence_packet/BANK.json",
                                       "case_id": x["case_id"], "text_sha256": sha(w["text"])},
                 "raw_question": x["raw_question"], "active_gap": x["active_gap"],
                 "relevant_committed_claims": x["relevant_committed_claims"],
                 "observation": {**w, "date": date_from(w["text"])},
                 "sampling_stratum": x["category"]})

# Frozen extra genuine Search previews. Chosen for direct, partial, NoGain,
# metadata and identity traps; no source text is created or edited.
EXTRA = [("P12", "W3"), ("P12", "W5"), ("P07", "W12"), ("P07", "W16"),
         ("P11", "W3"), ("P10", "W11"), ("P08", "W36"), ("P04", "W73")]
for rid, ref in EXTRA:
    packet = next(p for p in F3 if p["review_id"] == rid)
    matches = [(ai, z) for ai, a in enumerate(packet["actions"]) if a["name"] == "search"
               for z in a["result"].get("results", [])
               if z.get("preview_ref") == ref and z.get("preview")]
    assert len(matches) == 1, (rid, ref, len(matches))
    action_index, z = matches[0]
    w = {"doc_ref": z["doc_ref"], "window_ref": z["preview_ref"],
         "title": z.get("title", ""), "url": z.get("url", ""),
         "date": date_from(z["preview"]), "text": z["preview"]}
    bank.append({"case_id": f"F3_{rid}_{ref}", "qid": packet["qid"],
                 "historical_origin": {"path": "experiments/gap_evidence_claim_loop/single_gap_rollout/REVIEW_PACKETS.json",
                                       "review_id": rid, "action_index": action_index,
                                       "window_ref": ref, "text_sha256": sha(w["text"])},
                 "raw_question": packet["raw_question"],
                 "active_gap": packet["active_gap"],
                 "relevant_committed_claims": packet["seed_claims"],
                 "observation": w, "sampling_stratum": "F3_real_search_preview"})

# Materialize publication date only from the deterministic corpus registry.
# A missing date stays empty; source body beyond the observed W is never copied.
needed = {c["observation"]["url"] for c in bank if c["observation"]["url"]}
registry_dates = {}
db = sqlite3.connect(ROOT / "BCPlus/indexes/bcplus-qwen3-8b/documents.sqlite")
for docid, body, url in db.execute("SELECT docid,text,url FROM documents"):
    if url in needed:
        registry_dates[url] = date_from(body)
        if len(registry_dates) == len(needed):
            break
for c in bank:
    w = c["observation"]
    if not w["date"]:
        w["date"] = registry_dates.get(w["url"], "")
    assert w["window_ref"].startswith("W") and w["doc_ref"].startswith("D")
    assert w["text"] and w["url"]

assert len(bank) == 52 and len({c["qid"] for c in bank}) == 12
assert len({c["case_id"] for c in bank}) == 52
(HERE / "OBSERVATIONS.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n")
print("observations", len(bank), "qids", len({c["qid"] for c in bank}),
      "dates", sum(bool(c["observation"]["date"]) for c in bank))
