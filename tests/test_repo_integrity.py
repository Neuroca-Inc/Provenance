"""Disposable-copy regressions; preserved research inputs are never modified."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import update_hashes as hashes
import validate_repo as validator


class RepositoryIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot_dir = tempfile.TemporaryDirectory(prefix="provenance-test-snapshot-")
        cls.snapshot = Path(cls.snapshot_dir.name)
        for rel in hashes.repository_files(ROOT):
            target = cls.snapshot / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        hashes.write_outputs(cls.snapshot)

    @classmethod
    def tearDownClass(cls):
        cls.snapshot_dir.cleanup()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="provenance-test-case-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "repo"
        shutil.copytree(self.snapshot, self.root)

    def errors(self):
        return validator.validate(self.root)[0]

    def assert_failure(self, text):
        errors = self.errors()
        self.assertTrue(any(text in error for error in errors), errors)

    def rewrite_csv(self, rel, change):
        path = self.root / rel
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        rows = change(rows)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def mutate_manifest(self, change):
        path = self.root / hashes.MANIFEST
        manifest = json.loads(path.read_bytes())
        change(manifest)
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    def test_complete_snapshot_validates_with_explicit_legacy_warning(self):
        errors, warnings, master_count, source_count = validator.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("SRC-ORCH-003: known source/copy discrepancy preserved", warnings[0])
        self.assertGreaterEqual(master_count, 281)
        self.assertGreaterEqual(source_count, 21)

    def test_repeated_generation_is_byte_identical_and_acyclic(self):
        first = hashes.build_outputs(self.root)
        hashes.write_outputs(self.root)
        self.assertEqual(first, hashes.build_outputs(self.root))
        self.assertEqual(hashes.integrity_errors(self.root), [])
        selected_paths = {line.split("  ", 1)[1] for line in first[hashes.SELECTED].decode().splitlines()}
        manifest = json.loads(first[hashes.MANIFEST])
        manifest_paths = {item["path"] for item in manifest["files"]}
        sum_paths = {line.split("  ", 1)[1] for line in first[hashes.SUMS].decode().splitlines()}
        self.assertFalse(selected_paths & hashes.GENERATED)
        self.assertEqual(manifest_paths, selected_paths | {hashes.SELECTED})
        self.assertEqual(sum_paths, manifest_paths | {hashes.MANIFEST})
        self.assertNotIn(hashes.SUMS, sum_paths)
        self.assertEqual(manifest["file_count_excluding_manifest_and_sha256sums"], len(manifest_paths))

    def test_cli_write_check_and_validator(self):
        for script, args in (("update_hashes.py", ["--write"]), ("update_hashes.py", ["--check"]), ("validate_repo.py", [])):
            result = subprocess.run([sys.executable, str(self.root / "scripts" / script), "--root", str(self.root), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_corrupt_bytes_fail_without_regeneration(self):
        path = self.root / validator.NS_DIRECTORY / validator.NS_RECORDS[0]
        path.write_bytes(path.read_bytes() + b"changed\n")
        self.assert_failure("copied SHA256 mismatch")
        self.assert_failure("stale or corrupt generated integrity file")

    def test_same_size_byte_corruption_is_detected(self):
        path = self.root / validator.NS_DIRECTORY / validator.NS_RECORDS[1]
        data = path.read_bytes()
        path.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        self.assert_failure("copied SHA256 mismatch")

    def test_regeneration_cannot_bless_corrupted_correction(self):
        path = self.root / validator.NS_DIRECTORY / validator.NS_RECORDS[2]
        path.write_bytes(path.read_bytes() + b"changed\n")
        hashes.write_outputs(self.root)
        self.assertEqual(hashes.integrity_errors(self.root), [])
        self.assert_failure("copied SHA256 mismatch")

    def test_missing_correction_fails_even_after_regeneration(self):
        rel = validator.NS_DIRECTORY + "/" + validator.NS_RECORDS[3]
        (self.root / rel).unlink()
        hashes.write_outputs(self.root)
        self.assert_failure("missing " + rel)
        self.assert_failure("missing copied path " + rel)

    def test_source_unindexed_correction_fails_after_regeneration(self):
        self.rewrite_csv(validator.SOURCE_INDEX, lambda rows: [r for r in rows if r["Artifact_ID"] != "SRC-NS-001"])
        hashes.write_outputs(self.root)
        self.assert_failure("unindexed or multiply indexed correction record in source index")

    def test_master_unindexed_correction_fails_after_regeneration(self):
        self.rewrite_csv(validator.MASTER_INDEX, lambda rows: [r for r in rows if r["Evidence_ID"] != "SRC-NS-002"])
        hashes.write_outputs(self.root)
        self.assert_failure("unindexed or multiply indexed correction record in master index")

    def test_deleting_correction_and_both_index_rows_still_fails(self):
        rel = validator.NS_DIRECTORY + "/" + validator.NS_RECORDS[0]
        (self.root / rel).unlink()
        self.rewrite_csv(validator.SOURCE_INDEX, lambda rows: [r for r in rows if r["Copied_Path"] != rel])
        self.rewrite_csv(validator.MASTER_INDEX, lambda rows: [r for r in rows if r["URL_or_Path"] != rel])
        hashes.write_outputs(self.root)
        self.assert_failure("missing " + rel)
        self.assert_failure("unindexed or multiply indexed correction record in source index")

    def test_new_correction_needs_both_indexes(self):
        (self.root / validator.NS_DIRECTORY / "new-correction.md").write_text("Historical correction.\n")
        hashes.write_outputs(self.root)
        self.assert_failure("unindexed or multiply indexed correction record in source index")
        self.assert_failure("unindexed or multiply indexed correction record in master index")

    def test_each_generated_output_is_checked(self):
        for rel in sorted(hashes.GENERATED):
            with self.subTest(path=rel):
                path = self.root / rel
                original = path.read_bytes()
                path.write_bytes(original + b"corruption\n")
                self.assertIn("stale or corrupt generated integrity file: " + rel, hashes.integrity_errors(self.root))
                path.write_bytes(original)

    def test_missing_generated_output_is_detected(self):
        (self.root / hashes.MANIFEST).unlink()
        self.assert_failure("missing generated integrity file: MANIFEST.json")

    def test_manifest_size_hash_counts_and_membership_are_checked(self):
        changes = {
            "size": lambda data: data["files"][0].update(size=data["files"][0]["size"] + 1),
            "hash": lambda data: data["files"][0].update(sha256="0" * 64),
            "file_count": lambda data: data.update(file_count_excluding_manifest_and_sha256sums=0),
            "evidence_count": lambda data: data.update(evidence_rows=0),
            "source_count": lambda data: data.update(source_artifact_rows=0),
            "missing_entry": lambda data: data["files"].pop(),
        }
        for name, change in changes.items():
            with self.subTest(field=name):
                hashes.write_outputs(self.root)
                self.mutate_manifest(change)
                self.assert_failure("stale or corrupt generated integrity file: MANIFEST.json")

    def test_all_paths_including_hidden_scripts_tests_and_future_files_are_covered(self):
        new_paths = [".github/new-config.yml", "future-folder/new-record.csv", "historical/snapshots/example/MANIFEST.json", "historical/snapshots/example/SHA256SUMS"]
        for rel in new_paths:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"example\n")
        self.assertTrue(hashes.integrity_errors(self.root))
        hashes.write_outputs(self.root)
        paths = {item["path"] for item in json.loads((self.root / hashes.MANIFEST).read_bytes())["files"]}
        self.assertTrue(set(new_paths) <= paths)
        self.assertTrue({"scripts/update_hashes.py", "scripts/validate_repo.py", "tests/test_repo_integrity.py", ".gitignore"} <= paths)
        self.assertEqual(self.errors(), [])

    def test_git_cache_and_documented_temporary_files_are_ignored(self):
        expected = hashes.build_outputs(self.root)
        for rel in (".git/objects/example", "scripts/__pycache__/test.pyc", ".pytest_cache/state", ".cache/cache-data", ".DS_Store", "note.tmp", "~$example.xlsx", "backup.swp"):
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"local cache\n")
        self.assertEqual(hashes.build_outputs(self.root), expected)

    def test_original_external_source_assertions_are_not_regenerated(self):
        path = self.root / "hashes/SOURCE_ARCHIVES_SHA256SUMS.txt"
        original = path.read_bytes()
        hashes.write_outputs(self.root)
        self.assertEqual(path.read_bytes(), original)
        self.assertIn("  hashes/SOURCE_ARCHIVES_SHA256SUMS.txt\n", (self.root / hashes.SELECTED).read_text())

    def test_changed_external_source_assertion_fails(self):
        path = self.root / "hashes/SOURCE_ARCHIVES_SHA256SUMS.txt"
        text = path.read_text()
        path.write_text("0" * 64 + text[64:])
        hashes.write_outputs(self.root)
        self.assert_failure("SOURCE_ARCHIVES assertions do not match source index")

    def test_known_copy_corruption_is_not_grandfathered(self):
        path = self.root / validator.KNOWN_SOURCE_COPY_DISCREPANCY[1]
        path.write_bytes(path.read_bytes() + b"changed\n")
        hashes.write_outputs(self.root)
        self.assert_failure("documented source/copy discrepancy changed")
        self.assert_failure("ORCHESTRA copied-byte SHA256 mismatch")

    def test_known_source_assertion_cannot_be_silently_normalized(self):
        aid, _, _, copied_digest = validator.KNOWN_SOURCE_COPY_DISCREPANCY
        def normalize(rows):
            for row in rows:
                if row["Artifact_ID"] == aid:
                    row["SHA256"] = copied_digest
            return rows
        self.rewrite_csv(validator.SOURCE_INDEX, normalize)
        hashes.write_outputs(self.root)
        self.assert_failure("documented source/copy discrepancy changed")

    def test_unknown_source_copy_mismatch_fails(self):
        def change(rows):
            rows[0]["SHA256"] = "0" * 64
            return rows
        self.rewrite_csv(validator.SOURCE_INDEX, change)
        hashes.write_outputs(self.root)
        self.assert_failure("copied SHA256 mismatch")

    def test_duplicate_and_invalid_source_rows_fail(self):
        def change(rows):
            rows[0]["SHA256"] = "not-a-digest"
            return rows + [dict(rows[0])]
        self.rewrite_csv(validator.SOURCE_INDEX, change)
        hashes.write_outputs(self.root)
        self.assert_failure("duplicate Artifact_ID")
        self.assert_failure("invalid source SHA256")

    def test_duplicate_active_id_fails(self):
        self.rewrite_csv(validator.ACTIVE_INDEX, lambda rows: rows + [dict(rows[0])])
        hashes.write_outputs(self.root)
        self.assert_failure("duplicate Entry_ID")

    def test_missing_active_dependency_fails(self):
        self.rewrite_csv(validator.ACTIVE_INDEX, lambda rows: [row for row in rows if row["Entry_ID"] != "PC-0001"])
        hashes.write_outputs(self.root)
        self.assert_failure("unknown active-ledger dependency PC-0001")

    def test_missing_corrected_active_entry_fails(self):
        def change(rows):
            rows[0]["Supersedes_or_Corrects"] = "PC-9999"
            return rows
        self.rewrite_csv(validator.ACTIVE_INDEX, change)
        hashes.write_outputs(self.root)
        self.assert_failure("unknown corrected active-ledger entry PC-9999")

    def test_duplicate_master_id_fails(self):
        self.rewrite_csv(validator.MASTER_INDEX, lambda rows: rows + [dict(rows[0])])
        hashes.write_outputs(self.root)
        self.assert_failure("duplicate Evidence_ID")

    def test_master_source_hash_or_path_disagreement_fails(self):
        def change(rows):
            for row in rows:
                if row["Evidence_ID"] == "SRC-NS-003":
                    row["Hash_or_SHA"] = "0" * 64
            return rows
        self.rewrite_csv(validator.MASTER_INDEX, change)
        hashes.write_outputs(self.root)
        self.assert_failure("master/source hash, path or index-surface mismatch")

    def test_non_source_master_local_file_hash_is_checked(self):
        def change(rows):
            row = {field: "" for field in validator.MASTER_FIELDS}
            row.update(Evidence_ID="TEST-LOCAL", URL_or_Path="README.md", Hash_or_SHA="0" * 64)
            return rows + [row]
        self.rewrite_csv(validator.MASTER_INDEX, change)
        hashes.write_outputs(self.root)
        self.assert_failure("master local-file SHA256 mismatch")

    def test_traversal_and_absolute_source_paths_are_rejected(self):
        for unsafe in ("../outside.md", "/tmp/outside.md", "records/../../outside.md"):
            with self.subTest(path=unsafe):
                def change(rows):
                    rows[0]["Copied_Path"] = unsafe
                    return rows
                self.rewrite_csv(validator.SOURCE_INDEX, change)
                hashes.write_outputs(self.root)
                self.assert_failure("unsafe repository path")

    def test_symlinks_are_rejected(self):
        (self.root / "alias").symlink_to(self.root / "records", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink directory"):
            hashes.build_outputs(self.root)
        (self.root / "alias").unlink()
        (self.root / "alias.md").symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(ValueError, "symlink file"):
            hashes.build_outputs(self.root)

    def test_malformed_csv_columns_are_rejected(self):
        path = self.root / validator.SOURCE_INDEX
        with path.open("a", encoding="utf-8") as stream:
            stream.write("too,few,columns\n")
        hashes.write_outputs(self.root)
        self.assert_failure("wrong column count")

    def test_source_schema_enum_covers_actual_csv_vocabulary(self):
        schema = json.loads((self.root / "schemas/source-artifact.schema.json").read_bytes())
        self.assertEqual(set(schema["properties"]["public_inclusion"]["enum"]), validator.INCLUSIONS)

    def test_preparation_dates_do_not_invent_date_for_polarity_lock(self):
        with (self.root / validator.MASTER_INDEX).open(newline="", encoding="utf-8") as stream:
            rows = {row["Evidence_ID"]: row for row in csv.DictReader(stream)}
        self.assertEqual(rows["SRC-NS-001"]["Event_Date"], "")
        for number in range(2, 8):
            self.assertEqual(rows[f"SRC-NS-{number:03d}"]["Event_Date"], "2026-09-08")
            self.assertTrue(rows[f"SRC-NS-{number:03d}"]["Evidence_Class"].endswith("SOURCE_REPORT"))

    def test_private_reference_and_transcript_markers_are_rejected_in_public_research(self):
        # Synthetic markers only: these tests contain no real private URL or ID.
        markers = ("chatgpt" + ".com", "page_" + "example", "message" + "Id",
                   "library-" + "file", "libfile_" + "example", "<transcript_evidence>",
                   "User: example", "Assistant: example", "> example quotation")
        for rel in validator.PUBLIC_RESEARCH_FILES:
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            original = path.read_bytes() if path.exists() else None
            for marker in markers:
                with self.subTest(path=rel, marker=marker):
                    path.write_text(marker + "\n", encoding="utf-8")
                    hashes.write_outputs(self.root)
                    self.assert_failure("private reference or transcript formatting in public research file: " + rel)
            if original is None:
                path.unlink()
            else:
                path.write_bytes(original)

    def test_reconciliation_files_remain_optional(self):
        self.rewrite_csv(validator.MASTER_INDEX, lambda rows: [row for row in rows if row["Evidence_ID"] != "SYNC-20261111"])
        for rel in validator.PUBLIC_RESEARCH_FILES:
            path = self.root / rel
            if path.exists():
                path.unlink()
        hashes.write_outputs(self.root)
        self.assertEqual(self.errors(), [])


if __name__ == "__main__":
    unittest.main()
