---
id: ADR-2
type: Decision
title: A pack may change the form of building blocks — tokens first, block-scoped rules as the bounded rest
status: erledigt
tags: [architektur, packs, theming, underdoc]
created: 2026-11-21
---

# ADR-2 — Layout packs: a pack changes the form of building blocks, not only their colours

## Context

Rule from the product owner (2026-11-21): **structure comes only from C22 building blocks.** An app that does
not want the existing look of a layout gets **its own pack**, never block CSS with a look of its own. One
design layout looks the same everywhere. The pack is named after the repository (`underdoc`), is public and
may be taken by any other app.

Trigger: the app workspace (`c22/static/css/app-workspace.css`, ~990 lines, block
`blocks/navigation/app-workspace.html`, T-14) is UnderDoc's approved mockup taken over whole, with its own
classes (`.brandrow`, `.strip`, `.nav2`, `.nav3`, `.dtab`, `.tools`, `.doc` …) under `.c22-app-workspace` and
its own shapes and spacing. It takes only the colour roles and the axes from C22. In the gallery it therefore
looks different from everything else in the same pack, and nothing of it is reusable. The same structure
already exists as building blocks: `.workspace` (T-13) — top row, three columns, tabs, list, window head.

Today a pack is a **token set**: `c22/static/css/packs/<name>.css` sets custom properties (the axes in
`c22/axes.py`, checked by `tests/test_axes.py`), `scripts/build-gallery.sh` compiles one CSS per pack
(`c22-<pack>.css`) with the pack file imported **last**, after `components.css`. An app picks a pack by
linking that file; the gallery switches with `?pack=` (it enables one `<link data-pack>`). The vendored
Basecoat styles (nova, lyra, …) already change the form of components — but through class rules in the
vendor layer, not tokens, which is exactly why C22's own surfaces did not follow them before the axes.

The global axes are not enough for a layout pack: the UnderDoc look differs in things that belong to one
building block — a band behind the heading of an open collection, smaller capitals in the column heads, a
status line under the window, the width of the document column, tags as square chips.

## Options

1. **Global axes only** (radius, density, type scale …). Clean, but cannot say "the heading of a nav3
   section sits on a band" without changing every heading in every block.
2. **Form tokens of the building block.** A block exposes its form decisions as custom properties on its
   root with defaults that reproduce today's look (`.workspace` already does this for its geometry:
   `--workspace-row`, `--workspace-step-0…3`, `--workspace-nav3`). A pack sets them on the block's root
   selector in its pack file. Pure tokens, no markup, every other pack keeps the defaults.
3. **Block-scoped rules in the pack file.** The pack file carries `@layer components { … }` rules whose
   selectors start at a C22 block root (`.workspace …`) and only use canonical C22 classes, slots and
   attributes. Needed where the pack reshapes a *foundation* component inside the block (the search field's
   height in the top row, a `.badge` as a square chip in the window head) — a block token for every such
   value would multiply tokens no other pack turns.
4. **One shared CSS with `[data-pack=underdoc]` scoping.** Rejected: packs are separate compiled files
   already; an attribute would put every pack into every file and require the app's markup to name its pack.
5. **Keep `app-workspace.css` as the pack** (move it under `packs/`). Rejected: own classes are own
   structure, the thing the rule forbids.

## Decision

**2 first, 3 for the bounded rest** (2026-11-21).

- A **layout pack** is a pack file like every other (`packs/<name>.css`, `@c22-form: <vendor style>`, every
  axis named). It may additionally set **block form tokens** on the block root and carry **block-scoped
  rules** in `@layer components`. Its header names the blocks it shapes: `@c22-layout: workspace`.
- **A token** when the value belongs to the block itself and another pack could plausibly turn the same
  knob (band behind a section head, size of the column capitals, width of the document column, gap of the
  tabs). Defaults live in `components.css` and reproduce the current look exactly, so no other pack moves.
- **A rule** only for the fine fit of a foundation component *inside* a block. Constraints, checked by the
  suite: inside `@layer components` (so utilities still win, the lesson of UnderDoc ADR-31); every selector
  starts at a block root class that `components.css` defines; no new class names; values through tokens
  (the axis rules of `tests/test_axes.py` apply to pack files as well); no hex.
- **Every block token a pack sets has a reader**: it must be declared with a default in `components.css`.
  A token nobody reads is an invitation that does nothing.
- **Colour is never the only signal**: the pack may change the shape of a state (bar, band, weight, word),
  but every state keeps a non-colour mark.
- **Selection stays as it is**: an app links `c22-<pack>.css` (here `c22-underdoc.css`), the gallery takes
  `?pack=underdoc` and lists the pack in its picker. No new mechanism, no markup attribute.

## Consequences

- The UnderDoc workspace is rebuilt from `.workspace` and its parts (T-19). Without the pack it looks like
  the rest of the chosen pack; with `underdoc` it looks like the approved mockup. Visual references exist for
  both packs.
- Missing structure (status line under the window, document column with a width choice) becomes part of
  the building block for every app, not of the pack.
- `app-workspace.css` and its block stayed, marked deprecated, until UnderDoc had switched; T-20 removed them
  (2026-11-22, now in `archive/`). Rule 14 of the hygiene suite turned from "every selector under the root class"
  into "no `app-*.css` and no `.c22-app-*` root in the sources", so the pattern cannot come back.
- The vendored styles keep their own class rules; this decision is about C22's own building blocks only.
