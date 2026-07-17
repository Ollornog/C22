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
| Divider | `class="separator"` or `<hr role="separator">` | `separator.html` |
| Popover / menu / dropdown / listbox | `[data-popover]` + `role="menu"`/`"menuitem"`/`"option"` | `dropdown-menu.html`, `select.html`, `combobox.html` |

Do **not** write `<button class="inline-flex rounded-md px-3 py-2 …">` when `.btn` exists, and so on.

## Tokens, not fixed colours

Colours, radii and spacing come from **tokens / token utilities** only: `bg-primary`,
`text-muted-foreground`, `bg-accent`, `border-border`, `bg-popover`, `text-destructive`, `text-warning`, …
**No hex, no `bg-[#…]`/`text-[#…]` with a literal colour, no inline `oklch()`/`rgb()`** in component markup.
Re-theming must be "swap the tokens", which only works if nothing hardcodes a colour. The eight style packs
(`vega`/`nova`/`maia`/`lyra`/`mira`/`luma`/`sera`/`rhea`) are just different token sets.

**The one sanctioned exception** is a colour that must stay fixed *independent* of the theme — a brand
badge (shields-style), or a control sitting on an arbitrary photo (carousel overlay) that needs guaranteed
legibility. Even then, express it as a **dedicated token** (the way chart series use `--chart-1…5`), not a
literal `bg-blue-600`/`text-white` in the markup — so the exception is still one place to change.

## State conventions (keep these identical across components)

- **Hover / active in any menu or list** → `bg-accent` + `text-accent-foreground` (command, dropdown-menu,
  context-menu, combobox, calendar dropdown). Never `bg-muted` for this.
- **Selected option** (dropdown/select/calendar month-year) → a check (`var(--check-icon)`) on the right,
  like a selected `select` option. Not a filled `bg-primary` row and not an ad-hoc grey.
- **Down-chevron indicator** → the muted-50 look: token `--chevron-down-icon-50` or `opacity-50`. The
  combobox trigger chevron is `.combobox-trigger-icon`.
- **`.kbd` keys** → one cap per key; a constant `border-border`; the background only lightens to
  `bg-background` on the highlighted row (so keys never resize/"jump").
- **Command palette** opens **without** a pre-highlighted first row (handled once in `c22.js`).
- **Combobox auto-highlight** is opt-in via `data-auto-highlight="true"` on the one variant that shows it —
  not the default.

## Icons

Lucide SVGs, uniform markup: `viewBox="0 0 24 24"`, `fill="none"`, `stroke="currentColor"`,
`stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`. No filled icons unless the shape
needs it, no off-convention stroke widths.

**Sizing — never nail it down inline where a class already governs it.** Inside `.btn`, omit
`width`/`height`/`size-*`; the button scales its icon automatically. A **standalone** icon (not in `.btn`)
must carry a `size-*` class (e.g. `size-4`, `size-3.5`) — without it the SVG renders at 24px and dwarfs
adjacent `text-xs`/`text-sm`.

## Typography

Utility-based on semantic HTML (shadcn-flavoured — see `typography.html`), no `.prose`-style wrapper class.
Keep it consistent: secondary/help text is `text-muted-foreground`; small text is `text-sm`/`text-xs`;
error/validation text is `text-destructive text-xs`. Don't introduce ad-hoc sizes (`text-[13px]`); the only
sanctioned literal size is `<code class="text-[11px]">` inside example labels.

## Layout of the repo

```
c22/components/*.html   canonical HTML partials — one file per component, variants via the c22-examples pattern
c22/static/css/
  tokens.css            the token definitions (the look)
  components.css        shared C22 rules (@layer components) — the SPOT home for anything cross-component
  input.css             Tailwind entry (imports vendored basecoat + tokens + components)
  c22-<pack>.css        compiled output per style pack (generated — do not hand-edit)
c22/static/js/c22.js    minimal own behaviour (context menu, interactive calendar/carousel/chart, palette tweaks)
c22/vendor/basecoat/    vendored, pinned Basecoat (reproduce via scripts/vendor-basecoat.sh) — do not edit
gallery/build.py        builds gallery/index.html from the component list; numbers per component, letters per variant
```

## Changing or adding a component

1. Edit the partial in `c22/components/`. New component → add it to the `COMPONENTS` list in `gallery/build.py`
   and give it variants using the existing `c22-examples` / `c22-example` pattern.
2. Rebuild the gallery (`scripts/build-gallery.sh`) and **look at it** (screenshot or browser, light *and*
   dark) before deciding it's done — don't build UI blind.
3. Any styling that more than one component needs goes into `components.css` (or a token), not copied inline.
4. Run `scripts/check.sh` (component + hygiene suites) and keep it green before pushing. The hygiene suite
   enforces: no private infrastructure, tokens over hex, Actions pinned by commit SHA, valid CHANGELOG
   categories, README.de in sync.
5. CHANGELOG entry in the same commit (`## [Unreleased]`).

## Conventions

- Generated CSS packs (`c22-*.css`) and the Tailwind binary are build outputs — don't hand-edit or commit
  the binary.
- German example copy with real umlauts; UTF-8 without BOM; code identifiers in English.
- Never pin dependencies to `latest`; Basecoat is vendored at a fixed version.
- No private infrastructure anywhere (code, examples, docs, commits) — neutral placeholders only.
