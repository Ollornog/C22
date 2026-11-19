---
id: T-16
type: Task
title: Weitere Bausteinwünsche von UnderDoc (Nachtrag zum Sammeldurchgang)
status: offen
milestone: M-2
tags: [underdoc, bausteine, app-workspace]
created: 2026-11-19
---

# Weitere Bausteinwünsche von UnderDoc (Nachtrag zum Sammeldurchgang)

## Befund

Nach dem Sammeldurchgang (T-15) meldete UnderDoc sieben weitere Wünsche. Drei sind schon da:

- **Nutzungszahl in den Ressourcen-Listen:** Zähl-Badge (`.badge`, Beispiel „Zähler“) bzw. im Arbeitsbereich `.count`.
- **Herkunft bei Datei-Treffern:** `.badge` (`data-variant="outline"`), in der Schnellsuche als zweite Zeile `<small>`.
- **Fortschritt der Texterkennung nach dem Upload:** `progress.progress` (T-15), Wert aus `value`/`max`, ohne Inline-Stil.

Offen und hier gesammelt, weil sie das Markup von UnderDoc brauchen oder eine Entscheidung zum Aussehen:

- **Seitenwahl im Blockmenü:** „Block auf eine andere Seite verschieben“ wählt die Seite heute in einer `setrow`. Gesucht ist
  eine Auswahl im `.bmenu` (Suchfeld und Liste, wie `.cmdpop`), die zum kompakten Menü passt.
- **Art-Label für Einbettungen im Fakten-Panel:** ein kurzes Wort (Block, Teil, Abschnitt, Wert) vor dem Eintrag, ruhig,
  nicht als zweite Badge-Farbe.
- **Gefahrenbereich mit eingetippter Bestätigung:** „Delete for good“ verlangt die ID. Ein Block für C22: abgesetzte Fläche
  mit destruktivem Rahmen, Text, Feld, das den Wert nennt, Knopf erst aktiv, wenn der Wert stimmt (Verhalten in `c22.js`,
  `data-confirm-value`), ohne JS weiter serverseitig geprüft.
- **Stil für „(demo)“-Gruppen:** erfundene Inhalte im Arbeitsbereich sollen sich von echten absetzen. Wie (gedämpft,
  gestrichelt, Hinweiszeile) ist eine Entscheidung des PO.
  **Entschieden (PO 2026-11-19):** gestrichelter Rahmen plus ruhige Textmarke „Demo“ (Badge `outline`). Der Inhalt wird
  nicht gedämpft (lesbar, ohne Farbe unterscheidbar, auch im Druck); keine zusätzliche Hinweiszeile.

## Fertig, wenn

- Die offenen vier sind gebaut und in der Galerie, bzw. für die Demo-Gruppen ist die Entscheidung gefallen.
- UnderDoc hat die Behelfe ersetzt.
