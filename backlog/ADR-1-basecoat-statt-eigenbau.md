---
id: ADR-1
type: Decision
title: Fundament auf Tailwind + Basecoat statt Eigenbau-CSS
status: erledigt
tags: [architektur, css, tailwind]
created: 2026-07-15
---

# ADR-1 — Tailwind + Basecoat statt Eigenbau-CSS

## Kontext

Die Bibliothek entstand als **eigenes CSS**: Layout-Primitive, vendorte Farbskalen, eigene
Komponenten. Parallel sollte dasselbe Aussehen in zwei Anwendungen mit **verschiedenen
Template-Sprachen** landen.

## Optionen

1. **Eigenbau fortführen** — volle Kontrolle, keine fremde Abhängigkeit.
2. **Tailwind + Basecoat** — fertige Komponentenklassen, eine Quelle für beide Template-Sprachen.

## Entscheidung

**(2), am 2026-07-15.** Die frühere Festlegung „kein fremdes CSS-Framework" ist damit **revidiert**.

## Begründung

Der Eigenbau hätte für **jede** Komponente in **beiden** Template-Sprachen nachgezogen werden
müssen. Basecoat liefert kanonisches HTML plus Klassen, ohne eine JavaScript-Laufzeit
vorzuschreiben — die Anwendungen halten nur noch dünne Adapter.

Der ursprüngliche Einwand gegen fremde Frameworks (Umfang des ausgelieferten CSS) wiegt weniger,
seit der Erzeuger ungenutzte Klassen entfernt.

## Konsequenzen

- Die Eigenbau-Komponenten der Vorversion sind **abgelöst**; die dokumentierten Entscheidungen
  von damals bleiben als Historie lesbar.
- Eigene Regeln leben weiter in einer schmalen Ergänzungsschicht — dort, wo Basecoat nichts anbietet.
- Aussehen wird **hier** entschieden und von den Anwendungen übernommen, nie in der Anwendung
  hart gelöst.
