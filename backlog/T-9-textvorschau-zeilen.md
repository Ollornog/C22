---
id: T-9
type: Task
title: Textvorschau mit n Zeilen, Ausblenden und „mehr anzeigen"
status: offen
milestone: M-2
tags: [komponenten, text]
created: 2026-09-27
---

# Textvorschau mit n Zeilen und Ausblenden

## Befund

Das Pack hat weder `line-clamp-*` noch eine Klasse für einen ausblendenden Rand (Farbverlauf
oder Maske) noch kleine `max-h-*`-Stufen (die kleinste ist `max-h-48`). Einen langen Block auf
die ersten Zeilen kürzen, nach unten ausblenden und per Knopf aufklappen geht damit nicht.

paperlaiss braucht das für Eingabe/Ausgabe im Ablauf (Prompts, Nachrichten, Tabellen) und hat es
als Sonderweg gebaut (`panel/seiten.py`, `klapp()`/`klemmen()`, Repo `Ollornog/paperlaiss`):
Inline-Stil `max-height:5.6em; mask-image:linear-gradient(to bottom, black 60%, transparent)`,
nach dem Zeichnen gemessen — passt alles, fällt die Klemme weg.

## Fertig, wenn

Ein Baustein (etwa `data-klemme="3"` plus Knopf) einen Block auf n Zeilen kürzt, nach unten
ausblendet, den Knopf nur bei Überhang zeigt, in der Galerie steht und paperlaiss den Sonderweg
entfernen kann.
