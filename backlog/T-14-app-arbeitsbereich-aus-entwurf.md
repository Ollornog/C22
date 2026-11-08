---
id: T-14
type: Task
title: Arbeitsbereich des freigegebenen UnderDoc-Entwurfs als App-Baustein
status: erledigt
milestone: M-2
tags: [bausteine, layout, underdoc]
created: 2026-11-08
---

# Arbeitsbereich des freigegebenen UnderDoc-Entwurfs als App-Baustein

## Befund

Der PO will UnderDocs Oberfläche genau wie den freigegebenen klickbaren Entwurf. UnderDoc fährt dafür das Markup und
Skript des Entwurfs (`demo.js`) mit dessen Stylesheet `demo.css` (die Farben schon auf C22-Tokens, die Maße in px). Der
Baustein `.workspace` aus T-13 trägt andere Klassen und andere Maße; das Stylesheet gehört nach C22, damit UnderDoc nur
C22 lädt.

## Fertig, wenn

- Das Aussehen liegt in C22 unter einer Wurzelklasse (`.c22-app-workspace`), die Klassen von `demo.js` bleiben, andere
  Apps ändern sich nicht (Regel 14, Galerie-Referenzen der übrigen Abschnitte unverändert).
- Jede Länge hängt an einer Achse, die Vorgaben ergeben bei vega den Entwurf pixelgleich (Vergleich gegen `demo.css`).
- Hell, dunkel und Druck; Galerie-Eintrag mit beiden Themen.

## Stand (2026-11-08)

Erledigt: `c22/static/css/app-workspace.css`, Block `blocks/navigation/app-workspace.html`, Regel 14 in
`tests/test_conventions.py`. Vergleich mit UnderDocs heutigem Stand (C22 + `demo.css`) bei 1440, 1280 und 390 px, hell und
dunkel, mit demselben Skript: pixelgleich bis auf eine Schrift (`.embhead em` folgt jetzt `--font-mono` statt
`ui-monospace`) und Kantenglättung an einer Chip-Ecke (höchstens 2 von 255). Offen auf UnderDoc-Seite: Wurzelklasse an
`#root`, `demo.css` entfernen, C22 neu einbinden.
