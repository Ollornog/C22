---
id: T-6
type: Task
title: Ablaufdiagramm / Entscheidungsbaum als Baustein
status: offen
milestone: M-2
tags: [bausteine, diagramm, ablauf]
created: 2026-09-27
---

# Ablaufdiagramm / Entscheidungsbaum

## Anlass

paperlaiss zeigt zweimal einen Ablauf als senkrechte Kette von Knoten mit Pfeilen: den Weg eines
Dokuments durch den Klassifizierer (Knoten per Klick bearbeitbar, ähnlich n8n) und den Lauf
eines einzelnen Dokuments (Knoten mit Ergebnis-Badge). Entscheidungsknoten zeigen zwei Zweige
(ja/nein) nebeneinander. C22 hat dafür keinen Baustein; die App setzt ihn aus C22-Teilen
zusammen — ein Sonderweg (M-2).

## Wie die App es gelöst hat (Vorbild, nicht Vorgabe)

- **Knoten:** `.card[data-size=sm]`, im Kopf ein Badge für die Art (Schritt/Entscheidung/KI)
  und rechts ein Ergebnis-Badge bzw. „Bearbeiten"; klickbar mit `cursor-pointer hover:border-ring`.
- **Zweige:** `grid grid-cols-2 gap-3`, je Zweig ein umrandeter Block mit Badge `success`/`warning`.
- **Verbinder:** Lucide `arrow-down` in `size-10`/`size-12`, zentriert, `text-muted-foreground`.
- Quelle: `panel/seiten.py` im Repo `Ollornog/paperlaiss` (`ablauf()`, `knoten()` im JS).

## Offene Fragen für den Baustein

Waagerechte Variante (n8n-artig), Zweige, die wieder zusammenlaufen, aktiver/fehlgeschlagener
Knoten als Zustand, Tastatur (Knoten als Buttons), Druck.

## Fertig, wenn

Der Baustein liegt in `c22/components/` oder `c22/blocks/`, die Galerie zeigt ihn in allen
Zuständen, und paperlaiss nutzt ihn über einen dünnen Adapter.
