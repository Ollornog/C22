---
id: T-10
type: Task
title: Kit 0.28 übernehmen — jede Webseite hat ein Favicon
status: offen
milestone: M-2
tags: [hygiene, kit, favicon]
created: 2026-10-08
---

# Kit 0.28 übernehmen: jede Webseite hat ein Favicon

## Befund

Der PO hat am 2026-10-08 gesagt: „das favicon überall nicht vergessen. bitte auch als test generell überall in
repos und co einbauen bei websites“. repokit 0.28.0 bringt dafür zwei Teile:

- `pruefe_favicon`: Jede vollständige Seite (mit `<head>`) braucht ein `<link rel="icon">`.
- `favicon_befunde_html(html, eigener_host)`: misst Seiten, die erst beim Ausliefern entstehen (Galerie, Pages-Website).

Sobald C22 das Kit synct, verlangt `pruefe_kit_prueffunktionen_gerufen` den Aufruf.

Gemessen am 2026-10-08: In C22 liegen **0** vollständige Seiten, die Bausteine sind Fragmente. Die Dateiprüfung ist
damit sofort grün. Offen ist, ob die **gebaute** Galerie bzw. Pages-Website ein Favicon trägt. Die sieht nur ein Test
auf die fertige Seite.

## Zu tun

1. `repokit sync .` und den Aufruf `hygiene.pruefe_favicon(...)` in `tests/test_repo.py` einhängen. Muster: die anderen
   Repos, die das Kit nutzen (Rollout vom 2026-10-08).
2. In den Browser- oder Seitentest der Galerie `favicon_befunde_html` auf die ausgelieferte Seite anwenden. Dabei die
   **rohe Antwort** prüfen (`fetch` mit `Content-Type`), nicht das DOM. Chrome verpackt JSON und Text in eine eigene
   HTML-Hülle mit `<head>`, das ergab in DashMyBoard einen Fehlalarm.
3. Fehlt das Favicon, ein eigenes ausliefern (Datei oder `data:`-URI), nie von Dritten.
