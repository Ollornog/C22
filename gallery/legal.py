#!/usr/bin/env python3
"""Impressum und Datenschutz der veröffentlichten Galerie (`legal.html`).

Eine öffentliche Projektseite ist ein Telemedium, das nicht ausschließlich persönlichen
Zwecken dient — § 18 Abs. 1 MStV verlangt dafür Name, ladungsfähige Anschrift und einen
schnellen elektronischen Kontakt. Die Angaben stehen deshalb hier und nicht verstreut im
Markup: **eine** Quelle, die der Generator in die Seite stellt.

Der Text nutzt bewusst dieselben Typografie-Utilities wie `c22/typeset/prose.html` —
die Rechtsseite ist damit selbst ein Beleg dafür, dass der Kanon trägt.
"""
from __future__ import annotations

import html

# ── Anbieterkennzeichnung ─────────────────────────────────────────────────────
# Gilt NUR für die offizielle Projektseite. Wer C22 selbst hostet, ist selbst Anbieter:
# C22 ist eine Vorlage unter MIT-Lizenz, kein Angebot des Autors.
BETREIBER = {
    "name": "Daniel Brunthaler",
    "strasse": "Hebbelstraße 22",
    "ort": "23843 Bad Oldesloe",
    "land": "Deutschland",
    "email": "admin@ollornog.de",
}
SITE_URL = "ollornog.github.io/C22"
REPO_URL = "https://github.com/Ollornog/C22"

H2 = 'class="scroll-m-20 border-b pb-2 text-3xl font-semibold tracking-tight"'
H3 = 'class="scroll-m-20 text-2xl font-semibold tracking-tight"'
P = 'class="leading-7"'
LINK = 'class="font-medium underline underline-offset-4"'
CODE = ('class="bg-muted relative rounded px-[0.3rem] py-[0.2rem] '
        'font-mono text-sm font-semibold"')

