#!/usr/bin/env python3
"""Validate local custody, index coverage and exact-byte integrity outputs.

This is not theorem certification. Omitted archive/package digests remain source
assertions. The documented legacy source/copy discrepancy is accepted only for
its exact pinned tuple and is always reported as a warning, never as equality.
"""
import argparse
import csv
from pathlib import Path, PurePosixPath
import re
import sys

from update_hashes import ROOT, integrity_errors, sha256

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SOURCE_INDEX = "source-index/source-artifact-index.csv"
MASTER_INDEX = "ledgers/master-evidence-index.csv"
ACTIVE_INDEX = "ledgers/active-provenance-ledger.csv"
NS_DIRECTORY = "records/Navier-Stokes"
NS_RECORDS = (
    "CF10_NAVIER_STOKES_POLARITY_LOCK.md",
    "CF10_RECOVERY_PROOF_01_interface_accumulation.md",
    "LIR_CF10_OPENAI_PROVENANCE_AND_PERIMETER_PROOF_v2.md",
    "LIR_CF10_OpenAI_Provenance_Correction.md",
    "MASTER_PROVENANCE_RECOVERY_DOSSIER_v0.2.md",
    "MASTER_PROVENANCE_RECOVERY_DOSSIER_v0.3.md",
    "MASTER_PROVENANCE_RECOVERY_DOSSIER_v0.5.md",
)
REQUIRED = (
    "README.md", MASTER_INDEX, ACTIVE_INDEX, "ledgers/active-provenance-ledger.xlsx",
    "public/reach/20260907_reach.ods", "public/reach/reach.csv",
    "git-history/git-milestones.csv", "git-history/git-crosslinks.csv",
    "chronology/phase-calculus-chronology.md", "historical/legacy-cf/legacy-cf-index.csv",
    "ledgers/methodology-lineage.csv", SOURCE_INDEX, "methodology/ORCHESTRA/README.md",
    "methodology/Cairn/README.md", "methodology/ORCHESTRA/artifact-index.csv",
    "hashes/SOURCE_ARCHIVES_SHA256SUMS.txt", f"{NS_DIRECTORY}/README.md",
) + tuple(f"{NS_DIRECTORY}/{name}" for name in NS_RECORDS)
SOURCE_FIELDS = (
    "Artifact_ID", "Source_Container", "Original_Path_or_Artifact", "SHA256", "Classification",
    "Authority_Status", "Public_Inclusion", "Copied_Path", "Staleness_Risk", "Why_Keep",
)
MASTER_FIELDS = (
    "Evidence_ID", "Evidence_Class", "Event_Date", "Title_or_Event", "Identifier", "Source",
    "Status", "Hash_or_SHA", "URL_or_Path", "Related_Entry", "Index_Surface",
)
ACTIVE_FIELDS = (
    "Entry_ID", "Event_Date", "Recorded_Date", "Workstream", "Artifact", "Version", "Entry_Type",
    "Status", "Claim_or_Result", "Direct_Preconditions", "Dependency_IDs", "Invariant_Earned_or_Changed",
    "Falsifier_or_Rejected_Alternative", "Supersedes_or_Corrects", "Downstream_License", "Evidence_Anchor",
    "Public_ID_DOI_Commit", "Content_SHA256", "Verification", "Notes",
)
PUBLIC_RESEARCH_FILES = ("docs/RESEARCH_STATE.md", "source-index/research-crosswalk.csv")
PRIVATE_REFERENCE = re.compile(
    r"chatgpt\.com|page_[a-z0-9]+|messageId|library-file|libfile_|"
    r"<transcript_evidence>|^\s*(?:user|assistant|system|developer)\s*:|^\s*>\s",
    re.IGNORECASE | re.MULTILINE,
)
INCLUSIONS = {"INCLUDED", "SELECTED_DOC", "SELECTED_DOCS", "HASH_ONLY", "REVIEW_REQUIRED"}
# Observed at bb7bc32fe24ad1db2a20ec0033499ccfb194cb4f. The ORCHESTRA copied
# artifact index agrees with the copied digest. This does not establish the
# contents of the omitted source archive or explain the source/copy difference.
KNOWN_SOURCE_COPY_DISCREPANCY = (
    "SRC-ORCH-003",
    "methodology/ORCHESTRA/documents/RESEARCH_AND_EVIDENCE_STANDARD_v1.0.1_20260821.md",
    "ead6071e69929376f52061c3bdf17cfb7befaae25c1aa936b4474f09cd81a4f9",
    "4dad970c0de6771bd7269a5917762c567ba5c2d5531b54b45c7d12bfd5c48d9a",
)


