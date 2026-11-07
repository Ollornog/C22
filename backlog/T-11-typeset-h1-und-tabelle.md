---
id: T-11
type: Task
title: Prosa-Fluss in .typeset für h1 und Tabellen-Container
status: erledigt
milestone: M-2
tags: [typeset, komponenten]
created: 2026-11-06
---

# Prosa-Fluss in .typeset für h1 und Tabellen-Container

## Befund

`.typeset` regelt den Abstand nur zwischen `p, ul, ol, blockquote, pre, table, figure` und vor `h2`–`h4`. Zwei Fälle aus
gerendertem Markdown fehlen (gefunden in UnderDoc, gemessen 2026-11-06):

- Nach einem `h1` steht der nächste Block ohne Abstand. Die Regel `h2, h3, h4 + *` schließt `h1` nicht ein.
- Tabellen stehen im kanonischen `.table-container`. Dieses `div` kommt in der Liste nicht vor, also hat eine Tabelle keinen
  Abstand zu den Blöcken davor und danach.

UnderDoc hilft sich mit `mb-4` am `h1` und `my-4` am Container. Das gehört nach C22, damit die Fluss-Achse auch hier wirkt.

## Fertig, wenn

- `.typeset` deckt `h1` und `.table-container` ab, abgeleitet aus `--flow`.
- Der Prosa-Musterartikel zeigt beide Fälle.

## Erledigt (2026-11-07)

`.typeset` deckt `h1` und `.table-container` ab, beide aus `--flow`. Der Musterartikel zeigt beide Fälle. UnderDoc kann `mb-4` und `my-4` streichen.
