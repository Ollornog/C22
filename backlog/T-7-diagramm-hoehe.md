---
id: T-7
type: Task
title: Balkendiagramm mit einstellbarer Höhe bzw. Seitenverhältnis
status: offen
milestone: M-2
tags: [bausteine, diagramm, charts]
created: 2026-09-27
---

# Balkendiagramm mit einstellbarer Höhe

## Befund

`wireChart` zeichnet in ein festes `viewBox` 320×180 und skaliert mit der Breite
(`style="display:block;width:100%"`). Über die volle Breite einer Seite (≈1000 px) wird das
Diagramm damit ≈560 px hoch, und die Achsenbeschriftung wächst mit, bis sie sich überlappt.
Eine Option für Höhe oder Seitenverhältnis gibt es nicht (`cfg.height`/`cfg.aspect` fehlen).

paperlaiss braucht einen breiten, flachen Tagesverlauf (60 Balken, gestapelt, Klick je Tag) und
hat ihn deshalb als Sonderweg aus C22-Farben gebaut (`panel/seiten.py`, `verlauf()`, Repo
`Ollornog/paperlaiss`) — HTML-Balken statt SVG.

## Fertig, wenn

Das Balkendiagramm eine Höhe bzw. ein Seitenverhältnis annimmt, die Beschriftung dabei lesbar
bleibt (Textgröße unabhängig von der Breite), ein Klick auf eine Kategorie als Ereignis gemeldet
wird, und paperlaiss den Sonderweg wieder entfernen kann.
