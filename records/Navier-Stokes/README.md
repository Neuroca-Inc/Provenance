# Navier–Stokes historical correction lineage

These seven records preserve a historical correction lineage. Their original
bytes and wording are unchanged. They are source reports, not independent theorem
certification, endorsement of priority claims, or verification of external results.
In particular, an author's use of “proved,” “closure,” or “independent realization”
inside a preserved record is not an authority promotion by this repository.

| ID | Preserved record | Role and date stated by the record |
|---|---|---|
| SRC-NS-001 | `CF10_NAVIER_STOKES_POLARITY_LOCK.md` | Correction distinguishing original intent, first polarity inversion, and later rejected closure. Preparation date unstated. |
| SRC-NS-002 | `CF10_RECOVERY_PROOF_01_interface_accumulation.md` | Source-reported bridge proof claim; retained continuation remains the next burden. Dated 2026-09-08. |
| SRC-NS-003 | `LIR_CF10_OPENAI_PROVENANCE_AND_PERIMETER_PROOF_v2.md` | Source-reported lineage and normalized-annulus/perimeter correspondence proof claim. Prepared 2026-09-08. |
| SRC-NS-004 | `LIR_CF10_OpenAI_Provenance_Correction.md` | Correction of the later unconditional regularity direction, with source-reported priority/correspondence claims. Prepared 2026-09-08. |
| SRC-NS-005 | `MASTER_PROVENANCE_RECOVERY_DOSSIER_v0.2.md` | Non-exhaustive recovery dossier locating the first formalization's polarity inversion. Prepared 2026-09-08. |
| SRC-NS-006 | `MASTER_PROVENANCE_RECOVERY_DOSSIER_v0.3.md` | Extends earlier fluid-target chronology; does not claim recovery of a CF10-named November 4 artifact. Prepared 2026-09-08. |
| SRC-NS-007 | `MASTER_PROVENANCE_RECOVERY_DOSSIER_v0.5.md` | Adds pre-LIR lineage, claimed perimeter-law closure, and a normalization erratum. Prepared 2026-09-08. |

The dossier sequence v0.2 → v0.3 → v0.5 is retained rather than overwritten. The
v0.5 dossier mentions a correspondence-proof v1 file not present in this directory;
that reference is preserved as a source statement, not treated as a recovered
artifact. No v0.4 dossier is inferred.

The polarity lock distinguishes the original research intention from the first
CF10 formulation and the later rejected regularity proof. The recovery note leaves
the complete lifted state's continuation across an infinite interface accumulation
as an explicit further burden. Indexing these records does not resolve that burden.

## Exact-byte custody

The seven `SRC-NS-*` entries in
[`../../source-index/source-artifact-index.csv`](../../source-index/source-artifact-index.csv)
and [`../../ledgers/master-evidence-index.csv`](../../ledgers/master-evidence-index.csv)
contain file SHA-256 digests, source-reported roles, and the exact repository path
at `Neuroca-Inc/Provenance@bb7bc32fe24ad1db2a20ec0033499ccfb194cb4f`.
That snapshot is a custody anchor, not proof of first authorship or creation time.
The six stated preparation dates are preserved as source-reported event dates.
The polarity lock's Event_Date is blank: its embedded 2025-11-27 date describes the
older CF10 formalization, not preparation of the polarity-lock record.

## Integrity checks

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/update_hashes.py --write
python3 scripts/update_hashes.py --check
python3 scripts/validate_repo.py
```

Use `--write` only after intentional repository edits; checking never rewrites
source assertions. The generated layers have an acyclic dependency:

1. `hashes/SELECTED_ARTIFACTS_SHA256SUMS.txt` hashes all non-generated repository
   files, including hidden configuration, scripts, tests, and newly added paths.
2. `MANIFEST.json` records exact-byte sizes/hashes of those files plus the selected
   checksum file, and derives current master/source row counts from CSV records.
3. `SHA256SUMS` hashes those files plus the manifest, excluding itself.

Only these three exact root-relative generated paths are self-excluded. Historical
copies with the same filenames remain normal inputs. Git metadata, Python/tool
cache directories, and the temporary-file patterns declared in
`scripts/update_hashes.py` are excluded. Symlinks and ambiguous checksum filenames
are rejected. No wall-clock generation timestamp is emitted, so repeated runs
produce identical bytes. `hashes/SOURCE_ARCHIVES_SHA256SUMS.txt` is preserved input:
omitted source archives are not rehashed or silently replaced with local copies.

Validation checks the seven baseline records even if an index row is deleted,
requires both indexes for additional Markdown records in this directory (except
this README), and checks copied-file hashes independently of generated outputs.
Active-ledger IDs must be unique, and named dependencies/corrected-entry IDs must
exist. A documented legacy ORCHESTRA source/copy discrepancy is reported in
[`../../docs/PUBLIC_RELEASE_REVIEW.md`](../../docs/PUBLIC_RELEASE_REVIEW.md); it is
not erased or treated as equality.
