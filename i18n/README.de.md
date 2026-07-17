<p align="center"><img src="../docs/logo.png" alt="C22" width="250" height="250"></p>

<h1 align="center">C22</h1>

<p align="center"><a href="../README.md">English</a> · <b>Deutsch</b></p>

<p align="right">
<a href="https://github.com/Ollornog/C22/actions/workflows/ci.yml"><img src="https://github.com/Ollornog/C22/actions/workflows/ci.yml/badge.svg" alt="tests"></a>
<a href="../LICENSE"><img src="https://img.shields.io/badge/License-MIT-informational.svg" alt="License: MIT"></a>
<img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python">
</p>

> 🚧 **In Arbeit** — wird aktiv entwickelt; Schnittstellen und Struktur können sich vor einem stabilen `1.0`-Release noch ändern.

### Eine wiederverwendbare, framework-neutrale Design-Bibliothek im shadcn-Look.

C22 liefert shadcn-Optik als **kanonisches HTML + semantische Klassen + Design-Tokens** — kein React,
kein Build-Lock-in. Es bündelt [Basecoat](https://basecoatui.com/) (MIT) fest ein und kompiliert es mit
dem Tailwind-CSS-v4-Standalone-CLI, sodass jeder Stack dieselben Components nutzt. Ziel ist, eine Seite
oder ein Dashboard einmal zu bauen und nicht immer wieder dieselben Probleme zu lösen — Overflow,
Abstände, Kontrast, Responsive-Brüche — und die App-seitigen Adapter dünn zu halten: Ein Redesign heißt
„neue Tokens + Components, Galerie weiter grün", nicht jede App anfassen.

---

## Was es ist

- **Fest eingebundenes, gepinntes Upstream:** Basecoat liegt unter `c22/vendor/basecoat/`
  (reproduzierbar über `scripts/vendor-basecoat.sh`); das Tailwind-Binary wird geholt, nicht committet.
  Du besitzt den Code und baust ihn lokal — offline, kein CDN, keine Laufzeit-Abhängigkeit.
- **Tokens statt fester Werte:** Farbe, Radius, Abstände und Typografie kommen aus CSS Custom
  Properties (`c22/static/css/tokens.css`), sodass mehrere Sites einen Kern teilen und trotzdem völlig
  verschieden aussehen.
- **Eine Component-Galerie (die einzige Quelle der Wahrheit):** `gallery/build.py` rendert alle 65
  Components — jeden in seinen Varianten — aus kanonischen HTML-Partials in `c22/components/`. Sie
  verlinkt je Component die Basecoat- und shadcn-Quelldoku und schaltet zwischen acht Style-Packs sowie
  hell/dunkel um.
- **Engine-neutral, mit optionaler Jinja-Schicht:** Jeder Stack bindet das kompilierte CSS, das HTML
  der Partials und die minimale `c22.js`-Verhaltensschicht ein (die verdrahtet, was Basecoats JS nicht
  abdeckt, z.B. das Kontextmenü); `c22/macros` enthält optionale Seitengerüst-Makros für Python/Jinja-Apps.

## Status

In Arbeit. Alle 65 Components existieren mit ihren Varianten, aber Schnittstellen und Struktur können
sich vor einem stabilen `1.0` noch ändern. Noch nicht für den Produktiveinsatz verlassen.

## Verwendung

Python/Jinja-Apps installieren das Paket und mounten die Assets:

```python
from c22 import static_path
from fastapi.staticfiles import StaticFiles
app.mount("/c22", StaticFiles(directory=static_path()), name="c22")
```

Das Aussehen ist die geteilte Quelle der Wahrheit: Designfragen werden **in C22** gelöst (Tokens +
Components) und von den Apps übernommen — nicht je App hart codiert. Andere Stacks nehmen das HTML der
Partials und das kompilierte CSS direkt.

## Entwicklung

```bash
git config core.hooksPath .githooks   # einmalig pro Klon
./scripts/fetch-tailwind.sh           # Tailwind-v4-Standalone-CLI (gitignored)
./scripts/vendor-basecoat.sh          # vendored Basecoat pinnen/aktualisieren
./scripts/build-gallery.sh            # Galerie rendern + Pack-CSS kompilieren
./scripts/check.sh                    # Tests + Hygiene, vor jedem Push
```

Die kompilierten Pack-CSS und `gallery/index.html` sind Build-Outputs (gitignored) — lokal neu bauen.
Die Suite ist bewusst wiederholbar: zweimal laufen, beide grün. Siehe [CONTRIBUTING](CONTRIBUTING.de.md).

## Lizenz

MIT — siehe [LICENSE](../LICENSE).

## Credits

- UI-Primitive: [Basecoat](https://basecoatui.com/) (MIT), auf Tailwind CSS v4 aufbauend.
- Component-Referenzen: [shadcn/ui](https://ui.shadcn.com/).
- Beispielbilder: [Unsplash](https://unsplash.com/).
- Icon: <a href="https://www.flaticon.com/authors/iconjam" target="_blank" rel="noopener">Origami Bird PNG Image by Iconjam - flaticon.com</a>
