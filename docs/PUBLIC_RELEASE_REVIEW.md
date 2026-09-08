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

Review `ledgers/source-artifact-index.csv` for every row marked:

- `HASH_ONLY`
- `REVIEW_REQUIRED`
- `WORKING_NOTE`
- `HISTORICAL_BASELINE`

Those labels are part of the artifact's provenance and should remain visible if the artifact is published.
