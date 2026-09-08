# Ledgers

## Canonical machine-readable surfaces

- `git-milestones.csv`
- `git-crosslinks.csv`
- `methodology-lineage.csv`
- `source-artifact-index.csv`
- `provenance-candidates.csv`

## Human analysis surface

- `active-provenance-ledger.xlsx`

The spreadsheet is a view/analysis layer. CSV records should remain easy to diff in Git.

## Editing rule

Never replace an old provenance row to make history cleaner. Add a successor/correction row and link the two.
