<p align="center"><img src="docs/logo.png" alt="C22" width="250" height="250"></p>

<h1 align="center">C22</h1>

<p align="center"><b>English</b> · <a href="i18n/README.de.md">Deutsch</a></p>

<p align="right">
<a href="https://github.com/Ollornog/C22/actions/workflows/ci.yml"><img src="https://github.com/Ollornog/C22/actions/workflows/ci.yml/badge.svg" alt="tests"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-informational.svg" alt="License: MIT"></a>
<img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python">
</p>

> 🚧 **Work in progress** — under active development; interfaces and structure may still change before a stable `1.0` release.

### A reusable, framework-agnostic design system in the shadcn look.

C22 is shadcn-flavoured UI delivered as **canonical HTML + semantic classes + design tokens** — no
React, no build lock-in. It vendors [Basecoat](https://basecoatui.com/) (MIT) and compiles it with the
Tailwind CSS v4 standalone CLI, so any stack can use the same components. The goal is to build a page
or a dashboard once and stop re-solving the same problems — overflow, spacing, contrast, responsive
breakage — while keeping app-side adapters thin: a redesign becomes "new tokens + components, gallery
still green", not touching every app.

---

## What it is

- **Vendored, pinned upstream:** Basecoat lives under `c22/vendor/basecoat/` (reproducible via
  `scripts/vendor-basecoat.sh`); the Tailwind binary is fetched, not committed. You own the code and
  build it locally — offline, no CDN, no runtime dependency.
- **Tokens over hard-coded values:** colour, radius, spacing and typography come from CSS custom
  properties (`c22/static/css/tokens.css`), so several sites can share one core and still look nothing
  alike.
- **A component gallery (the single point of truth):** `gallery/build.py` renders all 65 components —
  each in its variants — from canonical HTML partials in `c22/components/`. It links every component's
  Basecoat and shadcn source docs and switches between eight style packs and light/dark.
- **Engine-neutral, with an optional Jinja layer:** any stack embeds the compiled CSS and the partials'
  HTML; `c22/macros` holds optional page-shell macros for Python/Jinja apps.

## Status

Work in progress. All 65 components exist with their variants, but interfaces and structure may still
change before a stable `1.0`. Do not depend on it for production yet.

## Using it

Python/Jinja apps install the package and mount the assets:

```python
from c22 import static_path
from fastapi.staticfiles import StaticFiles
app.mount("/c22", StaticFiles(directory=static_path()), name="c22")
```

The look is the shared source of truth: design questions are solved **in C22** (tokens + components)
and adopted by the apps — not hard-coded per app. Other stacks take the partials' HTML and the
compiled CSS directly.

## Development

```bash
git config core.hooksPath .githooks   # once per clone
./scripts/fetch-tailwind.sh           # Tailwind v4 standalone CLI (gitignored)
./scripts/vendor-basecoat.sh          # pin/refresh the vendored Basecoat
./scripts/build-gallery.sh            # render the gallery + compile the pack CSS
./scripts/check.sh                    # tests + hygiene, run before every push
```

The compiled pack CSS and `gallery/index.html` are build outputs (gitignored) — rebuild them locally.
The suite is repeatable by design: run it twice, both green. See [CONTRIBUTING](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

## Credits

- UI primitives: [Basecoat](https://basecoatui.com/) (MIT), built on Tailwind CSS v4.
- Component references: [shadcn/ui](https://ui.shadcn.com/).
- Example imagery: [Unsplash](https://unsplash.com/).
- Icon: <a href="https://www.flaticon.com/authors/iconjam" target="_blank" rel="noopener">Origami Bird PNG Image by Iconjam - flaticon.com</a>
