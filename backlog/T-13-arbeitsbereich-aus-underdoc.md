---
id: T-13
type: Task
title: Arbeitsbereich mit drei Spalten aus UnderDoc übernehmen
status: offen
milestone: M-2
tags: [bausteine, layout, underdoc]
created: 2026-11-08
---

# Arbeitsbereich mit drei Spalten aus UnderDoc übernehmen

## Befund

UnderDoc baut seine Oberfläche als Arbeitsbereich (UnderDoc ADR-16, M-28). C22 hat dafür noch keine Bausteine, deshalb
liegt in UnderDoc ein Sonderweg: `internal/web/assets/app/shell.css` und `shell.js`, Klassen mit dem Präfix `ud-`. Das
Stylesheet nutzt nur Tokens von C22 und keine eigenen Werte für Farben, Schriftgrößen, Schriftstärken oder Radien. Ein Test
in UnderDoc (`TestShellUsesOnlyTokens`) prüft das.

Die Bausteine:

- **Gerüst:** obere Zeile über den Spalten (Name, Suche, Neu) mit den Reitern daneben; drei Spalten nav1, nav2, nav3 und das
  Fenster; ein Raster, kein Seitenleisten-Element.
- **Spaltenbreite:** rechte Kante jeder Spalte ziehbar (Zeigerereignisse und Pfeiltasten). nav1 und nav2 rasten in vier
  Stufen ein: Symbol, Symbol mit Text darunter, Text, Symbol mit Text daneben. nav3 frei. Breiten als CSS-Variablen, vor
  dem ersten Zeichnen gesetzt, ohne Inline-Stil im Markup (strenge CSP).
- **Listeneintrag mit Pfeil:** Pfeil klappt auf, Name öffnet, Doppelklick klappt auf; aktueller Eintrag markiert.
- **Spaltenkopf mit „New +“:** Überschrift in Versalien, rechts ein deutlicher Knopf.
- **Ausgegraut:** Einträge, die eine App noch nicht gebaut hat, sichtbar mit `aria-disabled="true"`.
- **Kopf des Fensters:** Brotkrume mit Tags rechts daneben, Werkzeuge rechts, darunter Titel und Beschreibung.
- **Reiter:** allgemeiner Reiter (gestrichelt, kursiv); später Stapel, Verlauf, Kontextmenü.
- **Schublade über dem Fenster** (Zahnrad) und **Markierung mit Ausklappliste** (Inhaltsverzeichnis).
- **Handy:** nav2 und nav3 öffnen über dem Fenster, grob, bis UnderDoc sein Handy-Layout festlegt (UnderDoc T-10).

Stand und Aussehen: der klickbare Entwurf von UnderDoc (Runde 10) und der Bau in UnderDoc PR #22.

## Fertig, wenn

- Die Bausteine liegen in C22, in der Galerie in jedem Zustand (hell, dunkel, Druck), und gehen unter strenger CSP ohne
  Inline-Stil und ohne `onclick`.
- UnderDoc nutzt sie über die dünne Schicht von T-12 und hat `shell.css` und `shell.js` entfernt.
