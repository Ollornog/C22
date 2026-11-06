---
id: T-12
type: Task
title: Adapter für Go-Vorlagen
status: offen
milestone: M-2
tags: [adapter, go]
created: 2026-11-06
---

# Adapter für Go-Vorlagen

## Befund

C22 hat Python-Makros, aber nichts für `html/template`. UnderDoc ist die erste Go-App mit Oberfläche und hält deshalb eine
eigene dünne Schicht um das kanonische HTML (`internal/web/templates/components.html`): Icons, Brotkrume, Seitenleiste mit
Baum, Inhaltsverzeichnis, leerer Zustand.

Dazu kommen zwei Punkte, die jede Go-App trifft:

- **Pack bauen:** Die kompilierten Packs sind nicht eingecheckt. UnderDoc baut sie mit `scripts/vendor-c22.sh` selbst.
- **Strenge CSP:** Die Beispiele nutzen `style="--sidebar-width: …"` und `onclick`. Mit der CSP von UnderDoc geht das nicht,
  also bleibt die Standardbreite, und der Umschalter hängt an einem eigenen Skript.

## Fertig, wenn

- Eine zweite Go-App die Schicht aus C22 übernehmen kann, statt sie zu kopieren. Vorher lohnt sich der Umbau nicht.
- Die Seitenleiste lässt sich ohne Inline-Stil und ohne `onclick` bedienen, in der Galerie sichtbar.
