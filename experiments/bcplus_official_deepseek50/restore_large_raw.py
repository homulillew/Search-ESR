"""Restore oversized raw logs from the repository's byte-exact gzip files."""
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(path):
    h = sha256()
    with path.open("rb") as source:
        while block := source.read(4 * 1024 * 1024):
            h.update(block)
    return h.hexdigest()


def main():
    mapping = json.loads((HERE / "LARGE_RAW_MAP.json").read_text(encoding="utf-8"))
    for item in mapping["files"]:
        source = HERE / item["package"]
        target = HERE / item["original"]
        if digest(source) != item["package_sha256"]:
            raise ValueError(f"Compressed file hash mismatch: {source}")
        decoded = sha256()
        decoded_bytes = 0
        with gzip.open(source, "rb") as input_stream:
            while block := input_stream.read(4 * 1024 * 1024):
                decoded.update(block)
                decoded_bytes += len(block)
        if decoded_bytes != item["original_bytes"] or decoded.hexdigest() != item["original_sha256"]:
            raise ValueError(f"Compressed contents do not match raw file: {source}")
        if not target.exists():
            with gzip.open(source, "rb") as input_stream, target.open("wb") as output_stream:
                while block := input_stream.read(4 * 1024 * 1024):
                    output_stream.write(block)
        if target.stat().st_size != item["original_bytes"] or digest(target) != item["original_sha256"]:
            raise ValueError(f"Restored raw file hash mismatch: {target}")
    print(f"verified={len(mapping['files'])} oversized raw files")


if __name__ == "__main__":
    main()
