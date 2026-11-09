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
