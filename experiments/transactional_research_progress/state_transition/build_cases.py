"""Build exact-observation E1 packets and pre-call reviewer mutation labels."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from case_specs import BASE, T4, T5, T6, T7

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
A_ROWS = {x["case_id"]: x for x in json.loads((ROOT / "experiments/research_progress_frontier/closure_probe/review_cases.json").read_text())}
D_EVENTS = [json.loads(x) for x in (ROOT / "experiments/research_progress_frontier/one_step_evidence_gain/events.jsonl").read_text().splitlines()]
LEGACY = {
    "177": "experiments/observation_summary/runs/20260918T045524.575952Z/qid_177__visible__r1/events.jsonl",
    "517": "experiments/runs/v001_raw_windows/qid_517/20260917T181920.667694Z/events.jsonl",
}
BASELINE = {
    "311": "experiments/runs/v000_baseline/qid_311/20260917T090239.474309Z/events.jsonl",
    "324": "experiments/runs/v000_baseline/qid_324/20260917T090903.066977Z/events.jsonl",
    "776": "experiments/runs/v000_baseline/qid_776/20260917T090218.212513Z/events.jsonl",
    "186": "experiments/runs/v000_baseline/qid_186/20260917T084428.558480Z/events.jsonl",
}
OTHER = {**LEGACY, **BASELINE}
QUESTION = {}
for q, path in BASELINE.items():
    for e in map(json.loads, (ROOT / path).open()):
        if e["kind"] == "api_request":
            QUESTION[q] = next(m["content"] for m in e["request"]["messages"] if m["role"] == "user")
            break


def hash_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def obs_from_a(cid, *, index=0, alias="W1"):
    row = A_ROWS[cid]
    item = row["visible_evidence"][index]
    return {"ref": alias, "doc_ref": "D1" if alias == "W1" else "D2", "title": item["title"], "text": item["excerpt"],
            "provenance": {"source": "stage_A_review_packet", "case_id": cid,
                           "historical_ref": item["ref"], "historical_doc_ref": item["doc_ref"],
                           "checkpoint": row["checkpoint"], "text_sha256": hash_text(item["excerpt"])}}


def obs_from_d(cid, ref):
    e = next(x for x in D_EVENTS if x["kind"] == "tool_result" and x["case_id"] == cid)
    result = e["result"]
    if e["name"] == "search":
        item = next(x for x in result["results"] if x["doc_ref"] == ref and x.get("preview"))
        value, title, raw_ref = item["preview"], item["title"], item["preview_ref"]
    elif e["name"] == "find":
        item = next(x for x in result["matches"] if x["window_ref"] == ref)
        value, title, raw_ref = item["text"], "", ref
    else:
        raise ValueError(cid)
    return {"ref": "W1", "doc_ref": "D1", "title": title, "text": value,
            "provenance": {"source": "prior_stage_D_real_tool", "case_id": cid,
                           "historical_ref": raw_ref, "historical_doc_ref": item.get("doc_ref", result.get("doc_ref")),
                           "text_sha256": hash_text(value)}}


def obs_from_events(qid, docid, limit, alias="W1"):
    path = OTHER[qid]
    matches = []
    for e in map(json.loads, (ROOT / path).open()):
        if e["seq"] > limit or e["kind"] != "tool_result":
            continue
        results = e["result"] if isinstance(e["result"], list) else [e["result"]]
        for rank, item in enumerate(results, 1):
            if str(item.get("docid")) == docid and item.get("text"):
                matches.append((e, rank, item))
    if not matches:
        raise ValueError(f"No actual observation for {qid}:{docid} <= {limit}")
    e, rank, item = matches[0]
    value = item["text"]
    return {"ref": alias, "doc_ref": "D1" if alias == "W1" else "D2",
            "title": item.get("title", ""), "text": value,
            "provenance": {"source": path, "event_seq": e["seq"], "rank": rank,
                           "historical_doc_ref": docid, "historical_ref": item.get("window_ref"),
                           "text_sha256": hash_text(value)}}


def claim(cid, statement, status="open", refs=()):
    return {"claim_id": cid, "statement": statement, "status": status,
            "verified_evidence_refs": list(refs), "version": 1}


def gap(gid, description, claims, status="open"):
    return {"gap_id": gid, "description": description, "related_claim_ids": claims, "status": status}


def packet(cid, qid, kind, constraint, statements, unrelated, observation, expected,
           *, primary_gap=None, prior=None, close_gap=False, ambiguity="low", reason=""):
    claims = [claim(f"C{i}", text) for i, text in enumerate(statements, 1)]
    claims.append(claim(f"C{len(claims)+1}", unrelated))
    last = claims[-1]["claim_id"]
    g1 = gap("G1", primary_gap or "Resolve the current candidate's remaining question conditions.",
             [c["claim_id"] for c in claims])
    g2 = gap("G2", unrelated, [last])
    state = {"version": 1, "claims": claims, "gaps": [g1, g2]}
    projection = {"active_gap": "G1", "expected_source_type": "source relevant to the current gap",
                  "uncertainty_type": "closure" if kind != "T4" else "source", "target_doc": "D1",
                  "target_window": observation["ref"]}
    if kind == "T7":
        state["claims"][0]["status"] = "supported"
        state["claims"][0]["verified_evidence_refs"] = [prior["ref"]]
        state["gaps"][0]["status"] = "closed"
        state["gaps"][0]["related_claim_ids"] = ["C1"]
        projection["active_gap"] = "G2"
        projection["target_window"] = prior["ref"]
    if close_gap:
        state["gaps"][0]["related_claim_ids"] = ["C1"]
    required = [{"claim_id": name, "status": status} for name, status in expected.items()]
    labels = {"required_claim_mutations": required,
              "forbidden_claim_mutations": [c["claim_id"] for c in claims if c["claim_id"] not in expected],
              "required_gap_mutations": ([{"gap_id": "G1", "status": "open"}] if kind == "T7" else
                                         [{"gap_id": "G1", "status": "closed"}] if close_gap else []),
              "active_gap_should_retire": close_gap,
              "allowed_new_claims": [],
              "evidence_bindings": {name: [observation["ref"]] for name in expected},
              "ambiguity": ambiguity, "reason": reason}
    return {"case_id": cid, "qid": qid, "transition_type": kind,
            "question_constraint": constraint, "previous_state": state,
            "control_projection": projection,
            "prior_observations": [prior] if prior else [], "new_observation": observation,
            "review": labels}


def main():
    if (HERE / "CASES.json").exists():
        raise FileExistsError("CASES.json already exists")
    cases = []
    for qid, (support, refute, insufficient, unrelated) in BASE.items():
        for kind, source in (("T1", support), ("T2", refute), ("T3", insufficient)):
            row = A_ROWS[source]
            status = {"T1": "supported", "T2": "refuted"}.get(kind)
            multiple = len(row["visible_evidence"]) > 1
            prior = obs_from_a(source, index=0) if multiple else None
            obs = obs_from_a(source, index=-1, alias="W2") if multiple else obs_from_a(source)
            cases.append(packet(f"{kind}_{qid}", qid, kind, row["question_constraint"],
                                [row["claim"]], unrelated, obs,
                                {"C1": status} if status else {}, prior=prior,
                                reason=row["review_reason"]))
    for spec in T4:
        qid, source_kind, key, extra, statement = spec
        if source_kind == "prior_D":
            obs = obs_from_d(key, extra)
        else:
            obs = obs_from_events(qid, key, extra)
        cases.append(packet(f"T4_{qid}", qid, "T4", QUESTION.get(qid, "Maintain this unresolved local question."),
                            [statement], "Another independent original-question condition remains open.", obs,
                            {}, reason="This observed text does not establish or refute either state claim."))
    for spec in T5:
        qid, source_kind, key, *tail = spec
        if source_kind == "prior_D":
            ref, statements, unrelated = tail
            obs = obs_from_d(key, ref)
        elif source_kind == "stage_A":
            statements, unrelated = tail
            obs = obs_from_a(key)
        else:
            docid, limit, statements, unrelated = key, *tail
            obs = obs_from_events(qid, docid, limit)
        cases.append(packet(f"T5_{qid}", qid, "T5", QUESTION.get(qid, "Check the candidate's independent claims."),
                            statements, unrelated, obs, {f"C{i}": "supported" for i in range(1, 4)},
                            reason="One exact observed source independently supports three local claims."))
    for qid, source, gdesc in T6:
        row = A_ROWS[source]
        cases.append(packet(f"T6_{qid}", qid, "T6", row["question_constraint"],
                            [row["claim"]], BASE[qid][3], obs_from_a(source),
                            {"C1": "supported"}, close_gap=True, primary_gap=gdesc,
                            reason="This narrow active gap closes with the cited observation."))
    qid, old_doc, new_doc, statement = T7
    prior = obs_from_events(qid, old_doc, 4, alias="W1")
    new = obs_from_events(qid, new_doc, 8, alias="W2")
    cases.append(packet("T7_186", qid, "T7", QUESTION[qid], [statement],
                        "Check the game credits for two people sharing a family name.", new,
                        {"C1": "open"}, prior=prior, ambiguity="medium",
                        reason="The earlier Galacta page states 1993, while a later observed full-title page states November 1992; title equivalence is plausible but not certain."))
    if len(cases) != 41 or len({x["qid"] for x in cases}) != 12:
        raise ValueError(f"bank size/qids: {len(cases)}, {len({x['qid'] for x in cases})}")
    if Counter(x["transition_type"] for x in cases)["T4"] != 8:
        raise ValueError("NoGain quota")
    for c in cases:
        refs = {x["ref"] for x in c["prior_observations"] + [c["new_observation"]]}
        if len(refs) != len(c["prior_observations"]) + 1:
            raise ValueError(c["case_id"])
        for key in ("previous_state", "control_projection", "new_observation"):
            c[key + "_sha256"] = hashlib.sha256(json.dumps(c[key], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    labels = {x["case_id"]: x.pop("review") for x in cases}
    (HERE / "CASES.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2) + "\n")
    (HERE / "REVIEW_LABELS.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2) + "\n")
    print("cases", len(cases), "qids", len({x["qid"] for x in cases}),
          "types", dict(Counter(x["transition_type"] for x in cases)))


if __name__ == "__main__":
    main()
