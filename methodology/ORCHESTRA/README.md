# ORCHESTRA

ORCHESTRA is the provenance-tracking research methodology that emerged from the Taoism / Active-Study research process.

## Concrete preserved milestones

### 2026-08-04 — Research Package Template v2.0

Defines an iterative evidence package with:

- package identity and lineage;
- active semantic authority;
- stable claim IDs;
- burden and falsifier per claim;
- positive, negative, unresolved, and falsified findings;
- Guardian/Auditor review custody;
- immutable closeout ZIP + SHA-256.

### 2026-08-04 — Publication Package Template v2.0

Separates mutable research work from immutable reader-facing release custody and requires exact source-package IDs and manifest SHA-256 values.

### 2026-08-21 — Research and Evidence Standard v1.0.1

Generalizes the methodology beyond one package implementation and explicitly preserves source conflicts, negative findings, append-only lab history, formal-proof faithfulness, and the distinction between research closure and publication closure.

### 2026-08-26 — Ancestor Custody Workflow Upgrade v1.0

Adds exact ancestry and closeout disposition. Every closed package must identify:

1. what it descends from;
2. decisive local artifacts;
3. still-live ancestors;
4. superseded/historical ancestors;
5. the successor's exact start-here frontier.

The accompanying ORCHESTRA v2.1 template makes this machine-readable through `ANCESTRY.json` and `CLOSEOUT.json`.

## Source custody

The preserved artifacts are exact copies selected from the supplied internal standards bundle. Their source package/tree hashes are indexed in `../../ledgers/source-artifact-index.csv`.
