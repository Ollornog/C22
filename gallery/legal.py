#!/usr/bin/env python3
"""Impressum und Datenschutz der veröffentlichten Galerie (`legal.html`), zweisprachig.

Eine öffentliche Projektseite ist ein Telemedium, das nicht ausschließlich persönlichen
Zwecken dient — § 18 Abs. 1 MStV verlangt dafür Name, ladungsfähige Anschrift und einen
schnellen elektronischen Kontakt. Die Angaben stehen deshalb hier und nicht verstreut im
Markup: **eine** Quelle, die der Generator in die Seite stellt.

Der Text nutzt bewusst dieselben Typografie-Utilities wie `c22/typeset/prose.html` —
die Rechtsseite ist damit selbst ein Beleg dafür, dass der Kanon trägt.

Die englische Fassung ist eine **Übersetzung zum Verständnis**; verbindlich ist die deutsche
(deutsches Recht, deutscher Anbieter).
"""
from __future__ import annotations

import html

from i18n import zwei

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
P = 'class="leading-7"'
LINK = 'class="font-medium underline underline-offset-4"'
CODE = ('class="bg-muted relative rounded px-[0.3rem] py-[0.2rem] '
        'font-mono text-sm font-semibold"')

GITHUB_PRIVACY = ("https://docs.github.com/en/site-policy/privacy-policies/"
                  "github-general-privacy-statement")

