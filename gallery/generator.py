#!/usr/bin/env python3
"""Der Generator (`generator.html`) — zwei Reiter: **Design** und **Typeset**.

Vorbild sind `ui.shadcn.com/create` (Achsen links, echte Seite als Vorschau, „Get Code") und
`ui.shadcn.com/typeset` (Measure · Heading · Body · Mono · Size · Leading · Flow, Musterartikel
als Vorschau, fertiger CSS-Block als Ausgabe). Beides hier in C22-Bauteilen nachgebaut, mit einem
Unterschied, der uns wichtig ist: **die Bedienelemente kommen aus dem Achsen-Register**
(`c22/axes.py`), und die Ausgabe ist genau das Format, in dem C22 seine Packs pflegt
(`c22/static/css/packs/<name>.css`). Was hier herausfällt, kann man unverändert einchecken.

Warum das jetzt überhaupt funktioniert: alle Achsen sind Laufzeit-Tokens, und `tests/test_axes.py`
hält fest, dass kein Bauteil sie umgeht. Ein Regler muss deshalb nur eine CSS-Variable setzen —
die ganze Vorschau folgt. Vorher hätte derselbe Regler die Hälfte der Fläche nicht erreicht.

Die Vorschau ist **kein Sonderbau**: Design zeigt den Dashboard-Block, Typeset den
Prosa-Musterartikel — dieselben Dateien, die die Galerie zeigt.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from i18n import zwei

ROOT = Path(__file__).resolve().parent.parent

# ── Was der Generator dreht ───────────────────────────────────────────────────
# (token, Beschriftung de, Beschriftung en, Art, Konfiguration)
#   art "schieber": min, max, schritt, einheit
#   art "auswahl":  Optionen [(wert, label de, label en)]
#   art "farbe":    Farbfeld (setzt den Token als hex — im Export als Kommentar vermerkt)
SCHIEBER = "schieber"
AUSWAHL = "auswahl"
FARBE = "farbe"

DESIGN_ACHSEN = [
    ("--radius", "Rundung", "Rounding", SCHIEBER, dict(min=0, max=2, schritt=0.0625, einheit="rem")),
    ("--spacing", "Dichte", "Density", SCHIEBER, dict(min=0.2, max=0.32, schritt=0.005, einheit="rem")),
    ("--text-scale", "Schriftgröße", "Text size", SCHIEBER, dict(min=0.85, max=1.2, schritt=0.01, einheit="")),
    ("--icon-stroke", "Strichstärke", "Icon stroke", SCHIEBER, dict(min=1, max=3, schritt=0.25, einheit="")),
    ("--default-transition-duration", "Tempo", "Motion", SCHIEBER,
     dict(min=0, max=400, schritt=10, einheit="ms")),
    ("--font-weight-heading", "Überschrift-Fettung", "Heading weight", AUSWAHL,
     dict(optionen=[("400", "Normal", "Regular"), ("500", "Mittel", "Medium"),
                    ("600", "Halbfett", "Semibold"), ("700", "Fett", "Bold"),
                    ("800", "Extrafett", "Extrabold")])),
    ("--primary", "Akzent", "Accent", AUSWAHL, dict(optionen="AKZENTE")),
    ("--background", "Grundton", "Base tone", AUSWAHL, dict(optionen="GRUNDTOENE")),
]

TYPESET_ACHSEN = [
    ("--measure", "Zeilenlänge", "Measure", SCHIEBER, dict(min=40, max=100, schritt=1, einheit="ch")),
    ("--font-heading", "Überschrift-Schrift", "Heading font", AUSWAHL, dict(optionen=[])),
    ("--font-sans", "Fließtext-Schrift", "Body font", AUSWAHL, dict(optionen=[])),
    ("--font-mono", "Monospace", "Mono", AUSWAHL, dict(optionen=[])),
    ("--text-scale", "Schriftgröße", "Size", SCHIEBER, dict(min=0.85, max=1.25, schritt=0.01, einheit="")),
    ("--leading-body", "Zeilenhöhe", "Leading", SCHIEBER, dict(min=1.3, max=2.1, schritt=0.05, einheit="")),
    ("--flow", "Absatzabstand", "Flow", SCHIEBER, dict(min=0.6, max=2.2, schritt=0.05, einheit="em")),
    ("--tracking-heading", "Laufweite", "Tracking", SCHIEBER,
     dict(min=-0.05, max=0.12, schritt=0.005, einheit="em")),
    ("--font-weight-heading", "Überschrift-Fettung", "Heading weight", AUSWAHL,
     dict(optionen=[("400", "Normal", "Regular"), ("500", "Mittel", "Medium"),
                    ("600", "Halbfett", "Semibold"), ("700", "Fett", "Bold"),
                    ("800", "Extrafett", "Extrabold")])),
    ("--foreground", "Textfarbe", "Text colour", AUSWAHL, dict(optionen="TEXTFARBEN")),
]

# Schriftstapel zur Auswahl. Eingebettet ist nur Inter (tokens.css); alles andere sind
# System-Stapel — kein CDN, keine fremde Schrift nachladen (das ist Teil der Hausordnung).
SCHRIFTEN = [
    ('"Inter", ui-sans-serif, system-ui, sans-serif', "Inter (eingebettet)", "Inter (embedded)"),
    ("ui-sans-serif, system-ui, -apple-system, sans-serif", "System-Sans", "System sans"),
    ("ui-serif, Georgia, Cambria, serif", "System-Serif", "System serif"),
    ("ui-monospace, SFMono-Regular, Menlo, monospace", "System-Mono", "System mono"),
    ("ui-rounded, 'Nunito', system-ui, sans-serif", "Rund", "Rounded"),
]

# Farb-Achsen als benannte Sätze — wie „Base Color: Neutral" beim Vorbild. Kein Farbfeld:
# ein `<input type=color>` kennt nur Hex, das Repo schreibt oklch, und die Rückrechnung wäre eine
# zweite Wahrheit über denselben Wert. Werte = Tailwind-v4-Stufen in oklch.
AKZENTE = [
    ("oklch(0.205 0 0)", "Neutral (Standard)", "Neutral (default)"),
    ("oklch(0.546 0.245 262.881)", "Blau", "Blue"),
    ("oklch(0.596 0.145 163.225)", "Grün", "Green"),
    ("oklch(0.606 0.250 292.717)", "Violett", "Violet"),
    ("oklch(0.646 0.222 41.116)", "Orange", "Orange"),
    ("oklch(0.586 0.253 17.585)", "Rot", "Red"),
]
GRUNDTOENE = [
    ("oklch(1 0 0)", "Weiß (Standard)", "White (default)"),
    ("oklch(0.985 0 0)", "Sehr hell", "Very light"),
    ("oklch(0.97 0 0)", "Hellgrau", "Light grey"),
    ("oklch(0.985 0.002 106.423)", "Warm", "Warm"),
    ("oklch(0.984 0.003 247.858)", "Kühl", "Cool"),
]
TEXTFARBEN = [
    ("oklch(0.145 0 0)", "Fast schwarz (Standard)", "Near black (default)"),
    ("oklch(0.205 0 0)", "Weicher", "Softer"),
    ("oklch(0.269 0 0)", "Grau", "Grey"),
    ("oklch(0.216 0.006 56.043)", "Warmes Schwarz", "Warm black"),
]
SATZE = {"AKZENTE": AKZENTE, "GRUNDTOENE": GRUNDTOENE, "TEXTFARBEN": TEXTFARBEN}

# Achsen, deren Wert nur in EINEM Erscheinungsbild gilt. Alles andere (Radius, Dichte, Tempo …)
# ist bildunabhängig und gehört in `:root`.
FARB_TOKENS = {"--primary", "--background", "--foreground", "--card", "--popover", "--muted",
               "--accent", "--border", "--input", "--ring", "--sidebar", "--chart-1", "--chart-2",
               "--chart-3", "--chart-4", "--chart-5"}

def pack_voreinstellungen() -> list[tuple[str, str, str, dict[str, str]]]:
    """Die neun Style-Packs als Voreinstellungen — gelesen aus ihren eigenen Achsenschichten.

    Kein zweites Register: `c22/static/css/packs/<pack>.css` IST der Wertesatz des Packs. Wer dort
    eine Achse ändert, ändert damit die Voreinstellung im Generator mit. Gelesen wird nur der
    `:root`-Block (der `.dark`-Block gehört zum Erscheinungsbild, nicht zur Achse) und nur, was
    der Generator auch drehen kann.
    """
    drehbar = {t for t, *_ in DESIGN_ACHSEN} | {t for t, *_ in TYPESET_ACHSEN}
    basis = _basiswerte(drehbar)
    aus: list[tuple[str, str, str, dict[str, dict[str, str]]]] = []
    for datei in sorted((ROOT / "c22" / "static" / "css" / "packs").glob("*.css")):
        eigen = _bloecke(datei.read_text(encoding="utf-8"), drehbar)
        name = datei.stem
        # VOLLER Zustand: Basis + was das Pack überschreibt, und zwar JE ERSCHEINUNGSBILD.
        # Sonst blieben beim Wechsel Achsen des vorigen Packs stehen — und die Farben eines
        # Packs gelten nur in dem Bild, für das es sie nennt.
        aus.append((f"pack-{name}", name.capitalize(), name.capitalize(), {
            "root": {**basis["root"], **eigen["root"]},
            "dark": {**basis["dark"], **eigen["dark"]},
        }))
    return aus


def _bloecke(text: str, tokens: set[str]) -> dict[str, dict[str, str]]:
    """Die interessanten Tokens getrennt nach `:root` (hell) und `.dark` (dunkel).

    Warum getrennt: eine Farbe gilt nur in einem Erscheinungsbild. Ein Generator, der
    `--background` global setzt, macht im Dunkelmodus die Seite hell — das war genau der Fehler.
    """
    aus = {"root": {}, "dark": {}}
    for schluessel, muster in (("root", r":root\s*\{(.*?)\n\}"), ("dark", r"\.dark\s*\{(.*?)\n\}")):
        for block in re.findall(muster, text, re.S):
            for token, wert in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block):
                if token in tokens:
                    aus[schluessel][token] = wert.strip()
    return aus


def _basiswerte(tokens: set[str]) -> dict[str, dict[str, str]]:
    """Ausgangswerte der Achsen — aus Basecoats `base.css` und `tokens.css`, beide Bilder."""
    aus = {"root": {}, "dark": {}}
    for datei in (ROOT / "c22" / "vendor" / "basecoat" / "dist" / "base" / "base.css",
                  ROOT / "c22" / "static" / "css" / "tokens.css"):
        teil = _bloecke(datei.read_text(encoding="utf-8"), tokens)
        aus["root"].update(teil["root"])
        aus["dark"].update(teil["dark"])
    return aus


# Voreinstellungen (wie die 01–05 bei shadcn): Sätze, die zusammen etwas ergeben.
CHARAKTERE = [
    ("vega", "Standard", "Default", {}),
    ("kantig", "Kantig", "Sharp",
     {"--radius": "0rem", "--icon-stroke": "2.25", "--default-transition-duration": "100ms",
      "--font-weight-heading": "700", "--tracking-heading": "0em"}),
    ("weich", "Weich", "Soft",
     {"--radius": "1.5rem", "--spacing": "0.275rem", "--icon-stroke": "1.5",
      "--default-transition-duration": "260ms", "--font-weight-heading": "500"}),
    ("dicht", "Dicht", "Dense",
     {"--radius": "0.375rem", "--spacing": "0.215rem", "--text-scale": "0.94",
      "--default-transition-duration": "120ms"}),
    ("lesbar", "Lesbar", "Readable",
     {"--measure": "62ch", "--leading-body": "1.9", "--flow": "1.5em", "--text-scale": "1.06"}),
]

# Was die Leiste anbietet: erst die Charakter-Sätze, dann jedes Pack mit SEINEN Achsenwerten.
def _als_bloecke(satz: dict[str, str]) -> dict[str, dict[str, str]]:
    """Ein Charakter-Satz betrifft nur FORM-Achsen — die gelten in beiden Erscheinungsbildern."""
    return {"root": dict(satz), "dark": {}}


# Was die Leiste anbietet: erst die Charakter-Sätze, dann jedes Pack mit SEINEN Achsenwerten.
VOREINSTELLUNGEN = [(k, de, en, _als_bloecke(w)) for k, de, en, w in CHARAKTERE] \
    + pack_voreinstellungen()


def _block(datei: Path) -> str:
    """Ein bestehendes Partial als Vorschau einbetten — keine zweite Wahrheit.

    Die HTML-Kommentare der Partials sind MEHRZEILIG (Herkunftsnotizen); zeilenweise filtern
    liesse ihre Fortsetzung als Text in der Seite stehen. Ebenso weg: die Beispiel-Hülle
    (`c22-examples` + Beschriftungen) — hier ist der Block der Inhalt, nicht ein Exemplar.
    """
    text = re.sub(r"<!--.*?-->", "", datei.read_text(encoding="utf-8"), flags=re.S)
    text = re.sub(r'<span class="c22-example-label">.*?</span>', "", text, flags=re.S)
    return text.strip()


def _regler(token: str, de: str, en: str, art: str, cfg: dict) -> str:
    """Eine Zeile der Achsen-Leiste: Beschriftung, aktueller Wert, Bedienelement."""
    kopf = (f'<div class="flex items-baseline justify-between gap-3">'
            f'<span class="text-xs font-medium">{zwei(html.escape(de), html.escape(en))}</span>'
            f'<output class="text-muted-foreground font-mono text-xs" data-wert="{token}"></output></div>')
    if art == SCHIEBER:
        bedien = (f'<input class="input" type="range" data-achse="{token}" '
                  f'data-einheit="{cfg["einheit"]}" min="{cfg["min"]}" max="{cfg["max"]}" '
                  f'step="{cfg["schritt"]}" aria-label="{html.escape(de)}">')
    elif art == AUSWAHL:
        optionen = cfg["optionen"]
        optionen = SATZE[optionen] if isinstance(optionen, str) else (optionen or SCHRIFTEN)
        bedien = ('<select class="select" data-achse="' + token + '">'
                  + "".join(f'<option value="{html.escape(w)}">{html.escape(l_de)}</option>'
                            for w, l_de, _ in optionen)
                  + "</select>")
    else:
        bedien = (f'<input class="input h-8 w-full" type="color" data-achse="{token}" '
                  f'aria-label="{html.escape(de)}">')
    return f'<div class="flex flex-col gap-1.5 border-b px-4 py-3 last:border-b-0">{kopf}{bedien}</div>'


def _leiste(achsen: list, titel_de: str, titel_en: str) -> str:
    return (
        '<aside class="bg-card w-72 shrink-0 self-start overflow-hidden rounded-xl border">'
        f'<header class="flex items-center justify-between border-b px-4 py-3">'
        f'<span class="text-sm font-semibold">{zwei(titel_de, titel_en)}</span>'
        f'<button type="button" class="btn" data-variant="ghost" data-size="sm" data-wuerfeln>'
        f'{zwei("Würfeln", "Shuffle")}</button></header>'
        + "".join(_regler(*a) for a in achsen)
        + '</aside>')


def inhalt() -> str:
    """Das `main`-Innere der Generator-Seite (beide Reiter)."""
    dashboard = _block(ROOT / "c22" / "blocks" / "full-page" / "dashboard.html")
    prosa = _block(ROOT / "c22" / "typeset" / "prose.html")

    # Kanonische Tabs-Component: `.tabs > nav[role=tablist]` + Panels. Das Umschalten macht
    # basecoat.all.min.js von selbst — eigenes Reiter-JS wäre eine zweite Mechanik für dasselbe.
    reiter_nav = (
        '<nav role="tablist">'
        '<button type="button" role="tab" id="gen-t-design" aria-controls="gen-design" '
        'aria-selected="true" tabindex="0">' + zwei("Design", "Design") + '</button>'
        '<button type="button" role="tab" id="gen-t-typeset" aria-controls="gen-typeset" '
        'aria-selected="false" tabindex="-1">' + zwei("Typografie", "Typography") + '</button>'
        '</nav>')

    ausgabe = (
        '<section class="bg-card flex w-80 shrink-0 flex-col gap-3 self-start rounded-xl border p-4">'
        '<div class="flex items-center justify-between gap-2">'
        f'<h2 class="text-sm font-semibold">{zwei("Ergebnis", "Result")}</h2>'
        f'<button type="button" class="btn" data-variant="outline" data-size="sm" data-kopieren>'
        f'{zwei("Kopieren", "Copy")}</button></div>'
        f'<p class="text-muted-foreground text-xs leading-5">{zwei(
            "Das ist genau das Format einer C22-Achsenschicht — als "
            "<code class=\'code-inline\'>packs/mein-pack.css</code> ablegen, im Build-Skript "
            "eintragen, fertig.",
            "This is exactly the format of a C22 axis layer — save it as "
            "<code class=\'code-inline\'>packs/my-pack.css</code>, add it to the build script, done.")}</p>'
        '<pre class="code-block max-h-[420px] overflow-auto"><code data-ausgabe></code></pre>'
        f'<p class="text-muted-foreground text-xs">{zwei(
            "Farben stehen als benannte oklch-Werte zur Wahl — dasselbe Format, das im Repo steht.",
            "Colours are named oklch values — the same format the repository uses.")}</p>'
        '</section>')

    def gruppe(saetze, beschriftung, erstes_aktiv):
        return (
            f'<div class="button-group" role="radiogroup" aria-label="{html.escape(beschriftung)}">'
            + "".join(
                f'<button type="button" class="btn" data-variant="outline" data-size="sm" role="radio" '
                f'aria-checked="{"true" if (erstes_aktiv and i == 0) else "false"}" '
                f'data-voreinstellung="{k}">{zwei(html.escape(de), html.escape(en))}</button>'
                for i, (k, de, en, _) in enumerate(saetze))
            + '</div>')

    voreinstellungen = (
        '<div class="flex flex-wrap items-center gap-x-6 gap-y-2">'
        f'<span class="text-muted-foreground text-xs">{zwei("Charakter", "Character")}</span>'
        + gruppe(CHARAKTERE, "Charakter", True)
        + f'<span class="text-muted-foreground text-xs">{zwei("Pack", "Pack")}</span>'
        + gruppe(pack_voreinstellungen(), "Pack", False)
        + '</div>')

    return f"""
