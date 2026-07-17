#!/usr/bin/env python3
"""Benennt die Inline-Lucide-SVGs in den Components — die Grundlage der Achse „icon library".

WARUM ES DAS GIBT
    Die Lucide-Icons in den Partials sind anonyme Pfade: `<svg …><path d="M5 12h14"/>…`.
    Ohne Namen lässt sich kein Bibliothekswechsel zur Generierungszeit bauen (Achse 8 in
    docs/theming.md) — ein Generator kann Pfade nur tauschen, wenn er weiß, WELCHES Icon ein
    <svg> ist. Phosphor ist bereits benannt (`data-icon-ph="name"`, siehe c22.js). Für Lucide
    fehlte die Entsprechung. Dieses Werkzeug schreibt sie: es lädt die gepinnte `lucide-static`,
    baut aus jedem Lucide-SVG eine geometrische Signatur (die sortierten Kind-Elemente,
    normalisiert), berechnet dieselbe Signatur für jedes <svg> in den Components und schreibt den
    gefundenen Namen als maschinenlesbares Attribut ins Tag.

    ATTRIBUTNAME — `data-icon-lu`, NICHT `data-icon`.
    `data-icon` ist im Design-System bereits vergeben: Basecoat steuert damit das Icon-Padding im
    Button (`[data-icon=inline-start]` / `[data-icon=inline-end]`, echte CSS-Selektoren, sitzen am
    <svg> selbst). Der Bibliotheksname bekommt darum ein eigenes Attribut — symmetrisch zu
    Phosphors `data-icon-ph`: Lucide = `data-icon-lu`. So kollidieren Padding-Hinweis und Name nie.

WIE
    lucide-static wird als npm-Tarball in einen Cache AUSSERHALB des Repos geladen (nie committen —
    wie scripts/fetch-tailwind.sh es mit dem Binary hält). Version ist gePINNT (kein „latest" zur
    Laufzeit); Update = Konstante hochsetzen und erneut laufen lassen.

    Nicht jedes C22-Icon steckt in der aktuellen lucide-static: manche Partials tragen eine ÄLTERE
    Lucide-Form (Lucide hat Icons über die Zeit neu gezeichnet — z.B. das alte `download` mit
    polyline+line statt drei Pfaden) oder ein NICHT-Lucide-Sondericon (das GitHub-Logo in
    badge.html). Diese Fälle stehen kuratiert in OVERRIDES: je Eintrag der Name plus das rohe
    Kind-Markup, aus dem die Signatur berechnet wird — auditierbar und ohne Zweit-Download. Bleibt
    danach ein <svg> ohne Treffer, meldet das Werkzeug es (Datei:Zeile + Pfadauszug), statt zu raten.

IDEMPOTENT
    Ein bereits korrektes `data-icon-lu` bleibt unangetastet; ein falscher Wert wird korrigiert und
    gemeldet; ein fehlender wird ergänzt. Zweiter Lauf ⇒ 0 geänderte Dateien.

    Nur c22/components/*.html werden geschrieben. Die vier Lucide-SVG-STRINGS in c22.js (die per
    String-Konkatenation entstehen) tragen ihr `data-icon-lu` von Hand — sie sind kein statisches
    Markup, das ein zeilenweiser Scanner sicher fassen könnte.

    python3 tools/annotate-icons.py            # annotiert + Bericht
    python3 tools/annotate-icons.py --check     # schreibt nichts; Exit 1, wenn etwas offen/änderbar
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

# ── gepinnte Lucide-Version ───────────────────────────────────────────────────
# Aktuelle Version ermittelt via https://registry.npmjs.org/lucide-static/latest (2026-07-17).
# UPDATE: Version hochsetzen, Werkzeug laufen lassen, unmatched prüfen, Suite grün halten.
LUCIDE_VERSION = "1.25.0"
TARBALL_URL = f"https://registry.npmjs.org/lucide-static/-/lucide-static-{LUCIDE_VERSION}.tgz"

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = sorted((ROOT / "c22" / "components").glob("*.html"))
# Cache liegt bewusst AUSSERHALB des Repos (nie committen). Override per Env möglich.
CACHE = Path(os.environ.get("C22_LUCIDE_CACHE", Path(tempfile.gettempdir()) / "c22-annotate-icons"))

ATTR_NAME = "data-icon-lu"

# ── Kuratierte Sonderfälle (nicht in lucide-static 1.25.0) ────────────────────
# (a) CUSTOM: Kein Lucide-Icon — Eigenname.  (b) Ältere/abgewandelte Lucide-Form: dem heutigen
# Lucide-Namen zugeordnet (per Signatur einer älteren lucide-static verifiziert; alle Namen
# existieren in 1.25.0 weiter). Jeder Eintrag: (name, rohes Kind-Markup). Die Signatur wird daraus
# berechnet — dieselbe Funktion wie für die geladenen Icons.
OVERRIDES: list[tuple[str, str]] = [
    # GitHub-Logo (Octocat) — KEIN Lucide-Icon, Eigenname (badge.html).
    ("github", '<path d="M12 .3a12 12 0 0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2 0 1.9 1.2 1.9 1.2 1 1.8 2.8 1.3 3.5 1 0-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-6 0-1.2.5-2.3 1.3-3.1-.2-.4-.6-1.6 0-3.2 0 0 1-.3 3.4 1.2a11.5 11.5 0 0 1 6 0c2.3-1.5 3.3-1.2 3.3-1.2.6 1.6.2 2.8 0 3.2.9.8 1.3 1.9 1.3 3.2 0 4.6-2.8 5.6-5.5 5.9.5.4.9 1 .9 2.2v3.3c0 .3.1.7.8.6A12 12 0 0 0 12 .3"/>'),
    # Ältere/abgewandelte Lucide-Formen (heutiger Lucide-Name):
    ("triangle-alert", '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>'),
    ("file", '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>'),
    ("clock", '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
    ("file-code", '<path d="M10 12.5 8 15l2 2.5"/><path d="m14 12.5 2 2.5-2 2.5"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'),
    ("settings", '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>'),
    ("settings", '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>'),
    ("log-out", '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>'),
    ("dot", '<circle cx="12.1" cy="12.1" r="1"/>'),
    ("thumbs-up", '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z"/>'),
    ("thumbs-up", '<path d="M7 10v12"/><path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h.94a2 2 0 0 1 2 2.22Z"/>'),
    ("thumbs-down", '<path d="M17 14V2"/><path d="M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L13 22h-.94a2 2 0 0 1-2-2.22Z"/>'),
    ("heart", '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>'),
    ("search", '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'),
    ("download", '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>'),
    ("download", '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><path d="M12 15V3"/>'),
    ("file-plus", '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 15h6"/><path d="M12 12v6"/>'),
    ("file-text", '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>'),
    # UNSICHER: Datei-Glyphe mit zwei vollen Linien; kein exaktes Lucide, aber semantisch file-text (marker.html „Notizen").
    ("file-text", '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 15h6"/><path d="M9 11h6"/>'),
    ("calendar", '<rect width="18" height="18" x="3" y="4" rx="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>'),
    ("share", '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" x2="12" y1="2" y2="15"/>'),
    ("share-2", '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.59 13.51 6.83 3.98"/><path d="m15.41 6.51-6.82 3.98"/>'),
    ("pen-line", '<path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>'),
    ("mail", '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'),
    ("house", '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>'),
    ("users", '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    ("trash-2", '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>'),
    ("folder", '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>'),
    ("folder", '<path d="M4 22h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>'),
    ("folder", '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.91 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>'),
    ("cloud-upload", '<path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/>'),
    ("eye", '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>'),
    ("minus", '<line x1="5" x2="19" y1="12" y2="12"/>'),
    ("image", '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/>'),
    # UNSICHER: Koordinaten-Variante von arrow-up-right (marker.html „Pull Request ansehen").
    ("arrow-up-right", '<path d="M18 6 6 18"/><path d="M6 6h12v12"/>'),
    ("undo-2", '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5v0a5.5 5.5 0 0 1-5.5 5.5H11"/>'),
    ("redo-2", '<path d="m15 14 5-5-5-5"/><path d="M20 9H9.5A5.5 5.5 0 0 0 4 14.5v0A5.5 5.5 0 0 0 9.5 20H13"/>'),
    ("chart-column", '<path d="M3 3v18h18"/><rect width="3" height="6" x="7" y="12"/><rect width="3" height="10" x="12" y="8"/><rect width="3" height="14" x="17" y="4"/>'),
    ("text-align-start", '<line x1="21" x2="3" y1="6" y2="6"/><line x1="15" x2="3" y1="12" y2="12"/><line x1="17" x2="3" y1="18" y2="18"/>'),
    ("text-align-center", '<line x1="21" x2="3" y1="6" y2="6"/><line x1="17" x2="7" y1="12" y2="12"/><line x1="19" x2="5" y1="18" y2="18"/>'),
    ("funnel", '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>'),
    ("message-circle", '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>'),
    ("message-square", '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'),
    ("life-buoy", '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m4.93 19.07 4.24-4.24"/>'),
    ("send", '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>'),
    ("moon", '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'),
    ("list", '<line x1="8" x2="21" y1="6" y2="6"/><line x1="8" x2="21" y1="12" y2="12"/><line x1="8" x2="21" y1="18" y2="18"/><line x1="3" x2="3.01" y1="6" y2="6"/><line x1="3" x2="3.01" y1="12" y2="12"/><line x1="3" x2="3.01" y1="18" y2="18"/>'),
    ("bell", '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>'),
]

# ── Signatur ──────────────────────────────────────────────────────────────────
# Ein Icon ist durch seine geometrischen Kind-Elemente eindeutig. Je Kind die
# formbestimmenden Attribute in fester Reihenfolge, Werte whitespace-/trennzeichen-normalisiert;
# die Kinder sortiert (Reihenfolge im Markup ist irrelevant) und verbunden.
CHILD = re.compile(r"<(path|circle|rect|line|polyline|polygon|ellipse)\b([^>]*?)/?>", re.S)
ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
GEOM = {
    "path": ["d"],
    "circle": ["cx", "cy", "r"],
    "rect": ["x", "y", "width", "height", "rx", "ry"],
    "line": ["x1", "y1", "x2", "y2"],
    "polyline": ["points"],
    "polygon": ["points"],
    "ellipse": ["cx", "cy", "rx", "ry"],
}


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace(",", " ")).strip()


def signature(inner: str) -> str:
    parts = []
    for tag, attrs in CHILD.findall(inner):
        d = dict(ATTR.findall(attrs))
        parts.append(tag + ":" + ";".join(f"{k}={_norm(d[k])}" for k in GEOM[tag] if k in d))
    parts.sort()
    return "|".join(parts)


# ── Lucide laden (gecacht, ausserhalb des Repos) ──────────────────────────────
def lucide_dir() -> Path:
    """package/ der gepinnten lucide-static im Cache: icons/*.svg + icon-nodes.json."""
    pkg = CACHE / f"lucide-static-{LUCIDE_VERSION}"
    if (pkg / "icon-nodes.json").is_file() and any((pkg / "icons").glob("*.svg")):
        return pkg
    CACHE.mkdir(parents=True, exist_ok=True)
    tgz = CACHE / f"lucide-static-{LUCIDE_VERSION}.tgz"
    if not tgz.exists():
        print(f"↓ lade lucide-static {LUCIDE_VERSION} …", file=sys.stderr)
        urllib.request.urlretrieve(TARBALL_URL, tgz)  # noqa: S310 (feste, vertrauenswürdige URL)
    (pkg / "icons").mkdir(parents=True, exist_ok=True)
    with tarfile.open(tgz) as tar:
        for m in tar.getmembers():
            # nur die zwei gebrauchten Pfade, flach extrahiert — kein Pfad-Ausbruch möglich
            if not m.isfile():
                continue
            src = tar.extractfile(m)
            if src is None:
                continue
            if m.name.startswith("package/icons/") and m.name.endswith(".svg"):
                (pkg / "icons" / Path(m.name).name).write_bytes(src.read())
            elif m.name == "package/icon-nodes.json":
                (pkg / "icon-nodes.json").write_bytes(src.read())
    return pkg


def build_table() -> dict[str, str]:
    """Signatur → Name. Kanonische Namen zuerst: lucide-static liefert für umbenannte Icons
    ZWEI identische Dateien (Alias `bar-chart-3.svg` + kanonisch `chart-column.svg`);
    icon-nodes.json listet nur die kanonischen — die gewinnen bei Signatur-Dubletten.
    Danach die kuratierten OVERRIDES (füllen nur, was 1.25.0 nicht trägt; überschreiben nichts)."""
    import json
    pkg = lucide_dir()
    canonical = set(json.loads((pkg / "icon-nodes.json").read_text(encoding="utf-8")))
    table: dict[str, str] = {}
    svgs = sorted((pkg / "icons").glob("*.svg"),
                  key=lambda p: (p.stem not in canonical, p.stem))
    for svg in svgs:
        txt = svg.read_text(encoding="utf-8")
        inner = txt[txt.find(">", txt.find("<svg")):]
        table.setdefault(signature(inner), svg.stem)
    for name, inner in OVERRIDES:
        table.setdefault(signature(inner), name)
    return table


# ── Annotieren ────────────────────────────────────────────────────────────────
SVG_BLOCK = re.compile(r"<svg\b([^>]*)>(.*?)</svg>", re.S)
LU_ATTR = re.compile(rf'\s{ATTR_NAME}="([^"]*)"')


def is_lucide_like(open_attrs: str) -> bool:
    """Die drei Kennattribute eines Lucide-<svg> (identisch zu Regel 11 der Suite)."""
    return ('stroke="currentColor"' in open_attrs
            and 'stroke-linecap="round"' in open_attrs
            and 'stroke-linejoin="round"' in open_attrs)


def annotate_text(text: str, table: dict[str, str], relname: str,
                  stats: dict[str, int], unmatched: list[str]) -> str:
    def repl(m: re.Match[str]) -> str:
        open_attrs, inner = m.group(1), m.group(2)
        if not is_lucide_like(open_attrs):
            return m.group(0)
        stats["icons"] += 1
        name = table.get(signature(inner))
        if not name:
            line = text.count("\n", 0, m.start()) + 1
            excerpt = re.sub(r"\s+", " ", inner).strip()[:70]
            unmatched.append(f"{relname}:{line}  {excerpt}")
            stats["unmatched"] += 1
            return m.group(0)
        stats["matched"] += 1
        cur = LU_ATTR.search(open_attrs)
        if cur:
            if cur.group(1) == name:
                stats["ok"] += 1
                return m.group(0)
            new_attrs = open_attrs[:cur.start()] + f' {ATTR_NAME}="{name}"' + open_attrs[cur.end():]
            stats["corrected"] += 1
            line = text.count("\n", 0, m.start()) + 1
            print(f"  korrigiert {relname}:{line}  {cur.group(1)} → {name}")
        else:
            new_attrs = f' {ATTR_NAME}="{name}"' + open_attrs
            stats["added"] += 1
        return f"<svg{new_attrs}>{inner}</svg>"

    return SVG_BLOCK.sub(repl, text)


def main() -> int:
    ap = argparse.ArgumentParser(description="Lucide-Inline-Icons in den Components benennen.")
    ap.add_argument("--check", action="store_true",
                    help="nichts schreiben; Exit 1, wenn etwas zu ändern wäre oder unmatched bleibt")
    args = ap.parse_args()

    table = build_table()
    stats = {"icons": 0, "matched": 0, "added": 0, "corrected": 0, "ok": 0, "unmatched": 0}
    unmatched: list[str] = []
    changed: list[str] = []

    for f in COMPONENTS:
        rel = str(f.relative_to(ROOT))
        old = f.read_text(encoding="utf-8")
        new = annotate_text(old, table, rel, stats, unmatched)
        if new != old:
            changed.append(rel)
            if not args.check:
                f.write_text(new, encoding="utf-8")

    print(f"\nlucide-static {LUCIDE_VERSION} · {len(table)} Signaturen "
          f"({len(OVERRIDES)} Overrides)")
    print(f"Lucide-artige <svg>: {stats['icons']}  ·  benannt: {stats['matched']}  "
          f"(neu {stats['added']}, korrigiert {stats['corrected']}, unverändert {stats['ok']})")
    if unmatched:
        print(f"\nOHNE Treffer ({stats['unmatched']}):")
        for u in unmatched:
            print(f"  {u}")
    if changed:
        verb = "würde ändern" if args.check else "geändert"
        print(f"\n{verb}: {len(changed)} Datei(en): {', '.join(changed)}")
    else:
        print("\nkeine Änderung (idempotent).")

    if args.check and (changed or unmatched):
        return 1
    return 1 if unmatched else 0


if __name__ == "__main__":
    sys.exit(main())
