"""Die Achsen — geprüft in BEIDE Richtungen.

Ein Design-System, in dem ein Pack seinen Charakter nur zur Hälfte durchsetzt, ist kaputt, ohne
dass es jemand merkt: `lyra` ist eckig, aber die Fläche, die C22 selbst gestaltet hat, blieb rund.
Genau das lässt sich mechanisch ausschliessen, und zwar von zwei Seiten:

**A — jedes Pack gibt jede Achse an.** Für jedes Pack existiert eine Achsenschicht
(`c22/static/css/packs/<pack>.css`), sie nennt jede Achse aus `c22/axes.py` — entweder mit Werten
oder ausdrücklich als `@achse <name>: erbt`. „Vergessen" ist damit kein möglicher Zustand mehr,
nur noch „bewusst geerbt".

**B — keine Component umgeht eine Achse.** Im Markup (und im Galerie-Generator, der Markup
schreibt) darf nichts stehen, was eine Achse aushebelt: kein fester Radius, keine rohe
Schriftgrösse, kein fester Schatten, keine Dauer in Millisekunden, keine Paletten-Farbe.
Utilities, die an Tokens hängen (`rounded-lg`, `text-sm`, `shadow-md`, `p-4`), sind ausdrücklich
richtig — sie SIND der Weg, eine Achse zu lesen.

Warum das hier und nicht in `test_conventions.py`: dort geht es um den Varianten-/Klassen-Kanon
einer einzelnen Component. Hier geht es um das Verhältnis von Packs, Tokens und Markup — die
Systemebene.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _kit.report import Report  # noqa: E402
from c22 import axes  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "c22" / "static" / "css"
PACK_DIR = CSS / "packs"
MARKUP_DIRS = ("c22/components", "c22/blocks", "c22/charts", "c22/typeset")
# Die Kanon-Regeln selbst gehören mit geprüft: eine Component kann ihre Achse auch
# über eine @apply-Kette in components.css verlieren (so blieb `.bubble` rund).
# Seit ADR-2 (2026-11-21) dürfen Packs Regeln für Bausteine tragen; dieselben Achsen-Grenzen gelten auch dort.
KANON = ("c22/static/css/components.css",
         *sorted(f"c22/static/css/{p.name}" for p in (ROOT / "c22" / "static" / "css").glob("app-*.css")),
         *sorted(f"c22/static/css/packs/{p.name}" for p in (ROOT / "c22" / "static" / "css" / "packs").glob("*.css")
                 if "@c22-layout:" in p.read_text(encoding="utf-8")))
GENERATOR = ("gallery/build.py", "gallery/landing.py", "gallery/legal.py", "gallery/i18n.py")

r = Report("Achsen — Packs und Components")


def packs_aus_build() -> list[str]:
    """Die Pack-Liste steht im Build-Skript — eine Quelle, kein zweites Register."""
    text = (ROOT / "scripts" / "build-gallery.sh").read_text(encoding="utf-8")
    m = re.search(r"^PACKS=\(([^)]+)\)", text, re.M)
    assert m, "PACKS=(…) nicht in scripts/build-gallery.sh gefunden"
    return m.group(1).split()


def gesetzte_tokens(text: str) -> set[str]:
    """Custom Properties, die eine Datei setzt (Deklarationen, keine var()-Nutzung)."""
    return set(re.findall(r"^\s*(--[a-z0-9-]+)\s*:", text, re.M))


PACKS = packs_aus_build()
BASIS = gesetzte_tokens((CSS / "tokens.css").read_text(encoding="utf-8")) | gesetzte_tokens(
    (ROOT / "c22" / "vendor" / "basecoat" / "dist" / "base" / "base.css").read_text(encoding="utf-8"))

# ── A1: jedes Pack hat eine Achsenschicht ─────────────────────────────────────
fehlend = [p for p in PACKS if not (PACK_DIR / f"{p}.css").exists()]
r.check(f"jedes Pack hat eine Achsenschicht ({len(PACKS)} Packs)", not fehlend, ", ".join(fehlend))

# ── A2: jede Achsenschicht nennt JEDE Achse ───────────────────────────────────
# Entweder alle Pflicht-Tokens der Achse sind gesetzt, oder die Achse ist ausdrücklich als
# „erbt" markiert. Ein Pack, das eine Achse gar nicht erwähnt, hat sie vergessen.
luecken: list[str] = []
for pack in PACKS:
    datei = PACK_DIR / f"{pack}.css"
    if not datei.exists():
        continue
    text = datei.read_text(encoding="utf-8")
    gesetzt = gesetzte_tokens(text)
    markiert = {m.group(1) for m in re.finditer(r"@achse\s+([a-z-]+)\s*:", text)}
    for achse in axes.ACHSEN:
        vollstaendig = all(t in gesetzt for t in achse.pflicht)
        if not (vollstaendig or achse.name in markiert):
            luecken.append(f"{pack}: {achse.name}")
r.check(f"jede Achsenschicht nennt alle {len(axes.ACHSEN)} Achsen",
        not luecken, " | ".join(luecken[:6]))

# ── A3: jede Achse ist im Pack WIRKSAM (Token existiert irgendwo in der Kette) ─
# Der Marker „erbt" ist nur zulässig, wenn die Basis den Wert tatsächlich liefert — sonst wäre
# die Achse ein Versprechen ohne Deckung.
ohne_deckung: list[str] = []
for pack in PACKS:
    datei = PACK_DIR / f"{pack}.css"
    gesetzt = gesetzte_tokens(datei.read_text(encoding="utf-8")) if datei.exists() else set()
    for token in axes.PFLICHT_TOKENS:
        if token not in gesetzt and token not in BASIS:
            ohne_deckung.append(f"{pack}: {token}")
r.check(f"jede Achse ist gedeckt (Pack oder Basis, {len(axes.PFLICHT_TOKENS)} Tokens)",
        not ohne_deckung, " | ".join(sorted(set(ohne_deckung))[:6]))

# ── A4: abgeleitete Tokens werden NICHT pro Pack gesetzt ──────────────────────
# --radius-lg oder --text-sm gehören der Ableitung in tokens.css. Setzt ein Pack sie direkt,
# hat es zwei Wahrheiten über dieselbe Achse.
doppelt: list[str] = []
for pack in PACKS:
    datei = PACK_DIR / f"{pack}.css"
    if not datei.exists():
        continue
    gesetzt = gesetzte_tokens(datei.read_text(encoding="utf-8"))
    doppelt += [f"{pack}: {t}" for t in axes.ABGELEITETE_TOKENS if t in gesetzt]
r.check("kein Pack setzt ein abgeleitetes Token direkt", not doppelt, " | ".join(doppelt[:6]))

# ── B: kein Markup umgeht eine Achse ──────────────────────────────────────────
# Verboten sind LITERALE, die eine Achse aushebeln. Token-gebundene Utilities sind richtig.
VERBOTEN: list[tuple[str, str, str]] = [
    # (Achse, Regex, Erklärung)
    ("radius", r"rounded(?:-[a-z]{1,2})?-\[[^\]]+\]", "fester Radius statt --radius"),
    # Tailwind leitet NUR sm/md/lg/xl aus `--radius` ab (shadcn-Konvention in base.css).
    # `rounded-2xl/3xl/4xl` und das nackte `rounded` sind FESTE Werte — sie sehen aus wie
    # Token-Utilities, hängen aber an keiner Achse. Genau daran blieb `.bubble` in „lyra" rund.
    # `rounded-none` und `rounded-full` bleiben erlaubt: „immer eckig" bzw. „immer Kreis" ist
    # eine Aussage über die FORM des Bauteils, keine heimliche Radius-Entscheidung.
    ("radius", r"rounded-(?:2xl|3xl|4xl)\b", "feste Tailwind-Stufe, nicht an --radius gekoppelt"),
    ("radius", r"@apply[^;]*\brounded\b(?!-)", "nacktes `rounded` = fester Wert (0.25rem)"),
    ("radius", r"border-radius\s*:(?!\s*(?:var\(|calc\(|min\(|max\(|clamp\(|inherit|0\b))", "Radius als Festwert (var()/calc()/min() sind richtig)"),
    ("type-scale", r"text-\[(?!11px)[^\]]*(?:px|rem|em)\]", "rohe Schriftgrösse statt --text-*"),
    ("type-scale", r"font-size\s*:(?!\s*(?:var\(|calc\())", "Schriftgrösse als Festwert"),
    ("elevation", r"shadow-\[[^\]]+\]", "fester Schatten statt --shadow-*"),
    ("motion", r"duration-\[[^\]]+\]", "feste Dauer statt der Motion-Achse"),
    ("motion", r"transition-duration\s*:(?!\s*var\()", "Dauer als Festwert"),
    ("icon-weight", r'stroke-width="(?!2")[0-9.]+"', "abweichende Strichstärke statt --icon-stroke"),
    ("density", r"(?:^|[\s\"'])(?:p|px|py|pt|pb|ps|pe|m|mx|my|gap)-\[[^\]]+\]",
     "feste Abstände statt der Dichte-Achse"),
]
PALETTE = re.compile(
    r"\b(?:bg|text|border|ring|fill|stroke|from|to|via)-(?:slate|gray|zinc|neutral|stone|red|orange|"
    r"amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-\d{2,3}\b")


def dateien() -> list[Path]:
    aus: list[Path] = []
    for d in MARKUP_DIRS:
        aus += sorted((ROOT / d).rglob("*.html"))
    aus += [ROOT / g for g in GENERATOR]
    aus += [ROOT / k for k in KANON]
    return [p for p in aus if p.exists()]


def ohne_kommentare(text: str):
    """(Zeilennummer, Inhalt) — Zeilen INNERHALB eines Blockkommentars fallen weg.

    Erste Fassung prüfte nur, ob eine Zeile mit `*` beginnt: die Fortsetzungszeile eines
    CSS-Blockkommentars, die mit einem Backtick anfängt, schlug damit als Verstoss an. Ein
    Test, der über sein eigenes Beispiel stolpert, verliert seine Autorität.
    """
    im_block = False
    for nr, zeile in enumerate(text.splitlines(), 1):
        roh = zeile
        if im_block:
            if "*/" in zeile:
                im_block = False
                zeile = zeile.split("*/", 1)[1]
            else:
                continue
        while "/*" in zeile:
            vor, rest = zeile.split("/*", 1)
            if "*/" in rest:
                zeile = vor + rest.split("*/", 1)[1]
            else:
                zeile = vor
                im_block = True
                break
        if zeile.lstrip().startswith(("#", "//", "<!--")):
            continue
        # Bewusste Abweichung, die BENANNT ist (die Sprechblasen-Spitze etwa ist Form, nicht
        # Radius-Achse). Ohne diesen Weg würde der Test entweder lügen oder ignoriert werden.
        if "achse-ausnahme:" in roh:
            continue
        yield nr, zeile


verstoesse: list[str] = []
for pfad in dateien():
    rel = pfad.relative_to(ROOT)
    for nr, zeile in ohne_kommentare(pfad.read_text(encoding="utf-8")):
        for achse, muster, warum in VERBOTEN:
            if re.search(muster, zeile):
                verstoesse.append(f"{rel}:{nr} [{achse}] {warum}")
        if PALETTE.search(zeile):
            verstoesse.append(f"{rel}:{nr} [farbe] Paletten-Klasse statt Rollen-Token")
r.check(f"kein Markup umgeht eine Achse ({len(dateien())} Dateien)",
        not verstoesse, " | ".join(verstoesse[:6]))

# ── B2: die Ausnahme text-[11px] ist EINE Regel, keine 219 Kopien ─────────────
# CLAUDE.md erlaubt genau diesen Literalwert für Beispiel-Labels. Erlaubt heisst nicht kopiert:
# steht er im Markup, ist er 219 Gelegenheiten, ihn uneinheitlich zu machen.
kopien = sum(z.count("text-[11px]")
             for p in dateien()
             for _, z in ohne_kommentare(p.read_text(encoding="utf-8")))
r.check("text-[11px] steht nicht im Markup (Kanon-Klasse statt Kopien)", kopien == 0,
        f"{kopien} Kopien — gehört als Regel nach components.css")

# ── C: kein Bedienelement ohne Draht ──────────────────────────────────────────
# Der Generator verdrahtet seine Regler über `data-`Attribute. Spricht das Skript ein Attribut
# an, das im erzeugten Markup nicht vorkommt, ist der Regler ein Knopf, der nichts tut — und
# genau diese Fehlerklasse hatten wir in dieser Runde zweimal (unsichtbarer Zustand, Achse ohne
# Token). Die Gegenrichtung zählt ebenso: ein `data-achse` im Markup, das kein Token der
# Register-Liste nennt, dreht an nichts.
generator_py = (ROOT / "gallery" / "generator.py").read_text(encoding="utf-8")
angesprochen = set(re.findall(r"\[data-([a-z-]+)[\]=]", generator_py))
# Die Attribute stehen im Python-Quelltext, aus dem das Markup entsteht — dieselbe Datei,
# beide Seiten: was `querySelectorAll` sucht, muss ein `_regler`/`inhalt` auch schreiben.
geschrieben = set(re.findall(r"data-([a-z-]+)=", generator_py)) | set(
    re.findall(r"\bdata-([a-z-]+)\b(?=[ >])", generator_py))
ohne_draht = sorted(a for a in angesprochen if a not in geschrieben)
r.check(f"kein Bedienelement ohne Draht ({len(angesprochen)} Attribute)",
        not ohne_draht, ", ".join(ohne_draht))

tokens_im_generator = set(re.findall(r'data-achse="(--[a-z0-9-]+)"', generator_py)) | set(
    re.findall(r'\("(--[a-z0-9-]+)",', generator_py))
unbekannt = sorted(t for t in tokens_im_generator if t not in axes.ALLE_TOKENS)
r.check(f"jeder Regler dreht an einer registrierten Achse ({len(tokens_im_generator)} Regler)",
        not unbekannt, ", ".join(unbekannt))


# ── D: Layout-Packs (ADR-2) ───────────────────────────────────────────────────
# Ein Pack darf die FORM von Bausteinen ändern — über deren Form-Tokens und, für den Rest, über Regeln, die an einem
# Baustein hängen. Damit daraus kein zweites Block-CSS mit eigenem Aussehen wird, gelten vier Grenzen:
#   D1  ausserhalb eines Layers nur Custom Properties (Tokens), keine Regeln;
#   D2  jede Regel liegt in @layer components (Utilities gewinnen weiter) und beginnt an einem Baustein aus
#       `@c22-layout:` — eine Klasse, die components.css definiert; keine eigene Klasse;
#   D3  jedes Baustein-Token (`--<baustein>-…`), das ein Pack setzt, hat in components.css eine Vorgabe (sonst
#       ein Regler ohne Leser);
#   D4  jedes Form-Token, das components.css an einem Baustein vorgibt, wird dort auch gelesen.
KOMPONENTEN_CSS = (CSS / "components.css").read_text(encoding="utf-8")
VENDOR_CSS = (ROOT / "c22" / "vendor" / "basecoat" / "dist" / "basecoat-components.css").read_text(encoding="utf-8")
KANON_KLASSEN = {k for t in (KOMPONENTEN_CSS, VENDOR_CSS)
                 for k in re.findall(r"\.([a-z][a-z0-9-]*)", re.sub(r"/\*.*?\*/", "", t, flags=re.S))}
DEFINIERTE_KLASSEN = set(re.findall(r"\.([a-z][a-z0-9-]*)", re.sub(r"/\*.*?\*/", "", KOMPONENTEN_CSS, flags=re.S)))


def bausteine_des_packs(text: str) -> list[str]:
    m = re.search(r"@c22-layout:\s*([a-z0-9, -]+)", text)
    return [b for b in re.split(r"[,\s]+", m.group(1).strip()) if b] if m else []


def regelbloecke(text: str) -> list[tuple[str, str, bool]]:
    """(Selektor, Rumpf, in_layer_components) für jede Regel; @layer components { … } wird aufgelöst."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    aus: list[tuple[str, str, bool]] = []
    pos = 0
    tiefe_layer = None
    stapel: list[str] = []
    kopf = ""
    rumpf_start = 0
    while pos < len(text):
        z = text[pos]
        if z == "{":
            stapel.append(kopf.strip())
            rumpf_start = pos + 1
            kopf = ""
        elif z == "}":
            sel = stapel.pop() if stapel else ""
            if not sel.startswith("@"):
                im_layer = any(s.startswith("@layer components") for s in stapel)
                aus.append((sel, text[rumpf_start:pos], im_layer))
            kopf = ""
        elif z == ";" and not stapel:
            kopf = ""
        else:
            kopf += z
        pos += 1
    return aus


