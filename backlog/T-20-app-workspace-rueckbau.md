---
id: T-20
type: Task
title: Remove the old app workspace (app-workspace.css and its block) after UnderDoc switched
status: offen
milestone: M-2
blocked_by: [T-19]
tags: [underdoc, app-workspace, aufraeumen]
created: 2026-11-21
---

# Remove the old app workspace after UnderDoc switched

`c22/static/css/app-workspace.css`, `blocks/navigation/app-workspace.html`, `app-workspace-drag.js` (if the
building block's own drag has taken over) and rule 14 for it stay, marked deprecated, while UnderDoc still
emits the old classes ([ADR-2](ADR-2-layout-packs.md), [T-19](T-19-underdoc-workspace-aus-bausteinen.md)).

## Done when

- UnderDoc loads `c22-underdoc.css` and none of the classes of the replacement list in T-19.
- The CSS file and the block move to `archive/` (repo rule: archive instead of delete) with a line in its
  README; `input.css` and `scripts/build-gallery.sh` no longer import it; the reference images of the block
  are gone (`tests/test_visual.py --renew` removes orphans); CHANGELOG names the removal as breaking.
