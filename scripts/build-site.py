#!/usr/bin/env python3
"""Baut die veröffentlichte Website nach `_site/` — das, was GitHub Pages ausliefert.

    python3 scripts/build-site.py [ziel]      # Standard: _site/
    python3 scripts/build-site.py --schnell   # ohne Neubau der Pack-CSS (nur staffeln)

Die Website **ist** die Galerie — kein zweites Werk, keine zweite Quelle. Der Unterschied
zum lokalen Stand ist nur die Adressierung: lokal liegen die Seiten in `gallery/` und die
Assets eine Ebene höher (`../c22/…`), auf der Website liegen die Seiten im Wurzelverzeichnis
und die Assets darunter (`c22/…`). Deshalb baut dieses Skript die Seiten ein zweites Mal —
mit leerem Asset-Präfix — statt Pfade in fertigem HTML zu ersetzen.

Reihenfolge (nicht vertauschen): erst `build-gallery.sh` (Seiten nach `gallery/`, danach die
Pack-CSS — Tailwind scannt `gallery/**/*.html` und braucht die Seiten also VORHER), dann die
Seiten ein zweites Mal nach `_site/`.

Zum Schluss wird geprüft, dass **jede** lokale Adresse im gebauten HTML auch wirklich als
Datei im Zielverzeichnis liegt. Grund: eine Seite ohne Stylesheet rendert ohne Fehlermeldung
— sie sieht nur kaputt aus. Das fällt sonst erst im Browser auf.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gallery"))

import build as gallery  # noqa: E402

# Was neben den Seiten mitkommt. Verzeichnisse werden komplett kopiert.
ASSETS: list[str] = [
    "c22/static/css",
    "c22/static/js",
    "c22/static/fonts",
    "docs/logo.png",
]
# Build-Outputs anderer Läufe, die nichts auf der Website verloren haben.
NICHT_MITNEHMEN = {"_in-", "c22.css"}

ADRESSE = re.compile(r'(?:href|src)="([^"#][^"]*)"')


def baue_packs() -> None:
    subprocess.run(["bash", str(ROOT / "scripts" / "build-gallery.sh")], check=True)


def staffle_assets(ziel: Path) -> int:
    anzahl = 0
    for eintrag in ASSETS:
        quelle = ROOT / eintrag
        if not quelle.exists():
            raise SystemExit(f"fehlt: {eintrag} — erst scripts/build-gallery.sh laufen lassen")
        if quelle.is_dir():
            for datei in sorted(quelle.rglob("*")):
                if not datei.is_file() or any(t in datei.name for t in NICHT_MITNEHMEN):
                    continue
                out = ziel / datei.relative_to(ROOT)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(datei, out)
                anzahl += 1
        else:
            out = ziel / quelle.relative_to(ROOT)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(quelle, out)
            anzahl += 1
    return anzahl


def pruefe_adressen(ziel: Path) -> list[str]:
    """Jede lokale Adresse in den gebauten Seiten muss im Ziel als Datei existieren."""
    fehlend = []
    for seite in sorted(ziel.glob("*.html")):
        for adresse in ADRESSE.findall(seite.read_text(encoding="utf-8")):
            if adresse.startswith(("http://", "https://", "mailto:", "data:", "//")):
                continue
            pfad = ziel / adresse.split("?")[0].split("#")[0]
            if not pfad.exists():
                fehlend.append(f"{seite.name} -> {adresse}")
    return fehlend


def main(argumente: list[str]) -> int:
    schnell = "--schnell" in argumente
    rest = [a for a in argumente if not a.startswith("--")]
    ziel = Path(rest[0]) if rest else ROOT / "_site"
    ziel = ziel if ziel.is_absolute() else ROOT / ziel

    if not schnell:
        baue_packs()

    if ziel.exists():
        shutil.rmtree(ziel)
    ziel.mkdir(parents=True)

    # Seiten ein zweites Mal — ins Wurzelverzeichnis der Website, Assets ohne `../`.
    gallery.main(ziel, "")

    # `.nojekyll`: ohne die Datei schiebt GitHub die Dateien durch Jekyll, das alles
    # mit führendem Unterstrich ignoriert. Kostet nichts, verhindert stille Ausfälle.
    (ziel / ".nojekyll").write_text("", encoding="utf-8")

    anzahl = staffle_assets(ziel)
    fehlend = pruefe_adressen(ziel)
    if fehlend:
        for f in fehlend:
            print(f"  FEHLT: {f}", file=sys.stderr)
        raise SystemExit("Website unvollständig — eine Seite ohne Stylesheet meldet keinen Fehler, "
                         "sie sieht nur kaputt aus.")

    seiten = len(list(ziel.glob("*.html")))
    groesse = sum(f.stat().st_size for f in ziel.rglob("*") if f.is_file()) / 1_048_576
    print(f"→ {ziel}  ({seiten} Seiten, {anzahl} Assets, {groesse:.1f} MB, alle Adressen aufgelöst)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
