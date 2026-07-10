"""Das Paket lädt und liefert seine Asset-Pfade — die eine Zusage, auf die sich
konsumierende Apps verlassen. Der Inhalt (Tokens, Makros) kommt später; hier wird
nur die Struktur geprüft, damit die Zusage nicht unbemerkt wegbricht.
"""
from __future__ import annotations

import sys
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

sys.exit(r.done())
