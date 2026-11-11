# Public Release Review

This repository was assembled partly from a private internal source library. The source library itself explicitly distinguishes canonical authority from historical/profile/archive material.

## Included unchanged

The following classes were deliberately copied because their provenance role is clear:

- ORCHESTRA research/publication package templates;
- Research and Evidence Standard v1.0.1;
- Ancestor Custody Workflow Upgrade v1.0;
- Phase Calculus inverse-seed working note v0.3;
- Cortex retained baseline dated 2026-07-26;
- selected VLL run provenance and correction artifacts;
- Analogistical Constructivism project-status snapshot.

## Hash-only

The following are anchored but not copied:

- full private source archives;
- Phase Calculus derivation standard containing internal source-path custody;
- Analogistical Constructivism deep research draft;
- Analogistical Constructivism research archive.

## Before pushing public

Review `source-index/source-artifact-index.csv` for every row marked:

- `HASH_ONLY`
- `REVIEW_REQUIRED`
- `WORKING_NOTE`
- `HISTORICAL_BASELINE`

Those labels are part of the artifact's provenance and should remain visible if the artifact is published.

## Preserved source/copy discrepancy

`SRC-ORCH-003` asserts source SHA-256
`ead6071e69929376f52061c3bdf17cfb7befaae25c1aa936b4474f09cd81a4f9`.
The included Research and Evidence Standard file has copied-byte SHA-256
`4dad970c0de6771bd7269a5917762c567ba5c2d5531b54b45c7d12bfd5c48d9a`,
also recorded in `methodology/ORCHESTRA/artifact-index.csv`. Both assertions and
the historical file bytes are preserved. The cause of the discrepancy and the
identity of the omitted upstream source remain unresolved. Validation warns for
this exact known pair; it does not treat the two digests as equal or independently
verify an omitted archive. Any other copied-byte discrepancy fails validation.
