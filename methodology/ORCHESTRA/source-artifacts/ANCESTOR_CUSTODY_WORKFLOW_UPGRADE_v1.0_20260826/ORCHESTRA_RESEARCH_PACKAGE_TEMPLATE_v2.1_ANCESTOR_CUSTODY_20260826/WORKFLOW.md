# Orchestra Research Package Workflow

## Role and version law

- Operator work occurs inside the active version.
- Guardian PASS or FAIL is written into the same version and never advances `v#`.
- Auditor PASS or FAIL closes the adjudication and advances the next package version.
- A successor records the parent package ID and parent manifest SHA-256.
- Reviewers do not silently rewrite the evidence they adjudicate.

## Terminal rule

The branch remains active until its declared terminal condition is met. Intermediate repairs, infrastructure work, negative controls, and partial lemmas are not terminal unless explicitly declared so.

Normal terminal outcomes are:

- a nontrivial positive internally generated result;
- a proof that the branch hypothesis is false;
- an exact external dependency that makes further work impossible, recorded as `BLOCKED`, not `PASS`.

## Evidence classes

- `RULE`
- `CURRENT-CANON RESULT`
- `RECOVERED`
- `PROVISIONAL`
- `CONDITIONAL DOWNSTREAM`

## Working statuses

- `UNTESTED`
- `IN_PROGRESS`
- `PASS`
- `FAIL`
- `BLOCKED`
- `SUPERSEDED`
- `NOT_APPLICABLE`

`NOT_APPLICABLE` requires a scientific reason.

## Closure

1. Remove all active placeholder markers.
2. Confirm every claim has a burden, falsifier, and exact artifact references.
3. Confirm each notebook satisfies the no-I/O, one-cell-per-claim contract.
4. Confirm each decision figure also exists in top-level `figures/`.
5. Run `tools/finalize_package.py`.
6. Preserve the ZIP and external `.sha256` together.
7. Never alter a closed ZIP; create a successor version.

## Ancestor-custody law

Every active package must carry `ANCESTRY.json` from creation through closure.

- Every material upstream source gets a stable `ancestor_id` and an exact local path or URI.
- Package ancestors record their manifest SHA-256 when available.
- File ancestors record SHA-256 when the referenced bytes are locally available.
- Direct and transitive ancestors remain distinct through `depth` and `inherited_via`.
- A source may be historically important without remaining current authority; do not delete it from lineage to express supersession.
- Exact references are mandatory. Labels such as “Phase-5”, “Active-Study”, “the prior experiment”, or “latest paper” are insufficient.

Before work begins, read `ANCESTRY.json` and the exact controlling ancestors before broad corpus search.

## Closeout law

A package may not close until `CLOSEOUT.json` records:

1. the decisive artifacts of this package;
2. the important claims successors must retain;
3. one disposition for every ancestor in `ANCESTRY.json`;
4. which ancestors remain `CONTROLLING` or `STILL_RELEVANT`;
5. which ancestors are superseded or historical only, and exactly why;
6. the minimal ordered `successor_start_here` frontier.

Finalization fails if any ancestor is absent from the closeout disposition map or any closeout reference is vague, missing, placeholder text, or points to absent package bytes.
