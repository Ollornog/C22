# Theming — the axes C22 is built to expose

> Status: design concept. Some of this is **already true today** (radius scale, sidebar tokens,
> status tokens); some is a **target** the components must be refactored toward. The "Current state"
> table below marks which is which. This document builds on the SPOT/token rules in
> [`CLAUDE.md`](../CLAUDE.md) and must not contradict them.

## Goal

C22 is meant to be driven by a **self-built generator** modelled on
[`ui.shadcn.com/create`](https://ui.shadcn.com/create): a small set of **independent axes** that a user
mixes, where **every axis acts through tokens only** — never through per-component markup. Choosing a
different accent colour, a different radius, or a bigger type scale must be "swap the token values and
recompile", not "touch the components".

From that follows the **one hard rule of this document**, an extension of the token rule in `CLAUDE.md`:

> **No component may hard-code a value that an axis controls** — no literal colour, font-size, font
> family, or radius in component markup. If an axis owns it, the component reads it through a token or a
> token-backed utility (`bg-primary`, `text-sm`, `rounded-md`, `font-sans`).

The generator is a later chapter (Phase C). The job **now** is to make sure the token seams exist so that
generator can plug in without rewriting components.

## The 15 axes

| # | Axis | Controls (tokens) | shadcn parallel |
|---|------|-------------------|-----------------|
| 1 | **style** | the whole look bundle — today the 8 packs | `style` preset (vega…sera) |
| 2 | **base color** | neutral scale → `--background` `--foreground` `--muted` `--border` `--card` `--popover` | `baseColor` (neutral/stone/zinc/…) |
| 3 | **theme / accent** | `--primary` `--primary-foreground` `--ring` (+ derived charts) | `theme` (named accent) |
| 4 | **chart colors** | `--chart-1…5` | preview only? — see open points |
| 5 | **heading font** | `--font-heading` | *not a shadcn core token* — C22 extension |
| 6 | **base font** | `--font-sans` | `font` / `registry:font` |
| 7 | **typography scale** | `--text-*` sizes + line-heights (+ heading sizes derived) · `--tracking-*` · `--font-weight-heading` | *none* — deliberate C22 extension |
| 8 | **icon library** | which icon set the markup ships — C22 vendors **two** (lucide inline + Phosphor subset) | `iconLibrary` (lucide/radix/…) |
| 9 | **radius** | `--radius` → derived `--radius-sm/md/lg/xl` | `radius` |
| 10 | **menu** | sidebar colour scheme: `--sidebar*` (default / inverted) | `menuColor` |
| 11 | **menu accent** | `--sidebar-accent` intensity (subtle / bold) | `menuAccent` |
| 12 | **density** | `--spacing` (Tailwind-v4 spacing base) | *none* — C22 extension |
| 13 | **elevation / shadows** | `--shadow-*` | *none* — C22 extension |
| 14 | **motion** | `--tw-duration` / `--default-transition-duration` + easing vars | *none* — C22 extension |
| 15 | **icon weight / stroke** | `--icon-stroke` (lucide) · Phosphor weight variants | *none* — C22 extension |

**1 · style** — today the eight packs (`vega` `nova` `maia` `lyra` `mira` `luma` `sera` `rhea`) bundle
*everything*: base colour, accent, radius feel and component variants all ride inside one compiled pack
CSS. Seven of the names match shadcn's current style presets; `rhea` is C22-only. The **target** is to
decouple style from the other axes so that "style" governs spacing/shape/variant character while colour,
font and scale come from their own axes.

**2 · base color** — the neutral greyscale palette. It feeds the surface tokens (background, foreground,
muted, border, card, popover). shadcn's current values are `neutral/stone/zinc/mauve/olive/mist/taupe`
(the classic `gray`/`slate` were dropped).

**3 · theme / accent** — the single named accent that sets `--primary`/`--ring` and, downstream, the chart
palette. In shadcn this is the continuation of the old `ui.shadcn.com/themes` concept; the exact `/create`
field name is only **moderately** confirmed (see open points).

**4 · chart colors** — `--chart-1…5`, oklch, generator-settable. Per the research, shadcn most likely does
**not** expose charts as an independent axis — the chart swatches there are a *preview* of the palette
derived from the accent. C22 treats chart colours as tokens either way; whether they become a *user-facing
axis* or a *derived preview* is left open (Phase A only migrates them off hex).

**5 · heading font** — `--font-heading`, separate from the body font. shadcn does **not** carry this as a
core token (only `--font-sans`/`--font-mono` are documented; `--font-heading` appears in community
registries). C22 adopts it as a **deliberate extension** so headings can be themed independently.

**6 · base font** — `--font-sans`, the body/UI font.

**7 · typography scale** — a **deliberate C22 extension beyond shadcn** (explicit user requirement). The
size/line-height steps are exposed as overridable Tailwind-v4 `--text-*` tokens (with heading sizes
**derived** from them), so the generator can drive the whole scale. Components keep using `text-sm` /
`text-xl` utilities — those utilities sit **on** the tokens. See "Typography scale" below.
Two companions ride on this same axis: **letter-spacing** through the already var-based `--tracking-*`
tokens, and a dedicated **`--font-weight-heading`** so headings can be weighted independently of the body.

**8 · icon library** — lucide inline SVG is the default, but C22 already carries **two** libraries: it
vendors, alongside inline lucide, the **Phosphor** subset (MIT) brought over from the old C22
([`c22/static/js/icons.js`](../c22/static/js/icons.js): 6 weights, `viewBox="0 0 256 256"`,
`fill="currentColor"`). Like shadcn's `iconLibrary`, the *library switch* is an
**install-/generation-time** decision (which set the emitted markup imports), **not** a runtime switch,
and that switch stays a **later chapter** (Phase C) — only the vendoring happens now.

**9 · radius** — `--radius` with a derived scale. **Already present** (see below).

**10 · menu** — the **sidebar** colour scheme via the `--sidebar*` token set (`default` / `inverted`).
**This is NOT the dropdown `--accent`.** The menu axis lets the sidebar be coloured independently of the
rest of the app (e.g. dark sidebar + light content). Do not confuse it with hover/active states in
menus/lists, which use `bg-accent`/`text-accent-foreground` per `CLAUDE.md`.

**11 · menu accent** — the **intensity** of `--sidebar-accent` (hover/active inside the sidebar):
`subtle` (default) / `bold`. Again a *sidebar* token, not the general `--accent`.

**12 · density** — Tailwind v4 computes every spacing utility as `calc(var(--spacing) * N)`. A single
`--spacing` token is therefore the **entire density axis** (compact / normal / roomy): override it and
every gap, padding and control height scales together. Already var-based — the axis is just the
documented override point, not a new mechanism.

**13 · elevation / shadows** — shadows as `--shadow-*` **runtime** tokens (mapped through `@theme inline`),
so each style can carry its own shadow character (hard vs. soft). Components use `shadow-*` utilities that
sit **on** the tokens, never literal shadow values in markup.

**14 · motion** — transition duration and easing through the Tailwind vars
(`var(--tw-duration, var(--default-transition-duration))` and the easing vars). Gives a **calm / snappy**
axis and, more importantly, the single seam at which `prefers-reduced-motion` is honoured.

**15 · icon weight / stroke** — *(decided 2026-07-17, lifting the 2026-07-15 exclusion)*. Icon weight is
now an axis, expressed per library: for **stroke** icons (lucide) it rides on **`--icon-stroke`** as a CSS
variable; for **fill** icons (Phosphor) it rides on the weight variants
`thin` / `light` / `regular` / `bold` / `fill` / `duotone`.

> **Not an axis — hygiene only:** a small **z-index ladder** (a handful of named layering steps for
> popovers, overlays and toasts) is kept as a **convention**, not a user-facing axis. It exists so stacking
> stays consistent across components, not to be themed.

## The variant contract

Variants and parts work **the same way across every component**. This is lived convention, now normative:
a component's look and behaviour are selected by **attributes on its semantic class**, never by bolting on
utility classes. The vocabulary is fixed so a variant means the same thing everywhere.

| Concern | Mechanism | Examples |
|---------|-----------|----------|
| Visual variant | `data-variant` on the semantic class; values **lowercase-kebab** | `outline` `ghost` `destructive` `secondary` `muted` `warning` |
| Size | `data-size` | `sm` `xs` `lg` `icon` `icon-sm` |
| Position / direction | `data-side` / `data-align` / `data-orientation` | `top` `start` `horizontal` |
| State | `aria-*` + `data-state` / `data-invalid` / `data-disabled` / `data-selected` | `aria-expanded`, `data-state="open"` |
| Behaviour | component-specific `data-*` | `data-close` `data-auto-highlight` `data-filter` `data-mode` |
| Parts of a component | semantic slots `header` / `section` / `footer` / `figure` / `aside` + `role=` — **not** extra classes | `<header>`/`<footer>` inside a card, `role="group"` |

**Justified exceptions** (named so they stay exceptions, not drift):

- `avatar[data-shape]` — shape is **not** a visual variant, so it gets its own attribute.
- structural own-classes that carry their **own anatomy** rather than an optical variant:
  `badge-split`, `item-media`, `bubble-group`.

The contract is checked **mechanically** by the hygiene test suite
([`tests/test_conventions.py`](../tests/test_conventions.py)) — it is enforced, not just documented.

## Target token set

Full set defined in `:root` + `.dark`, colours in **oklch**, exposed to utilities through `@theme inline`
(Tailwind v4, shadcn convention) — producing `--color-*` utilities like `bg-background`,
`text-primary-foreground`, `bg-sidebar`.

**Naming follows shadcn v4** (`--sidebar`, *not* `--sidebar-background`; foreground suffix dropped on
surface pairs: `--primary` ⇄ `--primary-foreground`).

| Group | Tokens |
|-------|--------|
| Surfaces | `--background` `--foreground` `--card(-foreground)` `--popover(-foreground)` |
| Accent/semantic | `--primary(-foreground)` `--secondary(-foreground)` `--muted(-foreground)` `--accent(-foreground)` `--destructive` |
| Lines | `--border` `--input` `--ring` |
| Charts | `--chart-1…5` |
| Sidebar (menu) | `--sidebar` `--sidebar-foreground` `--sidebar-primary(-foreground)` `--sidebar-accent(-foreground)` `--sidebar-border` `--sidebar-ring` |
| Radius | `--radius` (+ derived `--radius-sm/md/lg/xl`) |
| Fonts | `--font-sans` `--font-heading` `--font-mono` |
| Type scale | `--text-xs … --text-4xl` (each with line-height) |
| **C22 additions** | `--success(-foreground)` `--warning(-foreground)` `--info(-foreground)` `--overlay-control` `--overlay-shadow-*` |

The C22 additions live in [`tokens.css`](../c22/static/css/tokens.css) — vega/Basecoat ships only
`--destructive`, so C22 adds the full traffic-light set plus the theme-independent overlay-control tokens
(the one sanctioned "fixed colour" case from `CLAUDE.md`, expressed as tokens).

### Radius scale (already present)

Derived from a single `--radius`, per shadcn:

```css
--radius: 0.625rem;
--radius-sm: calc(var(--radius) - 4px);
--radius-md: calc(var(--radius) - 2px);
--radius-lg: var(--radius);
--radius-xl: calc(var(--radius) + 4px);
```

### Typography scale (target — Phase A)

Today typography is hard-coded as utility chains directly in the markup
([`typography.html`](../c22/components/typography.html): `text-4xl`, `leading-7`, `text-xl`…). The **target**
is to expose the scale as overridable tokens so the generator can move the whole ramp at once, while
components keep the familiar utilities:

```css
@theme {
  --text-xs: 0.75rem;   --text-xs--line-height: 1rem;
  --text-sm: 0.875rem;  --text-sm--line-height: 1.25rem;
  --text-base: 1rem;    --text-base--line-height: 1.5rem;
  /* … up to --text-4xl; heading sizes reference these steps */
}
```

Rule: components **MUST** use the utility (`text-sm`), never a literal (`text-[13px]`) — the only
sanctioned literal stays `<code class="text-[11px]">` inside example labels, as in `CLAUDE.md`.

## Current state

Per axis: ✅ present · ⚠️ partial · ❌ missing.

| # | Axis | State | Today |
|---|------|-------|-------|
| 1 | style | ⚠️ | 8 packs, but **monolithic** — colour/accent/radius all bundled per pack |
| 2 | base color | ⚠️ | neutral greyscale in oklch, but fixed inside each pack, not its own axis |
| 3 | theme / accent | ⚠️ | `--primary`/`--ring` present; baked into the pack, not selectable |
| 4 | chart colors | ❌ | `--chart-1…5` shipped as **hex** (`#93c5fd`…), not oklch, not generator-set |
| 5 | heading font | ❌ | no `--font-heading`; headings inherit `--font-sans` |
| 6 | base font | ✅ | `--font-sans` = Inter, embedded web font in `tokens.css` |
| 7 | typography scale | ❌ | sizes/line-heights **hard-coded as utilities**; `--tracking-*` var-based, no `--font-weight-heading` yet |
| 8 | icon library | ⚠️ | lucide inline; Phosphor subset vendored (`icons.js`), but library-switch not parameterised |
| 9 | radius | ✅ | `--radius` + derived `--radius-sm/md/lg/xl` |
| 10 | menu | ✅ | full `--sidebar*` set in oklch (`:root` + `.dark`) |
| 11 | menu accent | ⚠️ | `--sidebar-accent` exists; no `subtle`/`bold` switch yet |
| 12 | density | ⚠️ | `--spacing` is Tailwind's default; not yet exposed as a labelled override |
| 13 | elevation / shadows | ❌ | raw `shadow-*` utilities; no `--shadow-*` runtime tokens |
| 14 | motion | ❌ | durations inline per component; no motion tokens / reduced-motion seam |
| 15 | icon weight / stroke | ⚠️ | lucide stroke fixed at `2`; Phosphor weights available but not tokenised |

## Generator / preset sketch (later)

shadcn's own output is **not** a CSS copy-paste block but a **preset**: the whole design-system config
(style, base, accent, fonts, iconLibrary, radius, menuColor/menuAccent) packed into a version-prefixed
**base62 code** (e.g. `a2r6bw`), applied via CLI:

- `init --preset <named|code|url>` — new project
- `apply <code>` — overwrite an existing project
- `apply <code> --only theme` / `--only font` — partial

A C22 equivalent is conceivable along the same lines: axis values → a generated `tokens-<name>.css` that
the build picks up, optionally addressable by a short code. **Details are deliberately left open** until
Phase C — the point of Phases A/B is only to make the token seams exist.

## Roadmap

| Phase | When | Scope |
|-------|------|-------|
| **A** | now (this branch) | add `--font-heading` + `--font-weight-heading`; expose the typography scale as `--text-*` tokens; migrate `--chart-1…5` to oklch; wire the `--spacing` **density** override, `--shadow-*` **elevation** tokens, **motion** vars + reduced-motion seam, `--icon-stroke` and **vendor the Phosphor weight subset**; add the z-index ladder |
| **B** | a later chapter | lift **base color** and **accent** out of the monolithic packs into their own axes |
| **C** | a later chapter | build the generator itself + the **icon-library** *switch* axis |

## Open points (from the research, kept honest)

- **Chart axis** — not confirmed as an independent axis in shadcn; likely a preview of the accent-derived
  palette. C22 keeps chart tokens either way; axis-vs-derived is undecided. *(confidence: low)*
- **`--font-heading`** — a **community convention**, not a documented shadcn core token. C22 adopts it as a
  deliberate extension, aware it diverges. *(confidence: medium)*
- **"theme" field name** — the accent axis's exact `/create` field name is only moderately evidenced;
  the *concept* (named accent → `--primary`/`--ring`) is solid. *(confidence: medium)*
- **Radius multipliers** — sources differ (`calc(… - 4px)` vs `× 0.6`); the principle "one `--radius`,
  scale derived" is certain, the exact steps are a C22 choice.

Full primary-source research (dated 2026-07-17, adversarially checked) is kept on the maintainer's
notes — this document is the repo-facing summary.