<div class="mx-auto flex w-[1500px] max-w-full flex-col gap-6">
  <header class="flex flex-col gap-3">
    <h1 class="text-3xl font-bold tracking-tight">{zwei("Generator", "Generator")}</h1>
    <p class="text-muted-foreground max-w-3xl leading-7">{zwei(
        "Jede Achse als Regler, die Vorschau daneben ist eine echte Seite aus der Galerie. "
        "Weil jede Component ausschließlich Tokens liest, wirkt jede Änderung überall — auch "
        "dort, wo ein Style-Pack allein nicht hinkäme.",
        "Every axis as a control; the preview beside it is a real page from the gallery. Because "
        "every component reads nothing but tokens, each change applies everywhere — including "
        "where a style pack alone would not reach.")}</p>
    <div>{voreinstellungen}</div>
  </header>

  <div class="tabs w-full" id="gen-tabs">
    {reiter_nav}

    <div role="tabpanel" id="gen-design" aria-labelledby="gen-t-design" tabindex="-1"
         class="flex flex-wrap gap-6 pt-6">
      {_leiste(DESIGN_ACHSEN, "Achsen", "Axes")}
      <div class="min-w-0 flex-1 overflow-hidden rounded-xl border p-4">{dashboard}</div>
      {ausgabe}
    </div>

    <div role="tabpanel" id="gen-typeset" aria-labelledby="gen-t-typeset" tabindex="-1" hidden
         class="flex flex-wrap gap-6 pt-6">
      {_leiste(TYPESET_ACHSEN, "Typografie", "Typography")}
      <div class="min-w-0 flex-1 rounded-xl border p-6">{prosa}</div>
      {ausgabe}
    </div>
  </div>
