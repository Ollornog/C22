---
id: T-4
type: Task
title: Druckbarer Block — einen Ausschnitt der Seite drucken, schwarz auf weiss
status: in-arbeit
milestone: M-2
tags: [bausteine, druck, dark-mode]
created: 2026-09-24
---

# Druckbarer Block

## Anlass

Eine Kunden-App braucht in einer Detailansicht eine **Checkliste zum Ausdrucken**: ein Block
auf der Seite, dessen Inhalt allein auf Papier soll, nicht die ganze Seite. Die App hat den
Baustein selbst gebaut, weil C22 keinen hat. Das ist ein Sonderweg (siehe M-2).

## Wie die App es gelöst hat (Vorbild, nicht Vorgabe)

- **Markup:** Ein Container trägt `data-druckbar`, ein Knopf darin `data-drucken`.
- **JS (ohne Framework, CSP-freundlich):** Der Klick auf `[data-drucken]` hängt eine
  **Kopie** des nächsten `[data-druckbar]`-Blocks als direktes Kind an `<body>`
  (`data-druck-kopie`), setzt `data-druck-auswahl` an `<html>` und ruft `print()`.
  Aufgeräumt wird über `afterprint` und ersatzweise über `matchMedia('print')`; vor jeder
  neuen Kopie werden Reste entfernt. Ein zugeklapptes `<details>` wird in der Kopie
  aufgeklappt.
- **CSS:** Die Kopie ist am Bildschirm unsichtbar. Im Druck ist bei gesetzter Auswahl alles
  ausser der Kopie ausgeblendet, `color-scheme: light`, schwarz auf weiss, auch aus dem
  dunklen Modus; `summary` und der Druckknopf selbst verschwinden im Druck.

Die Kopie statt „alles andere ausblenden" ist nötig, weil der Block tief im Layout sitzt
(Grid, Karten, Scrollcontainer) und dort beim Druck abgeschnitten würde.

## Aufgabe

- Den Baustein in C22 aufnehmen: Markup-Konvention, JS, CSS, mit Tokens statt fester Farben,
  wo das im Druck sinnvoll ist.
- **Galerie-Eintrag** mit Druckvorschau in hell und dunkel.
- Visueller Test des Druckbilds (M-1), sobald die visuelle Ebene steht.
- Klären, ob die Attributnamen deutsch bleiben (wie im Vorbild) oder einer
  C22-Namenskonvention folgen; die App passt ihren Adapter dann an.

**Fertig, wenn:** die App den Block nur noch über den C22-Baustein nutzt und ihr eigenes JS
und CSS dafür entfernt sind.

## Stand (2026-11-07)

Die C22-Seite ist erledigt: `components/print-block.html`, in der Galerie mit Druckvorschau. Das Druckbild prüft `tests/test_visual.py`.

Die Attribute heißen englisch wie der Rest von C22: `data-printable`, `data-print`, `data-print-copy`, `data-print-selection`.

**Offen:** Die App stellt ihren Adapter um und entfernt ihr eigenes JS und CSS.
