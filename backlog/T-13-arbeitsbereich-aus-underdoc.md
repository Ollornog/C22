---
id: T-13
type: Task
title: Arbeitsbereich mit drei Spalten aus UnderDoc übernehmen
status: erledigt
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

## Stand (2026-11-08)

C22 hat die Bausteine (Block `blocks/navigation/workspace.html`, Regeln in `components.css`, Verhalten in `c22.js`,
`workspace-boot.js` für die Breiten vor dem ersten Zeichnen). Galerie in hell, dunkel und Handy, Druck und Verhalten
prüft `tests/test_visual.py`. Die Maße sind Variablen an `.workspace`, die Vorgaben folgen der Abstands-Achse. Die Maße
aus dem Entwurf sind UnderDocs Wahl und gehören in UnderDocs eigenes Stylesheet (PO 2026-11-08: C22 hält die Bausteine,
jede App setzt ihr Aussehen selbst darauf).

Bewusst nicht in C22, weil App-Sache: Reiter ziehen und schließen, mehrere Fenster, Inhalt des Kontextmenüs, was „Neu“
anlegt. Der Verlauf am allgemeinen Reiter und die Inhaltsmarkierung sind ein `.dropdown-menu`.

UnderDoc hat umgestellt (UnderDoc PR #24, 2026-11-08). In UnderDoc bleiben nur sein Aussehen aus dem Entwurf (`shell.css`: die Maße an `.workspace` und ein paar Teile der eigenen Seiten) und App-Verhalten (`shell.js`: Fenster und Spalten nachladen, Aktionen im Menü eines Eintrags, Theme, Suchtasten). Damit ist „Fertig, wenn“ in der Sache erfüllt.
