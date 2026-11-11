#!/usr/bin/env python3
"""Generate/check an acyclic exact-byte repository integrity inventory.

SELECTED_ARTIFACTS_SHA256SUMS hashes every non-generated input (the historical
filename is retained). MANIFEST adds the selected checksum file. SHA256SUMS adds
the manifest and excludes itself. Source archive assertions are preserved input.
No wall-clock timestamp, Git state, third-party dependency or old output is used.
"""
import argparse
import csv
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SELECTED = "hashes/SELECTED_ARTIFACTS_SHA256SUMS.txt"
MANIFEST = "MANIFEST.json"
SUMS = "SHA256SUMS"
GENERATED = frozenset((SELECTED, MANIFEST, SUMS))
CACHE_DIRS = frozenset((".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"))
IGNORED_FILES = (".git", ".DS_Store", "*.pyc", "*.pyo", "~$*.xlsx", "*.tmp", "*.swp")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def repository_files(root):
    """Inventory hidden/ordinary inputs in POSIX order; never follow symlinks."""
    root = Path(root)
    files = []

    def walk_error(error):
        raise error

    for base, directories, names in os.walk(root, followlinks=False, onerror=walk_error):
        directories[:] = sorted(name for name in directories if name not in CACHE_DIRS)
        for name in directories:
            path = Path(base) / name
            if path.is_symlink():
                raise ValueError(f"symlink directory is not supported: {path.relative_to(root)}")
        for name in sorted(names):
            if any(fnmatch.fnmatchcase(name, pattern) for pattern in IGNORED_FILES):
                continue
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ValueError(f"symlink file is not supported: {rel}")
            if rel in GENERATED:
                continue
            if any(character in rel for character in ("\\", "\r", "\n")):
                raise ValueError(f"unsupported checksum filename: {rel!r}")
            if not path.is_file():
                raise ValueError(f"not a regular file: {rel}")
            files.append(rel)
    return sorted(files)


def checksum_bytes(files):
    return "".join(f"{sha256(files[path])}  {path}\n" for path in sorted(files)).encode("utf-8")


def row_count(data):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""), strict=True)
    return sum(1 for _ in reader)


def build_outputs(root=ROOT):
    root = Path(root)
    files = {rel: (root / rel).read_bytes() for rel in repository_files(root)}
    selected = checksum_bytes(files)
    files[SELECTED] = selected
    manifest = {
        "repository": "Neuroca-Inc/Provenance",
        "purpose": "thin cross-project provenance and custody graph",
        "format_version": 2,
        "generator": "scripts/update_hashes.py",
        "hash_algorithm": "SHA256",
        "evidence_rows": row_count(files["ledgers/master-evidence-index.csv"]),
        "source_artifact_rows": row_count(files["source-index/source-artifact-index.csv"]),
        "file_count_excluding_manifest_and_sha256sums": len(files),
        "files": [
            {"path": path, "sha256": sha256(files[path]), "size": len(files[path])}
            for path in sorted(files)
        ],
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    files[MANIFEST] = manifest_bytes
    return {SELECTED: selected, MANIFEST: manifest_bytes, SUMS: checksum_bytes(files)}


def integrity_errors(root=ROOT):
    errors = []
    for rel, expected in build_outputs(root).items():
        path = Path(root) / rel
        if not path.is_file():
            errors.append(f"missing generated integrity file: {rel}")
        elif path.read_bytes() != expected:
            errors.append(f"stale or corrupt generated integrity file: {rel}")
    return errors


def write_outputs(root=ROOT):
    # Build all layers before writing: no previous generated output is trusted.
    outputs = build_outputs(root)
    for rel, data in outputs.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return list(outputs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: script's repository)")
    args = parser.parse_args(argv)
    try:
        if args.write:
            for rel in write_outputs(args.root):
                print(rel)
            return 0
        errors = integrity_errors(args.root)
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        print(f"FAIL: cannot build integrity inventory: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: all three integrity outputs match exact repository bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
