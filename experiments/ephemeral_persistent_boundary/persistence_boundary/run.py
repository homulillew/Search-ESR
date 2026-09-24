"""Frozen L/I/X binding experiment; one call per cell, query-blind verification."""

import hashlib
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from experiments.model_backend_deepseek.cache_usage import extract

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CONFIG = json.loads((ROOT / "experiments/model_backend_deepseek/provider.json").read_text())
BANK = json.loads((HERE / "BANK.json").read_text())
EVENTS = HERE / "events.jsonl"
FREEZE = HERE / "freeze.json"
LOCK = threading.Lock()


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sources():
    paths = [STUDY / x for x in ("PROTOCOL.md", "HYPOTHESES.md", "STATE.md", "FROZEN_STATE.md",
             "persistence_boundary/PROTOCOL.md", "persistence_boundary/prepare_bank.py",
             "persistence_boundary/BANK.json", "persistence_boundary/run.py")]
    paths += sorted((STUDY / "prompts").glob("*.md"))
    paths += [ROOT / "experiments/model_backend_deepseek/provider.json",
              ROOT / "experiments/model_backend_deepseek/cache_usage.py",
              ROOT / "experiments/research_state_v2/claim_mutation/CASES.json",
              ROOT / "experiments/variable_preserving_state/test_representation/CASES.json"]
    return paths


def source_hashes():
    return {str(p.relative_to(ROOT)): sha(p) for p in sources()}


def order():
    return sorted(BANK, key=lambda c: digest(c["case_id"]))


def arms(i):
    seq = ("L", "I", "X")
    return seq[i % 3:] + seq[:i % 3]


def binder_request(case, arm):
    filename = {"L": "leaky_binder.md", "I": "isolated_binder.md", "X": "extractive_binder.md"}[arm]
    user = {"test_card": case["test_card"],
            "previous_persistent_bindings": case["previous_persistent_bindings"],
            "new_observation": {k: case["new_observation"][k] for k in ("ref", "text")}}
    if arm == "L":
        user["previous_search_query_as_action_history"] = case["ephemeral_query"]
    req = {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": (STUDY / "prompts" / filename).read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}
    if arm in ("I", "X"):
        assert case["ephemeral_query"] not in json.dumps(req, ensure_ascii=False)
    return req


def verify_request(case, proposal):
    user = {"test_condition": case["test_card"]["condition"],
            "slot": proposal["slot"], "proposed_value": proposal["value"],
            "new_observation": {k: case["new_observation"][k] for k in ("ref", "text")},
            "previous_verified_binding": case["previous_persistent_bindings"].get(proposal["slot"])}
    return {"model": CONFIG["model"], "messages": [
        {"role": "system", "content": (STUDY / "prompts/binding_verifier.md").read_text()},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}], "stream": False}


def freeze():
    if FREEZE.exists():
        raise FileExistsError(FREEZE)
    assert len(BANK) == 40 and len({c["qid"] for c in BANK}) == 11
    assert sum(c["category"] == "P6" for c in BANK) == 4
    f = {"frozen_at_utc": datetime.now(timezone.utc).isoformat(),
         "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         "provider": {"host": urlsplit(CONFIG["base_url"]).hostname, "model": CONFIG["model"],
                      "timeout_seconds": CONFIG["timeout_seconds"], "max_retries": 0},
         "source_hashes": source_hashes(), "case_order": [c["case_id"] for c in order()],
         "arm_order": {c["case_id"]: list(arms(i)) for i,c in enumerate(order())},
         "case_hashes": {c["case_id"]: digest(c) for c in BANK},
         "prefix_hashes": {c["case_id"]: digest([c["raw_question"], c["working_hypothesis"], c["semantic_gap"]]) for c in BANK},
         "test_card_hashes": {c["case_id"]: digest(c["test_card"]) for c in BANK},
         "observation_hashes": {c["case_id"]: digest(c["new_observation"]) for c in BANK},
         "query_hashes": {c["case_id"]: digest(c["ephemeral_query"]) for c in BANK},
         "request_hashes": {c["case_id"]+":"+a: digest(binder_request(c,a)) for c in BANK for a in ("L","I","X")},
         "schema": {"binder": {"binding_updates": [{"test_id":"T1","slot":"string","value":"string","evidence_ref":"new W ref"}]},
                    "verifier": {"status": ["supported","open","refuted"], "reason":"string"}},
         "gate": {"precision_min":.95,"recall_min":.85,"false_promotion_max":.05,
                  "nogain_preservation_min":.90,"alternative_recovery_min":.80,"conflict_recovery_min_count":3,
                  "paired_false_improvement_min":6,"reverse_worsening_less_than_half":True},
         "failure_policy":"One binder call per case/arm, zero retries. Failed/invalid cells score as misses; verification failure rejects. Every request, response and error retained."}
    FREEZE.write_text(json.dumps(f,ensure_ascii=False,indent=2)+"\n")