# (Anker, Überschrift, Absätze als HTML) — die Reihenfolge ist zugleich das Inhaltsverzeichnis.
ABSCHNITTE: list[tuple[str, str, list[str]]] = [
    ("impressum", "Impressum", [
        "Angaben gemäß § 5 DDG (löste am 14.05.2025 den § 5 TMG ab) und verantwortlich für den "
        "Inhalt nach § 18 Abs. 2 MStV.",
        "ADRESSBLOCK",
        f'Diese Angaben gelten für die Projektseite unter <code {CODE}>{SITE_URL}</code> und für '
        "sonst nichts. C22 ist freie Software unter der MIT-Lizenz — eine Vorlage. Wer sie auf "
        "einem eigenen Server einsetzt, betreibt einen eigenen Dienst, ist dessen Anbieter und "
        "verantwortet ihn selbst.",
    ]),
    ("zweck", "Was diese Seite ist", [
        "Diese Seite ist die Galerie eines nicht-kommerziellen Open-Source-Projekts: Sie zeigt "
        "jede Komponente des Design-Systems in ihren Varianten. Sie verkauft nichts, zeigt keine "
        "Werbung und verfolgt niemanden.",
        f'Der Quellcode liegt auf <a href="{REPO_URL}" {LINK}>GitHub</a>; die Seite wird bei jeder '
        "Änderung an <code {code}>main</code> neu gebaut.".replace("{code}", CODE),
    ]),
    ("hosting", "Hosting bei GitHub Pages", [
        "Diese Seite wird von GitHub Pages ausgeliefert (GitHub, Inc., 88 Colin P. Kelly Jr. St, "
        "San Francisco, CA 94107, USA). GitHub schreibt bei jedem Aufruf Server-Logs: IP-Adresse, "
        "Zeitpunkt, angefragte Datei, Referrer, Browser und Betriebssystem. <strong>Das passiert "
        "bei GitHub, auf GitHubs Systemen — der Betreiber dieser Seite bekommt diese Logs weder "
        "zu sehen noch kann er sie herausgeben.</strong> Rechtsgrundlage ist Art. 6 Abs. 1 lit. f "
        "DSGVO: das berechtigte Interesse, die Seite zuverlässig auszuliefern. GitHub verarbeitet "
        "Daten in den USA und ist unter dem EU-US Data Privacy Framework zertifiziert. Was GitHub "
        'damit tut, steht in seiner <a href="https://docs.github.com/en/site-policy/privacy-policies'
        f'/github-general-privacy-statement" {LINK}>Datenschutzerklärung</a>; Anfragen zu diesen '
        "Logs richte bitte direkt dorthin.",
    ]),
    ("fremde-inhalte", "Beispielbilder von Unsplash", [
        "Die Galerie braucht an einigen Stellen echte Bilder (Karten, Karussell, Seitenverhältnis, "
        "Anhänge). Diese Bilder liegen nicht hier, sondern werden von "
        f'<code {CODE}>images.unsplash.com</code> geladen (Unsplash, Inc.). Beim Laden erfährt '
        "Unsplash die IP-Adresse, das angefragte Bild und technische Angaben zum Browser — genau "
        "wie jeder andere Server, von dem ein Bild kommt. Rechtsgrundlage ist wieder Art. 6 Abs. 1 "
        "lit. f DSGVO: eine Komponentengalerie ohne Beispielbilder zeigt nicht, was sie zeigen "
        'soll. Es werden dabei <strong>keine Cookies</strong> gesetzt. Details in der '
        f'<a href="https://unsplash.com/privacy" {LINK}>Datenschutzerklärung von Unsplash</a>.',
        "Alles andere lädt diese Seite von ihrem eigenen Server: Stylesheets, Skripte, Symbole "
        "und die Schrift. Kein Analysedienst, kein Font-CDN, kein Werbenetzwerk.",
    ]),
    ("browser", "Was in deinem Browser gespeichert wird", [
        f'Genau eine Sache, und nur weil du sie anforderst: <code {CODE}>localStorage[\'c22-pack\']</code> '
        "merkt sich, welches Design-Pack du oben ausgewählt hast, damit es beim Seitenwechsel "
        "erhalten bleibt. Keine Cookies, keine Statistik, keine Kennungen — deshalb gibt es hier "
        "auch kein Cookie-Banner. Der Eintrag verlässt dein Gerät nie; Browserdaten löschen "
        "entfernt ihn.",
    ]),
    ("verantwortung", "Wer wofür verantwortlich ist", [
        "Für den <em>Inhalt</em> dieser Seite ist die oben genannte Person verantwortlich — sie hat "
        "entschieden, ihn zu veröffentlichen. Für den <em>Server</em> ist GitHub verantwortlich: "
        "dort laufen die Maschinen, dort entstehen die Logs, dort wird über deren Aufbewahrung "
        "entschieden. Diese Seite selbst erhebt nichts, hat keine Datenbank, keine Statistik und "
        "kein Kontaktformular.",
    ]),
    ("rechte", "Deine Rechte", [
        "Art. 15–21 DSGVO geben dir Auskunft, Berichtigung, Löschung, Einschränkung, Übertragung "
        "und Widerspruch — immer gegenüber dem, <strong>der die Daten tatsächlich hat</strong>. Die "
        "Server-Logs hat GitHub, dorthin gehören Anfragen dazu. Der Betreiber dieser Seite hat "
        "nichts: keine Datenbank, keine Logs, keine Adressen, keine Sicherungen. Es gibt schlicht "
        "nichts, worüber Auskunft zu geben oder was zu löschen wäre. Eine Beschwerde bei einer "
        "Aufsichtsbehörde steht dir jederzeit offen.",
    ]),
    ("haftung", "Haftung für Inhalt und Verweise", [
        "Die Inhalte dieser Seite werden mit Sorgfalt erstellt, sind aber Dokumentation eines "
        "Bastelprojekts — keine Zusicherung. Für eigene Inhalte gilt § 7 Abs. 1 DDG; nach §§ 8–10 "
        "DDG besteht keine Pflicht, fremde Informationen zu überwachen. Verlinkte Seiten "
        "verantworten deren Betreiber; zum Zeitpunkt der Verlinkung war dort nichts rechtswidrig "
        "erkennbar. Wird ein Rechtsverstoß bekannt, wird der Verweis entfernt.",
    ]),
    ("lizenz", "Lizenz", [
        f'C22 steht unter der <a href="{REPO_URL}/blob/main/LICENSE" {LINK}>MIT-Lizenz</a> — '
        "Nutzung, Änderung und Weitergabe sind erlaubt, die Software wird „wie besehen“ und ohne "
        "Gewährleistung bereitgestellt. Das vendorte "
        f'<a href="https://basecoatui.com/" {LINK}>Basecoat</a> ist ebenfalls MIT-lizenziert; die '
        f'Symbole stammen von <a href="https://lucide.dev/" {LINK}>Lucide</a> (ISC) und '
        f'<a href="https://phosphoricons.com/" {LINK}>Phosphor</a> (MIT), die Beispielbilder von '
        f'<a href="https://unsplash.com/" {LINK}>Unsplash</a> (Unsplash-Lizenz).',
    ]),
]


def _adressblock() -> str:
    b = {k: html.escape(v) for k, v in BETREIBER.items()}
    return (
        '<address class="border-border bg-muted/40 not-italic rounded-lg border p-4 leading-7">'
        f'<span class="font-semibold">{b["name"]}</span><br>'
        f'{b["strasse"]}<br>{b["ort"]}<br>{b["land"]}<br>'
        f'<a href="mailto:{b["email"]}" {LINK}>{b["email"]}</a>'
        '</address>'
    )


def inhalt() -> tuple[str, str]:
    """Liefert (toc_html, main_html) für die Rechtsseite."""
    toc, body = [], []
    for anker, titel, absaetze in ABSCHNITTE:
        toc.append(
            f'<a href="#{anker}" class="text-muted-foreground hover:bg-muted hover:text-foreground '
            f'rounded-md px-2 py-1 text-sm">{html.escape(titel)}</a>')
        teile = "".join(
            _adressblock() if a == "ADRESSBLOCK" else f'<p {P}>{a}</p>'
            for a in absaetze)
        body.append(
            f'<section id="{anker}" class="scroll-mt-6 flex flex-col gap-4 pt-10 first:pt-0">'
            f'<h2 {H2}>{html.escape(titel)}</h2>{teile}</section>')

    main = (
        '<article class="mx-auto flex w-[820px] max-w-full flex-col gap-4 pb-24">'
        '<h1 class="scroll-m-20 text-4xl font-extrabold tracking-tight">Impressum &amp; Datenschutz</h1>'
        '<p class="text-muted-foreground text-xl leading-7">Wer diese Seite betreibt, was dabei an '
        'Daten anfällt — und was nicht.</p>'
        + "".join(body) +
        '</article>'
    )
    return "".join(toc), main
