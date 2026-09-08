#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hashes" / "SELECTED_ARTIFACTS_SHA256SUMS.txt"

TARGETS = [
    ROOT / "chronology",
    ROOT / "methodology",
    ROOT / "records",
    ROOT / "ledgers",
    ROOT / "schemas",
    ROOT / "docs",
]

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def build():
    files = []
    for base in TARGETS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path != OUT:
                files.append(path)
    return "".join(
        f"{digest(path)}  {path.relative_to(ROOT).as_posix()}\n"
        for path in sorted(files)
    )

ap = argparse.ArgumentParser()
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--write", action="store_true")
g.add_argument("--check", action="store_true")
args = ap.parse_args()

current = build()

if args.write:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(current, encoding="utf-8")
    print(OUT.relative_to(ROOT))
    raise SystemExit(0)

if not OUT.exists():
    print("FAIL: hash manifest missing")
    raise SystemExit(1)

if OUT.read_text(encoding="utf-8") != current:
    print("FAIL: selected artifact hashes are stale")
    raise SystemExit(1)

print("PASS")
