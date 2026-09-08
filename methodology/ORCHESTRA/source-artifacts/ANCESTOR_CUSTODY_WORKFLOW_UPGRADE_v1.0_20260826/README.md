# Ancestor Custody Workflow Upgrade v1.0

This bundle adds exact ancestry and package-closeout custody to the existing research workflow.

## Contents

- `RESEARCH_ANCESTRY_CUSTODY_STANDARD_v1.0_20260826.md` — governing standard.
- `ORCHESTRA_RESEARCH_PACKAGE_TEMPLATE_v2.1_ANCESTOR_CUSTODY_20260826/` — enforced Orchestra package template.
- `VDM_ANALYSIS_TEMPLATE_v2.0_ANCESTOR_CUSTODY_20260826/` — experiment/analysis template.
- `RESEARCH_ANCESTOR_CUSTODY_OVERLAY_v1.0_20260826/` — drop-in custody files and validator for existing packages.

## Core invariant

Every closed package must answer with exact coordinates:

1. what it descends from;
2. which local artifacts matter;
3. which ancestors remain live;
4. which ancestors are superseded/historical;
5. what the successor must read first.

## Tested behavior

The v2.1 Orchestra inheritance tool was exercised with a parent and child package. The child retained the parent as depth 1, inherited the parent's source ancestor at depth 2, recorded `inherited_via`, and `prepare_closeout.py` populated both ancestors into the closeout disposition map.

The generic custody validator was also exercised in strict mode against exact local source and result hashes and returned `PASS`.
