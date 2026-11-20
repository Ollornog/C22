---
id: T-17
type: Task
title: Bausteine aus dem Stundenblatt von EightPerDay (M-6)
status: erledigt
milestone: M-2
tags: [eightperday, bausteine, tabelle]
created: 2026-11-20
---

# Bausteine aus dem Stundenblatt von EightPerDay (M-6)

## Befund

EightPerDay baute in M-6 (ein Blatt in drei Ansichten) und in den Folgepunkten acht Dinge mit Utilities und eigenem
Skript, die C22 nicht hatte, dazu eine Hinweiszeile unter einem Feld:

1. Eine Zwischenzeile (die Woche), die unter dem Tabellenkopf klebt; den Versatz setzte ein eigenes Skript als Inline-Stil.
2. Ein Feld ohne Rahmen, das die Zelle ist.
3. Eine Tabelle mit klebendem Kopf und klebender erster Spalte.
4. Ein Feld, das ohne Fokus als Chips erscheint (`group-focus-within`).
5. Utilities, die im Pack fehlten: `md:hidden`, `md:flex`, `z-20`, `top-10`, `border-l`, `grid-cols-7`, `table-fixed`,
   `group-focus-within:opacity-0`.
6. Ein Segment-Umschalter und ein Einstellungs-Popover außerhalb des Arbeitsbereichs, ohne JavaScript bedienbar.
7. Die Zeile von heute über `aria-current`.
8. Farbmarken je Arbeitgeber (Badge-Varianten reihum).
9. Eine Hinweiszeile unter einem Feld („sichtbar für …“, EightPerDay #24).

## Lösung (2026-11-20)

- 1 und 3: `.table[data-sticky]` mit `tr[data-group-row]`; c22.js hält `--table-head-height` (CSSOM, CSP-tauglich).
- 2 und 9: `td[data-field] > .input`, darunter `small`; `data-type="number"` rückt beides ans Ende. Außerhalb einer
  Tabelle bleibt die Hinweiszeile der Hilfetext von `.field`.
- 4: `.chip-input` (Feld über `[data-chips]`, sichtbar nur mit Fokus).
- 5: alle acht stehen im Galerie-Block „Stundenblatt“ und damit im Pack.
- 6: `details.popover` (c22.js schließt per Klick daneben und Escape); der Segment-Umschalter ist die vorhandene
  Toggle-Gruppe, hier als `.button-group` mit Absende-Knöpfen und `aria-pressed`.
- 7: `.table tr[aria-current="date"]`.
- 8: `.badge[data-mark="1"…"5"]`, Punkt in der Diagrammfarbe.

Galerie: Block „Stundenblatt“ (Daten erfassen), Beispiele in Badge und Popover. Verhalten in `tests/test_visual.py`.

## Fertig, wenn

- Alles liegt in C22 und in der Galerie. ✅
- EightPerDay ersetzt seine Behelfe beim nächsten Heben von C22 (Liste im Pull Request).
