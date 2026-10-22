#!/usr/bin/env python3
"""Append a validated entry to notes/journal.jsonl.

Stdlib only. The hash is computed over the canonical JSON of the entry without
the ``hash`` field; ``prev`` links to the previous entry's hash.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "notes/policy.json"


def canonical(entry):
    body = {k: v for k, v in entry.items() if k != "hash"}
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load_entries(path):
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--type", required=True)
    ap.add_argument("--status", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--summary", required=True)
    ap.add_argument("--decision", default="")
    ap.add_argument("--evidence", action="append", default=[])
    ap.add_argument("--artifact", action="append", default=[])
    ap.add_argument("--check", action="append", default=[])
    args = ap.parse_args()

    policy = json.loads(POLICY.read_text())
    schema = policy["journal_schema"]
    if args.type not in schema["types"]:
        raise SystemExit(f"unknown journal type: {args.type}")
    if args.status not in schema["statuses"]:
        raise SystemExit(f"unknown journal status: {args.status}")

    journal = ROOT / policy["journal"]
    entries = load_entries(journal)
    if any(e["id"] == args.id for e in entries):
        raise SystemExit(f"duplicate journal id: {args.id}")
    prev = entries[-1]["hash"] if entries else None
    entry = {
        "schema_version": 1,
        "id": args.id,
        "seq": len(entries) + 1,
        "date": args.date,
        "type": args.type,
        "status": args.status,
        "title": args.title,
        "summary": args.summary,
        "decision": args.decision,
        "evidence": args.evidence,
        "artifacts": args.artifact,
        "checks": args.check,
        "prev": prev,
    }
    entry["hash"] = hashlib.sha256(canonical(entry)).hexdigest()
    with journal.open("a") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(json.dumps({"id": entry["id"], "seq": entry["seq"], "sha256": entry["hash"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