</div>

<script>
(function () {{
  var VOREINSTELLUNGEN = {json.dumps({k: v for k, _, _, v in VOREINSTELLUNGEN}, ensure_ascii=False)};
  var FARB_ACHSEN = {json.dumps(sorted(FARB_TOKENS), ensure_ascii=False)};
  var wurzel = document.documentElement;
  // Zwei Blöcke statt Inline-Styles am <html>: eine FARBE gilt nur in ihrem Erscheinungsbild.
  // Ein Inline-Style am Wurzelelement schlägt `.dark` immer — damit wurde die Seite im
  // Dunkelmodus hell, sobald ein Pack-Preset seine Light-Farben setzte. Form-Achsen (Radius,
  // Dichte, Tempo …) sind bildunabhängig und stehen deshalb in `:root`.
  var werte = {{ root: {{}}, dark: {{}} }};
  var blatt = document.createElement('style');
  blatt.id = 'c22-generator';
  document.head.appendChild(blatt);

  function dunkel() {{ return wurzel.classList.contains('dark'); }}
  function bereich(token) {{
    return FARB_ACHSEN.indexOf(token) >= 0 ? (dunkel() ? 'dark' : 'root') : 'root';
  }}

  function einheit(el) {{ return el.dataset.einheit || ''; }}

  function anzeigen(token, wert) {{
    document.querySelectorAll('[data-wert="' + token + '"]').forEach(function (o) {{
      o.textContent = wert;
    }});
  }}

  function setzen(token, wert) {{
    if (wert === null || wert === undefined || String(wert).trim() === '') return;  // nie leer
    werte[bereich(token)][token] = wert;
    anzeigen(token, wert);
    ausgeben();
  }}

  function block(auswahl, satz) {{
    var namen = Object.keys(satz).sort();
    if (!namen.length) return '';
    return auswahl + ' {{\\n'
      + namen.map(function (t) {{ return '  ' + t + ': ' + satz[t] + ';'; }}).join('\\n')
      + '\\n}}\\n';
  }}

  function ausgeben() {{
    var css = block(':root', werte.root) + block('.dark', werte.dark);
    // Dasselbe CSS wirkt in der Vorschau UND steht als Ergebnis da — eine Quelle, kein
    // zweiter Weg, der abweichen könnte.
    blatt.textContent = css;
    var text = css
      ? '/* C22-Achsenschicht — vom Generator erzeugt */\\n' + css
      : '/* Noch nichts geändert. */\\n';
    document.querySelectorAll('[data-ausgabe]').forEach(function (c) {{ c.textContent = text; }});
  }}

  // Ausgangswerte aus dem AKTUELLEN Pack lesen, damit die Regler dort stehen, wo die Seite steht.
  function stand(token) {{
    return getComputedStyle(wurzel).getPropertyValue(token).trim();
  }}

  document.querySelectorAll('[data-achse]').forEach(function (el) {{
    var token = el.dataset.achse;
    var jetzt = stand(token);
    if (el.type === 'range') {{
      var zahl = parseFloat(jetzt);
      if (!isNaN(zahl)) el.value = zahl;
      anzeigen(token, el.value + einheit(el));
      el.addEventListener('input', function () {{ setzen(token, el.value + einheit(el)); }});
    }} else if (el.tagName === 'SELECT') {{
      if (jetzt) {{
        for (var i = 0; i < el.options.length; i++) {{
          if (el.options[i].value.replace(/\\s+/g, '') === jetzt.replace(/\\s+/g, '')) {{ el.selectedIndex = i; break; }}
        }}
      }}
      anzeigen(token, el.options[el.selectedIndex] ? el.options[el.selectedIndex].textContent : '');
      el.addEventListener('change', function () {{
        setzen(token, el.value);
        anzeigen(token, el.options[el.selectedIndex].textContent);
      }});
    }} else {{
      // Farbfeld: oklch() kann ein <input type=color> nicht anzeigen — deshalb rechnet der
      // Browser den aktuellen Wert für uns um (Canvas-freier Weg über eine Hilfsfläche).
      var probe = document.createElement('span');
      probe.style.color = jetzt || '#000000';
      document.body.appendChild(probe);
      var rgb = getComputedStyle(probe).color.match(/\\d+/g);
      probe.remove();
      if (rgb) {{
        el.value = '#' + rgb.slice(0, 3).map(function (n) {{
          return ('0' + parseInt(n, 10).toString(16)).slice(-2);
        }}).join('');
      }}
      anzeigen(token, el.value);
      el.addEventListener('input', function () {{ setzen(token, el.value); }});
    }}
  }});

  // Das Umschalten der Reiter macht die Tabs-Component selbst (basecoat.all.min.js).

  // Voreinstellungen + Würfeln
  // Ein Wert wird IMMER über das Bedienelement gesetzt und dann als `input`-Ereignis gemeldet.
  // Grund: die gefüllte Spur eines Schiebers rechnet Basecoats JS aus `--slider-value` — es
  // hört auf `input`. Wer `el.value` still zuweist, verschiebt den Griff und lässt die Füllung
  // stehen. Zwei Pfade (manuell/programmatisch) wären zwei Gelegenheiten, das falsch zu machen.
  // Nur SCHIEBER müssen ihre Änderung melden: Basecoat rechnet daraus die gefüllte Spur.
  // Bei einem Auswahlfeld wäre das Meldung schädlich — steht der Wert nicht in seinen Optionen,
  // setzt der Browser `value` auf LEER, das change-Ereignis schreibt diesen leeren Wert zurück,
  // und aus `--primary` wird `--primary: ;`. Genau so wurde die Pille im Dunkelmodus
  // unsichtbar (transparente Fläche) und `--font-heading` leer.
  function melden(el) {{
    if (el.type !== 'range') return;
    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
  }}

  function regler_stellen(el, wert) {{
    if (el.type === 'range') {{
      el.value = parseFloat(wert);
      melden(el);
      return el.value;
    }}
    // Auswahlfeld: nur stellen, wenn der Wert wirklich zur Wahl steht. Sonst bleibt die
    // Anzeige, wie sie ist — ein Feld, das den geltenden Wert nicht kennt, darf ihn nicht
    // überschreiben.
    for (var i = 0; i < el.options.length; i++) {{
      if (el.options[i].value.replace(/\s+/g, '') === String(wert).replace(/\s+/g, '')) {{
        el.selectedIndex = i;
        return el.options[i].textContent;
      }}
    }}
    return null;
  }}

  function anwenden(satz) {{
    // Ein Preset ersetzt den Zustand, es ergänzt ihn nicht: sonst blieben Achsen des vorigen
    // Packs stehen und man sähe eine Mischung, die es als Pack nie gibt.
    werte = {{ root: {{}}, dark: {{}} }};
    ['root', 'dark'].forEach(function (bereich_) {{
      var teil = satz[bereich_] || {{}};
      Object.keys(teil).forEach(function (t) {{ werte[bereich_][t] = teil[t]; }});
    }});
    ausgeben();
    // Die Regler auf den Stand des jeweils SICHTBAREN Erscheinungsbilds ziehen.
    document.querySelectorAll('[data-achse]').forEach(function (el) {{
      var t = el.dataset.achse;
      var wert = (werte[bereich(t)] || {{}})[t] || (werte.root || {{}})[t];
      if (!wert) return;
      var gezeigt = regler_stellen(el, wert);
      anzeigen(t, gezeigt === null ? wert : (el.type === 'range' ? gezeigt + einheit(el) : gezeigt));
    }});
  }}
  document.querySelectorAll('[data-voreinstellung]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      document.querySelectorAll('[data-voreinstellung]').forEach(function (x) {{
        x.setAttribute('aria-checked', x === b ? 'true' : 'false');
      }});
      anwenden(VOREINSTELLUNGEN[b.dataset.voreinstellung] || {{}});
    }});
  }});
  document.querySelectorAll('[data-wuerfeln]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      b.closest('aside').querySelectorAll('input[type=range]').forEach(function (el) {{
        var min = parseFloat(el.min), max = parseFloat(el.max), schritt = parseFloat(el.step) || 1;
        var stufen = Math.floor((max - min) / schritt);
        el.value = (min + Math.floor(Math.random() * (stufen + 1)) * schritt).toFixed(4);
        melden(el);
        setzen(el.dataset.achse, parseFloat(el.value) + einheit(el));
      }});
    }});
  }});

  // Kopieren
  document.querySelectorAll('[data-kopieren]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      var code = document.querySelector('[data-ausgabe]');
      if (!code) return;
      navigator.clipboard && navigator.clipboard.writeText(code.textContent);
    }});
  }});

  // Wechselt das Erscheinungsbild, gelten die Farbwerte des anderen Blocks — die Regler müssen
  // das zeigen, sonst behauptet die Leiste einen Wert, der gerade nicht wirkt.
  document.addEventListener('basecoat:themechange', function () {{
    document.querySelectorAll('[data-achse]').forEach(function (el) {{
      var t = el.dataset.achse;
      var wert = (werte[bereich(t)] || {{}})[t];
      if (!wert) return;
      var gezeigt = regler_stellen(el, wert);
      anzeigen(t, gezeigt === null ? wert : (el.type === 'range' ? gezeigt + einheit(el) : gezeigt));
    }});
  }});

  ausgeben();
}})();
</script>
"""
