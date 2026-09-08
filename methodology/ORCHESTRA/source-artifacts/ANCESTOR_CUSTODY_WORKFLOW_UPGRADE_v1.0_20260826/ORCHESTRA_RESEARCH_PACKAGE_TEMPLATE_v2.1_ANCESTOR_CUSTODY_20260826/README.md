# Orchestra Research Package Template v2.1 — Ancestor Custody

This is the canonical seed for one **iterative research evidence package** managed through Orchestra.

It is not a publication bundle. It contains no inherited scientific result, historical canon, sample figure, fake dataset, or pre-filled review verdict.

## Active package identity

```text
p<phase>-b<branch>-v<version>_<descriptive-name>_<YYYYMMDD_HHMMSS>
```

Example:

```text
p5-b3-v19_orthad-transport-commutator_20260804_223600
```

The directory name is navigation. `PACKAGE.json` is the machine authority for identity, lineage, roles, branch goal, terminal condition, and active semantic authority.

## Create a package

```bash
python tools/init_package.py   --phase 5 --branch 3 --version 19   --name orthad-transport-commutator   --origin-role Operator --target-role Guardian   --output /path/to/research/packages
```

## Working sequence

1. Declare the branch question and terminal condition in `PACKAGE.json` and `HANDOFF.md`.
2. Copy controlling inputs into `inputs/`; never silently edit them.
3. Record controlling authority and exclusions in `AUTHORITY.md`.
4. Assign stable claim IDs in `CLAIMS.md` before generating evidence.
5. Implement work in `src/`, `notebooks/`, or `lean/`.
6. Put every decision figure in top-level `figures/`.
7. Put generated data in `output_data/`, provenance in `source_maps/`, and ordered traces in `trace_logs/`.
8. Record positive, negative, unresolved, and falsified findings in `FINDINGS.md`.
9. Store Guardian and Auditor adjudication only in `review/` under the version law in `WORKFLOW.md`.
10. Freeze the package with `python tools/finalize_package.py .`.

## Non-negotiable rules

- No fake `.csv`, `.db`, `.h5`, `.json`, `.ipynb`, code, proof, or result placeholders.
- No handwritten release manifest. Generate it from final bytes.
- Every claim names its burden, falsifier, status, and exact artifacts.
- Negative and unresolved findings remain visible.
- Notebook runtime performs no file I/O.
- Each notebook claim cell emits numeric results, a declared threshold, a negative control, a decision figure, and explicit PASS/FAIL.
- Notebook figures do not replace individual package-level files in `figures/`.
- Guardian PASS or FAIL stays in the same version.
- Only Auditor PASS or FAIL advances the version.
- A package closes only on its declared terminal condition.

## Validation

Template mode:

```bash
python tools/validate_package.py .
```

Active closure mode:

```bash
python tools/validate_package.py . --strict
```

## Ancestor custody added in v2.1

Every experiment/package now has two mandatory machine-readable lifecycle records:

- `ANCESTRY.json`: exact roots and all material upstream ancestors.
- `CLOSEOUT.json`: decisive local artifacts plus the disposition of every ancestor when the package closes.

Use `tools/add_ancestor.py` during work and `tools/prepare_closeout.py` before finalization. Strict validation refuses packages with vague ancestry or incomplete closeout custody.

For successors, import the entire parent lineage with:

```bash
python tools/inherit_parent_ancestry.py . --parent /exact/path/to/parent-package
```

This makes the direct parent depth 1 and carries its material ancestors forward at depth 2+.
