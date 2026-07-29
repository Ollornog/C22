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

Mitgenommen wird **genau das, worauf die gebauten Seiten zeigen** — kein Verzeichnis wird
pauschal kopiert. Zwei Gründe: es kann nichts fehlen (jede Adresse wird aufgelöst, sonst
bricht der Bau ab — eine Seite ohne Stylesheet meldet keinen Fehler, sie sieht nur kaputt
aus), und es kann nichts Fremdes mitwandern. Letzteres ist kein theoretischer Fall: im
Arbeitsbaum liegen leicht Pack-CSS, die nie veröffentlicht werden sollen.
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

ADRESSE = re.compile(r'(?:href|src)="([^"#][^"]*)"')   # Seiten -> CSS/JS/Bilder
CSS_URL = re.compile(r'url\(\s*["\']?([^"\')]+)')      # CSS -> Schriften

FREMD = ("http://", "https://", "mailto:", "data:", "//")


def baue_packs() -> None:
    subprocess.run(["bash", str(ROOT / "scripts" / "build-gallery.sh")], check=True)


def _hole(adresse: str, relativ_zu: Path, ziel: Path, fehlend: list[str]) -> Path | None:
    """Kopiert die Datei hinter einer Adresse ins Ziel; merkt sie sich, wenn es sie nicht gibt.

    `relativ_zu` ist das Verzeichnis, aus dem die Adresse stammt (Seite bzw. Stylesheet) —
    innerhalb der Website, nicht im Quellbaum.
    """
    if adresse.startswith(FREMD):
        return None
    pfad = (relativ_zu / adresse.split("?")[0].split("#")[0]).resolve()
    try:
        rel = pfad.relative_to(ziel.resolve())
    except ValueError:
        # `../etwas` aus einer Seite im Wurzelverzeichnis: zeigt aus der Website heraus und
        # wäre online ein 404. Kein Absturz — ein benannter Fehler.
        fehlend.append(f"{adresse} (zeigt aus der Website heraus)")
        return None
    out = ziel / rel
    if out.is_file():
        return out          # schon da: eine generierte Seite oder eine bereits geholte Beilage
    quelle = ROOT / rel
    if not quelle.is_file():
        fehlend.append(str(rel))
        return None
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(quelle, out)
    return out


def staffle_assets(ziel: Path) -> tuple[int, list[str]]:
    """Holt, worauf die Seiten zeigen — und danach, worauf deren Stylesheets zeigen."""
    fehlend: list[str] = []
    geholt: set[Path] = set()

    for seite in sorted(ziel.glob("*.html")):
        for adresse in ADRESSE.findall(seite.read_text(encoding="utf-8")):
            datei = _hole(adresse, seite.parent, ziel, fehlend)
            if datei:
                geholt.add(datei)

    # Die Schriften stehen nicht im HTML, sondern als url() im kompilierten Pack-CSS.
    for datei in sorted(d for d in geholt if d.suffix == ".css"):
        for adresse in CSS_URL.findall(datei.read_text(encoding="utf-8")):
            weitere = _hole(adresse, datei.parent, ziel, fehlend)
            if weitere:
                geholt.add(weitere)

    return len(geholt), fehlend


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

    anzahl, fehlend = staffle_assets(ziel)
    if fehlend:
        for f in sorted(set(fehlend)):
            print(f"  FEHLT: {f}", file=sys.stderr)
        raise SystemExit("Website unvollständig — eine Seite ohne Stylesheet meldet keinen Fehler, "
                         "sie sieht nur kaputt aus. Erst scripts/build-gallery.sh laufen lassen?")

    seiten = len(list(ziel.glob("*.html")))
    groesse = sum(f.stat().st_size for f in ziel.rglob("*") if f.is_file()) / 1_048_576
    print(f"→ {ziel}  ({seiten} Seiten, {anzahl} Assets, {groesse:.1f} MB, alle Adressen aufgelöst)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
