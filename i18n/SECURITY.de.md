<p align="center"><img src="../docs/logo.png" alt="C22" width="60"></p>

<h1 align="center">Sicherheitsrichtlinie</h1>

<p align="center"><a href="../SECURITY.md">English</a> · <b>Deutsch</b></p>

## Schwachstellen melden

Bitte vertraulich über GitHubs
[private Meldung](https://github.com/Ollornog/C22/security/advisories/new) statt über ein
öffentliches Issue. Eine erste Antwort kommt binnen einer Woche.

## Umfang und Entwurfsentscheidungen, die man kennen sollte

- **C22 liefert statische Assets, keinen laufenden Dienst.** Es hat keinen Netzzugriff,
  keine Anmeldung und keinen eigenen Zustand; es stellt CSS, etwas JavaScript und
  optionale Jinja-Vorlagen bereit.
- **Alles ist in sich geschlossen.** Die Assets verweisen zur Laufzeit auf kein externes
  CDN, keinen Font-Host und keinen Tracker — eine konsumierende App macht wegen C22 keine
  Anfrage an Dritte. Ein Asset, das das tut, ist ein meldenswerter Fehler.
- **Die Jinja-Makros escapen standardmäßig.** Ein Makro, das vom Aufrufer geliefertes HTML
  ausgibt, kennzeichnet das bewusst; ein Makro, das ungefiltert durchlässt, ist ein Fehler.

## Nicht im Umfang

Wie eine konsumierende Anwendung sich anmeldet, Daten speichert oder Anfragen weiterleitet
— das gehört zur App, nicht zu dieser Darstellungsschicht.
