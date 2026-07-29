#!/usr/bin/env python3
"""Startseite der Website (`index.html`) — was C22 ist, wo es hingeht, wer es betreibt.

Zweisprachig wie der Rest der Seite (`i18n.zwei`). Gebaut **aus C22-Components**: Karten,
Knöpfe, Plaketten — kein Sonderlayout und keine rohen Utility-Ketten für Dinge, für die es
eine Component gibt. Die Startseite ist damit selbst ein Beleg dafür, dass das System trägt.

Hier sitzen auch die Verweise, die vorher in jeder Kopfleiste standen: **GitHub** und
**Impressum**. Eine Leiste, die auf jeder Seite mitläuft, ist der falsche Ort für Angaben,
die man einmal im Leben anklickt.
"""
from __future__ import annotations

import html

from i18n import zwei

REPO = "https://github.com/Ollornog/C22"

# (Datei, Titel, Beschreibung de/en, Einheit de/en für die Anzahl)
# Die ANZAHL steht hier bewusst nicht: sie kommt beim Bauen aus dem, was wirklich da ist
# (`build.py` zählt die Einträge) — eine gepflegte Zahl im Text veraltet still.
EINSTIEGE: list[tuple[str, str, tuple[str, str], tuple[str, str]]] = [
    ("components.html", "Components",
     ("Jeder Baustein in allen Varianten — Knöpfe, Formulare, Menüs, Tabellen, Dialoge.",
      "Every building block in all its variants — buttons, forms, menus, tables, dialogs."),
     ("Components", "components")),
    ("blocks.html", "Blocks",
     ("Größere Kompositionen: App-Gerüst, Verwaltungsseite, Dashboard, Anmeldung, Tabellen.",
      "Larger compositions: app shell, admin page, dashboard, sign-in, tables."),
     ("Blocks", "blocks")),
    ("charts.html", "Charts",
     ("Diagramme allein auf den Tokens <code>--chart-1…5</code> — ohne Diagramm-Bibliothek.",
      "Charts built purely on the <code>--chart-1…5</code> tokens — no charting library."),
     ("Diagramm-Muster", "chart patterns")),
    ("typeset.html", "Typeset",
     ("Typografie im Zusammenhang: die komplette Text-Hierarchie einer echten Seite.",
      "Typography in context: the full text hierarchy of a real page."),
     ("Muster", "patterns")),
]

# Was C22 ausmacht — (Titel de/en, Text de/en)
MERKMALE: list[tuple[tuple[str, str], tuple[str, str]]] = [
    (("Kanonisches HTML", "Canonical HTML"),
     ("Kein React, kein Build-Zwang. Eine Component ist semantisches HTML mit "
      "Basecoat-Klassen — jeder Stack kopiert dasselbe Markup.",
      "No React, no build lock-in. A component is semantic HTML with Basecoat classes — "
      "every stack copies the same markup.")),
    (("Tokens statt Farbwerte", "Tokens, not colour values"),
     ("Farbe, Radius, Abstand und Schrift kommen aus CSS-Variablen. Ein Redesign heißt "
      "„andere Tokens“, nicht „jede App anfassen“.",
      "Colour, radius, spacing and type come from CSS variables. A redesign means "
      "“different tokens”, not “touch every app”.")),
    (("Neun Style-Packs", "Nine style packs"),
     ("Oben umschalten: derselbe Bausatz in neun Charakteren, hell und dunkel — "
      "und keine Component weiß davon.",
      "Switch above: the same kit in nine characters, light and dark — "
      "and no component knows about it.")),
    (("Mechanisch geprüft", "Mechanically checked"),
     ("Eine Testsuite verbietet Hex-Farben, willkürliche Größen und erfundene Varianten. "
      "Die Regeln hängen nicht am Vorsatz.",
      "A test suite forbids hex colours, arbitrary sizes and invented variants. "
      "The rules don't rely on good intentions.")),
]

CODE = ('class="code-inline"')

ICON_ARROW = ('<svg data-icon-lu="arrow-right" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
              'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>')
ICON_GITHUB = ('<svg data-icon-lu="github" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
               'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
               'stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5'
               '.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0'
               'C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5'
               '-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/>'
               '<path d="M9 18c-4.51 2-5-2-7-2"/></svg>')


