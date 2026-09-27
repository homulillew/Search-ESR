"""Store oversized immutable raw logs as reversible gzip files for GitHub."""
import gzip
from hashlib import sha256
import json
from pathlib import Path

from experiments.bcplus_native_deepseek50.runner import write_json

HERE = Path(__file__).resolve().parent
LIMIT_BYTES = 95_000_000


def digest(path):
    h = sha256()
    with path.open("rb") as source:
        while block := source.read(4 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main():
    archive = json.loads((HERE / "RUN_ARCHIVE_MANIFEST.json").read_text(encoding="utf-8"))
    if (HERE / "LARGE_RAW_MAP.json").exists():
        raise ValueError("Large raw package already exists")
    archived = {Path(x["path"]).relative_to("experiments/bcplus_official_deepseek50"): x
                for x in archive["files"]}
    records = []
    ignored = []
    for source in sorted((HERE / "runs").rglob("*")):
        if not source.is_file() or source.stat().st_size <= LIMIT_BYTES:
            continue
        relative = source.relative_to(HERE)
        expected = archived[relative]
        if digest(source) != expected["sha256"]:
            raise ValueError(f"Raw file changed since integrity audit: {relative}")
        target = source.with_name(source.name + ".gz")
        if target.exists():
            raise ValueError(f"Package already exists: {target}")
        with source.open("rb") as original, target.open("wb") as raw_output:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw_output, compresslevel=6, mtime=0) as output:
                while block := original.read(4 * 1024 * 1024):
                    output.write(block)
        records.append({"original": str(relative), "original_bytes": expected["bytes"],
                        "original_sha256": expected["sha256"],
                        "package": str(target.relative_to(HERE)),
                        "package_bytes": target.stat().st_size, "package_sha256": digest(target)})
        ignored.append(str(relative))
    write_json(HERE / "LARGE_RAW_MAP.json", {
        "threshold_bytes": LIMIT_BYTES,
        "encoding": "gzip, mtime=0, compression level 6; byte-exact restoration",
        "files": records,
    })
    (HERE / ".gitignore").write_text("# Oversized raw files are stored byte-exact as .gz packages.\n"+
                                     "\n".join(ignored)+("\n" if ignored else ""), encoding="utf-8")
    print(f"packaged={len(records)} raw_bytes={sum(x['original_bytes'] for x in records)} gzip_bytes={sum(x['package_bytes'] for x in records)}")


if __name__ == "__main__":
    main()