# (Anker, (Titel de, Titel en), [(Absatz de, Absatz en) …]) — die Reihenfolge ist das Menü.
# "ADRESSBLOCK" als Absatz setzt die Anbieterangaben ein.
ABSCHNITTE: list[tuple[str, tuple[str, str], list[tuple[str, str]]]] = [
    ("impressum", ("Impressum", "Imprint"), [
        ("Angaben gemäß § 5 DDG (löste am 14.05.2025 den § 5 TMG ab) und verantwortlich für den "
         "Inhalt nach § 18 Abs. 2 MStV.",
         "Details pursuant to § 5 DDG (which replaced § 5 TMG on 14 May 2025) and responsible for "
         "the content under § 18(2) MStV."),
        ("ADRESSBLOCK", "ADRESSBLOCK"),
        (f'Diese Angaben gelten für die Projektseite unter <code {CODE}>{SITE_URL}</code> und für '
         "sonst nichts. C22 ist freie Software unter der MIT-Lizenz — eine Vorlage. Wer sie auf "
         "einem eigenen Server einsetzt, betreibt einen eigenen Dienst, ist dessen Anbieter und "
         "verantwortet ihn selbst.",
         f'These details apply to the project site at <code {CODE}>{SITE_URL}</code> and to nothing '
         "else. C22 is free software under the MIT licence — a template. Anyone running it on their "
         "own server operates their own service, is its provider and answers for it themselves."),
    ]),
    ("zweck", ("Was diese Seite ist", "What this site is"), [
        ("Diese Seite ist die Galerie eines nicht-kommerziellen Open-Source-Projekts: Sie zeigt "
         "jede Komponente des Design-Systems in ihren Varianten. Sie verkauft nichts, zeigt keine "
         "Werbung und verfolgt niemanden.",
         "This site is the gallery of a non-commercial open-source project: it shows every "
         "component of the design system in its variants. It sells nothing, shows no advertising "
         "and tracks nobody."),
        (f'Der Quellcode liegt auf <a href="{REPO_URL}" {LINK}>GitHub</a>; die Seite wird bei jeder '
         f'Änderung an <code {CODE}>main</code> neu gebaut.',
         f'The source code lives on <a href="{REPO_URL}" {LINK}>GitHub</a>; the site is rebuilt on '
         f'every change to <code {CODE}>main</code>.'),
    ]),
    ("hosting", ("Hosting bei GitHub Pages", "Hosting on GitHub Pages"), [
        ("Diese Seite wird von GitHub Pages ausgeliefert (GitHub, Inc., 88 Colin P. Kelly Jr. St, "
         "San Francisco, CA 94107, USA). GitHub schreibt bei jedem Aufruf Server-Logs: IP-Adresse, "
         "Zeitpunkt, angefragte Datei, Referrer, Browser und Betriebssystem. <strong>Das passiert "
         "bei GitHub, auf GitHubs Systemen — der Betreiber dieser Seite bekommt diese Logs weder "
         "zu sehen noch kann er sie herausgeben.</strong> Rechtsgrundlage ist Art. 6 Abs. 1 lit. f "
         "DSGVO: das berechtigte Interesse, die Seite zuverlässig auszuliefern. GitHub verarbeitet "
         "Daten in den USA und ist unter dem EU-US Data Privacy Framework zertifiziert. Was GitHub "
         f'damit tut, steht in seiner <a href="{GITHUB_PRIVACY}" {LINK}>Datenschutzerklärung</a>; '
         "Anfragen zu diesen Logs richte bitte direkt dorthin.",
         "This site is served by GitHub Pages (GitHub, Inc., 88 Colin P. Kelly Jr. St, San "
         "Francisco, CA 94107, USA). GitHub writes server logs on every request: IP address, time, "
         "file requested, referrer, browser and operating system. <strong>That happens at GitHub, "
         "on GitHub's systems — the operator of this site neither sees those logs nor can hand them "
         "over.</strong> The legal basis is Art. 6(1)(f) GDPR: the legitimate interest in serving "
         "the site reliably. GitHub processes data in the USA and is certified under the EU-US Data "
         f'Privacy Framework. What GitHub does with it is set out in its '
         f'<a href="{GITHUB_PRIVACY}" {LINK}>privacy statement</a>; please address requests about '
         "those logs directly there."),
    ]),
    ("fremde-inhalte", ("Beispielbilder von Unsplash", "Example images from Unsplash"), [
        ("Die Galerie braucht an einigen Stellen echte Bilder (Karten, Karussell, "
         "Seitenverhältnis, Anhänge). Diese Bilder liegen nicht hier, sondern werden von "
         f'<code {CODE}>images.unsplash.com</code> geladen (Unsplash, Inc.). Beim Laden erfährt '
         "Unsplash die IP-Adresse, das angefragte Bild und technische Angaben zum Browser — genau "
         "wie jeder andere Server, von dem ein Bild kommt. Rechtsgrundlage ist wieder Art. 6 "
         "Abs. 1 lit. f DSGVO: eine Komponentengalerie ohne Beispielbilder zeigt nicht, was sie "
         "zeigen soll. Es werden dabei <strong>keine Cookies</strong> gesetzt. Details in der "
         f'<a href="https://unsplash.com/privacy" {LINK}>Datenschutzerklärung von Unsplash</a>.',
         "In a few places the gallery needs real images (cards, carousel, aspect ratio, "
         "attachments). Those images are not hosted here — they are loaded from "
         f'<code {CODE}>images.unsplash.com</code> (Unsplash, Inc.). In doing so Unsplash learns '
         "the IP address, the image requested and technical details about the browser — just like "
         "any other server an image comes from. The legal basis is again Art. 6(1)(f) GDPR: a "
         "component gallery without example images fails to show what it is meant to show. "
         "<strong>No cookies</strong> are set in the process. Details in "
         f'<a href="https://unsplash.com/privacy" {LINK}>Unsplash\'s privacy policy</a>.'),
        ("Alles andere lädt diese Seite von ihrem eigenen Server: Stylesheets, Skripte, Symbole "
         "und die Schrift. Kein Analysedienst, kein Font-CDN, kein Werbenetzwerk.",
         "Everything else is served from this site's own server: stylesheets, scripts, icons and "
         "the web font. No analytics, no font CDN, no ad network."),
    ]),
    ("browser", ("Was in deinem Browser gespeichert wird", "What is stored in your browser"), [
        (f'Zwei Dinge, beide weil du sie angefordert hast: <code {CODE}>c22-pack</code> merkt sich '
         f'das gewählte Design-Pack, <code {CODE}>c22-lang</code> die gewählte Sprache, und '
         f'<code {CODE}>themeMode</code> hell oder dunkel. Keine Cookies, keine Statistik, keine '
         "Kennungen — deshalb gibt es hier auch kein Cookie-Banner. Die Einträge verlassen dein "
         "Gerät nie; Browserdaten löschen entfernt sie.",
         f'A couple of things, each because you asked for it: <code {CODE}>c22-pack</code> '
         f'remembers the style pack you picked, <code {CODE}>c22-lang</code> your language, and '
         f'<code {CODE}>themeMode</code> light or dark. No cookies, no analytics, no identifiers — '
         "which is why there is no cookie banner here either. These entries never leave your "
         "device; clearing browser data removes them."),
    ]),
    ("verantwortung", ("Wer wofür verantwortlich ist", "Who is responsible for what"), [
        ("Für den <em>Inhalt</em> dieser Seite ist die oben genannte Person verantwortlich — sie "
         "hat entschieden, ihn zu veröffentlichen. Für den <em>Server</em> ist GitHub "
         "verantwortlich: dort laufen die Maschinen, dort entstehen die Logs, dort wird über deren "
         "Aufbewahrung entschieden. Diese Seite selbst erhebt nichts, hat keine Datenbank, keine "
         "Statistik und kein Kontaktformular.",
         "The person named above is responsible for the <em>content</em> of this site — they chose "
         "to publish it. GitHub is responsible for the <em>server</em>: that is where the machines "
         "run, where the logs are created and where their retention is decided. The site itself "
         "collects nothing, has no database, no analytics and no contact form."),
    ]),
    ("rechte", ("Deine Rechte", "Your rights"), [
        ("Art. 15–21 DSGVO geben dir Auskunft, Berichtigung, Löschung, Einschränkung, Übertragung "
         "und Widerspruch — immer gegenüber dem, <strong>der die Daten tatsächlich hat</strong>. "
         "Die Server-Logs hat GitHub, dorthin gehören Anfragen dazu. Der Betreiber dieser Seite "
         "hat nichts: keine Datenbank, keine Logs, keine Adressen, keine Sicherungen. Es gibt "
         "schlicht nichts, worüber Auskunft zu geben oder was zu löschen wäre. Eine Beschwerde bei "
         "einer Aufsichtsbehörde steht dir jederzeit offen.",
         "Art. 15–21 GDPR grant you access, rectification, erasure, restriction, portability and "
         "objection — always against whoever <strong>actually holds the data</strong>. GitHub holds "
         "the server logs, so requests about them belong there. The operator of this site holds "
         "nothing: no database, no logs, no addresses, no backups. There is simply nothing to give "
         "access to or delete. You may lodge a complaint with a supervisory authority at any time."),
    ]),
    ("haftung", ("Haftung für Inhalt und Verweise", "Liability for content and links"), [
        ("Die Inhalte dieser Seite werden mit Sorgfalt erstellt, sind aber Dokumentation eines "
         "Bastelprojekts — keine Zusicherung. Für eigene Inhalte gilt § 7 Abs. 1 DDG; nach "
         "§§ 8–10 DDG besteht keine Pflicht, fremde Informationen zu überwachen. Verlinkte Seiten "
         "verantworten deren Betreiber; zum Zeitpunkt der Verlinkung war dort nichts "
         "rechtswidrig erkennbar. Wird ein Rechtsverstoß bekannt, wird der Verweis entfernt.",
         "The content of this site is prepared with care, but it documents a hobby project — it is "
         "not a warranty. § 7(1) DDG applies to our own content; under §§ 8–10 DDG there is no "
         "obligation to monitor third-party information. Linked sites are the responsibility of "
         "their operators; nothing unlawful was apparent there when the link was created. If a "
         "violation becomes known, the link will be removed."),
    ]),
    ("lizenz", ("Lizenz", "Licence"), [
        (f'C22 steht unter der <a href="{REPO_URL}/blob/main/LICENSE" {LINK}>MIT-Lizenz</a> — '
         "Nutzung, Änderung und Weitergabe sind erlaubt, die Software wird „wie besehen“ und ohne "
         "Gewährleistung bereitgestellt. Das vendorte "
         f'<a href="https://basecoatui.com/" {LINK}>Basecoat</a> ist ebenfalls MIT-lizenziert; die '
         f'Symbole stammen von <a href="https://lucide.dev/" {LINK}>Lucide</a> (ISC) und '
         f'<a href="https://phosphoricons.com/" {LINK}>Phosphor</a> (MIT), die Beispielbilder von '
         f'<a href="https://unsplash.com/" {LINK}>Unsplash</a> (Unsplash-Lizenz).',
         f'C22 is published under the <a href="{REPO_URL}/blob/main/LICENSE" {LINK}>MIT licence</a> '
         "— use, modification and redistribution are permitted, the software is provided “as is” "
         "and without warranty. The vendored "
         f'<a href="https://basecoatui.com/" {LINK}>Basecoat</a> is MIT-licensed as well; icons '
         f'come from <a href="https://lucide.dev/" {LINK}>Lucide</a> (ISC) and '
         f'<a href="https://phosphoricons.com/" {LINK}>Phosphor</a> (MIT), the example images from '
         f'<a href="https://unsplash.com/" {LINK}>Unsplash</a> (Unsplash licence).'),
    ]),
]