def read_csv(root, rel, fields, errors):
    try:
        with (root / rel).open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames != list(fields):
                errors.append(f"{rel}: unexpected CSV header")
                return []
            rows = list(reader)
            for number, row in enumerate(rows, 2):
                if None in row or any(value is None for value in row.values()):
                    errors.append(f"{rel}: record {number}: wrong column count")
            return [row for row in rows if None not in row and all(value is not None for value in row.values())]
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"{rel}: cannot read CSV: {exc}")
        return []


def unique_ids(rows, key, rel, errors):
    seen = set()
    for number, row in enumerate(rows, 2):
        value = row[key].strip()
        if not value:
            errors.append(f"{rel}: record {number}: missing {key}")
        elif value in seen:
            errors.append(f"{rel}: record {number}: duplicate {key} {value}")
        seen.add(value)


def local_path(root, rel, errors):
    parts = PurePosixPath(rel).parts
    if not parts or rel.startswith("/") or ".." in parts or "\\" in rel or any(c in rel for c in "\r\n"):
        errors.append(f"unsafe repository path: {rel!r}")
        return None
    path = root / rel
    if not path.resolve().is_relative_to(root.resolve()):
        errors.append(f"path escapes repository: {rel!r}")
        return None
    if any(root.joinpath(*parts[:i]).is_symlink() for i in range(1, len(parts) + 1)):
        errors.append(f"symlink repository path: {rel!r}")
        return None
    return path


