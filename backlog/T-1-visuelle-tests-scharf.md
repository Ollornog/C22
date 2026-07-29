---
id: T-1
type: Task
title: Visuelle Tests scharf schalten
status: offen
milestone: M-1
tags: [testing, screenshots]
created: 2026-07-23
---

# T-1 — Visuelle Tests scharf schalten

Das Gerüst steht, aber es bricht noch nichts. Offen sind die beiden Fragen, an denen visuelle
Tests üblicherweise scheitern:

- **Was ist eine Abweichung?** Ein Pixel Unterschied durch Kantenglättung darf nicht rot werden,
  eine verrutschte Schaltfläche schon. Also Schwellwert, nicht Gleichheit.
- **Wer pflegt die Referenzbilder?** Ohne klaren Weg, sie bewusst zu erneuern, werden sie beim
  ersten Fehlschlag blind überschrieben — und der Test ist wertlos.

**Fertig, wenn:** ein absichtlich verschobenes Element den Lauf rot macht und das Erneuern der
Referenz ein eigener, sichtbarer Schritt ist.