def _adressblock() -> str:
    b = {k: html.escape(v) for k, v in BETREIBER.items()}
    return (
        '<address class="border-border bg-muted/40 not-italic rounded-lg border p-4 leading-7">'
        f'<span class="font-semibold">{b["name"]}</span><br>'
        f'{b["strasse"]}<br>{b["ort"]}<br>'
        f'{zwei(b["land"], "Germany")}<br>'
        f'<a href="mailto:{b["email"]}" {LINK}>{b["email"]}</a>'
        '</address>'
    )


def inhalt() -> tuple[str, str]:
    """Liefert (toc_html, main_html) für die Rechtsseite."""
    toc, body = [], []
    for anker, (titel_de, titel_en), absaetze in ABSCHNITTE:
        toc.append(
            f'<a href="#{anker}" class="text-muted-foreground hover:bg-muted hover:text-foreground '
            f'rounded-md px-2 py-1 text-sm">{zwei(html.escape(titel_de), html.escape(titel_en))}</a>')
        teile = "".join(
            _adressblock() if de == "ADRESSBLOCK" else f'<p {P}>{zwei(de, en)}</p>'
            for de, en in absaetze)
        body.append(
            f'<section id="{anker}" class="scroll-mt-6 flex flex-col gap-4 pt-10 first:pt-0">'
            f'<h2 {H2}>{zwei(html.escape(titel_de), html.escape(titel_en))}</h2>{teile}</section>')

    main = (
        '<article class="mx-auto flex w-[820px] max-w-full flex-col gap-4 pb-24">'
        '<h1 class="scroll-m-20 text-4xl font-extrabold tracking-tight">'
        + zwei("Impressum &amp; Datenschutz", "Imprint &amp; privacy") +
        '</h1>'
        '<p class="text-muted-foreground text-xl leading-7">'
        + zwei("Wer diese Seite betreibt, was dabei an Daten anfällt — und was nicht.",
               "Who runs this site, what data that involves — and what it does not.") +
        '</p>'
        '<p class="text-muted-foreground text-sm italic">'
        + zwei("Verbindlich ist die deutsche Fassung.",
               "The German version is the legally binding one.") +
        '</p>'
        + "".join(body) +
        '</article>'
    )
    return "".join(toc), main
