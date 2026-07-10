<p align="center">
  <img src="docs/logo.png" alt="" width="120">
</p>
<h1 align="center">C22</h1>
<p align="center"><em><a href="README.md">English version</a></em></p>

C22 ist eine wiederverwendbare, framework-neutrale Layout- und Design-Bibliothek. Ihr Kern
ist reines CSS (Design-Tokens, Layout-Primitives, Seitengerüste, native Popover) und etwas
JavaScript — aus jedem Stack nutzbar. Darüber liegt eine **optionale** Jinja-Makro-Schicht
für Python/Jinja-Anwendungen. Ziel ist, eine Seite oder ein Dashboard einmal zu bauen und
nicht immer wieder dieselben Layout-Probleme zu lösen — Overflow, Abstände, Kontrast,
Responsive-Brüche.

## Was es ist

- **Ein neutraler Kern:** `c22/static/css` und `c22/static/js`. Keine Abhängigkeit von
  einem Framework, kein CDN und kein Tracker zur Laufzeit. Jede Anwendung — statisch, PHP,
  Node, Python — kann diese Dateien einbinden.
- **Eine optionale Jinja-Schicht:** `c22/macros` enthält Seitengerüst- und
  Komponenten-Makros für Apps, die schon mit Jinja rendern. Niemand muss sie nutzen.
- **Theming über Tokens:** Designs unterscheiden sich durch CSS Custom Properties, sodass
  mehrere Sites einen Kern teilen und trotzdem völlig verschieden aussehen.

## Status

Früh. Dies ist das Repo-Gerüst — gehärtete CI, geteilte Hygiene-Basis, Paketstruktur und
die Helfer `static_path()` / `macros_path()`. **Die Design-Assets selbst fehlen noch;** sie
folgen, sobald das Layout-Fundament steht. Nicht für den Produktiveinsatz verlassen.

## Verwendung

Python/Jinja-Apps installieren das Paket und mounten die Assets:

```python
from c22 import static_path
from fastapi.staticfiles import StaticFiles
app.mount("/c22", StaticFiles(directory=static_path()), name="c22")
```

Andere Stacks nehmen die Dateien direkt aus `c22/static/` (oder aus einem Release-Tarball)
— ohne Python.

## Entwicklung

```bash
git config core.hooksPath .githooks   # einmalig pro Klon
./scripts/check.sh                     # Tests + Hygiene, vor jedem Push
```

Die Suite ist bewusst wiederholbar: zweimal laufen, beide grün. Siehe
[CONTRIBUTING](CONTRIBUTING.de.md).

## Lizenz

MIT — siehe [LICENSE](LICENSE).

---

<sub>Logo: <a href="https://www.flaticon.com/free-icons/cultures" title="cultures icons">Cultures icons created by Iconjam - Flaticon</a></sub>
