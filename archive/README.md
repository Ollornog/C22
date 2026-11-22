# Archive

Built work that is no longer used: kept here instead of deleted, so it can come back when a design needs it again. Nothing in
this folder is built, imported, tested or shipped; each file says what it did, why it was taken out and the last commit where it
was live (the full context is in the history of that commit).

**Rule:** When something that was built and worked (a component, a variant, a rule set, a behaviour) is taken out of `c22/`,
move it here with that header instead of deleting it, and add a line below. Pruning the archive is a separate, deliberate step.
Fixes and refactors of live code are not archived; neither are experiments that never worked.

| File | What | Archived |
|------|------|----------|
| [`app-frame-head-rows.css`](app-frame-head-rows.css) | Centred brand row and a head row with two ends (`[data-frame-center]`, `[data-frame-split]`), menus as full-height row triggers | 2026-11-09 |
| [`app-frame-head-rail.css`](app-frame-head-rail.css) | Head over the rail only (`data-head="rail"`) | 2026-11-09 |
| [`breadcrumb-menu-step.css`](breadcrumb-menu-step.css) | A dropdown menu as a breadcrumb step | 2026-11-09 |
| [`sidebar-panel-tools.css`](sidebar-panel-tools.css) | Panel header with tools (`header[data-tools]`, `[data-tools-wide]`) | 2026-11-09 |
| [`table-open-target.css`](table-open-target.css), [`table-open-target.js`](table-open-target.js) | Bold "what a double click opens" in explorer tables (`data-open-target`) | 2026-11-09 |
| [`app-frame-head-bar-centred.css`](app-frame-head-bar-centred.css) | Head bar with a centred middle group (three columns) | 2026-11-09 |
| [`app-workspace-drop-lines.css`](app-workspace-drop-lines.css) | Lines on the edge of an entry where a dragged one lands, frames for a drop onto nav2 | 2026-11-09 |
| [`app-workspace-drag-ghost.css`](app-workspace-drag-ghost.css) | A picture of a dragged entry floating at the pointer, with a count | 2026-11-09 |
| [`app-workspace-nav2-children-box.css`](app-workspace-nav2-children-box.css) | The children of a collection in nav2, inside its box (a trial) | 2026-11-09 |
| [`app-workspace-block-bar.css`](app-workspace-block-bar.css) | The bar below each block in editing (UnderDoc): Block below, Delete, Copy address, ID | 2026-11-09 |
| [`app-workspace-editor-bar-sticky.css`](app-workspace-editor-bar-sticky.css) | The page editor's bar sticky inside the editor (UnderDoc) | 2026-11-10 |
| [`app-workspace.css`](app-workspace.css), [`app-workspace.html`](app-workspace.html) | The old app workspace: UnderDoc's mockup taken over whole under `.c22-app-workspace`, and its gallery block (T-20; successor `.workspace` + pack `underdoc`, ADR-2) | 2026-11-22 |