def validate(root=ROOT):
    root = Path(root)
    errors, warnings = [], []
    for rel in REQUIRED:
        path = local_path(root, rel, errors)
        if path is not None and not path.is_file():
            errors.append(f"missing {rel}")
    # These optional public summaries contain standalone research information,
    # not private navigation or conversation excerpts. This detects recognizable
    # references/transcript formatting; publication still needs prose review.
    for rel in PUBLIC_RESEARCH_FILES:
        path = local_path(root, rel, errors)
        if path is not None and path.is_file():
            try:
                if PRIVATE_REFERENCE.search(path.read_text(encoding="utf-8")):
                    errors.append(f"private reference or transcript formatting in public research file: {rel}")
            except (OSError, UnicodeError) as exc:
                errors.append(f"cannot read public research file {rel}: {exc}")
    sources = read_csv(root, SOURCE_INDEX, SOURCE_FIELDS, errors)
    master = read_csv(root, MASTER_INDEX, MASTER_FIELDS, errors)
    active = read_csv(root, ACTIVE_INDEX, ACTIVE_FIELDS, errors)
    unique_ids(sources, "Artifact_ID", SOURCE_INDEX, errors)
    unique_ids(master, "Evidence_ID", MASTER_INDEX, errors)
    unique_ids(active, "Entry_ID", ACTIVE_INDEX, errors)
    active_ids = {row["Entry_ID"] for row in active}
    for row in active:
        for dependency in filter(None, (value.strip() for value in row["Dependency_IDs"].split(";"))):
            if dependency not in active_ids:
                errors.append(f"{row['Entry_ID']}: unknown active-ledger dependency {dependency}")
        for corrected in re.findall(r"\bPC-\d{4}\b", row["Supersedes_or_Corrects"]):
            if corrected not in active_ids:
                errors.append(f"{row['Entry_ID']}: unknown corrected active-ledger entry {corrected}")

    for row in sources:
        aid, asserted, copied = row["Artifact_ID"], row["SHA256"], row["Copied_Path"]
        if not HEX64.fullmatch(asserted):
            errors.append(f"{aid}: invalid source SHA256")
        if not row["Source_Container"] or not row["Original_Path_or_Artifact"]:
            errors.append(f"{aid}: missing source coordinate")
        inclusion = row["Public_Inclusion"]
        if inclusion not in INCLUSIONS:
            errors.append(f"{aid}: unknown Public_Inclusion {inclusion!r}")
        if inclusion in {"INCLUDED", "SELECTED_DOC", "SELECTED_DOCS"} and not copied:
            errors.append(f"{aid}: included source has no Copied_Path")
        if copied:
            path = local_path(root, copied, errors)
            if path is None:
                continue
            if not path.exists():
                errors.append(f"{aid}: missing copied path {copied}")
            elif inclusion == "SELECTED_DOCS":
                if not path.is_dir():
                    errors.append(f"{aid}: SELECTED_DOCS must name a directory")
                # This digest identifies a source package, not the copied directory.
            elif not path.is_file():
                errors.append(f"{aid}: copied path must be a regular file: {copied}")
            else:
                actual = sha256(path.read_bytes())
                observed = (aid, copied, asserted, actual)
                if aid == KNOWN_SOURCE_COPY_DISCREPANCY[0] and observed != KNOWN_SOURCE_COPY_DISCREPANCY:
                    errors.append(f"{aid}: documented source/copy discrepancy changed; explicit custody resolution required")
                if observed == KNOWN_SOURCE_COPY_DISCREPANCY:
                    warnings.append(f"{aid}: known source/copy discrepancy preserved: asserted source SHA256 {asserted}; copied-byte SHA256 {actual}; upstream identity unresolved")
                elif actual != asserted:
                    errors.append(f"{aid}: copied SHA256 mismatch for {copied}: asserted {asserted}; actual {actual}")
        linked = [item for item in master if item["Evidence_ID"] == aid]
        if len(linked) != 1:
            errors.append(f"{aid}: source artifact must have exactly one matching master Evidence_ID")
        elif any((linked[0]["Hash_or_SHA"] != asserted,
                  linked[0]["URL_or_Path"] != copied,
                  linked[0]["Index_Surface"] != SOURCE_INDEX)):
            errors.append(f"{aid}: master/source hash, path or index-surface mismatch")

    # Hash local non-source master artifacts too. Legacy package directories are
    # retained coordinates, not invented local copies. No reconciliation required.
    source_ids = {row["Artifact_ID"] for row in sources}
    for row in master:
        rel, digest = row["URL_or_Path"], row["Hash_or_SHA"]
        if row["Evidence_ID"] in source_ids or not rel or "://" in rel:
            continue
        path = local_path(root, rel, errors)
        if path is not None and HEX64.fullmatch(digest) and not rel.endswith("/"):
            if not path.is_file():
                errors.append(f"{row['Evidence_ID']}: missing hashed master local file: {rel}")
            elif sha256(path.read_bytes()) != digest:
                errors.append(f"{row['Evidence_ID']}: master local-file SHA256 mismatch: {rel}")

    # A hard baseline prevents deletion of a file and both index rows from hiding
    # a lost correction; new Markdown records in this directory also need custody.
    ns_paths = {f"{NS_DIRECTORY}/{name}" for name in NS_RECORDS}
    ns_paths.update(path.relative_to(root).as_posix() for path in (root / NS_DIRECTORY).glob("*.md") if path.name != "README.md")
    for rel in sorted(ns_paths):
        if len([row for row in sources if row["Copied_Path"] == rel]) != 1:
            errors.append(f"unindexed or multiply indexed correction record in source index: {rel}")
        if len([row for row in master if row["URL_or_Path"] == rel]) != 1:
            errors.append(f"unindexed or multiply indexed correction record in master index: {rel}")

    orch_fields = ("copied_document", "original_source_coordinate", "sha256")
    orch_rows = read_csv(root, "methodology/ORCHESTRA/artifact-index.csv", orch_fields, errors)
    unique_ids(orch_rows, "copied_document", "methodology/ORCHESTRA/artifact-index.csv", errors)
    for row in orch_rows:
        rel = "methodology/ORCHESTRA/documents/" + row["copied_document"]
        path = local_path(root, rel, errors)
        if path is None:
            continue
        if not path.is_file():
            errors.append(f"missing indexed ORCHESTRA copy: {rel}")
        elif not HEX64.fullmatch(row["sha256"]) or sha256(path.read_bytes()) != row["sha256"]:
            errors.append(f"ORCHESTRA copied-byte SHA256 mismatch: {rel}")

    # External archives are unavailable locally. Cross-check assertions without
    # claiming their omitted bytes have been independently rehashed.
    anchors = {row["Source_Container"]: row["SHA256"] for row in sources
               if row["Classification"] == "SOURCE_ARCHIVE" or row["Artifact_ID"] == "SRC-REACH-001"}
    try:
        lines = (root / "hashes/SOURCE_ARCHIVES_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        recorded = {}
        for line in lines:
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
            if not match:
                errors.append("invalid SOURCE_ARCHIVES checksum line")
                continue
            digest, name = match.groups()
            if name in recorded:
                errors.append(f"duplicate SOURCE_ARCHIVES checksum: {name}")
            recorded[name] = digest
        if recorded != anchors:
            errors.append("SOURCE_ARCHIVES assertions do not match source index")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read SOURCE_ARCHIVES assertions: {exc}")
    try:
        errors.extend(integrity_errors(root))
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        errors.append(f"cannot build integrity inventory: {exc}")
    return errors, warnings, len(master), len(sources)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        errors, warnings, master_count, source_count = validate(args.root)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"FAIL: cannot validate repository: {exc}")
        return 1
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print("FAIL")
        for error in errors:
            print(error)
        return 1
    print("PASS: byte integrity and index coverage (not theorem certification)")
    print("master evidence rows:", master_count)
    print("source artifact rows:", source_count)
    print("External archive/package digests remain source assertions; omitted bytes were not rehashed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
