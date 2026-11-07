"""Das Paket lädt und liefert seine Asset-Pfade — die eine Zusage, auf die sich
konsumierende Apps verlassen. Der Inhalt (Tokens, Makros) kommt später; hier wird
nur die Struktur geprüft, damit die Zusage nicht unbemerkt wegbricht.
"""
from __future__ import annotations

import fnmatch
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # tests/ für _kit
sys.path.insert(0, str(HERE.parent))   # Repo-Root für das Paket c22 (Quellbaum, ohne Installation)
from _kit.report import Report  # noqa: E402

import c22  # noqa: E402

r = Report("Paket — c22")

r.check("static_path() zeigt auf einen existierenden Ordner", c22.static_path().is_dir())
r.check("macros_path() zeigt auf einen existierenden Ordner", c22.macros_path().is_dir())
r.check("static/ enthält css und js",
        (c22.static_path() / "css").is_dir() and (c22.static_path() / "js").is_dir())
r.check("__version__ ist gesetzt", bool(c22.__version__))

# The font ships with its licence (the OFL demands it with every copy), and both reach the
# wheel: a glob in package-data that misses them drops them silently, the source tree still works.
schriften = c22.static_path() / "fonts"
r.check("Inter liegt im Paket", (schriften / "inter.woff2").is_file())
ofl = schriften / "OFL.txt"
r.check("OFL-Lizenztext liegt neben der Schrift",
        ofl.is_file() and "SIL OPEN FONT LICENSE" in ofl.read_text(encoding="utf-8").upper())
daten = tomllib.loads((HERE.parent / "pyproject.toml").read_text(encoding="utf-8"))
globs = daten["tool"]["setuptools"]["package-data"]["c22"]
for name in ("static/fonts/inter.woff2", "static/fonts/OFL.txt"):
    r.check(f"package-data nimmt {name} mit", any(fnmatch.fnmatch(name, g) for g in globs))

sys.exit(r.done())
