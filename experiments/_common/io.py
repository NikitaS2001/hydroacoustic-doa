"""Small JSON/JSONL and run-directory helpers for experiment bundles."""
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, payload):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def append_jsonl(path, payload):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open("a") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def run_dir(root, run_id):
    path = Path(root) / "results" / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path