def selektoren_einzeln(sel: str) -> list[str]:
    """Eine Selektorliste an den Kommas der obersten Ebene teilen — `:is(a, button)` bleibt ganz."""
    aus, tiefe, teil = [], 0, ""
    for z in sel + ",":
        tiefe += z in "(["
        tiefe -= z in ")]"
        if z == "," and tiefe == 0:
            aus.append(" ".join(teil.split()))
            teil = ""
        else:
            teil += z
    return [a for a in aus if a]


def nur_tokens(rumpf: str) -> bool:
    deklarationen = [d.strip() for d in rumpf.split(";") if d.strip()]
    return all(d.startswith("--") for d in deklarationen)


layout_befunde: list[str] = []
layout_packs = 0
for pack in PACKS:
    datei = PACK_DIR / f"{pack}.css"
    if not datei.exists():
        continue
    text = datei.read_text(encoding="utf-8")
    bausteine = bausteine_des_packs(text)
    if bausteine:
        layout_packs += 1
    for b in bausteine:
        if b not in DEFINIERTE_KLASSEN:
            layout_befunde.append(f"{pack}: @c22-layout nennt .{b}, das components.css nicht definiert")
    for sel, rumpf, im_layer in regelbloecke(text):
        if not im_layer:
            if not nur_tokens(rumpf):
                layout_befunde.append(f"{pack}: `{sel}` ausserhalb von @layer components setzt mehr als Tokens")
            continue
        for einzel in selektoren_einzeln(sel):
            m = re.match(r"\.([a-z][a-z0-9-]*)", einzel)
            wurzel = m.group(1) if m else ""
            if not any(wurzel == b or wurzel.startswith(b + "-") for b in bausteine):
                layout_befunde.append(f"{pack}: `{einzel}` beginnt nicht an einem Baustein aus @c22-layout")
            for klasse in re.findall(r"\.([a-z][a-z0-9-]*)", einzel):
                if klasse not in KANON_KLASSEN:
                    layout_befunde.append(f"{pack}: `.{klasse}` ist keine Klasse von C22")
    for token in sorted(gesetzte_tokens(text)):
        if any(token.startswith(f"--{b}-") for b in bausteine) and not re.search(
                rf"^\s*{re.escape(token)}\s*:", KOMPONENTEN_CSS, re.M):
            layout_befunde.append(f"{pack}: {token} hat in components.css keine Vorgabe (Regler ohne Leser)")
r.check(f"Layout-Packs halten ihre Grenzen ({layout_packs} Layout-Pack(s))", not layout_befunde,
        " | ".join(layout_befunde[:6]))

# D4: die Gegenrichtung — ein Form-Token, das components.css vorgibt, muss dort auch gelesen werden.
# Gelesen heisst: per var() in components.css oder vom Verhalten in c22.js (die Grenzen von nav3 misst das Skript).
C22_JS = (ROOT / "c22" / "static" / "js" / "c22.js").read_text(encoding="utf-8")
vorgaben = set(re.findall(r"^\s*(--workspace-[a-z0-9-]+)\s*:", KOMPONENTEN_CSS, re.M))
ungelesen = sorted(t for t in vorgaben if f"var({t})" not in KOMPONENTEN_CSS and f"var({t}," not in KOMPONENTEN_CSS
                   and f"'{t}'" not in C22_JS)
r.check(f"jedes Form-Token eines Bausteins wird gelesen ({len(vorgaben)} Tokens)", not ungelesen, ", ".join(ungelesen))

sys.exit(r.done())
