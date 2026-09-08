# VDM Analysis / Experiment Template v2.0 — Ancestor Custody

Use this directory for one experiment or analysis run.

## Required before work

1. Replace the root declarations in `ANCESTRY.json` with exact repository/data roots.
2. Register every material upstream source, proof, package, dataset, code root, or earlier experiment with a stable ancestor ID and exact path/URI.
3. Hash locally available ancestor files.
4. Use `source_maps/ANCESTOR_SOURCE_MAP_TEMPLATE.md` to connect local claims/results to ancestor IDs.

## During work

- `scripts/`: executable analysis code.
- `reviewer_friendly_notebooks/`: executed claim notebooks.
- `analysis_data/`: exact generated/consumed data for this run.
- `figures/`: decision figures.
- `trace_logs/`: ordered execution traces.
- `docs/`: methods/results documentation.

Do not use vague ancestry such as “Active-Study”, “previous run”, or “latest package” when the exact path is known.

## Closeout

Before tying up the experiment:

1. identify the decisive package artifacts in `CLOSEOUT.json`;
2. hash each decisive artifact;
3. classify every ancestor as `CONTROLLING`, `STILL_RELEVANT`, `SUPERSEDED_BY_THIS_PACKAGE`, `HISTORICAL_ONLY`, or `NO_LONGER_RELEVANT`;
4. state why and tell successors what to do with each ancestor;
5. populate `successor_start_here` with the minimum ordered continuation frontier;
6. run:

```bash
python tools/validate_custody.py . --strict
```

An experiment is not tied up until that validation passes.
