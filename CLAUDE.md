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
| Multi-line code block | `<pre class="code-block"><code>…</code>` — copy button via `.btn.code-block-copy` + `[data-copy]`, line numbers via `data-line-numbers` | `code-block.html` |
| Scrollable area | the token scrollbar is the **global default** (arrowless) — no class needed; variants via `class="scrollbar"` + `data-size`/`data-track`/`data-buttons`; rounded scroll containers get the track inset automatically (`data-scrollbar-inset` to force/disable) | `scrollbar.html` |
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
