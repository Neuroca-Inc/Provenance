#!/usr/bin/env python3
from pathlib import Path
import csv
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HEX64 = re.compile(r"^[0-9a-f]{64}$")

errors = []

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

source_index = ROOT / "ledgers" / "source-artifact-index.csv"
if not source_index.exists():
    errors.append("missing ledgers/source-artifact-index.csv")
else:
    rows = read_csv(source_index)
    ids = set()
    for n,row in enumerate(rows, start=2):
        aid = row.get("Artifact_ID","").strip()
        if not aid:
            errors.append(f"{source_index}:{n}: missing Artifact_ID")
        elif aid in ids:
            errors.append(f"{source_index}:{n}: duplicate Artifact_ID {aid}")
        ids.add(aid)
        digest = row.get("SHA256","").strip()
        if not HEX64.match(digest):
            errors.append(f"{source_index}:{n}: invalid SHA256")
        inc = row.get("Public_Inclusion","").strip()
        copied = row.get("Copied_Path","").strip()
        if inc == "INCLUDED":
            if not copied:
                errors.append(f"{source_index}:{n}: INCLUDED row lacks Copied_Path")
            elif not (ROOT / copied).exists():
                errors.append(f"{source_index}:{n}: copied path missing: {copied}")

for rel in [
    "ledgers/git-milestones.csv",
    "ledgers/git-crosslinks.csv",
    "ledgers/methodology-lineage.csv",
    "ledgers/provenance-candidates.csv",
    "chronology/phase-calculus-chronology.md",
    "methodology/ORCHESTRA/README.md",
    "methodology/Cairn/README.md",
]:
    if not (ROOT / rel).exists():
        errors.append(f"missing {rel}")

if errors:
    print("FAIL")
    for e in errors:
        print(e)
    sys.exit(1)

print("PASS")
print("source artifact rows:", len(read_csv(source_index)))
