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
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _kit.report import Report  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# Geltungsbereich: Components + die Seiten-Verzeichnisse der Galerie
# (Blocks/Charts/Typeset) — dieselben Konventionen gelten überall.
KOMPONENTEN = sorted([
    *(ROOT / "c22" / "components").glob("*.html"),
    *(ROOT / "c22" / "blocks").glob("*/*.html"),
    *(ROOT / "c22" / "charts").glob("*.html"),
    *(ROOT / "c22" / "typeset").glob("*.html"),
])
JS = ROOT / "c22" / "static" / "js" / "c22.js"
TOKENS = ROOT / "c22" / "static" / "css" / "tokens.css"

# Markup-Quellen (Regeln 1–5 + 10): Components + die Klassen-Strings im Behaviour-JS.
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


# ── Regel 7: kein width/height an IRGENDEINEM <svg> ──────────────────────────
# Jedes Icon im Repo wird ausnahmslos per size-*-Klasse ODER per dimensionierendem
# Vorfahren (Regel 8 garantiert genau das) gemessen — ein inline `width`/`height`
# am <svg> ist damit toter, nur rückfallgefährdeter Ballast (CLAUDE.md „Icons —
# Sizing"). Blanket: KEIN <svg> trägt ein width=/height=-Attribut. Zeilenweise
# geprüft (svg-Öffnungs-Tags stehen im Repo je auf einer Zeile); der Lookbehind
# schließt stroke-width/-height aus (der `-` bzw. ein Wortzeichen davor heißt:
# kein eigenständiges Attribut).
SVG_OPEN = re.compile(r"<svg\b")


def r7_svg_masse() -> list[str]:
    treffer: list[str] = []
    for p in KOMPONENTEN:
        for i, ln in enumerate(zeilen(p.read_text(encoding="utf-8")), 1):
            for m in SVG_OPEN.finditer(ln):
                ende = ln.find(">", m.start())
                tag = ln[m.start():ende if ende != -1 else len(ln)]
                for attr in ("width", "height"):
                    if re.search(rf"(?<![\w-]){attr}\s*=", tag):
                        treffer.append(f"{rel(p)}:{i}  <svg> trägt {attr}= "
                                       f"— Icon wird per size-*/CSS gemessen, Attribut weg")
    return treffer


# ── Regel 8: 24px-Icon ohne size-* braucht einen dimensionierenden Vorfahren ──
# Ein nacktes Lucide-<svg> rendert 24px und erschlägt danebenstehenden text-xs/-sm
# (CLAUDE.md „Icons — Sizing"). Zulässig ohne size-*-Klasse ist es NUR, wenn ein
# Vorfahre (oder das svg selbst) zu einem Kontext gehört, dessen Component-CSS die
# Icon-Größe bereits setzt — sonst ist es ein echter Fund. Echte Verschachtelung
# über html.parser (kein Zeilen-Raten), damit „im .btn" ≠ „irgendwo drunter" sauber
# unterschieden wird.
#
# Whitelist = die Kontexte, in denen C22-CSS `svg { size }` setzt (Klasse als
# Wort-Token, sonst greift `alert` fälschlich in `alert-dialog`):
#   • .btn / .kbd / .badge            — Steuer-/Chip-CSS dimensioniert ihre Icons
#   • .item-media / .avatar-badge     — Medien-Kachel bzw. Status-Punkt am Avatar
#   • .alert / .select                — Alert-Icon-Spalte; Select-Trigger-Chevron
#   • <figure>                        — .item/.card-Figur (bei .item NUR figure —
#                                       <aside> NICHT, darum war item:120 ein Fund)
#   • [data-carousel-arrow|-dot]      — Carousel-Pfeile/Punkte
#   • combobox-trigger-icon           — Klasse sitzt am svg selbst (Trigger-Chevron)
#   • .command + <header>             — die Such-Lupe im Command-Header
#   • .input-group + [data-align]     — Icon-Slot im Input-Group-Rahmen
#   • role^=menuitem / =option / =heading — Menü-/Options-/Rubrik-Icons
#   • <summary> / .accordion / .collapsible — Aufklapp-Chevron
_VOID = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse",
         "br", "img", "input", "hr", "source", "meta", "use", "stop", "defs"}
