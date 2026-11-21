# CLAUDE.md — working in this repo

Guidance for AI assistants (and humans) contributing to **C22**. Read this before touching components.
For process/style basics see [`CONTRIBUTING.md`](CONTRIBUTING.md); this file is about the *design-system
rules* that keep the components consistent. Keep it free of private infrastructure (no hostnames, paths,
CI internals) — repo-only conventions.

## What C22 is

A shared design system delivered as **canonical HTML**: semantic markup + [Basecoat](https://basecoatui.com/)
classes + Tailwind CSS v4 + C22 tokens, with a thin behaviour layer for what Basecoat's JS doesn't cover.
Apps don't restyle — they copy the same HTML behind a thin adapter. The HTML in `c22/components/` **is**
the source of truth; the gallery renders it.

## The one rule: build on the foundation (SPOT)

Every component reuses the shared building blocks instead of re-inventing their look with raw utilities.
A shortcut is a `.kbd`, a button is a `.btn`, a menu is `[data-popover]` + `role="menuitem"`. If two
components would style the same thing, that styling belongs in **one** place (`components.css` or a token),
not copied. When a design question comes up, solve it here and make it visible in the gallery — never fork
the look per component.

### Foundation blocks — always reuse, never hand-roll

| Need | Use | Reference |
|------|-----|-----------|
| Button / icon button | `class="btn"` + `data-variant` (`primary`/`outline`/`ghost`/`destructive`/`secondary`) + `data-size` (`sm`/`icon-sm`/`icon-xs`…) | `button.html` |
| Text field | `class="input"` | `input.html` |
| Label / field group / input group | `class="label"` / `class="field"` / `class="input-group"` | `label.html`, `field.html`, `input-group.html` |
| Checkbox / radio | `class="input"` with `type=` | `checkbox.html`, `radio-group.html` |
| Keyboard shortcut | `<kbd class="kbd">` — one cap per key | `kbd.html` |
| Badge / avatar | `class="badge"` / `class="avatar"` | `badge.html`, `avatar.html` |
| Brand mark (logo lockup: glyph plate + wordmark) | `class="brand"` (+ `data-orientation="vertical"`), glyph plate `class="brand-mark"` — on a coloured surface the plate is dropped and the glyph stands bare | `brand.html` |
| Flow diagram / stepper | `ol.flow`, nodes `.card[data-size="sm"]` + `data-state`, branches `.flow-branches` > `.flow-branch` | `flow.html` |
| Text cut to n lines with "show more" | `class="text-clamp"` + `data-lines`, `[data-clamp-body]`, `[data-clamp-toggle]` | `text-clamp.html` |
| Printing one block | `[data-printable]` + a button `[data-print]`, paper look `.print-sheet` | `print-block.html` |
| Divider | `class="separator"` or `<hr role="separator">` | `separator.html` |
| Multi-line code block | `<pre class="code-block"><code>…</code>` — copy button via `.btn.code-block-copy` + `[data-copy]`, line numbers via `data-line-numbers` | `code-block.html` |
| Scrollable area | the token scrollbar is the **global default** (arrowless) — no class needed; variants via `class="scrollbar"` + `data-size`/`data-track`/`data-buttons`; rounded scroll containers get the track inset automatically (`data-scrollbar-inset` to force/disable) | `scrollbar.html` |
| Popover / menu / dropdown / listbox | `[data-popover]` + `role="menu"`/`"menuitem"`/`"option"` | `dropdown-menu.html`, `select.html`, `combobox.html` |
| Application frame (rail + panel) | `.app-frame` + `.sidebar` with `data-variant="rail"` / `"panel"`, toggle via `[data-panel-toggle]`; with a head over both (brand, title, search; drawer below md): `data-head` + `header.app-frame-head`, menu button `[data-frame-menu]`; `data-head="bar"` makes the head one row over rail and content, its groups lined up from the start | `sidebar.html`, `blocks/navigation/app-frame.html` |
| Workspace (three columns, tabs, head of the window) | `.workspace` > `.workspace-top`, `.workspace-tabs`, `.workspace-nav[data-level][data-step]` + `[data-grip]`, `.workspace-main`; entries `.workspace-item`, list `.workspace-tree`; document column `main > section > article.typeset[data-width="slim\|wide\|full"]`, status line `main > footer` (`[data-fill]` pushes the rest to the end); sizes and form tokens as `--workspace-*` on `.workspace`; stored widths via `data-workspace-store` + `workspace-boot.js` | `blocks/navigation/workspace.html`, `document-workspace.html` |
| Several windows; contents beside the document | `.workspace-windows` > `.workspace-window` (own `.workspace-tabs` + `.workspace-main`), active `data-focus`; `nav.toc` first in `main > section` | `blocks/navigation/document-workspace.html` |
| Block editor (bar, block, handle, embed, part) | `.editor-bar[role=toolbar]` (groups `div[role=group]`, wraps; window row `.workspace-main > .editor-bar`), `.editor-block` (`[data-add]` + `.textarea`), `.editor` (`[data-used]` + `small`), `[data-block]` > `.dropdown-menu.editor-handle`, `figure.editor-embed[data-state=missing]`, `[data-part][data-framed]`, read/edit `.btn[data-mode]` in the window head | `blocks/navigation/workspace-editing.html` |
| Dragging entries of a list | `app-workspace-drag.js` (`C22AppWorkspaceDrag.attach`); on `.workspace-tree` the module's `.dropgap`/`.idle`/`.copy`/`.drop-into` are styled; selected `aria-selected`, reference `data-ref`, rename `.input` in the row | `blocks/navigation/workspace-more.html` |
| An app's own look for a layout | its own **layout pack** `packs/<repo>.css` (ADR-2): block form tokens on the block root, block-scoped rules in `@layer components`, header `@c22-layout: <block>`; never block CSS with own classes. Example: `underdoc` | `packs/underdoc.css`, `blocks/navigation/document-workspace.html` |
| ~~An app's approved mockup taken over whole~~ — **deprecated** (ADR-2, removal T-20) | root class `.c22-app-<name>`, everything scoped to it (rule 14); only the old UnderDoc workspace still uses it, until it has switched to `.workspace` + pack `underdoc` (replacement list in backlog T-19) | `blocks/navigation/app-workspace.html` |
| Filters with sign, count and text | `class="filter-bar"` | `filter-bar.html` |
| One row of filter buttons, groups as menus | `class="filter-menus"`: links, `.dropdown-menu` (state `data-an` / `data-teil`), `span[role=separator]`; split button `.filter-split` (link takes the group, arrow menu or a plain button beside it) | `filter-bar.html` |
| Table with hierarchy lines, row selection | `class="table" data-variant="levels"` + `data-selectable` (`="explorer"` adds opening; a link with `data-follow` opens on a click; merged-cell content in a `div` sticks under the head, `--levels-sticky-top`) | `blocks/tables/merge-table.html` |
| Page title as path | `class="breadcrumb" data-variant="title"`, last step is the `<h1>` | `breadcrumb.html` |
| Stack of messages, closable alert | `class="alert-stack"`, `.btn-close` as direct child of `.alert` | `alert.html` |
| Confirmation before an action | `[data-confirm="text"]` or `form[data-confirm]`, never `confirm()`; c22.js takes every such element over by itself (an app's own handler on it never runs, so use another attribute name there); texts on `<html>` as `data-confirm-title/-ok/-cancel`, `data-confirm-variant="destructive"` per trigger | `alert-dialog.html` |
| Floating button with counter | `class="btn" data-fab` | `button.html` |
| Phone navigation along the bottom edge | `nav.tab-bar` with links, open one `aria-current="page"`; gone from md, `data-always` keeps it; its parent gets room below by itself | `tab-bar.html` |
| QR code / key to type off by hand | `img.qr-code` / `code.secret-key` | `input-otp.html` |
| Collapsible card | `details.card` with `summary` as its head | `card.html` |
| Long lines in a code block wrapped | `.code-block[data-wrap]` | `code-block.html` |
| Log of what happened (who, when, what) | `ol.timeline` > `li` > `header` (badge in words, who, `time`) + `p`; `data-size="sm"`; a long log is a table with a status column | `timeline.html`, `table.html` |
| A month to read or pick days in / a year of short codes | `table.month-sheet` (cell: number + code, optional checkbox in a `label`; `data-weekend`, `data-outside`, `aria-current="date"`) / `table.year-grid` (12 × 31) | `blocks/data-entry/month-sheet.html`, `year-grid.html` |
| Compact field in a table row | `.input` with `data-size="sm"` (a native `select.select` has the same size) | `input.html` |
| Progress without inline style (strict CSP) | `progress.progress` (+ `data-variant` status) | `progress.html` |
| Drop zone that lights up while files are dragged | `[data-dropzone]` (c22.js sets `data-over`) | `empty.html` |
| A page that prints as a report | `.print-sheet` on the page, `print:hidden` on what stays off paper | `blocks/data-entry/week-report.html` |
| Long table in a scrolling box: head, first column and a group row stick | `.table[data-sticky]`, group row `tr[data-group-row]` (sticks under the head, c22.js keeps `--table-head-height`); today `tr[aria-current="date"]`, or as a column `th`/`td[aria-current="date"]` (the sticky first cell is tinted too) | `blocks/data-entry/time-sheet.html` |
| A spreadsheet: column letters and row numbers stick, cells and ranges selected | `.table[data-variant="grid"][data-sticky="sheet"]` inside a `.table-container` (scrolls both ways, height `--table-max-height` or a `max-h-*`); letters in `thead th`, numbers as `th[scope="row"]`; selection `td[aria-selected="true"]` (tint + thin frame), active cell `td[data-active]` (thick frame), selected letter/number `th[aria-selected="true"]` (bold + bar); `role="grid"` + `aria-multiselectable="true"` when it reacts | `table.html` |
| A field that is the cell, a hint line below it | `td[data-field] > .input` + `small` (`data-type="number"` aligns to the end); outside a table the hint is the `.field`'s help text | `blocks/data-entry/time-sheet.html`, `field.html` |
| A value shown as chips until it is typed into | `.chip-input` > `.input` + `[data-chips]` | `blocks/data-entry/time-sheet.html` |
| Popover without JavaScript (settings, segment buttons) | `details.popover` > `summary.btn` + `[data-popover]`; segments `.button-group` of buttons with `aria-pressed` | `popover.html`, `toggle-group.html` |
| A form in steps (e.g. name, then sharing) | `form[data-steps]` > `fieldset[data-step]`, `ol.steps`, buttons `[data-step-back]` / `[data-step-next]` / `[data-step-done]` (c22.js) | `blocks/data-entry/steps-dialog.html` |
| Rights of an object; picking a person, a group or everyone | owner/inheritance as `.item[data-size="sm"]`, origin and role as `.badge-split`, a grouped `.combobox` with an icon per kind | `blocks/data-entry/rights.html` |
| A settings panel outside the app workspace (what `setrow`/`chip`/`modrow`/`hint`/`lab` are there) | `h3`, `.item[data-size="sm"]`, `.btn[data-variant="outline"][data-size="sm"]`, muted `text-sm`, `.label`; a number with its unit is an `.input-group` | `blocks/data-entry/admin-panel.html` |
| A public page behind a link (no app frame) | `main.mx-auto.max-w-3xl.p-4`, head with a muted line, `.alert`, content | `blocks/full-page/public-page.html` |
| Telling entities apart (employers, projects, people) | `.badge[data-mark="1"…"5"]` — the text tells, the chart-colour dot adds | `badge.html` |

Do **not** write `<button class="inline-flex rounded-md px-3 py-2 …">` when `.btn` exists, and so on.

## Archive instead of delete

Built work that is taken out (a component, a variant, a rule set, a behaviour that worked) is not deleted: move it to
[`archive/`](archive/README.md) with a header (what, why, last live commit) and a line in the archive's README. The archive is
never built or shipped; pruning it is a separate, deliberate step.

## Tokens, not fixed colours

Colours, radii and spacing come from **tokens / token utilities** only: `bg-primary`,
`text-muted-foreground`, `bg-accent`, `border-border`, `bg-popover`, `text-destructive`, `text-warning`, …
**No hex, no `bg-[#…]`/`text-[#…]` with a literal colour, no inline `oklch()`/`rgb()`** in component markup.
Re-theming must be "swap the tokens", which only works if nothing hardcodes a colour. The style packs
(`vega`/`nova`/`maia`/`lyra`/`mira`/`luma`/`sera`/`rhea`, plus the brand packs `spica` and `ankaa`) are just different token sets.
A **layout pack** (`underdoc`, ADR-2) additionally changes the *form* of building blocks — through their form tokens first,
through block-scoped rules for the rest — and never brings classes or markup of its own.

**The one sanctioned exception** is a colour that must stay fixed *independent* of the theme — a brand
badge (shields-style), or a control sitting on an arbitrary photo (carousel overlay) that needs guaranteed
legibility. Even then, express it as a **dedicated token** (the way chart series use `--chart-1…5`), not a
literal `bg-blue-600`/`text-white` in the markup — so the exception is still one place to change.

**Role pairs are the shared core of every variant.** Each `data-variant` (on a button, bubble, badge,
alert, …) just reaches for a `bg-<role>` / `text-<role>-foreground` token pair — the same pairs, reused.
The living overview is [`color-roles.html`](c22/components/color-roles.html) (the gallery’s Color Roles section): the core pairs
(background, primary, secondary, muted, accent, destructive, card, popover) and the status pairs. Re-colouring
is therefore "change the tokens" (`tokens.css` / a pack), never the component. The status roles
(`success`/`warning`/`info`) are **full pairs** like the rest — used via `data-variant` on badge/slider and
via the utilities; **buttons deliberately omit them** (they don't fit a button's job). The variant
vocabulary is **closed and mechanically checked** (rule 12): every `data-variant` value must come from the
fixed list — a new role goes into `color-roles.html` + the list first, not into the markup by a typo.

These conventions are not honour-system: the hygiene suite (`tests/test_conventions.py`) checks them
**mechanically** — tokens over hex, the variant contract, and the rest — and must stay green before a push.

## State conventions (keep these identical across components)

- **Hover / active in any menu or list** → `bg-accent` + `text-accent-foreground` (command, dropdown-menu,
  context-menu, combobox, calendar dropdown). Never `bg-muted` for this.
- **Selected option / checked menu item** (dropdown radio/checkbox, select/combobox option, calendar
  month-year) → **bold + filled `primary` row** (one shared canon rule in `components.css`). Not a
  check on the right — a check/dot indicator column is the explicit variant `data-mark="indicator"`
  on the menu.
- **Down-chevron indicator** → the muted-50 look: token `--chevron-down-icon-50` or `opacity-50`. The
  combobox trigger chevron is `.combobox-trigger-icon`.
- **`.kbd` keys** → one cap per key; a constant `border-border`; the background only lightens to
  `bg-background` on the highlighted row (so keys never resize/"jump").
- **Command palette** opens **without** a pre-highlighted first row (handled once in `c22.js`).
- **Combobox auto-highlight** is opt-in via `data-auto-highlight="true"` on the one variant that shows it —
  not the default.
- **Optical alignment for corner actions** (close button & friends): the visible glyph sits on the
  container's normal content grid (same inset as text); the invisible hit area is the sanctioned
  exception — it bleeds into the padding (`.btn-close[data-corner]`, item `data-actions="corner"`).
  Never move the glyph off the grid to make room for the hit area.

## Variant contract

Variants and parts are selected by **attributes on the semantic class**, never by adding utility classes:
`data-variant` (visual look, lowercase-kebab), `data-size`, `data-side`/`data-align`/`data-orientation`
(position), `aria-*` + `data-state`/`data-invalid`/`data-disabled`/`data-selected` (state), and
component-specific `data-*` (behaviour); parts of a component are semantic slots (`header`/`section`/
`footer`/…) + `role=`, not extra classes. The full contract, its justified exceptions and the axes it
rides on live in [`docs/theming.md`](docs/theming.md) — don't restate it here.

## Icons

Lucide SVGs, uniform markup: `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`,
`stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`. No filled icons unless the shape
needs it, no off-convention stroke widths.

**Brand marks are not icons.** Lucide has no brand logos; a GitHub/Google/… mark carries
`data-icon-brand="<name>"` and sits **outside** the icon-library axis (a brand must not be
restyled or substituted). Rule 11 fails on a brand name inside `data-icon-lu` — see `docs/icons.md`.

**Every inline lucide icon carries its name**: `data-icon-lu="<lucide-name>"` (the foundation of the
icon-library axis — see `docs/icons.md`). Adding an icon? Run `python3 tools/annotate-icons.py` (or set
the name yourself); rule 11 of the hygiene suite fails on unnamed lucide-like SVGs. Don't confuse it with
`data-icon="inline-start|inline-end"`, which is Basecoat's icon-padding hint, not a name.

**Sizing — never nail it down inline where a class already governs it.** Inside `.btn`, omit
`width`/`height`/`size-*`; the button scales its icon automatically. A **standalone** icon (not in `.btn`)
must carry a `size-*` class (e.g. `size-4`, `size-3.5`) — without it the SVG renders at 24px and dwarfs
adjacent `text-xs`/`text-sm`.

## Typography

Utility-based on semantic HTML (shadcn-flavoured — see `typography.html`), no `.prose`-style wrapper class.
Keep it consistent: secondary/help text is `text-muted-foreground`; small text is `text-sm`/`text-xs`;
error/validation text is `text-destructive text-xs`. Don't introduce ad-hoc sizes (`text-[13px]`), not even in example
labels: code there is a plain `<code>`, its size comes from the label (the axes suite fails on `text-[11px]` in markup).

## Layout of the repo

```
c22/components/*.html   canonical HTML partials — one file per component, variants via the c22-examples pattern
c22/blocks/<cat>/*.html Blocks — larger compositions, grouped by category directory
                        (navigation / full-page / login-signup / tables); first line
                        <!-- c22-title: … --> names the entry, otherwise the filename does
c22/charts/*.html       chart patterns (one file per chart type, --chart-1…5 tokens only); a second
                        line `<!-- c22-tab: <rank> | <German> | <English> -->` says which TAB of the
                        charts page takes the file (several files may share one tab, ordered by rank)
c22/typeset/*.html      typography in context (typeset page; base for the future typeset generator)
c22/static/css/
  tokens.css            the token definitions (the look)
  components.css        shared C22 rules (@layer components) — the SPOT home for anything cross-component
  app-<name>.css        an app's whole look taken over as one building block, every selector under the root
                        class .c22-app-<name> (rule 14); unlayered, see the file head — except the
                        element defaults (button, table cells …), which sit in @layer base so C22
                        components and utilities used inside the root win over them
  packs/<name>.css      OWN style packs = token overrides riding on the vega shape
                        (de-monolithisation phase B; e.g. packs/spica.css — brand blue); a layout pack
                        (@c22-layout, ADR-2; packs/underdoc.css) also sets block form tokens and carries
                        block-scoped rules in @layer components (tests/test_axes.py part D)
  input.css             Tailwind entry (imports vendored basecoat + tokens + components)
  c22-<pack>.css        compiled output per style pack (generated — do not hand-edit)
c22/static/js/c22.js    minimal own behaviour (context menu, interactive calendar/carousel/chart, palette tweaks)
c22/vendor/basecoat/    vendored, pinned Basecoat (reproduce via scripts/vendor-basecoat.sh) — do not edit
gallery/build.py        builds the gallery PAGES (index/blocks/charts/typeset.html, shadcn-style):
                        components from the COMPONENTS list; blocks/charts/typeset are discovered
                        by directory scan — no central registry for them
gallery/landing.py      the start page (index.html): what C22 is, entry points, GitHub + imprint
gallery/legal.py        imprint + privacy text of the PUBLISHED site (legal.html) — one source
                        for the mandatory details, rendered with the same typography canon
gallery/i18n.py         the site's two languages (de/en) and the two pill switches. Every page
                        carries BOTH languages, CSS shows one (`?lang=`, remembered). Website
                        text is bilingual; the example copy INSIDE components stays German
scripts/build-site.py   builds the published website into _site/ (GitHub Pages): the same gallery,
                        built a second time with an empty asset prefix, plus the assets it links
```

The gallery pages are `components.html` / `blocks.html` / `charts.html` / `typeset.html`;
`index.html` is the start page and `legal.html` the imprint. The header names **no page title** —
the highlighted tab already says which page is open — and carries only the three switches
(pack · language · appearance). `?pack=`, `?lang=` and `?theme=` deep-link any combination, which
is also how a visual test pins a state.

The website **is** the gallery — not a second work. Locally the pages sit in `gallery/` and address
their assets as `../c22/…`; on the site they sit at the root and address them as `c22/…`. That prefix
is the only difference (`ZIEL` / `ASSETS` in `build.py`), so nothing can drift apart. `pages.yml`
rebuilds and deploys it on every push to `main` — a pull request only builds it, as a check.

## Changing or adding a component / block / chart / typeset entry

1. Edit the partial in `c22/components/`. New component → add it to the `COMPONENTS` list in `gallery/build.py`
   and give it variants using the existing `c22-examples` / `c22-example` pattern.
   New **block/chart/typeset** entry → just drop an `.html` file into the right directory
   (`c22/blocks/<category>/`, `c22/charts/`, `c22/typeset/`) with a `<!-- c22-title: … -->` first line —
   the gallery discovers it on rebuild. New block CATEGORY → extend `BLOCK_KATEGORIEN` in `gallery/build.py`.
   New **chart** entry → additionally a `<!-- c22-tab: … -->` line for the tab it belongs to; without it
   the entry still shows up, in the trailing "Weitere/More" tab. All conventions below apply to those
   directories too (the hygiene suite scans them).
2. Rebuild the gallery (`scripts/build-gallery.sh`) and **look at it** (screenshot or browser, light *and*
   dark) before deciding it's done — don't build UI blind.
3. Any styling that more than one component needs goes into `components.css` (or a token), not copied inline.
4. Run `scripts/check.sh` (component + hygiene suites) and keep it green before pushing. The hygiene suite
   enforces: no private infrastructure, tokens over hex, Actions pinned by commit SHA, valid CHANGELOG
   categories, README.de in sync.
5. CHANGELOG entry in the same commit (`## [Unreleased]`).
6. The browser suite (`tests/test_visual.py`, part of `scripts/check.sh`) compares every gallery section to
   its reference image in `tests/visual/`. A deliberate change of the look means
   `python3 tests/test_visual.py --renew`: it rewrites only the images that moved, so the pull request shows
   what changed. Never renew to get a red run green without looking at the difference. Behaviour no picture
   can show (scrolling, clicks, printing) belongs in the `verhalten` part of the same suite.

## Conventions

- Generated CSS packs (`c22-*.css`) and the Tailwind binary are build outputs — don't hand-edit or commit
  the binary.
- German example copy with real umlauts; UTF-8 without BOM; code identifiers in English.
- Never pin dependencies to `latest`; Basecoat is vendored at a fixed version.
- No private infrastructure anywhere (code, examples, docs, commits) — neutral placeholders only.
