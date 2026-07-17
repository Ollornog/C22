# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — theming axes (phase A) and the Phosphor icon set

- Five more token axes, each a documented override seam a future theme generator can drive
  (see `docs/theming.md`, now fifteen axes plus the normative **variant contract**): icon stroke
  width (`--icon-stroke`, scoped so chart lines stay untouched), shadows as runtime tokens
  (`--shadow-2xs…2xl`; `shadow-md`/`shadow-lg` now resolve at runtime), motion
  (`--default-transition-duration`/easing seam plus a global `prefers-reduced-motion` fallback),
  heading weight (`--font-weight-heading`), and a named z-index ladder (`--z-popover`/`--z-context`)
  replacing the last magic number.
- The Phosphor icon subset (MIT) from C22 0.2.0 returns as the second icon library: 21 icons ×
  6 weights in `c22/static/js/icons.js`, a declarative `data-icon-ph`/`data-weight` host filled by
  `c22.js` (plus `window.C22.phIcon(name, weight)`), and a new **Icon** gallery component — the
  gallery now shows 66 components. Weights double as the icon-weight axis for fill-based icons.

### Added — icon names (`data-icon-lu`), the foundation of the icon-library axis

- Every inline lucide `<svg>` in the partials (419 across 51 files) now carries its machine-readable
  name as `data-icon-lu="<lucide-name>"` — the prerequisite for the generation-time library switch
  (axis 8): a tool can only swap icon markup by *name*. Names are the **canonical** lucide-static
  1.25.0 ones (aliases like `x-circle`/`bar-chart-3` resolved to `circle-x`/`chart-column`); the
  four icon strings in `c22.js` (calendar chevrons/nav) are named by hand. `data-icon` itself stays
  Basecoat's `inline-start`/`inline-end` padding hint — untouched, hence the separate attribute.
- `tools/annotate-icons.py`: repeatable annotator — downloads the pinned `lucide-static` npm tarball
  to a cache outside the repo, builds a geometry signature per icon (normalised, sorted child
  elements), matches every lucide-like `<svg>` in the partials and writes/corrects `data-icon-lu`
  idempotently (second run: zero changes). Older redesigned lucide forms and the one custom glyph
  (GitHub logo in `badge.html` → `data-icon-lu="github"`) live in a curated override table;
  anything unmatched is reported with file:line instead of guessed.
- `docs/icons.md`: the icon registry — the two-library situation, the semantic → lucide → Phosphor
  name mapping for the 21 vendored Phosphor icons (lucide side verified against the pinned
  download), the custom-icon list, and how the table grows. Suite rule 11 enforces that every
  lucide-like `<svg>` carries a non-empty `data-icon-lu`.

### Added — convention hygiene suite

- `tests/test_conventions.py` enforces the design-system contract mechanically over all
  `c22/components/*.html` and the class strings in `c22/static/js/c22.js`: no literal colours in
  markup, no Tailwind palette classes (tokens only), no arbitrary sizes (only the sanctioned
  `text-[11px]`), a lowercase-hyphen `data-variant`/`-size`/`-align`/`-side` vocabulary, one `.kbd`
  cap per key, and the presence of the token axes in `tokens.css` (`--font-heading`, `--chart-1…5`,
  `--info`, `--overlay-control`). Auto-discovered by `run_all.py`.
- Two icon-sizing rules extend the suite: no `width`/`height` on **any** `<svg>` in the partials
  (blanket — every icon is sized by a `size-*` class or by its component CSS) and — via a real HTML
  parser, not line-guessing — a 24px `<svg>` without a `size-*` class must sit under an ancestor whose
  component CSS sets the icon size (whitelist: `.btn`, `.kbd`, `.badge`, `.item-media`, `.avatar-badge`,
  `.alert`, `.select`, `<figure>`, carousel arrows/dots, `combobox-trigger-icon`, the `.command`
  header, `.input-group` `data-align` slots, `role=menuitem`/`option`/`heading`, and
  `<summary>`/`.accordion`/`.collapsible`) — for `.item` only `<figure>` counts, not `<aside>`.
- Two regression rules close out the audit: no stray generation artifacts (`</content>`/`</invoke>`/
  `<content`) in the partials, and no `aria-pressed:`/`aria-checked:` arbitrary-variant utilities in
  markup (the pressed/checked look now comes from the `.btn[aria-pressed='true']` foundation rule).

### Fixed — token/variant contract violations the suite surfaced

- The badge `Info` variant now uses the `--info` token (`bg-info text-info-foreground
  border-transparent`, solid like OK/Warnung) instead of literal `blue-*` palette classes.
- Keyboard shortcuts in `menubar`, `input-group` and `empty` now render one `.kbd` cap per key
  (e.g. `Strg` + `T`) instead of a single box with a space (`Strg T`).
