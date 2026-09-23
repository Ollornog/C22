---
id: T-3
type: Task
title: Fremdressourcen — der zweite Blickwinkel fehlt noch (laufende Seite)
status: offen
milestone: M-1
tags: [testing, datenschutz, hygiene]
created: 2026-09-23
---

# Fremdressourcen: der zweite Blickwinkel fehlt noch

Die **Quelltext-Seite** ist erledigt (Kit 0.18.0, `pruefe_keine_fremdressourcen`, läuft in
`tests/test_repo.py`): 116 Hotlinks auf ein fremdes Bild-CDN sind weg, die Bilder liegen unter
`c22/static/img/demo/` mit REUSE-Nachweis.

**Was noch fehlt, und warum es nicht dasselbe ist:** Der Quelltext sieht nicht, was JavaScript zur
Laufzeit zusammenbaut. Die Regel verlangt ausdrücklich **beide** Blickwinkel:

> Der Quelltext sieht nicht, was JavaScript zusammenbaut; die laufende Seite sieht nicht, was auf
> einer anderen Route steht. — `context/fremdressourcen.md` auf dem Tower

## Aufgabe

Die Galerie mit einem **CDP-Netzwerkprotokoll** laden und **jede tatsächlich angeforderte Herkunft**
gegen eine Liste halten. Das gehört in die Browser-Tests, die die Test-Policy ohnehin verlangt —
nicht in eine weitere Quelltext-Prüfung.

Erwartung nach dem heutigen Stand: **nur der eigene Ursprung.** Die gebaute Galerie enthält kein
einziges `src="https://` mehr; die verbliebenen `https://`-Vorkommen sind alle `href=` auf
Quellenangaben (shadcn, basecoat, unsplash, github, phosphoricons, lucide) — also Türen, keine Boten.

## Warum das für C22 mehr zählt als für andere Repos

C22 vererbt sein Markup an jede App. Ein Hotlink hier wird zu einem Hotlink in jeder App, die einen
Block abschreibt — und fällt dort nicht auf, weil das Bild ja erscheint. Deshalb priorisiert die
Regel C22 namentlich: *zuerst, was veröffentlicht ist, und zuerst, was sich vererbt.*

## Nicht bauen

- **Kein Bild-Cache-Proxy.** Der ist der richtige Griff nur für Adressen, die erst zur Laufzeit
  entstehen (ein Nutzer trägt eine fremde URL ein) — diesen Fall gibt es hier nicht.
- **SRI ist keine Datenschutzmaßnahme.** `integrity=` schützt die Integrität, nicht die IP des
  Besuchers, gilt nur für `script` und `link rel=stylesheet` und wirkt bei Bildern gar nicht.