def gate():
    f=json.loads(FREEZE.read_text())
    checks={"source_hashes":f["source_hashes"]==source_hashes(),
            "provider":f["provider"]=={"host":urlsplit(CONFIG["base_url"]).hostname,"model":CONFIG["model"],
                                      "timeout_seconds":CONFIG["timeout_seconds"],"max_retries":CONFIG["max_retries"]},
            "case_order":f["case_order"]==[c["case_id"] for c in order()],
            "case_hashes":f["case_hashes"]=={c["case_id"]:digest(c) for c in BANK},
            "requests":all(f["request_hashes"][c["case_id"]+":"+a]==digest(binder_request(c,a)) for c in BANK for a in ("L","I","X"))}
    (HERE/"gate.txt").write_text("\n".join(("PASS " if v else "FAIL ")+k for k,v in checks.items())+"\n")
    if not all(checks.values()):raise AssertionError(checks)


def emit(kind, **fields):
    with LOCK:
        with EVENTS.open("a") as out:
            out.write(json.dumps({"time":datetime.now(timezone.utc).isoformat(),"kind":kind,**fields},ensure_ascii=False)+"\n")


def call(client, request, cell, kind):
    emit(kind+"_request",cell=cell,request=request,request_hash=digest(request))
    started=time.monotonic()
    try:
        raw=client.chat.completions.create(**request).model_dump(mode="json")
        emit(kind+"_response",cell=cell,response=raw,cache_usage=extract(raw),latency_seconds=time.monotonic()-started)
        if raw["choices"][0]["finish_reason"]!="stop":raise ValueError("abnormal_finish")
        content=raw["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        emit(kind+"_error",cell=cell,error_type=type(e).__name__,http_status=getattr(e,"status_code",None),
             error=str(e)[:500],latency_seconds=time.monotonic()-started)
        return None


def proposals(case, value):
    if not isinstance(value,dict) or set(value)!={"binding_updates"} or not isinstance(value["binding_updates"],list):
        raise ValueError("binder_schema")
    found=[]
    for p in value["binding_updates"]:
        if not isinstance(p,dict) or set(p)!={"test_id","slot","value","evidence_ref"}:
            raise ValueError("proposal_schema")
        if p["test_id"]!="T1" or p["slot"]!=case["test_card"]["unknown"][0] or p["evidence_ref"]!=case["new_observation"]["ref"] or not isinstance(p["value"],str) or not p["value"].strip():
            raise ValueError("proposal_invalid")
        found.append(p)
    return found


def binder_cell(client,case,arm):
    cell=case["case_id"]+":"+arm
    value=call(client,binder_request(case,arm),cell,"binder")
    if value is None:return {"cell":cell,"error":"binder_failure","proposals":[],"mechanically_accepted":[],"verifications":[],"committed":[]}
    try:ps=proposals(case,value)
    except Exception as e:
        emit("binder_validation_error",cell=cell,error_type=type(e).__name__,error=str(e))
        return {"cell":cell,"error":"binder_validation","raw_output":value,"proposals":[],"mechanically_accepted":[],"verifications":[],"committed":[]}
    emit("binder_outcome",cell=cell,output=value)
    accepted=[p for p in ps if arm!="X" or p["value"].lower() in case["new_observation"]["text"].lower()]
    for p in ps:
        if p not in accepted:emit("mechanical_rejection",cell=cell,proposal=p,reason="value_absent_from_exact_new_W")
    return {"cell":cell,"error":None,"proposals":ps,"mechanically_accepted":accepted,"verifications":[],"committed":[]}


def verify_cell(client,case,result):
    cell=result["cell"]
    for j,p in enumerate(result["mechanically_accepted"]):
        answer=call(client,verify_request(case,p),cell+f":V{j}","verifier")
        if not isinstance(answer,dict) or set(answer)!={"status","reason"} or answer.get("status") not in ("supported","open","refuted") or not isinstance(answer.get("reason"),str):
            emit("verifier_validation_error",cell=cell,proposal=p,output=answer)
            verdict={"status":"error","reason":"invalid or failed verifier response"}
        else:verdict=answer
        result["verifications"].append({"proposal":p,"verdict":verdict})
        if verdict["status"]=="supported":result["committed"].append(p)
    emit("cell_outcome",cell=cell,output=result)
    return result


def run():
    gate()
    if EVENTS.exists():raise FileExistsError(EVENTS)
    key=dotenv_values(ROOT/CONFIG["credential_file"]).get(CONFIG["credential_field"])
    if not key:raise ValueError("DeepSeek credential unavailable")
    cases=order()
    tasks=[(c,a) for i,c in enumerate(cases) for a in arms(i)]
    with OpenAI(api_key=key,base_url=CONFIG["base_url"],timeout=CONFIG["timeout_seconds"],max_retries=0) as client:
        results={}
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(binder_cell,client,c,a):(c,a) for c,a in tasks}
            for f in as_completed(futures):
                c,a=futures[f]
                results[c["case_id"]+":"+a]=f.result()
                print("binder",c["case_id"],a,flush=True)
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures={pool.submit(verify_cell,client,c,results[c["case_id"]+":"+a]):(c,a) for c,a in tasks}
            for f in as_completed(futures):
                c,a=futures[f];f.result();print("verified",c["case_id"],a,flush=True)
    (HERE/"outcomes.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")


if __name__=="__main__":
    action=sys.argv[1]
    if action=="freeze":freeze()
    elif action=="gate":gate();print("PASS")
    elif action=="run":run()
    else:raise SystemExit("freeze|gate|run")
