# Research Ancestor Custody Overlay v1.0

Drop this overlay into any experiment or research package that is not already using Orchestra Research Package Template v2.1.

It enforces two lifecycle records:

- `ANCESTRY.json`: exact roots and every material ancestor source/package/artifact.
- `CLOSEOUT.json`: decisive local artifacts and the post-close relevance of every ancestor.

The contract is designed to prevent provenance amnesia, stale-status resurrection, and local agents rediscovering known derivations from scratch.

## Required lifecycle

1. At package creation, declare one or more exact roots in `ANCESTRY.json`.
2. Before using an upstream source materially, assign it an `ancestor_id` and exact root-relative path or URI.
3. During work, claims/source maps may refer to ancestor IDs, but IDs never replace exact coordinates.
4. Before closure, run `python tools/prepare_closeout.py .`.
5. Classify every ancestor in `CLOSEOUT.json`.
6. List the package's decisive files with hashes and the minimum `successor_start_here` frontier.
7. Run `python tools/validate_custody.py . --strict`.

A package cannot close merely because all results are present. It closes only when a successor can identify exactly where the work came from, which local files matter, and which ancestors remain live.