- Icon sizing brought in line with the `.btn`/`size-*` convention: error micro-text in `radio-group`
  and `switch` is now `text-destructive text-xs`; standalone 24px icons that dwarfed adjacent small
  text got a `size-*` class (`hover-card` calendar → `size-3.5`; `item` link-row chevrons and the
  `message` file-tile icon → `size-4`; `message` error micro-icon → `size-3.5`); and
  `width="24" height="24"` was stripped from **every** `<svg>` root whose size is set otherwise (all
  66 across the partials, incl. `.btn`, figure/media icons, `.alert`, carousel, the `.command` header
  and the `toast` runtime-icon string), leaving `grep width="24"` at zero.
- Final polish batch: stray `</content>`/`</invoke>` generation artifacts removed from `dropdown-menu`,
  `collapsible` and `select`; the `.btn` dropdown-trigger chevrons in `data-table` and `input-group`
  now carry `opacity-50` (the muted-50 canon `.select` triggers already get via CSS); the redundant
  `text-muted-foreground` dropped from `select`'s chevrons (CSS already colours them); `sidebar`
  `<details>` submenu links got `role="menuitem"` (matching the top level); and an ineffective
  `data-active="true"` was removed from the `message-scroller` scroll-to-bottom `.btn`.

### Changed — foundation/SPOT consolidation (component audit)

- Toggle state is now one rule (`components.css`): `.btn[aria-pressed='true']`/`[aria-checked='true']`
  → `bg-accent text-accent-foreground`, replacing ~35 inline `aria-pressed:…`/`aria-checked:…` chains
  across `toggle`, `toggle-group` and `theme-switcher`.
- `toggle-group`'s exclusive (single-select) groups are now `role="radiogroup"`/`role="radio"` +
  `aria-checked` — a11y-correct like `theme-switcher`; multi-select groups keep `aria-pressed`.
- `message-scroller` now uses the `.bubble` foundation (`muted` = received, default = sent via
  `data-align="end"`) instead of raw `bg-muted`/`bg-primary … rounded-lg` chains — one bubble look
  system-wide (rounded-2xl + tail).
- New shared classes in `components.css` replace duplicated utility chains: `.hover-card` (the popover
  surface, was 4× identical in `hover-card`), `.badge[data-variant='success'|'warning'|'info']`
  (status chains → `data-variant` in `badge`, `data-table`, `item`, `table`, `message-scroller`),
  and `.input-otp-slot` (~30 repeated OTP-cell chains).
- `progress` icon tile → `.item-media`; `drawer` nav links → `.btn` `data-variant="ghost"`;
  `direction` initials avatars → `.avatar`; `navigation-menu` active page now uses the `bg-accent`
  state canon instead of `bg-muted`.

### Fixed — missing `.separator` foundation and error micro-text canon

- `.separator` (listed as a foundation in `CLAUDE.md`) had no CSS and lived as a repeated utility
  chain in the markup — now a real class (`bg-border shrink-0` + `data-orientation` for thickness);
  `separator.html` and its ad-hoc dividers use it.