def inhalt(anzahl: dict[str, int] | None = None, assets: str = "../") -> str:
    """Das `main`-Innere der Startseite. Kein Inhaltsverzeichnis — die Seite ist kurz.

    `anzahl` bildet Dateiname → Anzahl Einträge ab; der Generator kennt die echten Zahlen.
    Fehlt eine, bleibt die Plakette weg — lieber keine Zahl als eine falsche.

    `assets` ist dasselbe Präfix wie im Rumpf (lokal `../`, auf der Website leer) — die
    Startseite lädt das Logo aus `docs/`.
    """
    anzahl = anzahl or {}
    karten = "".join(
        f'<a href="{datei}" class="card hover:border-ring transition-colors">'
        f'<header><h3 class="flex items-center gap-2">{html.escape(titel)}'
        + (f'<span class="badge" data-variant="secondary">'
           f'{zwei(f"{anzahl[datei]} {html.escape(einheit_de)}", f"{anzahl[datei]} {html.escape(einheit_en)}")}'
           f'</span>' if datei in anzahl else "")
        + f'</h3><p>{zwei(beschr_de, beschr_en)}</p></header>'
        f'<footer><span class="btn" data-variant="ghost" data-size="sm">'
        f'{zwei("Ansehen", "Open")}{ICON_ARROW}</span></footer></a>'
        for datei, titel, (beschr_de, beschr_en), (einheit_de, einheit_en) in EINSTIEGE)

    merkmale = "".join(
        f'<div class="flex flex-col gap-1">'
        f'<h3 class="font-semibold tracking-tight">{zwei(html.escape(t_de), html.escape(t_en))}</h3>'
        f'<p class="text-muted-foreground text-sm leading-6">{zwei(x_de, x_en)}</p></div>'
        for (t_de, t_en), (x_de, x_en) in MERKMALE)

    return f"""
<div class="mx-auto flex w-[1100px] max-w-full flex-col gap-16 pb-20">

  <section class="flex flex-col items-center gap-5 pt-8 text-center">
    <span class="badge" data-variant="outline">{zwei("In Arbeit — Schnittstellen können sich ändern",
                                                     "Work in progress — interfaces may still change")}</span>
    <!-- Marke groß: das Logo trägt den Kopf, die Überschrift bleibt der Text daneben.
         `width`/`height` stehen mit dabei, damit beim Laden nichts springt; `alt=""`, weil
         die Überschrift direkt darunter dasselbe sagt. -->
    <img src="{assets}docs/logo.png" alt="" width="512" height="512" class="size-40 sm:size-48">
    <h1 class="scroll-m-20 text-5xl font-extrabold tracking-tight">C22</h1>
    <p class="text-muted-foreground max-w-2xl text-xl leading-8">{zwei(
        "Ein wiederverwendbares Design-System im shadcn-Look — als kanonisches HTML, "
        "semantische Klassen und Design-Tokens. Für jeden Stack, ohne React.",
        "A reusable design system in the shadcn look — canonical HTML, semantic classes "
        "and design tokens. For any stack, without React.")}</p>
    <div class="flex flex-wrap items-center justify-center gap-3">
      <a href="components.html" class="btn" data-variant="primary">
        {zwei("Galerie ansehen", "Browse the gallery")}{ICON_ARROW}</a>
      <a href="{REPO}" class="btn" data-variant="outline">{ICON_GITHUB}{zwei("Auf GitHub", "On GitHub")}</a>
    </div>
    <p class="text-muted-foreground text-sm">{zwei(
        f'MIT-Lizenz · Python 3.10+ · Basecoat + Tailwind CSS v4 · alles lokal, kein CDN',
        f'MIT licence · Python 3.10+ · Basecoat + Tailwind CSS v4 · everything local, no CDN')}</p>
  </section>

  <section class="grid gap-4 sm:grid-cols-2">{karten}</section>

  <section class="flex flex-col gap-6">
    <h2 class="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight">{zwei(
        "Wofür das gut ist", "What it is good for")}</h2>
    <div class="grid gap-6 sm:grid-cols-2">{merkmale}</div>
  </section>

  <section class="flex flex-col gap-4">
    <h2 class="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight">{zwei(
        "Einbinden", "Getting started")}</h2>
    <p class="leading-7">{zwei(
        f'Python-Apps installieren das Paket und binden die Beilagen ein; jeder andere Stack '
        f'kopiert das kompilierte Pack-CSS, <code {CODE}>c22.js</code> und das Markup der '
        f'Component. Wie ein Pack gebaut wird, steht im Repo.',
        f'Python apps install the package and mount the assets; any other stack copies the '
        f'compiled pack CSS, <code {CODE}>c22.js</code> and the component markup. How a pack '
        f'is built is documented in the repository.')}</p>
    <pre class="code-block w-full"><code>git clone {REPO}.git
cd C22
scripts/vendor-basecoat.sh     # Basecoat vendoren (gepinnte Version)
scripts/fetch-tailwind.sh      # Tailwind-CLI holen
scripts/build-gallery.sh       # Galerie + neun Pack-CSS bauen</code></pre>
  </section>

  <footer class="text-muted-foreground flex flex-wrap items-center gap-x-6 gap-y-2 border-t pt-6 text-sm">
    <span>© 2026 C22 contributors · {zwei("MIT-Lizenz", "MIT licence")}</span>
    <a href="{REPO}" class="hover:text-foreground underline-offset-4 hover:underline">GitHub</a>
    <a href="{REPO}/blob/main/CHANGELOG.md" class="hover:text-foreground underline-offset-4 hover:underline">Changelog</a>
    <a href="legal.html" class="hover:text-foreground underline-offset-4 hover:underline">{zwei(
        "Impressum &amp; Datenschutz", "Imprint &amp; privacy")}</a>
  </footer>
</div>
"""
