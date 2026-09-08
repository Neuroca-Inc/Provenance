# Provenance

Auditable lineage for Neuroca research, methods, artifacts, corrections, and downstream inheritance.

This repository exists to answer a narrow question with exact coordinates:

> **Where did this result, method, constraint, or research decision come from, what was its status at the time, and what later work is entitled to inherit from it?**

It is not a replacement for the source repositories. It is a custody layer across them.

## Core rule

**Inclusion is not authority.**

A file can be historically important, superseded, rejected, stale, provisional, or merely a source anchor and still belong here. Authority is carried explicitly by status, lineage, hashes, exact source coordinates, and supersession records.

The repository therefore preserves:

- positive results;
- failed and rejected branches;
- corrections;
- open burdens;
- historical baselines;
- exact Git milestones;
- publication/DOI lineage;
- methodology evolution;
- source hashes for private or non-public artifacts that should not be copied into a public repository.

## Current provenance spine

```text
VDM / primitive work
    ↓
CF000
    ↓
Farey remainder recursion
    ↓
CF19 / lifted-object construction
    ↓
Phase Calculus operator development
    ↓
Active-Study / Phase 5 / QBL / Orthad
    ├── mathematical closure and downstream applications
    └── research-practice formalization
             ↓
          ORCHESTRA
             ↓
     ancestor-custody formalization
             ↓
           Cairn
```

The mathematical and methodological lineages are coupled but not collapsed into one another.

## Repository map

| Path | Role |
|---|---|
| `ledgers/` | Machine-readable provenance records and the analysis workbook |
| `chronology/` | Human-readable research chronology |
| `methodology/ORCHESTRA/` | Concrete ORCHESTRA methodology artifacts and lineage |
| `methodology/Cairn/` | Cairn continuation frontier |
| `records/` | Selected dated research records and evidence examples |
| `source-index/` | Rules for handling private/internal source material |
| `schemas/` | Status, entry, and classification contracts |
| `hashes/` | SHA-256 anchors for original source bundles and selected files |
| `scripts/` | Repository validation and deterministic hashing |
| `docs/` | Authority, methodology, release-review, and repository documentation |

## Canonical machine records

The CSV files are the canonical machine-readable surfaces.

- `ledgers/git-milestones.csv`
- `ledgers/git-crosslinks.csv`
- `ledgers/methodology-lineage.csv`
- `ledgers/source-artifact-index.csv`
- `ledgers/provenance-candidates.csv`

`ledgers/active-provenance-ledger.xlsx` is the human analysis/view layer.

## Private-source policy

The initial source review included material from a private internal standards/research repository.

The private archives themselves are **not** copied here. Their SHA-256 hashes are retained in `hashes/SOURCE_ARCHIVES_SHA256SUMS.txt`. Only artifacts deliberately selected for provenance value are copied into the public-ready tree.

A private artifact can therefore be represented in three ways:

1. **Included**: copied unchanged because its provenance role is clear.
2. **Hash-only**: exact source coordinate and SHA-256 retained, bytes withheld.
3. **Review required**: candidate indexed for deliberate later publication review.

See `ledgers/source-artifact-index.csv`.

## Append-only correction rule

Do not rewrite an old result to make it agree with a later result.

When a claim changes:

1. preserve the old row/artifact;
2. add the correcting or superseding row;
3. link it explicitly;
4. state what survives and what no longer controls.

The history of error correction is part of the provenance.

## Validation

```bash
python3 scripts/validate_repo.py
python3 scripts/update_hashes.py --check
```

To intentionally refresh the selected-artifact hash manifest:

```bash
python3 scripts/update_hashes.py --write
```

## Public release state

This tree is prepared as a public-ready provenance repository, but artifacts marked `HASH_ONLY`, `REVIEW_REQUIRED`, `WORKING_NOTE`, or `HISTORICAL_BASELINE` must retain those labels. Do not promote them merely because they are present here.

See `docs/PUBLIC_RELEASE_REVIEW.md`.
