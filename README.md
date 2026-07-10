# C22

*[Deutsche Fassung](README.de.md)*

C22 is a reusable, framework-agnostic layout and design system. Its core is plain CSS
(design tokens, layout primitives, page shells, native popovers) and a small amount of
JavaScript — usable from any stack. On top sits an **optional** Jinja macro layer for
Python/Jinja applications. The goal is to build a page or a dashboard once and stop
re-solving the same layout problems — overflow, spacing, contrast, responsive breakage.

## What it is

- **A neutral core:** `c22/static/css` and `c22/static/js`. No dependency on any
  framework, no CDN or tracker fetched at runtime. Any application — static, PHP, Node,
  Python — can embed these files.
- **An optional Jinja layer:** `c22/macros` holds page-shell and component macros for
  apps that already render with Jinja. Nobody is required to use them.
- **Theming by tokens:** designs differ by CSS custom properties, so several sites can
  share one core and still look nothing alike.

## Status

Early. This is the repository skeleton — hardened CI, shared hygiene kit, package layout
and the `static_path()` / `macros_path()` helpers. **The design assets themselves are not
in yet;** they follow once the layout foundation is settled. Do not depend on it for
production.

## Using it

Python/Jinja apps install the package and mount the assets:

```python
from c22 import static_path
from fastapi.staticfiles import StaticFiles
app.mount("/c22", StaticFiles(directory=static_path()), name="c22")
```

Other stacks take the files from `c22/static/` directly (or from a release tarball) — no
Python required.

## Development

```bash
git config core.hooksPath .githooks   # once per clone
./scripts/check.sh                     # tests + hygiene, run before every push
```

The suite is repeatable by design: run it twice, both green. See
[CONTRIBUTING](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