- Error micro-text canon `.field[data-invalid] > p[role='alert'] { text-xs }` — `select` and
  `textarea` field errors now render at `text-xs` like the explicit `checkbox`/`radio-group`/`switch`
  ones (colour already comes from Basecoat's `data-invalid` rule).

### Changed — rebuilt on Basecoat + Tailwind CSS v4 (shadcn look)

C22's own component CSS/JS is superseded by a vendored, pinned copy of
[Basecoat](https://basecoatui.com/) (MIT), driven by the Tailwind CSS v4 standalone CLI. The design
system is now shadcn-flavoured semantic HTML + Basecoat classes + C22 tokens, with app-side adapters
kept thin. Basecoat is vendored under `c22/vendor/basecoat/` (reproducible via
`scripts/vendor-basecoat.sh`); the Tailwind binary is fetched, not committed.

### Added — component gallery (the single point of truth)

- A generated gallery (`gallery/build.py` → `gallery/index.html`) showing all 65 components, each in
  its variants — numbered per component, lettered per variant — with an eight-pack style switcher and
  a light/dark toggle. Every component links its Basecoat and shadcn source docs.
- Canonical HTML partials for all 65 components under `c22/components/`, each carrying its variants via
  one reusable `c22-examples` pattern (full-width dividers and spacing defined once in `components.css`).
- Reusable C22 component rules in `components.css`: `badge-split` (shields-style two-part badges),
  `bubble`/`bubble-group` (chat bubbles), avatar shapes (`data-shape`), accordion `bordered`/`card`,
  a text shimmer for in-progress states, context-menu and resizable skins, and slider status colours.
- A minimal own behaviour layer (`c22/static/js/c22.js`) for what Basecoat's JS does not cover:
  the context menu — right-click to open, viewport-aware placement that flips left/up near the edges,
  close on leave / after a short delay / manually (`data-close`), and a right-click inside the menu
  acting like a normal click. Apps embed it alongside `basecoat.all.min.js`.
- Example imagery sourced from Unsplash; a global `cursor: pointer` on interactive buttons.
- The behaviour layer now also renders interactive calendars (`data-calendar`: single/range selection,
  multiple months, month/year dropdown, disabled days, today/weekend/holiday styling), carousels and
  charts.
- Menu components share one hover/active state (`accent`) across command, dropdown-menu, context-menu,
  combobox and the calendar dropdown. Keyboard-shortcut keys render as `.kbd` key-caps (a single point
  of truth with `kbd`/`dropdown-menu`), one cap per key, that keep a constant border and only lighten
  their background on the highlighted row. The calendar's month/year dropdown marks the current choice
  with a check like a selected `select` option instead of a filled row. The command palette gains
  popover- and dialog-triggered variants plus a scrollable list, and opens without a pre-highlighted
  first row. Combobox `auto-highlight` is limited to its dedicated variant.
- Consistency pass across components 1–20: keyboard shortcuts in `context-menu` render as one `.kbd`
  key-cap per key (was a single combined box); `alert` gains a token-based `data-variant="warning"`
  instead of hardcoded `amber-*`; shields-style split badges use a new `--info` token instead of
  `bg-blue-600`; carousel photo-overlay controls use new `--overlay-control`/`--overlay-shadow-*` tokens
  instead of literal white/black — the sanctioned way to keep a deliberately theme-independent colour a
  token; the breadcrumb dropdown trigger inherits the `.breadcrumb` link hover via a shared rule; the
  calendar trigger chevron and an avatar check-icon follow the icon conventions (opacity-50, stroke-2).
- `attachment` is rebuilt on the `.item` row primitive plus a shared `.item-media` icon-tile class,
  instead of repeating the row/tile utility chains per entry.
- A repo `CLAUDE.md` documenting the build-on-the-foundation (SPOT) rule, the foundation blocks, the
  token/state/icon/typography conventions, and how to add or change a component.
- `docs/theming.md`: the theming concept — independent axes (style, base color, accent, chart
  colors, heading font, base font, typography scale, icon library, radius, menu, menu accent, and
  later density, shadows, motion and icon weight) that a future generator drives through tokens only. Phase A lands in this release: a `--font-heading` token
  (headings follow it via one base rule; default = body font), the chart palette moved from hex to
  oklch (same colours, generator-settable), and the documented override seam for the Tailwind v4
  `--text-*` type-scale tokens.

## [0.2.0] - 2026-07-12

### Added — component library and pattern book

The first design release: a framework-free component library (vanilla CSS + minimal vanilla JS,
no build step, no runtime dependency, single-file friendly) with a live pattern book at
`examples/musterbuch.html`.

- **Four independent look axes**, switchable without touching behaviour: colour theme
  (`data-theme`: hell/ambient/dunkel), size/density (`data-size`), corner shape
  (`--radius-scale`, a free value, plus per-corner `--rc-*`), and icon weight
  (`data-icon-weight`) over an inlined [Phosphor](https://phosphoricons.com/) subset.
- **Components**: buttons and segmented switches (including click-anywhere toggle chips and an
  icon toggle with a split thumb), forms with floating labels and `:user-invalid` validation
  timing, tabs (sliding underline and a browser-style variant), accordion, cards, navigation,
  chips, list, table, divider, media, single- and dual-thumb sliders, combobox/autocomplete,
  an ARIA menu, tooltip and popover, and custom scrollbars.
- **Notification system** from a single source of truth (the `KIND` registry) feeding banner,
  toast, centred popup and a notification centre/history — with grouped per-app notifications,
  a history filter by app, and an ARIA-live announcer for screen readers.
- Design principles (`docs/prinzipien.md`) and a BeerCSS-parity component checklist
  (`docs/komponenten-checkliste.md`).

Interaction patterns (combobox, menu, tabs, dual-thumb slider, live announcer) follow the
[WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/). Brand/app logos come from
[selfh.st/icons](https://selfh.st/icons/) (CC BY 4.0), bundled and self-hosted — never via CDN.

### Changed — unified layout of the documentation subpages

`CONTRIBUTING`, `SECURITY` and the German `i18n/` versions now carry the language switcher directly
below the heading and the logo bottom-right — the same pattern across all own repos. The English
`CODE_OF_CONDUCT.md` stays untouched and **pure** so GitHub recognises it as Contributor Covenant
rather than "Other".

The Flaticon credit now links straight to the author page (Iconjam) and opens in a new tab, in the
format shared across the repos: `Icon: … PNG Image by … - flaticon.com`.

## [0.1.0] - 2026-07-10

### Added
- Repository skeleton: package layout (`c22/static/{css,js}`, `c22/macros`),
  the `static_path()` and `macros_path()` helpers, a `Report`-based test harness,
  the shared hygiene kit via `repokit`, and a hardened CI workflow.
- Bilingual community files (README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT).
- Project logo (`docs/logo.png`) in both README versions, with Flaticon attribution.

No design assets are included yet; they follow once the layout foundation is settled.
