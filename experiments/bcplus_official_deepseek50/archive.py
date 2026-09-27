"""Hash and check the completed raw trajectories and judge records."""
from hashlib import sha256
import json
from pathlib import Path

from experiments.bcplus_native_deepseek50.runner import write_json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def hash_file(path):
    h = sha256()
    size = 0
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            h.update(block)
            size += len(block)
    return {"sha256": h.hexdigest(), "bytes": size}


def secret_values():
    values = []
    for path in (ROOT / ".env", ROOT / ".env.deepseek"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split("=", 1)
            if key in {"OPENAI_API_KEY", "DASHSCOPE_API_KEY", "DEEPSEEK_API_KEY"}:
                candidate = value.strip().strip("\"'")
                if candidate:
                    values.append(candidate.encode())
    return values


def main():
    end = json.loads((HERE / "runs/BATCH_END.json").read_text(encoding="utf-8"))
    batch = HERE / "runs" / end["batch_id"]
    qids = [str(qid) for qid, _ in end["results"]]
    if len(qids) != 50 or len(set(qids)) != 50:
        raise ValueError("Batch end must list 50 unique qids")
    records = []
    for qid in qids:
        directory = batch / f"qid_{qid}"
        for name in ("input.json", "manifest.json", "events.jsonl", "trajectory.md", "answer.md", "summary.json"):
            if not (directory / name).is_file():
                raise ValueError(f"Missing raw file: {qid}/{name}")
        if not (HERE / "judgments" / f"qid_{qid}.json").is_file():
            raise ValueError(f"Missing Qwen judgment: {qid}")
        events = [json.loads(line) for line in (directory / "events.jsonl").open(encoding="utf-8")]
        if [e["seq"] for e in events] != list(range(1, len(events)+1)) or events[-1]["kind"] != "run_end":
            raise ValueError(f"Invalid event sequence: {qid}")
        summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
        if summary["status"] != events[-1]["status"]:
            raise ValueError(f"Mismatched run status: {qid}")
    files = sorted([p for folder in (HERE / "runs", HERE / "judgments") for p in folder.rglob("*") if p.is_file()])
    secrets = secret_values()
    leaked = []
    for path in files:
        record = {"path": str(path.relative_to(ROOT)), **hash_file(path)}
        data = path.read_bytes()
        if any(secret in data for secret in secrets):
            leaked.append(record["path"])
        records.append(record)
    if leaked:
        raise ValueError(f"Credential bytes found in {len(leaked)} raw files")
    write_json(HERE / "RUN_ARCHIVE_MANIFEST.json", {
        "batch_id": end["batch_id"], "file_count": len(records),
        "total_bytes": sum(x["bytes"] for x in records), "files": records,
    })
    write_json(HERE / "INTEGRITY_AUDIT.json", {
        "batch_id": end["batch_id"], "question_count": len(qids),
        "raw_file_count": len(records), "all_event_sequences_valid": True,
        "all_qwen_judgments_present": True, "credential_byte_matches": 0,
    })


if __name__ == "__main__":
    main()
