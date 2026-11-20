---
id: T-18
type: Task
title: Bausteine aus den Rechten von UnderDoc (#92, Rechte-Sprint, #109)
status: erledigt
milestone: M-2
tags: [underdoc, bausteine, rechte]
created: 2026-11-20
---

# Bausteine aus den Rechten von UnderDoc (#92, Rechte-Sprint, #109)

## Befund

UnderDoc baute die Rechte (ADR-29), das Anlegen einer Sammlung mit Freigabe (#92) und Passwörter im Text (#109) mit
Behelfen. Zehn Wünsche, zusammengelegt, wo sie dasselbe meinen:

1. Rechte-Liste (Rollen hier und von oben) und Badge Rolle + Herkunft.
2. Freigabe-Auswahl und Auswahl Person/Gruppe (eine Combobox, gruppiert).
3. Stepper-Dialog (erst Name, dann Freigabe).
4. Zahlenfeld mit Einheit (Aufbewahrung in Tagen).
5. `setrow`/`chip`/`modrow`/`hint`/`lab` außerhalb von `.c22-app-workspace` (der Rechte-Dialog liegt außerhalb).
6. Layout der öffentlichen Seite hinter einem Link.
7. Protokoll als Zeitleiste.
8. Nachtrag #109: `.cm-ud-plain`, die wellige Unterstreichung eines Werts, nach dem der Editor fragt.

## Lösung (2026-11-20)

- 1 und 2: Block „Rechte eines Objekts“: Besitzer und Vererbung als `.item[data-size="sm"]`, Rollen als Tabelle mit
  `select.select`, Herkunft und Rolle als `.badge-split` (Herkunft | Rolle), Freigabe als gruppierte `.combobox`
  (Alle · Gruppen · Personen, Symbol je Art) mit Rolle und Knopf.
- 3: `form[data-steps]` mit `fieldset[data-step]`, `ol.steps`, Knöpfe `[data-step-back]`/`[data-step-next]`/
  `[data-step-done]` (c22.js); Block „In Schritten anlegen“.
- 4: schon da: `.input-group` mit Einheit dahinter (Input Group, „Text-Präfix & -Suffix“), gezeigt im Panel-Block.
- 5: kein zweiter Satz globaler Klassen. Außerhalb des Arbeitsbereichs gelten die allgemeinen Teile: Kopf `h3`, Zeile mit
  Aktionen `.item[data-size="sm"]`, kleine Aktion `.btn[data-variant="outline"][data-size="sm"]`, Hinweis muted
  `text-sm`, Beschriftung `.label`. Block „Verwaltung in einem Panel“.
- 6: Block „Öffentliche Seite hinter einem Link“ (ganze Seite).
- 7: schon da: `ol.timeline` (T-15), im Panel-Block mit „Neuere Einträge“.
- 8: `.cm-ud-plain` im App-Arbeitsbereich (`app-workspace.css`, gehört zum Editor wie `.cm-ud-ask`), Beispiel im
  Seiten-Editor.

## Fertig, wenn

- Alles liegt in C22 und in der Galerie. ✅
- UnderDoc ersetzt seine Behelfe beim nächsten Heben von C22 (Liste im Pull Request).
