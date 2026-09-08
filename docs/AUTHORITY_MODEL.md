# Authority Model

Provenance answers **where a statement came from**. Authority answers **what controls now**. They are related but not identical.

## Artifact classes

- `CURRENT_CANON` — controls the stated mathematical/research scope.
- `METHODOLOGY_SOURCE` — controls or documents a research-methodology rule.
- `RESEARCH_EVIDENCE` — evidence supporting, testing, falsifying, or correcting a claim.
- `WORKING_NOTE` — active or historical work with explicitly open burdens.
- `HISTORICAL_BASELINE` — exact dated snapshot retained for comparison.
- `HISTORICAL_SOURCE` — chronology/discovery evidence, not current authority.
- `SUPERSEDED` — replaced for a stated scope but preserved.
- `REJECTED` — failed model/claim/implementation retained as negative provenance.
- `HASH_ANCHOR` — source bytes withheld; exact hash and coordinate retained.
- `REVIEW_REQUIRED` — provenance candidate not yet cleared for public/current use.

## Precedence

1. Exact active semantic authority for the claim's scope.
2. Explicit successor/supersession record.
3. Exact source/package ancestry.
4. Timestamp/commit history as chronology evidence.

A later timestamp does not automatically imply stronger mathematical authority.

## Conflict handling

Do not silently reconcile contradictory artifacts. Record:

- both exact sources;
- their authority class;
- the scope of the conflict;
- the controlling source;
- the reason it controls.
