---
id: T-15
type: Task
title: Gesammelte Bausteinwünsche von EightPerDay und UnderDoc
status: erledigt
milestone: M-2
tags: [eightperday, underdoc, bausteine]
created: 2026-11-19
---

# Gesammelte Bausteinwünsche von EightPerDay und UnderDoc

## Befund

Beide Apps haben beim Bauen Wünsche an C22 gesammelt und sich bis dahin mit vorhandenen Klassen beholfen:
Monatskalender und Jahresgitter mit Kürzeln, Spalten auf dem Handy ausblenden, ein Drucklayout für Berichte, kompakte
Felder in Tabellenzeilen, ein Protokoll (wer, wann, was), Zustände in Worten, Ablehnen mit Begründung, Verbrauch
„genutzt / Grenze“, Fortschritt ohne Inline-Stil, eine Ablagezone, die beim Ziehen aufleuchtet, und im
App-Arbeitsbereich die vorläufigen Regeln von UnderDocs M-3 (Löschwege, Teile, Platzhalter für Entferntes).

## Fertig, wenn

- Jeder Wunsch ist gebaut, als schon vorhanden belegt (mit Galerie-Beispiel) oder hier mit Grund zurückgestellt.
- Beide Apps können ihre Behelfe durch die Bausteine ersetzen.

## Stand (2026-11-19)

Teil 1 (Bausteine und Blöcke): Timeline, Monatskalender, Jahresgitter, Wochenbericht als Drucklayout, Ablehnen mit
Begründung, kompaktes Feld, natives `progress.progress`, Ablagezone `[data-dropzone]`, Tab-Leiste schafft sich selbst
Platz; Beispiele für Zustände in Worten, ausgeblendete Spalten, Dateiliste, Versionen, Anmelde-Protokoll, Einmal-Link,
Anmelde-Karte eines Mandanten. Teil 2 (App-Arbeitsbereich): Löschweg-Dialog, Teile im Text und ihre Grenzen, Platzhalter
für Entferntes, Namensfeld der Markierungsleiste, Modulzeile nur zur Anzeige, Chip als Link und als Formularknopf,
Datumsfeld im Panel, Vorschau im Rahmen, Aktionen in der letzten Tabellenzelle, Hochladebalken.

Schon vorhanden und nur gezeigt bzw. benannt: Checkbox mit Beschreibung (`.field` mit `<section>`, Checkbox), QR-Code mit
Schlüssel (`img.qr-code` + `code.secret-key`), kleiner nativer Select (`data-size="sm"` vom Hersteller), Schnellsuche
mit Pfad und Ausschnitt (`.cmdpop`, Eintrag `<span>Name<small>…</small></span>`), Hinweiszeile im Panel (`.hint`/`.note`),
Trefferstelle nach dem Sprung (`mark.cur`), Knopfreihe für Datei-Aktionen (`.tagrow` ist die Reihe von Chips), Datei-Icons
je Typ (Lucide `file-text`, `file-image`, `file-spreadsheet`, `folder`).

Zurückgestellt: T-12 (Adapter für Go-Vorlagen) bleibt offen, siehe dort.
