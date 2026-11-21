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

## Replacement list for UnderDoc (step 1, core)

Load `c22-underdoc.css` instead of `c22-vega.css` and drop the root class `.c22-app-workspace`. Markup to copy:
`blocks/navigation/document-workspace.html`. Behaviour (column grips, list toggles, tab history, drawer) is
`c22.js`; stored widths `data-workspace-store` + `workspace-boot.js`.

| Old class (app-workspace.css) | Building block |
|---|---|
| `.c22-app-workspace` (root), `.main`, `.side`, `.navs`, `.rail`, `.work`, `.wins` | `.workspace` — one grid, no wrappers |
| `.brandrow` | `header.workspace-top` |
| `.brand` (`img` + `span`) | `a.brand` > `span.brand-mark` (glyph) + `span` (the pack drops the plate) |
| `input.search` | `form[role=search]` > `input.input[type=search]` |
| `.ic.newbtn` | `.btn[data-variant=outline][data-size=icon-sm]` |
| `nav.strip.col.s0`…`s3` | `nav.workspace-nav[data-level="1"][data-step="0"…"3"]` |
| `.n1top` / `.n1bot` | the column's `div` / `footer` |
| `.navitem` (+ `aria-pressed="true"`) | `.workspace-item` (+ `aria-current="page"`) |
| `.lbl` | the item's `span` |
| `.sep` | `hr` |
| `.spacer` (in nav1) | `span[data-fill]` |
| `.n1lab` | `.workspace-label` |
| `.avatar.tiny` | `.avatar[data-size=sm]` inside the item |
| `.grip[data-grip=n]` (+ `--w1/--w2/--w3` on `html`) | `span[data-grip][role=separator][tabindex=0]` as last child of the column; widths `--workspace-step-0…3`, `--workspace-nav3` |
| `nav.nav2.col` | `nav.workspace-nav[data-level="2"][data-step]` |
| `.n2head` + `.addbtn.newplus` (`.nt`) | the column's `header` > `span` + `.btn[data-variant=outline][data-size=xs]` with `<span>Neu</span>` and the plus icon |
| `#clist`, `.collrow` | the column's `div` with `.workspace-item`s (`data-pinned` stays) |
| `.collrow.deco[data-deco=line]` | `hr` |
| `.nav3`, `.tree` | `nav.workspace-nav[data-level="3"]` > `div` > one `section` per open collection |
| `.cheadrow` (`.first`) | `section > header` (the first section has no line above it) |
| `.chead` | `header > a` (+ `span`) |
| `.addbtn.newplus` in a section head | `.btn[data-variant=outline][data-size=xs]` |
| `ul.t.top` / `ul.t` | `ul.workspace-tree` / nested `ul` (`hidden` when closed) |
| `.row` | `li > div` |
| `.arrow.open` / `.arrow` / `.arrow.none` | `button[data-toggle][aria-expanded=true]` / `…=false` / `span[data-toggle][aria-hidden=true]` |
| `.name` (+ `span`) | `button` (or `a`) after the toggle, with its icon and `span` |
| `.row.cur` (`::after` "open") | `aria-current="page"` on the name + `<small>offen</small>` |
| `.count` | `small` in the row |
| `section.win.focus` | `main.workspace-main` (one window; several windows: step 2) |
| `.tabrow` | `.workspace-tabs` |
| `.tabscroll` | `div[role=tablist]` |
| `.dtab` / `.dtab.on` | `.workspace-tab` / its `button[role=tab][aria-selected=true]` |
| `.dtab.general` / `.stack` | `.workspace-tab[data-general]` / `[data-stack]` |
| `.sel` | `button[role=tab]` (+ `span`) |
| `.mini.histbtn` | `.dropdown-menu` > `button` + `[data-popover]` menu "Vorher hier geöffnet" |
| `.ic.tabend`, `.aibtn` | `.btn[data-variant=ghost][data-size=icon-sm]` directly in `.workspace-tabs` |
| `.tools` | `main > header > div` |
| `.place` | `nav.breadcrumb` > `ol` > `li` (separators `li[aria-hidden]` with a chevron) |
| `.tagline`, `.tagc` | `a.badge[data-variant=outline]` (the pack makes it a square chip) |
| `.tspace` | `span[data-fill]` before the tools |
| `.marker` + `.chip` + `.fly` (sections) | `.dropdown-menu` > `.btn[data-variant=outline][data-size=xs]` + `[data-popover]` > `role=menu` with links |
| `.ic` in the tools | `div[role=toolbar]` > `.btn[data-variant=ghost][data-size=icon-sm]` |
| `.dtitle h1` | `main > header > h1` (a description: `p`) |
| `.wbody`, `.scroll` | `main > section` |
| `article.doc.slim` / `.wide` / `.full` | `article.typeset[data-width="slim"/"wide"/"full"]` |
| `.status` (+ `.spacer`) | `main > footer` (+ `span[data-fill]`) |

Still open for step 2 and 3: `.toc` (contents column beside the document), several windows (`.wins.many`, drop
zones), `.strip .tab`/`.seg`/`.bar` of the old top bar, and every class of the editing and panel examples
(`.bedit`, `.btool`, `.bmenu`, `.emb*`, `.facts`, `.kids`, `.imgs`, `.note`, `.v`, `.tw`, `.src`, `.spanel` …).
