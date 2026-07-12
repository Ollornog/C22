# C22 · Komponenten-Checkliste & Roadmap

Vollständigkeits-Abgleich gegen die BeerCSS-Komponentengalerie (deren Doku-Seiten als **Checkliste**,
nicht als Vorlage — Verhalten/Umfang übernehmen wir, **Stil + Engine bleiben C22**, nichts kopiert).
Quelle der Liste: `github.com/beercss/beercss/tree/main/docs` (Stand 2026-07-11).

## Abdeckung (BeerCSS → C22)

| BeerCSS | C22 | Status |
|---|---|---|
| Badge | `.badge` (+ok/warn/bad/info/dot) | ✅ |
| Button | `.btn` (accent/ghost/danger) + `.icon-btn` + State-Layer | ✅ |
| Card | `.card` (interactive/media/skeleton) | ✅ |
| Checkbox | `.choice` (Haken via stroke-dashoffset) | ✅ |
| Chip | `.chip` (assist/filter/outline/input+×) | ✅ (Batch 1) |
| Container/Grid/Layout | `primitives.css` (Every-Layout: center/stack/cluster/grid/sidebar/switcher) | ✅ |
| Dialog | `<dialog>` Confirm + Popup + Progress-Popup + Scrim | ✅ |
| Divider | `.divider` (+ vertical + `.divider-label`) | ✅ (Batch 1) |
| Expansion (Accordion) | `.accordion` (grid 0fr↔1fr, data-single) | ✅ |
| Icon | Phosphor-Subset + Gewicht-Achse | ✅ |
| Input | `.field`/`.input` (schwebendes Label, native Validierung) | ✅ |
| List | `.list`/`.list-item` (lead/body/trail) | ✅ (Batch 1) |
| Media | `.card-media` + `.media.r-16-9/…` (+ `figure`) | ✅ (Batch 3) |
| Menu | `<details>`-Dropdown **+ `.c22-menu`** (echtes `role=menu`, Roving/Typeahead) | ✅ (Batch 3) |
| Navigation | `.navbar`/`.sidenav`/`.breadcrumbs`/`.skip-link` | ✅ |
| Overlay (Scrim) | `#c22-popup-scrim` | ✅ |
| Page (Transitions) | — | ⏭️ übersprungen (nischig) |
| Progress | in Popup + `.spinner` + `progress.c22-progress` (linear, nativ) | ✅ (Batch 1) |
| Radio | `.choice.radio` | ✅ |
| Select | `.field-select`/`.select` (+ Caret) | ✅ |
| Shape (Radius) | Form-Achse `--radius-scale` (ein Wert → alles) | ✅ (stärker) |
| Slider | `.c22-range` (natives range gestylt, `.range-field`+output) | ✅ (Batch 2) |
| Snackbar (Toast) | `c22Toast` + Gruppierung + **Notification-Center** | ✅✅ (stärker) |
| Switch (Toggle) | `.toggle` (gleitende Pille) | ✅ |
| Table | `.table` (striped/hover/num/caption, `.table-wrap`) | ✅ (Batch 1) |
| Tabs | `.tabs` (Indikator) + `.tabs.reiter` (Chrome) | ✅ (2 Varianten) |
| Textarea | `.textarea.auto` (field-sizing) | ✅ |
| Tooltip | `.c22-tooltip` + **Popover** (placeFloating) | ✅ (+Popover) |
| Typography | Fluide Typo-Skala (clamp) | ✅ |

## C22-Extras (hat BeerCSS NICHT)
Notification-Center/Historie · 4 Look-Achsen (Theme/Größe/Form/Icon-Gewicht) · Banner (eigene Art) ·
Popover getrennt vom Tooltip · Custom-Scrollbars · Segmented-Switch (≠ Toggle) · SPOT-Kind-Registry ·
State-Layer-Utility · **Combobox/Autocomplete** (`.c22-combobox`, Virtual Focus — hat BeerCSS gar nicht) · **ARIA-Live-Announcer** · **Dual-Thumb-Slider**.

## Umsetzung

Alle oben gelisteten Komponenten sind gebaut und im **Musterbuch** (`examples/musterbuch.html`) versammelt.
Die komplexeren Interaktionsmuster — **Combobox/Autocomplete** (Virtual Focus), **ARIA-Menu**
(Roving-Tabindex/Typeahead), **Tabs** (Roving-Tabindex/Pfeiltasten), **Dual-Thumb-Slider**,
**ARIA-Live-Announcer** und das Validierungs-Timing über `:user-invalid` — folgen den
[WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/).
