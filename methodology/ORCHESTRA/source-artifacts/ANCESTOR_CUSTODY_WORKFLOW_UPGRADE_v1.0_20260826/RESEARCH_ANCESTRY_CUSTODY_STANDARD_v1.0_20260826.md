# Research Ancestry Custody Standard v1.0

Date: 2026-08-26

## Purpose

Every experiment and research package must preserve enough exact ancestry that a future researcher or agent can answer, without corpus-wide rediscovery:

1. Where did this work come from?
2. Which exact source bytes, packages, proofs, datasets, code roots, discussions, or prior experiments materially constrain it?
3. Which outputs in this package are decisive?
4. Which ancestors remain controlling or relevant after this package closes?
5. Which ancestors were superseded, narrowed, or reduced to historical provenance?
6. What exact files should a successor read first?

The standard separates **lineage** from **authority**. An ancestor is never deleted from lineage merely because it is superseded. Supersession changes its post-close relevance, not the fact that the package descends from it.

## Required package files

Every experiment/package must contain:

- `ANCESTRY.json` — machine authority for roots and material ancestors.
- `CLOSEOUT.json` — machine authority for decisive artifacts and ancestor disposition.
- `ANCESTRY.md` — optional/required human-readable explanation depending on host template.
- `CLOSEOUT.md` — human-readable closeout summary.

## Exact-reference rule

Every material ancestor gets a stable `ancestor_id` and either:

- an exact declared root plus root-relative path; or
- an exact URI.

Vague references are invalid. These do not satisfy custody:

- "Phase-5"
- "Active-Study"
- "the previous package"
- "the old proof"
- "latest run"
- "June Orthad work"

When bytes are locally available, record SHA-256. Package ancestors should record their manifest SHA-256 when available.

## Root registry

A package declares stable roots once, for example:

```json
{
  "root_id": "PC_CORPUS",
  "kind": "repository",
  "exact_path": "/media/justin/IronWolf/Data/VDM/Phase-Calculus-Research-Corpus"
}
```

Ancestors then use `root_id` plus `relative_path`, preventing both vague names and repeated giant absolute paths.

## Direct and transitive ancestry

Every ancestor records `depth`:

- `1` = direct ancestor used by this package;
- `2+` = transitive ancestor inherited through another package/source.

`inherited_via` identifies the direct ancestor through which a transitive source remains relevant.

When a successor package is created, transitive ancestry should be imported rather than forgotten and rediscovered.

## Authority is separate

`current_relevance` during work may be:

- `controlling`
- `active_upstream`
- `supporting`
- `historical_only`
- `superseded`

A source can remain an ancestor while no longer controlling current mathematics.

Artifact creation time, historical discovery time, current review time, and logical dependency order must not be conflated.

## Closeout rule

Before finalization, every package must identify its important local artifacts. These are not every file. They are the files a successor must understand to recover the package's actual contribution, such as:

- decisive result data;
- formal proof;
- executed notebook;
- negative control;
- verification report;
- exact derivation document;
- canonical code path;
- final handoff/custody artifact.

Each important artifact records:

- exact package-relative path;
- role;
- SHA-256;
- why it matters.

## Ancestor disposition at closeout

Every ancestor in `ANCESTRY.json` must appear exactly once in `CLOSEOUT.json` with one disposition:

- `CONTROLLING` — remains authoritative for successors.
- `STILL_RELEVANT` — remains required, but this package extends or narrows it.
- `SUPERSEDED_BY_THIS_PACKAGE` — replaced for the stated scope; preserve for provenance.
- `HISTORICAL_ONLY` — useful for chronology/discovery history, not current authority.
- `NO_LONGER_RELEVANT` — successors no longer need it; exact reason required.

Each row must also state:

- why that disposition is correct;
- what a successor should do with the ancestor.

Finalization fails if even one ancestor is absent from the disposition map.

## Successor frontier

Every closed package declares `successor_start_here`: the smallest ordered set of exact artifacts a successor should read first.

This is deliberately not a package summary. It is the continuation frontier that prevents agents from restarting archaeology from zero.

A good frontier usually begins with:

1. `CLOSEOUT.json`
2. `ANCESTRY.json`
3. the decisive derivation/result/proof artifacts

## Package-creation gate

An active package must declare at least one exact root at creation. Material ancestors must be registered before they are used as load-bearing sources.

## Package-finalization gate

A package may close only when:

- exact ancestry is complete;
- local decisive artifacts are explicitly identified and hashed;
- every ancestor has a post-close disposition;
- live ancestors are named explicitly;
- superseded ancestors remain in lineage with an exact replacement reason;
- `successor_start_here` is complete;
- the package validator passes.

## Failure modes this standard is designed to stop

- a later agent knows a theorem was proved but cannot locate the proof;
- a package says "derived from Phase-5" instead of naming the exact artifact;
- an older OPEN/PENDING label is resurrected after later closure;
- a successor reads a downstream package but loses the still-live upstream source;
- a local agent performs corpus-wide search even though exact ancestor coordinates already exist;
- a package contains hundreds of files but does not say which five actually matter;
- supersession is expressed by deleting provenance rather than classifying it;
- package version numbers are mistaken for global chronology.

## Governing invariant

A closed package must be self-locating in the research graph.

A successor should never need to infer ancestry from filenames, timestamps, prose memory, or broad semantic search when the exact source was known at package creation or closeout.
