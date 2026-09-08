# Provenance Method

The repository treats research history as a directed constraint graph.

For a major result, preserve the chain:

```text
artifact
  → claim/result earned
  → burden or falsifier
  → alternatives eliminated
  → authority/status
  → downstream work licensed
```

## Minimum provenance record

A durable entry should identify, where available:

- stable entry ID;
- event date;
- recorded date;
- repository/package/artifact;
- exact SHA-256 or Git SHA;
- claim/result;
- status at the time;
- direct dependencies;
- correction/supersession relation;
- evidence class;
- downstream license;
- public DOI/URL or exact private source coordinate.

## Research correction

A failed formalization is not deleted from the record.

```text
hypothesis
  → attempted formalization
  → falsifier / insufficiency
  → correction
  → new result
```

The correction record is positive provenance evidence because it establishes that the later result was not obtained by silently redefining the earlier claim.

## Continuation frontier

Every mature branch should eventually state the smallest exact set a successor must read first. ORCHESTRA ancestor custody formalizes this as a successor start-here set.