_CLASS_KONTEXTE = {"btn", "kbd", "badge", "item-media", "avatar-badge",
                   "alert", "select", "accordion", "collapsible"}


def _tokens(attrs: dict[str, str]) -> list[str]:
    return (attrs.get("class") or "").split()


def _dimensionierter_vorfahre(svg: dict[str, str],
                              vorfahren: list[tuple[str, dict[str, str]]]) -> bool:
    if "combobox-trigger-icon" in _tokens(svg):
        return True
    hat_command = any("command" in _tokens(a) for _, a in vorfahren)
    hat_header = any(t == "header" for t, _ in vorfahren)
    if hat_command and hat_header:
        return True
    hat_inputgroup = any("input-group" in _tokens(a) for _, a in vorfahren)
    hat_dataalign = any("data-align" in a for _, a in vorfahren)
    if hat_inputgroup and hat_dataalign:
        return True
    for t, a in vorfahren:
        if t in ("figure", "summary"):
            return True
        if _CLASS_KONTEXTE & set(_tokens(a)):
            return True
        if "data-carousel-arrow" in a or "data-carousel-dot" in a:
            return True
        role = a.get("role", "")
        if role.startswith("menuitem") or role in ("option", "heading"):
            return True
    return False


class _IconParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.funde: list[int] = []

    def _pruefe(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "svg":
            return
        d = {k: (v or "") for k, v in attrs}
        if d.get("width") == "24" and "size-" not in d.get("class", ""):
            if not _dimensionierter_vorfahre(d, self.stack):
                self.funde.append(self.getpos()[0])

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._pruefe(tag, attrs)
        if tag not in _VOID:
            self.stack.append((tag, {k: (v or "") for k, v in attrs}))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._pruefe(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def r8_icon_masse_vorfahre() -> list[str]:
    treffer: list[str] = []
    for p in KOMPONENTEN:
        parser = _IconParser()
        parser.feed(p.read_text(encoding="utf-8"))
        for line in parser.funde:
            treffer.append(f"{rel(p)}:{line}  24px-<svg> ohne size-*-Klasse und ohne "
                           f"dimensionierenden Vorfahren — size-* setzen")
    return treffer


# ── Regel 9: keine Generierungs-Artefakte (Streuner-Tags) ────────────────────
# Ein Partial endet mit dem </div> seiner .c22-examples. Verirrte </content>-/
# </invoke>-/<content-Reste aus der HTML-Erzeugung sind kein gültiges Markup —
# Regressionsnetz gegen genau diese Artefakte (Vorfall: Batch-Generierung ließ
# solche Streuner am Dateiende zurück).
STREUNER = re.compile(r"</?(?:content|invoke)\b")


def r9_streuner_tags() -> list[str]:
    treffer: list[str] = []
    for p in KOMPONENTEN:
        for i, ln in enumerate(zeilen(p.read_text(encoding="utf-8")), 1):
            m = STREUNER.search(ln)
            if m:
                treffer.append(f"{rel(p)}:{i}  Streuner-Tag `{m.group(0)}` "
                               f"— Generierungs-Artefakt, entfernen")
    return treffer


# ── Regel 10: kein aria-pressed:/aria-checked:-Arbitrary-Variant im Markup ───
# Der Pressed/Checked-Look kommt aus der Foundation-Regel `.btn[aria-pressed='true']`
# (bzw. `[aria-checked='true']`) in components.css — SPOT, an einer Stelle. Er darf
# nicht mehr per Utility-Variante (`aria-pressed:bg-accent` …) je Component gestreut
# werden. Das Attribut selbst (`aria-pressed="true"`) ist unberührt: davor steht ein
# `=`, keine `:` — nur die Variante mit dem Doppelpunkt ist gemeint.
ARIA_VARIANT = re.compile(r"\baria-(?:pressed|checked):")


def r10_aria_variant_utilities() -> list[str]:
    treffer: list[str] = []
    for p in QUELLEN:
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            for m in ARIA_VARIANT.finditer(ln):
                treffer.append(f"{rel(p)}:{i}  Arbitrary-Variant `{m.group(0)}…` "
                               f"— Pressed/Checked-Look kommt aus .btn[aria-pressed] "
                               f"(components.css), nicht per Utility")
    return treffer


# ── Regel 11: jedes Lucide-Icon trägt seinen Namen (data-icon-lu) ────────────
# Fundament der Achse „icon library" (docs/theming.md Achse 8, docs/icons.md): ein
# Bibliothekswechsel zur Generierungszeit tauscht Icon-Markup anhand des NAMENS —
# anonyme Pfade machen die Achse unbaubar. Lucide-artig = die drei Kennattribute
# (stroke="currentColor" + stroke-linecap/linejoin="round", dieselbe Heuristik wie
# tools/annotate-icons.py — das Werkzeug schreibt die Namen, diese Regel hält sie).
# BEWUSST data-icon-lu, nicht data-icon: `data-icon` ist Basecoats Padding-Hinweis
# (inline-start/inline-end) und bleibt unberührt. Nur Components — die SVG-Strings
# in c22.js entstehen per Konkatenation (CAL_ICO) und sind von Hand benannt.
LUCIDE_KENN = ('stroke="currentColor"', 'stroke-linecap="round"', 'stroke-linejoin="round"')
ICON_LU = re.compile(r'data-icon-lu="([^"]*)"')


def r11_lucide_namen() -> list[str]:
    treffer: list[str] = []
    for p in KOMPONENTEN:
        for i, ln in enumerate(zeilen(p.read_text(encoding="utf-8")), 1):
            for m in SVG_OPEN.finditer(ln):
                ende = ln.find(">", m.start())
                tag = ln[m.start():ende if ende != -1 else len(ln)]
                if not all(k in tag for k in LUCIDE_KENN):
                    continue
                name = ICON_LU.search(tag)
                if not name or not name.group(1).strip():
                    treffer.append(f"{rel(p)}:{i}  Lucide-<svg> ohne data-icon-lu "
                                   f"— tools/annotate-icons.py laufen lassen")
    return treffer


# ── Regel 12: geschlossenes Varianten-Vokabular ──────────────────────────────
# Regel 4 prüft die FORM eines data-variant (lowercase-kebab); Regel 12 prüft die
# MITGLIEDSCHAFT: jeder Wert muss aus einer festen Liste stammen. Die Farb-Rollen
# (primary/secondary/muted/accent/tinted/outline/ghost/link/destructive/success/
# warning/info) sind der geteilte Kern aller Varianten — die sichtbare Übersicht
# dazu ist components/color-roles.html; „Umfärben = Tokens tauschen" hängt daran.
# Dazu die wenigen Nicht-Farb-Ausführungen derselben Achse (Form/Struktur statt
# eigener Rolle), die real existieren. Ein neuer Variantenname gehört ZUERST hierher
# (bewusste Entscheidung + color-roles.html), nicht per Tippfehler ins Markup —
# genau so wie Regel 6 das Wegrefactoren der Achsen-Tokens verhindert.
ERLAUBTE_VARIANTEN = {
    # Farb-Rollen — greifen die Token-Paare ab (siehe color-roles.html):
    "primary", "secondary", "muted", "accent", "tinted",
    "outline", "ghost", "link", "destructive",
    "success", "warning", "info",
    # Nicht-Farb-Ausführungen derselben Achse (Form/Struktur, keine eigene Farb-Rolle):
    "line", "label", "elevated", "card", "bordered", "separator", "mono", "browser", "grid",
}
VARIANT_ATTR = re.compile(r'data-variant="([^"]*)"')


def _variant_verstoesse(quelle: str, name: str) -> list[str]:
    """Kernprüfung (auch vom Selbsttest genutzt): meldet data-variant-Werte, die nicht
    im Vokabular stehen. Kommentare/<code>-Labels sind vom Aufrufer schon ausgeblendet."""
    treffer: list[str] = []
    for i, ln in enumerate(zeilen(quelle), 1):
        for wert in VARIANT_ATTR.findall(ln):
            if wert not in ERLAUBTE_VARIANTEN:
                treffer.append(f"{name}:{i}  data-variant=\"{wert}\" nicht im Vokabular "
                               f"— Wert in color-roles.html/ERLAUBTE_VARIANTEN aufnehmen "
                               f"oder an eine bestehende Rolle angleichen")
    return treffer


def r12_variant_vokabular() -> list[str]:
    treffer: list[str] = []
    for p in KOMPONENTEN:
        treffer += _variant_verstoesse(strip_kommentare(p.read_text(encoding="utf-8")), rel(p))
    return treffer


def r12_selbsttest() -> bool:
    """Ein Wächter, der nie anschlägt, ist wertlos (Lektion aus früheren Regex-Wächtern):
    ein erfundener Wert MUSS gemeldet, ein gültiger NICHT gemeldet werden."""
    bad = _variant_verstoesse('<span data-variant="knallrot">x</span>', "selftest")
    good = _variant_verstoesse('<span data-variant="primary">x</span>'
                               '<span data-variant="success">x</span>', "selftest")
    return len(bad) == 1 and good == []


# ── Regel 13: keine RTL-Demos außerhalb von direction.html (Galerie-Linie, PO) ─
# RTL wird EINMAL in der Direction-Component gezeigt; verstreute dir="rtl"-Demos in
# anderen Partials wurden systematisch entfernt und sollen nicht zurückkehren.
# Kopfkommentare (Doku-Hinweise wie „funktioniert mit dir=rtl") sind ausgenommen.
def r13_rtl_demos() -> list[str]:
    treffer: list[str] = []
    for p in KOMPONENTEN:
        if p.name == "direction.html":
            continue
        for i, ln in enumerate(zeilen(strip_kommentare(p.read_text(encoding="utf-8"))), 1):
            if 'dir="rtl"' in ln:
                treffer.append(f'{rel(p)}:{i}  dir="rtl" — RTL-Demos leben nur in direction.html')
    return treffer


r = Report("Konventionen — Varianten-Vertrag & Tokens")
r.check("Regel 1 — keine Literal-Farben im Markup", not (t := r1_literalfarben()), " | ".join(t[:4]))
r.check("Regel 2 — keine Tailwind-Palette-Klassen", not (t := r2_palette_klassen()), " | ".join(t[:4]))
r.check("Regel 3 — keine willkürlichen Größen (nur text-[11px])",
        not (t := r3_willkuerliche_groessen()), " | ".join(t[:4]))
r.check("Regel 4 — Varianten-Vokabular ^[a-z0-9-]+$", not (t := r4_varianten_vokabular()), " | ".join(t[:4]))
r.check("Regel 5 — kbd: eine Box je Taste", not (t := r5_kbd_vertrag()), " | ".join(t[:6]))
r.check("Regel 6 — Achsen-Tokens in tokens.css vorhanden", not (t := r6_achsen_tokens()), " | ".join(t))
r.check("Regel 7 — kein width/height an irgendeinem <svg>", not (t := r7_svg_masse()), " | ".join(t[:4]))
r.check("Regel 8 — 24px-Icon ohne size-* braucht dimensionierenden Vorfahren",
        not (t := r8_icon_masse_vorfahre()), " | ".join(t[:6]))
r.check("Regel 9 — keine Streuner-Tags (</content>/</invoke>/<content)",
        not (t := r9_streuner_tags()), " | ".join(t[:6]))
r.check("Regel 10 — kein aria-pressed:/aria-checked:-Arbitrary-Variant im Markup",
        not (t := r10_aria_variant_utilities()), " | ".join(t[:6]))
r.check("Regel 11 — jedes Lucide-<svg> trägt ein nicht-leeres data-icon-lu",
        not (t := r11_lucide_namen()), " | ".join(t[:6]))
r.check("Regel 12 — data-variant nur aus dem festen Vokabular (color-roles.html)",
        not (t := r12_variant_vokabular()), " | ".join(t[:6]))
r.check("Regel 12 — Selbsttest (Vokabular-Regel greift wirklich)", r12_selbsttest())
r.check("Regel 13 — keine RTL-Demos außerhalb von direction.html",
        not (t := r13_rtl_demos()), " | ".join(t[:6]))

sys.exit(r.done())
