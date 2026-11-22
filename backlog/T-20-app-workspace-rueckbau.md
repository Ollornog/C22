---
id: T-20
type: Task
title: Remove the old app workspace (app-workspace.css and its block) after UnderDoc switched
status: erledigt
milestone: M-2
blocked_by: [T-19]
tags: [underdoc, app-workspace, aufraeumen]
created: 2026-11-21
---

# Remove the old app workspace after UnderDoc switched

`c22/static/css/app-workspace.css`, `blocks/navigation/app-workspace.html`, `app-workspace-drag.js` (if the
building block's own drag has taken over) and rule 14 for it stayed, marked deprecated, while UnderDoc still
emitted the old classes ([ADR-2](ADR-2-layout-packs.md), [T-19](T-19-underdoc-workspace-aus-bausteinen.md)).

## Done when

- UnderDoc loads `c22-underdoc.css` and none of the classes of the replacement list in T-19.
- The CSS file and the block move to `archive/` (repo rule: archive instead of delete) with a line in its
  README; `input.css` and `scripts/build-gallery.sh` no longer import it; the reference images of the block
  are gone (`tests/test_visual.py --renew` removes orphans); CHANGELOG names the removal as breaking.

## State (2026-11-22)

Done. UnderDoc no longer emits the old classes: since UnderDoc #137 (`17ec0b3`) its root class is gone and its class
check and browser suite are green against a stylesheet built from this branch (without `app-workspace.css`); the last
gaps it found were closed in C22 first (#153). Merged with:

- `app-workspace.css` and `blocks/navigation/app-workspace.html` in `archive/` (header, line in its README); no longer
  imported by `input.css` or `scripts/build-gallery.sh`; reference images of the block removed.
- `app-workspace-drag.js` stays under its name (UnderDoc vendors it, it drags the entries of `.workspace-tree`); its
  code was generic already, only its comments named the old block. The gallery demo in `c22.js` runs on
  `.workspace-tree` only.
- Rule 14: no `app-*.css` and no `c22-app-…` in the sources of `c22/` and `gallery/` (ADR-2), instead of "every
  selector under the root class".
- `tests/test_visual.py`: the checks of the old block are gone; the spreadsheet and the number-cell checks run on the
  example of `workspace-more.html`, dragging on `.workspace-tree`.
