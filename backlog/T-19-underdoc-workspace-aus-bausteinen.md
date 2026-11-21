---
id: T-19
type: Task
title: UnderDoc workspace from C22 building blocks plus the pack underdoc
status: in-arbeit
milestone: M-2
tags: [underdoc, bausteine, packs, app-workspace]
created: 2026-11-21
---

# UnderDoc workspace from C22 building blocks plus the pack `underdoc`

## Finding

`app-workspace.css` (T-14) carries UnderDoc's approved mockup as one look with its own classes. Rule and
decision: [ADR-2](ADR-2-layout-packs.md). The structure is rebuilt from `.workspace` and its parts; the look
of the mockup moves into the pack `underdoc` (`c22/static/css/packs/underdoc.css`).

## Steps

1. **Core** — top row, nav1/nav2/nav3 with the list, the window with its tab, tools, title, document and
   status line; light, dark, phone. New block `blocks/navigation/document-workspace.html`, reference images in
   `vega` and `underdoc`, the pack in the gallery's picker. Replacement list for UnderDoc (below, filled with
   the core).
2. **Editing parts** of the old block (examples c–i): editor bar of a block, `/` menu, handle with its menu,
   embedded block, page editor bar with table tools, quick notes with handle. Each as part of an existing
   component or a new one, the mockup look in the pack.
3. **Panels and dialogs** (examples j–p): New from a template, gear view as segments, deleting what is used
   elsewhere, marked text in the editor, file in a window with its panel, spreadsheet in the workspace (the
   grid is already `.table[data-variant="grid"]`).

## Done when

- Every example of `app-workspace.html` has a counterpart from building blocks that looks like the rest of
  a pack without `underdoc` and like the mockup with it (reference images for both).
- The replacement list covers every class of `app-workspace.css` that UnderDoc emits.
- UnderDoc runs on `.workspace` + `c22-underdoc.css`; then T-20 removes the old block.
