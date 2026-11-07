---
id: T-5
type: Task
title: Schrift Inter ohne OFL-Lizenztext ausgeliefert
status: in-arbeit
milestone: M-2
tags: [lizenz, schrift, fremdressourcen]
created: 2026-09-27
---

# Schrift Inter ohne OFL-Lizenztext

## Befund

`c22/static/fonts/inter.woff2` liegt im Paket, und `c22-<pack>.css` lädt sie über
`url(../fonts/inter.woff2)`. Inter steht unter der **SIL Open Font License 1.1**; die OFL
verlangt, dass Copyright-Hinweis und Lizenztext mit jeder Kopie der Schrift weitergegeben
werden. Im Repo gibt es dazu keine Datei (Suche nach „OFL"/„Open Font License" über das Repo:
kein Treffer, gemessen 2026-09-27).

Jede App, die C22 vendort (FleetCommander, paperlaiss), gibt die Schrift damit ohne Lizenz
weiter. paperlaiss legt den Text deshalb selbst daneben (`panel/static/c22/fonts/OFL.txt`,
Quelle: `LICENSE.txt` im Repo `rsms/inter`) — das ist ein Sonderweg.

## Fertig, wenn

`c22/static/fonts/OFL.txt` (oder gleichwertig) liegt neben der Schrift, das Paket liefert sie
mit, und die Vendor-Skripte der Apps kopieren sie aus C22 statt aus eigener Quelle.

## Stand (2026-11-07)

Die C22-Seite ist erledigt: `c22/static/fonts/OFL.txt` (gleich `LICENSE.txt` von `rsms/inter`) liegt neben der Schrift und kommt ins Wheel.

Die Website trägt den Text jetzt auch, verlinkt aus dem Impressum.

**Offen:** Die Vendor-Skripte der Apps, die die Schrift mitnehmen, kopieren den Text noch nicht aus C22 (paperlaiss, UnderDoc und eine Kunden-App).
