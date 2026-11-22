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

## State (2026-11-21)

- Step 1 (core): #140. Steps 2 and 3: blocks `workspace-editing.html` and `workspace-more.html`, the third example of
  `document-workspace.html`; reference images in vega and `underdoc` (#141).
- Step 4 (2026-11-22): the other views (mail, messages, tasks, calendar, board, assistant, comments, search), dragging a
  tab and the drop zones of a window, menus of the workspace at the mockup's size: block `workspace-views.html`,
  reference images in vega and `underdoc`. The switch `data-behaviour="app"` leaves the workspace to an app that drives
  it itself (c22.js keeps its other parts).
- Fix (2026-11-22, from UnderDoc's switch): the read/edit toggle has its own size (`--workspace-mode-size`) and no
  longer lets a wrapped tool row run over the title; a window without a tab row takes that row too.

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

## Replacement list for UnderDoc (steps 2 and 3)

Markup to copy: `blocks/navigation/workspace-editing.html` (editing), `workspace-more.html` (drag, New, gear, file,
sheet) and the third example of `document-workspace.html` (several windows, contents as a column). Every class of
`app-workspace.css` not in the core list above:

| Old class | Building block |
|---|---|
| **Editor** | |
| `.bedit` | `.editor-block` (block being edited: `[data-add]` button + `textarea.textarea`) |
| `.btool`, `.btool.edbar` | `.editor-bar[role=toolbar]` — above a block inside `.editor-block`, as a window row `.workspace-main > .editor-bar` |
| `.bgroup`, `.bsep` | `div[role=group]` inside `.editor-bar` (the line before a group is the group's) |
| `.btype` | `select.select[data-size=sm]` first in the bar |
| `.asking`, `.cnum` | `.btn[data-variant=ghost][data-size=icon-sm]` with `aria-pressed`; a count via `[data-count]` |
| `.bplus` | `.btn[data-add][data-variant=ghost][data-size=icon-xs]` |
| `.bslash`, `.cm-ud-slashbox` | `.command` (list of block kinds, `aria-disabled` + "später") |
| `.bhandle`, `.bmenu`, `.bused` | `[data-block]` > `.dropdown-menu.editor-handle` (trigger `.btn` ghost icon-xs with grip icon; `data-align="end"` in a card); "Verwendet in" as `div[role=heading]` after an `hr` |
| `.cblk`, `.has` | comment bubble `.comment-anchor` > `[data-comment]` (+ `data-count`) |
| `.dstatus` | `.btn[data-mode]` first in `.workspace-main > header`, `aria-pressed="true"` while editing |
| `.cm-editor.cm-ud` (and `.cm-line`) | the page in the editor: `.editor` (CodeMirror keeps its own DOM; its decorations take these:) |
| `.cm-ud-used`, `-used-first/-last`, `-usedlabel` | `.editor [data-used]` + `small` (where it is used) |
| `.cm-ud-ask` | `.item[data-variant=muted][data-size=sm]` with the question in `section` and `.btn[data-size=xs]` in `aside` |
| `.cm-ud-plain` | `underline decoration-wavy decoration-destructive` (utilities) |
| `.cm-ud-embed`, `-embed-what` | `a.badge[data-variant=secondary]` with a muted first `span` |
| `.cm-ud-part`, `-partlabel`, `.partedge`, `.partlabel` | `[data-part="<name>"]` (dotted underline), `data-framed` shows frame and name |
| `.cm-ud-marker` | stays the app's (an empty CodeMirror widget, no look) |
| `.embed`, `.embhead`, `.embedbody` | `figure.editor-embed` (content, `figcaption` with the link back) |
| `.embed.broken`, `.unplaced` | `figure.editor-embed[data-state=missing]` with the words; removed with actions: buttons inside |
| `.badge[data-removed]`, `.placed` | `.badge[data-variant=destructive]` + `.btn[data-variant=outline][data-size=xs]` |
| `.wayspop`, `.wayitem`, `.wayrow`, `.waysame` | a `.card` (or `.dialog`) with one section per thing: `h4`, muted `p`, `.btn[aria-pressed]` choices + `select.select`; `label` > checkbox "Dasselbe für alle"; `.btn` destructive + outline |
| `.keep`, `.kard`, `.noteadd` | `.input` to add, a grid of `article.card[data-size=sm][data-block]` (handle inside) |
| `.findin` | `.input-group` in the bar (search on the page) |
| `.src` | `pre.code-block[data-line-numbers]` |
| **Lists, drag, New** | |
| `.dropgap`, `.held`, `.idle`, `.copy`, `.drop-into`, `body.dragging`, `body.ud-bdrag` | same classes, written by `app-workspace-drag.js`; styled for `.workspace-tree`/`.workspace-nav` (rows `li > div`, clones `.dropgap > div`) |
| `.row.just` | `li > div[aria-selected="true"]` (tint + frame) |
| `.ren`, `.renin` | `.input[data-size=sm]` in place of the name inside the row |
| `.drop-before`, `.drop-after`, `.slot` (tabs) | `.workspace-tab[data-drop="before"/"after"/"slot"]` (the dragging itself stays the app's) |
| `.blank` (tabs) | open — the empty general tab has no example yet |
| `.coll`, `.acc` | `section > header` of nav3 (the band) |
| `.n2lab`, `.slab`, `.lab` | `.workspace-label` |
| `.fav`, `.favsep` | `.workspace-item` / `hr` |
| `.lockline` | `.workspace-label` with lock icon |
| `.cmdpop`, `.command` (inside it) | `.command` with `header` filter, groups, `hr`; inside `.workspace` (the pack gives it the mockup's 13px rows) |
| `.addmenu`, `.addpop`, `.newpop`, `.pop`, `.opt` | `.dropdown-menu` / `.command`; New of the top row as a popover card: `.button-group` (where), `.input`, muted `p` |
| `.newtypes`, `.tplcards` | grid of `a.item[data-variant=outline][data-size=sm]` (icon, `h4`, two-line muted `p`) |
| entry with description (template) | menu item `div > span + small` in `.command`/`.dropdown-menu` |
| `.tabmenu`, `.tlistpop`, `.histpop`, `.tabctx`, `.ctxpop` | `.dropdown-menu` / `.context-menu` |
| **Windows** | |
| `.wins.many`, `.win`, `.focus` | `.workspace-windows` > `.workspace-window` (own `.workspace-tabs` + `.workspace-main`), active one `data-focus` |
| `.winbar` | not needed (hidden in the mockup as well) |
| `.zone-left` / `.zone-right` ("New column"), `.zone-mid` ("Move here"), `.zone-open` ("Open here") | `.workspace-main > [data-drop-zone="start"/"end"/"here"]` with the word as content, `hidden` when no drag runs |
| `.newwin`, `.left`, `.right` | `[data-drop-zone="start"/"end"][data-size="sm"]` (a strip at the edge) |
| `.toc` | `nav.toc[data-variant=compact][data-marker=bar]` first in `.workspace-main > section`, width `--workspace-toc` |
| `.dhead`, `.b`, `.c`, `.place.two`, `.crumbs` | `main > header` (variants of the head are the path + `h1`/`p` there) |
| `.page`, `.pad` | `main > section` |
| **Panels and settings** | |
| `.fdrawer`, `.fhead`, `.hint` | `.workspace-main > aside[data-drawer]` with `header`, `h3`, muted `p` |
| `.seg` | `.button-group` of `.btn[data-variant=outline][data-size=xs][aria-pressed]` (disabled: `disabled` + `aria-disabled` on the group) |
| `.setrow`, `.modrow` | a row `div.flex.items-center.justify-between` / `.item[data-variant=outline][data-size=sm]` (admin-panel block) |
| `.spanel`, `.facts`, `.colfacts` | `aside.card` with `h3`, `dl` (drawer `dl`), `.item` lists |
| `.dropzone` | `[data-dropzone]` (`empty.html`) |
| `.progress` (in a list) | `progress.progress` |
| `.preview`, `.vid`, `.slide`, `.thumb`, `.thumbs`, `.imgs` | `figure.card` / `.aspect-ratio` with the image; a grid of them |
| `.stepper` | `.input-group` with buttons (number) |
| `.addtag`, `.tagrow` | `.input[data-size=sm]` / `.badge` row |
| `.signout`, `.who`, `.avatar.small` | `.btn` / `.item` with `.avatar` |
| **Content in the document** | |
| `.sub` | `main > header > p` |
| `.v` | `code` |
| `a.l` | `a` (typeset link) |
| `.tw` | `.table-container` > `table.table` |
| `.note` | `.alert` |
| `.kids` | `a.item[data-variant=outline]` list |
| `.i` (`svg.i`) | lucide icon with `data-icon-lu` (size from its parent block) |
| `.empty` | `.empty` |
| `.withic`, `.blk`, `.accbadge`, `.later`, `.due`, `.tick` | `.badge` / muted `small` / `.btn` icon |
| **Other views of the mockup** (step 4: `blocks/navigation/workspace-views.html`) | |
| `.mailrow` (`.cur`, `.unread`), `.mfrom` (+ `em`), `.msubj` | `a.item[data-size=sm]` in a `div.item-group[role=list]`: `header` > `span` (sender) + `time`, `section > h4` (subject); `aria-current="page"`, `data-state="unread"` |
| `.chead` above a mail list | `.workspace-label` (no band); a collection of tasks keeps `section > header` |
| `.mailhead` (also the facts of a task or an entry) | `dl` first in `main > section > article` |
| `.note` | `.alert` > `section` |
| `.todos`, `.todo`, `.done`, `.box`, `.due`, `.tick` | `label.item[data-variant=outline][data-size=sm]` > `input.input[type=checkbox]` + `section > h4` + `aside > time`, in `main > section > div.item-group`; in nav3 `label.item[data-size=xs]`; done = checked |
| `.calgrid`, `.day`, `.today`, `.day small` | `table.month-sheet` in `main > section`: `td > span` (number) + `small` (entry), `aria-current="date"`, empty days `data-outside`; entries in nav3 as `.workspace-tree` rows with `small > time` |
| `.board`, `.kard` (board) | `.board` > `section.card[data-size=sm]` (`header > h3.card-title` + `small` count, `section` > `article.card[data-size=sm]`) |
| `.keep`, `.kard`, `.noteadd` (quick notes) | as in steps 2 and 3 |
| `.aidrawer`, `.fhead`, `.aictx`, `.aichat`, `.aiq`, `.aia`, `.aiin`, `.tagrow` (prompts) | `.workspace-main > aside[data-drawer]`: `header` (icon, name, close), muted `p`, `div[role=log]` > `.bubble[data-align=end]` (question) / `.bubble[data-variant=outline]` (answer), `.btn[data-variant=outline][data-size=xs]` prompts, `form.input-group` |
| `.cmtrow`, `.reply`, `.done`, `.tagrow`, `.tagc` (comments) | the drawer with `h3` + `ol.timeline[data-size=sm]` > `li` > `header` (`b` who, `time`) + `p` (+ `div` of `a.badge[data-variant=outline]`); a reply is an `ol.timeline` inside the `li`; done `li[data-state=done]` with a badge "erledigt" |
| `.ssbar`, `.chip` (saved search) | `.filter-bar` (one `section` per part, values as buttons with `aria-pressed`) |
| `.sshits`, `.hit`, `.snip`, `mark` | `div.item-group` of `a.item[data-size=sm]` > `figure` (icon) + `section` > `h4`, `p` (place), `p` (excerpt with `mark`) |
| `.filters`, `.filterbtn` (nav3 of search) | `.btn[data-variant=outline][data-size=xs]`, `.workspace-label`, `.workspace-tree` rows (recent), `a.badge[data-variant=outline]` (tags) |
| `.clockbtn` | `[data-clock]` (`date-picker.html`) |
| `.toast` | `.toast` |
| `.intorow`, `.lands`, `.cfor`, `.cgo`, `.cfocus`, `.cmore`, `.copy` (button) | `.item`/`.btn`; focus ring of C22 |
| `.bar`, `.tab`, `.strip .tab`, `.tight`, `.text`, `body.resizing` | old top bar of round 1: `header.workspace-top`, `.workspace-item`, `[data-grip]` (`.workspace[data-resizing]`) |

Open after step 4: the empty general tab (`.blank`); UnderDoc switches (then T-20). Menus of the workspace take the pack's size only inside
`.workspace`; an app that appends them to `<body>` keeps the plain pack look.
