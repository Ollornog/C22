# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
