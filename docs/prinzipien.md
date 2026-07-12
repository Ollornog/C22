# C22 · Prinzipien

Verbindliche Leitlinien für alle Bausteine. Wer einen Baustein baut, hält sie ein.

## 1. Bedeutung nie allein über Farbe (Farbsehschwäche)

Etwa **8 % der Männer** und ~0,5 % der Frauen sehen Rot/Grün eingeschränkt. Ein Zustand, der
sich **nur** durch Farbe unterscheidet (grüner vs. roter Punkt), ist für sie nicht unterscheidbar.

**Regel:** Wo Farbe Bedeutung trägt — Erfolg / Warnung / Fehler / Info, Status ok/warn/down,
gültig/ungültig, aktiv/inaktiv — kommt **immer ein zweites, farbunabhängiges Merkmal** dazu:
ein **Icon mit eigener Form** je Zustand und/oder **Text**. Farbe *verstärkt*, sie trägt nie allein.

Konkret in C22:
- **Toasts / Meldungen:** je Art ein eigenes Icon — Erfolg = Haken, Warnung = Dreieck,
  Fehler = Kreuz-im-Kreis, Info = i-im-Kreis — **plus** Farbe. Nie nur der farbige Balken.
- **Statuspunkte / Meter:** eigene Form/Icon oder Beschriftung zusätzlich zur Farbe.
- **Danger-Aktion:** Text („Löschen") + Icon, nicht nur ein roter Knopf.
- **Kontrast:** Statusfarben im Dunkelmodus aufgehellt, damit der WCAG-Kontrast zum Grund stimmt.
  Das prüft die CI (axe-core) automatisch.

Prüffrage vor jedem Merge: *„Erkenne ich den Zustand, wenn ich das Bild in Graustufen ansehe?"*
Wenn nein — ein Icon/Text fehlt.

## 2. Framework-frei über die Plattform

Erst die Browser-Plattform (`<dialog>`, Popover-API, `<details>`, `:focus-visible`, `@container`),
dann minimal JS. Kein Komponenten-Framework, kein Build.

## 3. Drei Themes über `data-theme`

`hell` / `ambient` / `dunkel` — **nicht** `light-dark()` (kann nur zwei). Jeder Baustein trägt
das aktive Theme über Tokens, ohne eigene Farb-Hardcodes.

## 4. SPOT — eine Quelle je Wiederholung (Single Point of Truth)

Was an mehreren Stellen gleich sein muss, wird **an genau einer Stelle** definiert und überall
**verwendet** — nie kopiert. Wer etwas ändern will, ändert eine Stelle, und es wirkt überall.

Konkret in C22:
- **Meldungsarten** (Fehler/Warnung/Info/Erfolg/Status/App/Fortschritt) stehen **einmal** in der
  Registry `KIND` (`c22.js`): Icon (eigene Form → Prinzip 1), Filter-Gruppe, Priorität, Label.
  **Banner, Toast, Popup und Historie** ziehen alle daraus. Die **Farbe** je Art liefert **ein**
  gleichnamiges Token (`--bad/--warn/--info/--ok/--status/--app/--progress`), angewandt über die
  Klasse `.<kind>`. Eine neue Art = ein Registry-Eintrag + ein Token, nicht sieben Copy-&-Paste-Stellen.
- **Design-Werte** (Farben, Abstände, Radien, Bewegung) stehen als **Tokens** in `tokens.css`;
  Bausteine rechnen über `var(--…)`, nie mit Hardcodes.

**Regel:** Bevor du einen Wert oder eine Fallunterscheidung zum zweiten Mal schreibst — zieh ihn in
eine Quelle (Token / Registry / Utility) und verwende die. Gilt für **jeden** Baustein, wo sinnvoll.

## 5. Mechanik vs. Look — schaltbare Achsen

Das **Verhalten** eines Bausteins (Slide, Bündelung, Fokus, Schließ-Logik …) ist konstant. Der
**Look** ist über unabhängige Achsen schaltbar, **ohne** die Mechanik anzufassen:

- **Theme (Farbe)** → `data-theme` (`hell/ambient/dunkel`, Prinzip 3)
- **Größe/Dichte** → `data-size` (`s/m/l`, skaliert über die Root-Schrift, alles in rem/em)
- **Form/Ecken** → `data-shape` (`eckig/normal/rund`) bzw. direkt `--radius-scale` (flexibler Wert,
  „Prozent"), optional je Ecke `--rc-tl/tr/br/bl` → **alle** Boxen UND Pillen/Buttons/Wechsler werden
  eckig/rund (auch das Pill-Radius `--radius-pill` skaliert mit; bei `scale 0` sind selbst Pillen kantig)
- **Icon-Gewicht** → `data-icon-weight` (`thin/light/regular/bold/fill/duotone`) — schaltet alle
  Icons zugleich. **UI-Icons** sind ein **Phosphor**-Subset (MIT) inline in `icons.js` (EINE Quelle,
  monochrom `currentColor`), das Gewicht wird zur Renderzeit gelesen; `[data-c22-ico="<name>"]`-Hosts
  rendern per `renderIcons()` neu.

**Marken-/App-Logos** (bunt, z.B. in App-Benachrichtigungen) kommen NICHT aus Phosphor, sondern aus
**selfh.st/icons** (CC BY 4.0, Attribution nötig). Sie werden vom Autor eingespeist — `opts.icon`
bzw. `item.icon` (ein `<img>` oder Inline-SVG) — und **gebündelt/self-gehostet**, nie per CDN
(kein externer Host; Offline-/Artifact-tauglich). Merksatz: **Phosphor = Bedienung, selfh.st = Marke.**

**Regel:** Ein Baustein hardcodet weder Farbe noch Radius noch Dichte noch Icon-Strich — er liest die
Achsen-Tokens/-Attribute. So macht **ein** Schalter den ganzen Look konsistent, und neue Achsen (z.B.
Schatten-Stil) lassen sich nach demselben Muster ergänzen, ohne einen einzigen Baustein umzuschreiben.
