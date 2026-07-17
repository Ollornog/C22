"""Konventionen: der Varianten-Vertrag und die Token-Pflicht des Design-Systems,
mechanisch geprüft. Was CLAUDE.md als Regel beschreibt, hält hier eine Maschine fest,
damit „Tokens statt Hex" und „eine Box je Taste" nicht am Vorsatz hängen.

Geltungsbereich: alle `c22/components/*.html` und die Klassen-Strings in
`c22/static/js/c22.js`. Die Token-*Definitionen* (`c22/static/css/*.css`) sind bewusst
ausgenommen — dort leben die Werte; Regel 6 liest tokens.css nur lesend.

Stil wie das übrige Repo: jede Prüffunktion gibt eine Liste von Befunden
(`datei:zeile  meldung`) zurück; die Suite ist grün, wenn alle Listen leer sind.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kit.report import Report  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KOMPONENTEN = sorted((ROOT / "c22" / "components").glob("*.html"))
JS = ROOT / "c22" / "static" / "js" / "c22.js"
TOKENS = ROOT / "c22" / "static" / "css" / "tokens.css"

# Markup-Quellen (Regeln 1–5): Components + die Klassen-Strings im Behaviour-JS.
QUELLEN = KOMPONENTEN + [JS]


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def strip_kommentare(text: str) -> str:
    """Dokumentation ausblenden, damit sie die Markup-Regeln nicht auslöst — durch
    gleich langen Leerraum ersetzt, Zeilennummern bleiben erhalten. Betrifft:
      • HTML-Kommentare — dokumentieren u.a. das Optionsvokabular (`data-side="top|right|…"`).
      • den *Textinhalt* von <code>…</code> — die Beispiel-Labels zeigen dort Optionsstrings
        wörtlich (`data-side="inline-start/inline-end"`, `data-variant="ghost"`); das sind
        keine echten Attribute an echten Elementen. Das öffnende Tag (mit seiner class,
        z.B. text-[11px]) bleibt erhalten und wird weiter geprüft."""
    def leer(s: str) -> str:
        return re.sub(r"[^\n]", " ", s)
    text = re.sub(r"<!--.*?-->", lambda m: leer(m.group(0)), text, flags=re.S)
    text = re.sub(r"(<code[^>]*>)(.*?)(</code>)",
                  lambda m: m.group(1) + leer(m.group(2)) + m.group(3), text, flags=re.S)
    return text


def zeilen(text: str) -> list[str]:
    return text.split("\n")


# ── Regel 1: keine Literal-Farben im Markup ──────────────────────────────────
# #hex in class/style, rgb(/oklch( in irgendeinem Attribut, arbitrary-Farb-Utilities.
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
ATTR = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
FARB_UTIL = re.compile(r"(?:bg|text|border|ring|fill|stroke|divide|from|via|to|shadow)-\[#"
                       r"|-\[oklch|-\[rgb")


def r1_literalfarben() -> list[str]:
    treffer: list[str] = []
    for p in QUELLEN:
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            for name, wert in ATTR.findall(ln):
                if name in ("class", "style") and HEX.search(wert):
                    treffer.append(f"{rel(p)}:{i}  Hex-Farbe in {name}=\"…{HEX.search(wert).group(0)}…\"")
                if ("rgb(" in wert or "oklch(" in wert):
                    treffer.append(f"{rel(p)}:{i}  rgb()/oklch() im Attribut {name}")
            m = FARB_UTIL.search(ln)
            if m:
                treffer.append(f"{rel(p)}:{i}  arbitrary-Farb-Utility ({m.group(0)}…)")
    return treffer


# ── Regel 2: keine Tailwind-Palette-Klassen ──────────────────────────────────
PALETTE = ("slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|"
           "teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose")
PROPS = ("bg|text|border|ring|fill|stroke|from|via|to|decoration|outline|accent|caret|"
         "divide|shadow")
# Kern-Utility; Varianten-Präfixe (dark:/hover:/…) stehen davor, `!`-Suffix dahinter.
# \b vor der Property greift auch nach einem `:`-Präfix, da ':' eine Wortgrenze ist.
TW_PALETTE = re.compile(rf"\b(?:{PROPS})-(?:{PALETTE})-\d{{2,3}}\b!?")


def r2_palette_klassen() -> list[str]:
    treffer: list[str] = []
    for p in QUELLEN:
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            for m in TW_PALETTE.finditer(ln):
                treffer.append(f"{rel(p)}:{i}  Palette-Klasse `{m.group(0)}` — Token nutzen "
                               f"(bg-success/warning/info/destructive/muted/…)")
    return treffer


# ── Regel 3: keine willkürlichen Größen ──────────────────────────────────────
# text-[Npx] verboten; einzige sanktionierte Ausnahme text-[11px] (Beispiel-Labels,
# CLAUDE.md „Typography" / docs/theming.md).
TEXT_PX = re.compile(r"text-\[(\d+)px\]")


def r3_willkuerliche_groessen() -> list[str]:
    treffer: list[str] = []
    for p in QUELLEN:
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            for m in TEXT_PX.finditer(ln):
                if m.group(1) != "11":
                    treffer.append(f"{rel(p)}:{i}  willkürliche Größe `{m.group(0)}` "
                                   f"(nur text-[11px] ist sanktioniert)")
    return treffer


# ── Regel 4: Varianten-Vokabular ─────────────────────────────────────────────
DATA_ATTR = re.compile(r'data-(variant|size|align|side)="([^"]*)"')
VOKABEL = re.compile(r"^[a-z0-9-]+$")


def r4_varianten_vokabular() -> list[str]:
    treffer: list[str] = []
    for p in QUELLEN:
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            for attr, wert in DATA_ATTR.findall(ln):
                if not VOKABEL.match(wert):
                    treffer.append(f"{rel(p)}:{i}  data-{attr}=\"{wert}\" verletzt ^[a-z0-9-]+$")
    return treffer


# ── Regel 5: kbd-Vertrag ─────────────────────────────────────────────────────
# Eine Box je Taste: der Textinhalt eines <kbd class="kbd"> enthält kein Leerzeichen.
# Icon-Tasten (SVG-Inhalt) haben Kind-Elemente → [^<]* matcht nicht → korrekt übersprungen.
KBD = re.compile(r'<kbd\s+class="kbd[^"]*"[^>]*>([^<]*)</kbd>')


def r5_kbd_vertrag() -> list[str]:
    treffer: list[str] = []
    for p in QUELLEN:
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            for text in KBD.findall(ln):
                if " " in text.strip():
                    treffer.append(f"{rel(p)}:{i}  <kbd> mit Leerzeichen: \"{text.strip()}\" "
                                   f"— je Taste eine eigene <kbd>")
    return treffer


# ── Regel 6: Achsen-Tokens vorhanden ─────────────────────────────────────────
# Schutz gegen Wegrefactoren: tokens.css muss diese Achsen weiter definieren.
def r6_achsen_tokens() -> list[str]:
    css = TOKENS.read_text(encoding="utf-8")
    fehlend: list[str] = []
    pflicht = {
        "--font-heading": re.compile(r"--font-heading\s*:"),
        "--info (oklch)": re.compile(r"--info\s*:\s*oklch\("),
        "--overlay-control": re.compile(r"--overlay-control\s*:"),
    }
    for n in range(1, 6):
        pflicht[f"--chart-{n} (oklch)"] = re.compile(rf"--chart-{n}\s*:\s*oklch\(")
    for name, rx in pflicht.items():
        if not rx.search(css):
            fehlend.append(f"{rel(TOKENS)}  Token {name} fehlt")
    return fehlend


r = Report("Konventionen — Varianten-Vertrag & Tokens")
r.check("Regel 1 — keine Literal-Farben im Markup", not (t := r1_literalfarben()), " | ".join(t[:4]))
r.check("Regel 2 — keine Tailwind-Palette-Klassen", not (t := r2_palette_klassen()), " | ".join(t[:4]))
r.check("Regel 3 — keine willkürlichen Größen (nur text-[11px])",
        not (t := r3_willkuerliche_groessen()), " | ".join(t[:4]))
r.check("Regel 4 — Varianten-Vokabular ^[a-z0-9-]+$", not (t := r4_varianten_vokabular()), " | ".join(t[:4]))
r.check("Regel 5 — kbd: eine Box je Taste", not (t := r5_kbd_vertrag()), " | ".join(t[:6]))
r.check("Regel 6 — Achsen-Tokens in tokens.css vorhanden", not (t := r6_achsen_tokens()), " | ".join(t))

sys.exit(r.done())
