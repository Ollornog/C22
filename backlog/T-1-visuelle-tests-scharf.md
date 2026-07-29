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

## Erster Kandidat: die Lesemarke des Inhaltsverzeichnisses (2026-07-30)

Der Scrollspy der `Toc`-Component war fertig, sah im Standbild richtig aus — und stand beim
Scrollen still: `scrollElter()` begann bei `parentElement`, fand den scrollenden Container
deshalb nicht (in der Galerie scrollt `main` SELBST) und hängte den Listener an `window`.
Kein statischer Test kann das sehen; gefunden wurde es erst durch eine Wegwerf-Seite, die den
Container per JS scrollt und danach ausliest, welcher Eintrag `aria-current` trägt.

Genau das sollte die visuelle/Browser-Ebene können:
1. Seite laden, Container gezielt scrollen (`element.scrollTop = …`).
2. Auslesen, welcher Eintrag markiert ist — je Verzeichnis, denn mehrere auf einer Seite sind
   ausdrücklich erlaubt.
3. Erwartung vergleichen (Abschnitt 3 ⇒ dritter Eintrag; Kopfbereich ⇒ Seitentitel-Eintrag).
Dasselbe Muster deckt danach Karussell, Kalender und die Chart-Engine ab.

