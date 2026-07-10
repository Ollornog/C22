"""C22 — a reusable, framework-agnostic layout & design system.

The core is plain CSS and a little JavaScript, usable from any stack. The Jinja
macros under ``macros/`` are an optional convenience layer for Python/Jinja apps.

    from c22 import static_path
    from fastapi.staticfiles import StaticFiles
    app.mount("/c22", StaticFiles(directory=static_path()), name="c22")

Apps that are not Python simply take the files from ``c22/static/`` (or the
release tarball) — no import required.
"""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("c22")
except PackageNotFoundError:  # running from a source tree without an install
    __version__ = "0+unknown"

_HERE = Path(__file__).resolve().parent


def static_path() -> Path:
    """Filesystem path to the bundled static assets (``css/``, ``js/``). Mount this."""
    return _HERE / "static"


def macros_path() -> Path:
    """Filesystem path to the optional Jinja macro templates."""
    return _HERE / "macros"


__all__ = ["__version__", "static_path", "macros_path"]
