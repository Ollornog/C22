---
id: T-2
type: Task
title: Eigene Web-Schrift einbetten
status: erledigt
milestone: M-1
tags: [typografie, datenschutz]
created: 2026-07-23
---

# T-2 — Eigene Web-Schrift einbetten

Derzeit hängt die Darstellung an den Schriften des Systems. Eine mitgelieferte Schrift macht das
Erscheinungsbild über Geräte hinweg gleich — und vermeidet, sie von einem fremden Server zu laden
(jeder Aufruf verrät dem Anbieter die Adresse des Besuchers).

**Fertig, wenn:** die Schrift im Paket liegt, lokal eingebunden ist und die Lizenz das erlaubt.

## Erledigt (2026-11-07)

Die Schrift lag schon im Quellbaum und ist über `tokens.css` lokal eingebunden. Ins Wheel kam sie aber nicht: `package-data` nannte `static/fonts/*` nicht. Das Glob ist ergänzt, `tests/test_paket.py` hält es fest. Lizenz: siehe T-5.
