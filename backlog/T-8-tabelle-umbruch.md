---
id: T-8
type: Task
title: Tabelle mit umbrechenden Zellen
status: offen
milestone: M-2
tags: [komponenten, tabelle]
created: 2026-09-27
---

# Tabelle mit umbrechenden Zellen

## Befund

`.table td` und `.table th` setzen fest `white-space: nowrap`. Eine Zelle mit einem Satz statt
eines Werts läuft damit aus der Karte und die Tabelle scrollt seitlich. Eine Variante oder
Utility zum Umbrechen gibt es im Pack nicht (`whitespace-normal`, `break-words` fehlen).

paperlaiss zeigt Regeln als Tabelle „Wenn → Dann" (`panel/seiten.py`, `schritt()`, Repo
`Ollornog/paperlaiss`) und hat den langen Text deshalb gekürzt und in den Absatz über der
Tabelle verlegt — ein Umweg über den Inhalt statt über das Aussehen.

## Fertig, wenn

Eine Tabelle (oder einzelne Spalten) per Variante umbrechen kann, etwa
`<table class="table" data-wrap>`, das in der Galerie gezeigt wird und paperlaiss seine Regeln
wieder in voller Länge in die Zelle schreiben kann.
