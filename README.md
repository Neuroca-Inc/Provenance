# Neuroca Provenance

**Auditable lineage, not a code warehouse.**

This repository answers:

> What existed, when did it exist, what was its status, where is the exact source, and what later work inherited from it?

It deliberately does **not** mirror Neuroca's research or production repositories. Code, notebooks, datasets, large execution packages, and private source trees stay where they were created. This repository carries the evidence graph needed to locate and interpret them.

## Unified evidence surfaces

| Surface | What it preserves |
|---|---|
| `ledgers/master-evidence-index.csv` | One cross-surface index spanning public releases, Git milestones, methodology, legacy manuscripts, and selected internal artifacts |
| `public/reach/` | The supplied reach ODS plus normalized 188-record public Zenodo/GitHub release ledger |
| `git-history/` | Major commit milestones and theory crosslinks from VDM, primitive bifurcation, Taoism/Active-Study, Cortex, and vdm_rt |
| `chronology/` | Human research/dependency chronology |
| `historical/legacy-cf/` | Complete metadata/hash index for the supplied legacy CF archive plus three decisive historical snapshots |
| `methodology/ORCHESTRA/` | Decisive methodology documents only; package tools/scaffolding remain in the source archive |
| `methodology/Cairn/` | The post-ORCHESTRA methodology frontier |
| `records/` | A small number of dated/corrective research records whose historical wording itself is provenance evidence |
| `source-index/` | Hash/source-coordinate custody for omitted private or bulky artifacts |
| `ledgers/active-provenance-ledger.xlsx` | Human analysis view over the canonical CSV surfaces |

## Public release corpus

The supplied `20260907_reach.ods` contains **188 records**: **156 Zenodo** and **32 GitHub**, covering **2025-01-08 through 2026-09-04**. It is preserved unchanged under `public/reach/` and normalized to CSV for diffs and analysis.

## Provenance rule

Presence is not authority. Historical, rejected, superseded, open, working, and current records may all be present. Status and lineage determine authority.

When a result changes, preserve the old record and add the correction. Never clean the historical path to make the present look inevitable.

## What is intentionally omitted

- source-code mirrors;
- notebook forests;
- model/runtime binaries;
- large datasets and experiment outputs;
- full private internal bundles;
- ORCHESTRA helper scripts and template scaffolding that are implementation details rather than lineage evidence.

Those remain recoverable through repository URLs, commit SHAs, archive hashes, package hashes, and source coordinates recorded here.

## Start here

1. `ledgers/master-evidence-index.csv`
2. `chronology/phase-calculus-chronology.md`
3. `public/reach/major-public-milestones.csv`
4. `git-history/git-milestones.csv`
5. `ledgers/methodology-lineage.csv`
6. `historical/legacy-cf/legacy-cf-index.csv`
7. `source-index/source-artifact-index.csv`
