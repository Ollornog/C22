# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- **Sonner aus der Galerie entfernt — in Toast aufgegangen** (PO-Entscheid): „Sonner"
  ist nur shadcns Name für die Toast-Bibliothek — beide Einträge feuerten denselben
  Basecoat-Primitiv `.toaster > .toast` über dieselbe API an, vier von fünf
  Beispielreihen waren deckungsgleich. Die Sonner-Unikate („Alle schließen" via
  `closeAll`, robuster Trigger-Helfer) leben in Toast weiter (Helfer heißt jetzt
  `c22Toast(config, opts)`). Galerie 69 → 68.
- **Sheet aus der Galerie entfernt — in Drawer aufgegangen** (PO-Entscheid): Sheet war
  nur der shadcn-Name für dasselbe `.drawer`-Primitive (Basecoat hat kein Sheet-CSS),
  und beide Galerie-Einträge deklinierten dieselbe `data-side`-Achse doppelt durch.
  Die Sheet-Beispiele „Formular rechts" (mit Schließen-Knopf, als shadcn-„Sheet"-Muster
  ausgewiesen) und „Breite Variante" (`sm:max-w-lg`) leben jetzt als Drawer-Beispiele
  d/f weiter; der Kopfkommentar von `drawer.html` erklärt die Abdeckung. Galerie 70 → 69.

### Changed — Feinschliff-Runde 4 (PO)

- **Mehrfachauswahl-Kanon: Haken statt Hintergrund** (PO, repo-weit): angehakte
  native Checkboxen zeigen den Haken in Vordergrundfarbe auf transparentem Grund
  (Rahmen bleibt) statt der primary-Füllung; Menü-Mehrfachauswahl
  (`menuitemcheckbox`) markiert per Häkchen rechts ohne Zeilen-Füllung (vorhandene
  `[data-indicator]` werden sichtbar, ohne einen zeichnet `::after` den Haken aus
  `var(--check-icon)`). EINZELAUSWAHL (Radios, Listbox-Optionen, Kalender-Dropdown)
  behält die fette primary-gefüllte Zeile; `data-mark="indicator"` bleibt die
  explizite Alle-Indikatoren-Variante.
- **Menü-Auswahl-Kanon: Haken auch für Radios** (PO, repo-weit): Einzelauswahl in
  Menüs (`menuitemradio`) markiert jetzt wie die Mehrfachauswahl per Haken rechts
  statt fetter primary-Füllung — eine gemeinsame Kanon-Regel für beide Rollen.
  Listbox-Optionen (Select/Combobox) und das Kalender-Dropdown behalten ihre
  eigene, abgenommene Markierung. **Data Table (#21):** das Bulk-Element sitzt
  jetzt IN der Werkzeugzeile zwischen Suche und Icons (kompakte Accent-Pille
  „N ausgewählt" + Aktions-Dropdown); das **Rechtsklick-Menü entscheidet nach
  Ziel-Zeile** — markierte Zeile → Sammel-Aktionen, nicht markierte →
  Einzel-Menü (Capture vor dem Öffnen).
- **Data Table (#21): Bulk-Leiste als Zwischenzeile** (PO): die Auswahl-Leiste
  ersetzt die Werkzeugzeile nicht mehr, sondern erscheint als eigene Zeile
  ZWISCHEN Toolbar und Tabelle — Zähler links, rechts ein **Dropdown-Pfeil mit
  den Sammel-Aktionen** (Exportieren · Löschen · Auswahl aufheben); das
  **Rechtsklick-Menü wechselt bei aktiver Auswahl auf dieselben Aktionen**
  (`data-dt-cm-row`/`data-dt-cm-bulk`). „Zeilen pro Seite" ist zurück im
  Einstellungs-Flyout, vorausgewählt **„Alle anzeigen"** (`data-dt-pagesize-opt=
  "0"`); die Seitennavigation blendet sich bei nur einer Seite komplett aus und
  erscheint erst mit 5/10/20.
- **Data Table (#21): Recherche-Nachzug** (PO, Basis
  `deep-research/2026-07-19_datentabellen-ui-design.md`): **Bulk-Toolbar nach
  Carbon/Ant-Muster** — bei Auswahl ersetzt sie die Werkzeugzeile oben („N
  ausgewählt" + Exportieren/Löschen/Auswahl-aufheben, `data-dt-bulkbar`/
  `data-dt-clearselect`); die Fußzeile zeigt nur noch die Gesamtzahl.
  **Standard zeigt alle Einträge** (NN/g-Linie statt Zeilen-pro-Seite-Dropdown)
  — Pagination inkl. „Zeilen pro Seite" bleibt die eigene Variante (dort schon
  Carbon-konform links neben der Navigation); das Flyout im Einstellungs-Menü
  entfällt. **Sortierpfeil-Schacht als Kanon**: Pfeile/Rang erscheinen absolut in
  reserviertem Platz — die Spaltenbeschriftung verschiebt sich beim Sortieren
  nicht mehr (Regel aus Pencil & Paper; Position/Breite nachgemessen stabil).
- **Data Table (#21): Filter auf Facetten-Semantik korrigiert** (PO): vorher
  Excel-Stil (alles vorangehakt, Klick = abwählen) — jetzt die
  Datentabellen-Grundregel: **kein Haken = kein Filter = alles sichtbar**; ein
  Wert anklicken filtert AUF ihn (Haken + Chip + Trichter-Accent), weitere
  Klicks erweitern, Chip-X entfernt, alle angehakt wirkt wie kein Filter;
  Zurücksetzen leert die Haken. Das Spalten-Panel behält bewusst die
  Sichtbarkeits-Semantik (Haken = Spalte sichtbar).
- **Data Table (#21): Spalten-/Filter-Feinschliff** (PO): **Ausrichtung als
  Attribut** — neuer Kanon `data-type="number"` an th/td (text-end +
  tabular-nums) ersetzt die text-right-Utilities je Zelle; die POSITION regelt
  die Tabelle automatisch (erste sichtbare Spalte links, letzte sichtbare läuft
  bis zur rechten Kante — rechts anzeigen ≠ rechtsbündig). **Filter-Chips nur
  bei aktivem Filter** (alle Werte gewählt = keine Chips). Die Filter-Panels
  sind jetzt selbst stille Menü-Kompositionen: **„Sortieren" als
  nicht-klickbare Gruppen-Überschrift** (role=heading) mit den drei Einträgen
  direkt darunter (statt Klappmenü), **„Filtern" als Überschrift über den
  Chips**; Werte-/Spaltenlisten unter Überschriften leicht eingerückt (Kanon).
- **„Stilles" Dropdown-Menü als komponierte Variante** (PO 21a/#29): Das
  Einstellungs-Menü war handgestrickt (btn-Zeilen = zu luftig, eigene
  Überschrift) — jetzt ist es eine reine Component-Kombination: `class="popover
  dropdown-menu"` + vorgesetztes `data-dropdown-menu-initialized` lässt das
  Vendor-Menü-CSS (kompakte Einträge, role=heading, Trenner) wirken, ohne dass
  das Menü-Schließ-JS bindet (Einstellungs-Panels bleiben beim Klicken offen);
  der Eintrag-Hover ist als Kanon nachgereicht (Vendor koppelt ihn an sein JS).
  Neue Galerie-Variante in Dropdown Menu (#29) zeigt das Muster. Dazu drei echte
  Flyout-Fixes: Vendor-`[data-popover]` clippt per overflow-x-hidden — Popover
  mit `[data-submenu]` geben den Overflow frei (das Flyout war unsichtbar UND
  unklickbar); Zuklapp-**Gnadenfrist** 300ms (der diagonale Mausweg zum Panel
  verlässt den Eintrag kurz — nachgemessen am 8-Schritt-Pfad) plus unsichtbare
  Hover-Brücke über die 4px-Lücke. Außerdem: Tabellen frieren ihre Höhe nach
  `document.fonts.ready` neu ein — die Fallback-Font-Messung ließ beim Laden
  unten Luft, die erst beim Seitenwechsel verschwand.
- **Data Table (#21): Einstellungs-Menü neu geordnet** (PO): Zahnrad-Icon
  (lucide settings) als EINZIGES Werkzeug neben der Suche; Menüaufbau: Zeile 1
  „Filter zurücksetzen", Zeile 2 „Zeilen pro Seite" als **Rechts-Flyout**
  (neuer Kanon `[data-submenu]`/`[data-submenu-panel]`, öffnet bei Hover/Fokus
  neben dem Auslöser), darunter „Spalten" **im Filter-Combobox-Stil**: Chips der
  sichtbaren Spalten (X blendet aus) über der Spaltenliste mit Haken
  (`data-dt-colpanel`, gleiche wireFilterCombo-Quelle) — inklusive Suchfeld im
  Chips-Feld wie in 18e (tippen filtert die Spaltenliste, Leer-Hinweis); das
  funnel-x-Icon steht ZUSÄTZLICH wieder in der Toolbar (Reset-Anker mehrfach
  verdrahtbar). Der **Zähler** steht
  jetzt in derselben Zeile wie der Seitenwechsler (der springt nicht mehr) und
  zeigt ohne Auswahl die Gesamtzahl („12 Einträge") statt sich auszublenden.
- **Data Table (#21): Vollausbau verfeinert** (PO): **jede Spalte** ist jetzt
  filter- UND sortierbar (Trichter mit Sortieren-Submenü auch an E-Mail/Betrag;
  lange Wertelisten scrollen im Panel); Suche und die zwei Werkzeug-Icons teilen
  sich EINE Zeile dicht über der Tabelle; das **Einstellungs-Icon bündelt alles
  mit Untermenüs** („Spalten" ein/aus + „Zeilen pro Seite" als Menü-Radios — der
  Fußzeilen-Select entfällt; Falle behoben: wireMenuChecks stoppt die
  Capture-Propagation, der Radio-Listener sitzt deshalb am Menü). Der
  **Auswahl-Zähler** ist klein (text-xs), sitzt direkt unter der Tabelle und
  erscheint nur bei Auswahl; die **Zeilen-Checkboxen sind unsichtbar**, bis die
  Zeile gehovert, markiert oder fokussiert ist (Kopf-Checkbox bleibt);
  **Rechtsklick-Aktionen sind im Standard aktiv** (Context Menu um die Tabelle).
  **Doppelrahmen-Fix (i):** die letzte SICHTBARE Zeile verliert ihren
  Unterstrich (der Vendor kannte nur :last-child — bei Pagination/Filter ist die
  letzte sichtbare selten das letzte Kind). Suche mit echten Tastenanschlägen
  verifiziert (funktionierte auch vorher — bei Bedarf hart neu laden).
- **Data Table (#21): Standard = Vollausbau** (PO): a) vereint jetzt alles —
  Suche (umbenannt von „Filtern"), Auswahl (Checkbox + Zeilenklick + Zähler),
  **Mehrspalten-Sortierung** mit stillen Icons (kein Doppelpfeil im Ruhezustand,
  Pfeil erst bei aktiver Sortierung), **Spaltenfilter-Trichter erst bei
  Kopf-Hover** (Kanon; offen/aktiv/fokussiert bleibt sichtbar), im Filter-Panel
  ein **Sortieren-Submenü** (aufsteigend/absteigend/nicht sortieren,
  `data-dt-sortdir` — wirkt auf die Spalte des Panels), oben rechts **nah an der
  Tabelle** Filter-Reset (funnel-x) und ein **Einstellungs-Icon** (Spalten
  ein-/ausblenden), plus nummerierte Pagination mit Zeilen-pro-Seite.
  **Höhenverhalten jetzt Variante:** Standard hält die Tabellengröße, neue
  Variante `data-dt-shrink` lässt sie mit dem Inhalt schrumpfen (eigenes
  Beispiel). Alle Datenbeispiele haben jetzt **12 Einträge** (Zeilenaktionen/
  Rechtsklick bleiben bewusst bei 3 — dort geht es ums Menü); SPOT: alles über
  dieselben `data-dt-*`-Anker, keine Sonderlogik je Beispiel.
- **Spaltenfilter-Popover repariert** (PO 21e/f): `wireTableMenu` fand die
  Popover-Trigger nicht (suchte `aria-haspopup`, Popover-Trigger tragen nur
  `aria-expanded`) — die Panels blieben absolut im `.table-container` und ließen
  ihn scrollen; zudem explodierte das fix positionierte Panel auf Viewport-Breite
  (Vendor `min-w-full` bezieht sich bei `position: fixed` plötzlich auf den
  Viewport → inline neutralisiert). Und: die Panels erben im fetten Spaltenkopf
  das font-bold — `[data-filter-combo]` setzt jetzt `font-normal text-start`,
  abgewählte Einträge stehen normal.
- **Tabellen schrumpfen nicht mehr — Standard** (PO): fehlende Einträge (Filter,
  kurze Seiten) verkleinern die Tabelle nicht mehr — die Höhe des vollen Zustands
  bleibt als min-height eingefroren, nichts schiebt sich (ersetzt den
  margin-Ausgleich, der den Abstand hielt, die Tabelle selbst aber sichtbar
  schrumpfen ließ). **Filter-Combobox jetzt wirklich wie 18e:** die Auswahl
  erscheint als **Chips mit Entfernen-X** im Suchfeld (gleiche Vendor-Klassen
  `.combobox-chip`/`-chip-remove` wie die Multi-Combobox); Chip-X wählt ab und
  filtert die Tabelle mit, Zurücksetzen stellt die Chips wieder her
  (`c22-fc-change`/`c22-fc-refresh`-Ereignisse).
- **Combobox (#18): neue Variante „Als Filter-Dropdown"** (PO): die komplette
  Mehrfachauswahl-Combobox (18e) lebt in EINEM Popover — Trichter-Trigger,
  Suchfeld filtert die Liste, Klick togglet die Auswahl, Leer-Hinweis bei null
  Treffern; kein Dropdown im Dropdown. Kanon `[data-filter-combo]` + `wireFilterCombo`;
  dazu neuer Kanon: **Mehrfachauswahl-Listboxen** (`aria-multiselectable`) markieren
  per Haken statt Füllung (gleiche Linie wie menuitemcheckbox/Checkbox; die
  Combobox selbst behält ihren Vendor-Haken). **Data Table nutzt sie:** die
  Spaltenfilter (e/f) sind jetzt Filter-Comboboxen statt Checkbox-Menüs.
  **Mehrspalten-Sortierung:** sekundäre/tertiäre Schlüssel tragen ²/³ hinter dem
  Pfeil (primär bleibt unmarkiert). **Zurücksetzen (f)** ist ein Icon-Knopf
  (funnel-x) statt Textknopf.
- **Data Table (#21), fünfte Runde** (PO): **Icon-Bug behoben** — `svg.hidden = …`
  ist bei SVG nur eine JS-Expando (`hidden` ist HTMLElement-IDL), die Sortier-Pfeile
  wechselten deshalb nie und die früheren Asserts lasen die eigene Expando zurück;
  jetzt `toggleAttribute` (auch beim Slider-Stummschalter). Beim Sortieren wird aus
  dem Doppelpfeil der Richtungspfeil, Zyklus unsortiert→auf→ab→unsortiert.
  **Neu:** d) Mehrspalten-Sortierung (`data-dt-multisort` — zuletzt geklickt =
  primär, vorige bleiben sekundäre Schlüssel); e) **Spaltenfilter** statt
  Freitextsuche (Trichter-Icon je Spalte, Dropdown mit an-/abhakbaren Werten,
  aktiver Filter zeigt den Pressed-Accent); f) Sortieren & Filter kombiniert
  **mit Zurücksetzen-Knopf** (`data-dt-reset` leert Suche, Filter und
  Sortier-Stapel); h) Zeilenaktionen **per Rechtsklick** (gleiches Menü als
  Context Menu). Zeilenmenüs öffnen jetzt nach unten UND **nach rechts**
  (Start-bündig); die Höhen-/Platzreserve gegen springende Fußzeilen ist
  **Standard für alle Data Tables** (auch beim Filtern), nicht nur bei Pagination.
- **Galerie: Abhängigkeits-Anzeige je Component** (PO): unter jedem Titel steht
  jetzt „nutzt: …" und „genutzt von: …" — abgeleitet aus kuratierten
  Markup-Signaturen (`SIGNATURES` in build.py, ein eindeutiger Marker je
  Component; Icon bewusst ausgenommen, es steckt in fast jedem Partial). Die
  Einträge verlinken auf die jeweilige Sektion.
- **Data Table (#21), vierte Runde** (PO): Sortieren zykliert jetzt
  **unsortiert → auf → ab → unsortiert** (die dritte Stufe stellt die
  Ursprungsreihenfolge wieder her, Icon zurück auf neutral, aria-sort entfällt).
  Neue Varianten **„Mit Filter"** und **„Sortieren & Filter kombiniert"**.
  Zeilenmenüs öffnen wie bei shadcn **unter dem Trigger, Ende-bündig** (Delta 0px
  nachgemessen; data-side="left" bleibt möglich) — die „Flug-Animation von oben"
  ist weg (Koordinaten werden übergangsfrei gesetzt; Breite per offsetWidth
  statt Rect, das die Scale-Öffnungsanimation verfälschte). **Zellpolster auf den
  Vendor-Kanon normalisiert** (SPOT): 120 von Hand wiederholte `px-3 py-2`/`px-2
  py-2` entfernt — Data Table nutzt jetzt dieselben shadcn-Zellmaße wie das
  Table-Primitiv (th `px-2 h-10`, td `p-2`); Sonderfälle (Checkbox-Spalte,
  Sortier-Köpfe) bleiben explizit.
- **Audit-Runde (autonom):** Galerie-Linie „keine RTL-Demos außerhalb von
  Direction" ist jetzt **mechanisch geprüft** (Hygiene-Regel 13); die letzte
  verbliebene RTL-Demo (Textarea) ist entfernt. Konsolen-Sweep über die ganze
  Galerie (Laden + 51 Trigger auf/zu): null Fehler/Warnungen; keine doppelten
  IDs über alle Partials. Sheet-Restverweis in einem CSS-Kommentar bereinigt,
  veraltete Galerie-Nummer in CLAUDE.md neutralisiert.
- **Data Table (#21), dritte Runde** (PO): **Dropdown-/Scrollbalken-Ursache
  gefunden** — schon die GESCHLOSSENEN Popover (opacity-0, absolut positioniert)
  blähten den Scrollbereich des `.table-container` auf: dauerhafter vertikaler
  Scrollbalken, der beim Öffnen sprang, und geclippte Menüs. Neuer Ansatz
  `wireTableMenu`: Popover in Tabellen sind ab Verdrahtung `position: fixed`
  (raus aus dem Container-Fluss), beim Öffnen kommen die Viewport-Koordinaten
  (data-side="left" links neben den Trigger, sonst darunter, an den Viewport
  geklemmt) — Container bleibt durchgehend scrollbar, nichts springt; die
  Overflow-Umschalt-Regel ist ersetzt. **Sortierte Spalte sichtbar** (c): der
  aktive Spaltenkopf trägt den Accent-Zustand, nicht nur den Pfeil. **Tabelle
  endet am letzten Eintrag** (e): statt den Rahmen auf volle Seitenhöhe zu
  ziehen, endet die Tabelle mit der letzten Zeile — der Platz der vollen Seite
  bleibt als margin-bottom reserviert, die Fußzeile steht fest.
- **Data Table (#21), zweite Runde** (PO): Auswahl per **Zeilenklick ist Standard**
  (Klick irgendwo auf der Zeile togglet; Bedienelemente bleiben unberührt,
  Zeiger-Cursor auf den Zeilen) + neue Variante „Auswahl per Zeilenklick" ohne
  Checkbox-Spalte (`data-dt-rowselect`, Zähler zählt `data-state`). Die
  Auswahlspalte ist schmal (`w-px`, pe-1) — die Folgespalte beginnt direkt.
  Pagination hält die **Tabellenhöhe stabil** (volle Seitenhöhe wird als minHeight
  eingefroren — die Fußzeile springt auf kürzeren Seiten nicht mehr hoch). Die
  Overflow-Freigabe des `.table-container` greift jetzt für alle Popover-Arten
  (`aria-expanded` ODER offenes `data-popover`).
- **Data Table (#21) funktional + fette Köpfe + Dropdown-Fix** (PO): neues
  `wireDataTable` (c22.js) macht die komponierten Muster echt — Filter siebt
  Zeilen, Zeilenauswahl pflegt `data-state=selected`, Zähler und
  Alle-auswählen-Checkbox, das Spalten-Menü blendet Spalten ein/aus
  (`data-dt-col`), Spaltenköpfe sortieren zyklisch auf/ab (`data-dt-sort=
  "text|number|date"`, aria-sort am `th`, Icon-Trio folgt), und die Pagination
  paginiert wirklich (12 Demo-Zeilen, Zeilen-pro-Seite-Select 5/10/20,
  nummerierte Knöpfe generiert, Rand-Knöpfe disabled). Spaltenbeschriftungen
  jetzt fett (font-bold, auch in den Sortier-Buttons). Kanon-Fix:
  `.table-container` (overflow-x-auto) kappte offene Dropdowns — solange ein
  Menü darin offen ist (`:has([aria-expanded='true'])`), wird der Overflow
  freigegeben.
- **Table (#56) / Data Table (#21) ausgedünnt** (PO-Entscheid: kein Merge — Primitiv
  vs. Komposition, wie Bubble/Message): die deckungsgleichen Doppel-Beispiele sind
  raus — „Einfache Tabelle (nur Lesen, mit Caption)" aus Data Table (= Table a),
  „Mit Zeilenaktionen" aus Table (Interaktion gehört in die Komposition, bleibt
  Data Table c). Kopfkommentare verweisen jetzt gegenseitig.
- **Switch (#55): Pille exakt mittig + Variante „Switch am Zellenanfang"** (PO):
  Der Vendor-Track ist `1.15rem` = 18.4px hoch — der 0.4px-Bruchteil verteilt sich
  beim Pixel-Snapping ungleich, die 16px-Pille hing sichtbar außermittig
  (nachgemessen 9/17 Achtel-Pixel oben/unten). Kanon-Fix: 18px Track ⇒ 16px
  Innenhöhe = exakt Pillenhöhe, jetzt 11/11. Neue Karten-Variante mit dem Switch
  am Zeilenanfang (Text rechts daneben), als Ergänzung zu „Switch am Zeilenende".
- **Progress (#45): Ring-Variante im Spinner-Stil** (PO): neuer Kanon
  `.progress-ring` — ein Ring, der sich ab 12 Uhr im Uhrzeigersinn füllt
  (conic-gradient primary/muted, per Radial-Maske zum Ring gestanzt; Dicke =
  Balkenhöhe h-1.5). Wert über `--progress` wie bei `.progress-surface`, Größe per
  `size-*`, Statusfarben über `data-variant` (gleiche Rollen wie Balken/Slider);
  Beispiel mit zentriertem Prozentwert im Ring. **Attachment (#5d)**: neue
  Zustand-Zeile „Fortschrittsring" — der Ring sitzt in der `.item-media`-Kachel,
  wo sonst der Spinner dreht (Kontext-Kanon: Icon-Maßstab size-5, Ringdicke 3px,
  Rest-Track in Hintergrundfarbe — muted wäre auf der muted-Kachel unsichtbar),
  mit Prozent/Größen-Angabe und Abbrechen/Stopp-Aktionen wie die Nachbarzeilen.
- **Toast (#60): Alert als Design-Vorlage** (PO): Toasts sprechen jetzt dieselbe
  Status-Sprache wie Alert/Badge — die Kategorie-Icons bekommen die Status-Token
  (`success`/`warning`/`info`, error = `destructive`-Rolle); vorher färbte
  `data-category` im Vendor NICHTS, Erfolg/Fehler/Warnung sahen farblich identisch
  aus. **Zusatz-Variante `data-variant="mono"`**: alles einfarbig, nur das
  Fehler-Icon bleibt rot (exakt Alerts Schema; „mono" neu im Varianten-Vokabular
  als Nicht-Farb-Ausführung). **Anatomie = Alert:** das Icon sitzt oben links neben
  dem Titel (Grid, translate-y-0.5) statt vertikal mittig; Aktions-Spalte bleibt
  rechts. **Hintergrund-Variationen:** `data-variant="tinted"` = getönter
  Status-Hintergrund (gleiches Muster wie `.alert[data-variant='warning']`:
  `border-<rolle>/40` + `bg-<rolle>/10`), `data-variant="ghost"` = ohne
  Hintergrund. **Geteilte Größenleiter:** Standard-Toast = S (13px),
  `data-size="lg"` = EXAKT die Alert-Maße (text-sm, px-4 py-3, Icon size-4 —
  nachgemessen identisch), `sm` = kompakte Stufe darunter. Da das Vendor-JS das
  Toast-Markup generiert, stempelt der Galerie-Helfer `c22Toast()` Variante/Größe
  auf den erzeugten Toast — kein Vendor-Eingriff. Nebenbei-Fix: das
  Aktion-Beispiel übergab `action` ohne `href`/`onclick` — der Vendor rendert den
  Knopf dann gar nicht, es erschien nur „Später".
- **Slider (#53) bedienfreundlicher**: Zeiger-Cursor auf dem ganzen Regler und der
  Hover-Ring des Griffs zündet beim Hover irgendwo auf dem Slider (Kanon-Regel;
  Vendor löste ihn nur auf dem Thumb-Pseudo selbst aus). **Neue Variante
  „Mit Stummschalter"** (`data-mute` + `wireMute`): der Knopf setzt den Füllstand
  auf die Track-Hintergrundfarbe (`data-muted` — Track wirkt leer, kein Ausgrauen,
  bleibt bedienbar) und tauscht auf das Durchgestrichen-Icon; Klick/Ziehen im
  Regler entstummt wieder. **Vier shadcn-Varianten nachgebaut, die Basecoat bewusst
  auslässt:** „Bereich" (zwei Griffe) und „Mehrfach" (drei Griffe) über den neuen
  Kanon `[data-slider-multi]` — native Range-Inputs deckungsgleich gestapelt, nur
  die Griffe nehmen Zeiger-Events an, die Hülle malt die Füllung zwischen kleinstem
  und größtem Wert (`wireMultiSlider` klemmt Griffe an ihre Nachbarn). Track-Klick
  springt wie beim einfachen Slider: der DICHTESTE Griff springt an die Klickstelle
  und bleibt bei gehaltener Maus gegriffen (Pointer-Capture auf der Hülle; bei
  übereinanderliegenden Griffen gewinnt der in Klickrichtung), Zeiger-Cursor auch
  auf dem Track, und beim Track-Hover zeigt der dichteste Griff den Hover-Ring
  (`data-hover` — kündigt an, wen ein Klick greifen würde);
  „Vertikal" (`data-orientation="vertical"`, natives Element via `writing-mode:
  vertical-rl` + `direction: rtl` → min unten, Füllung nach oben, Griff-Querversatz
  über die Block-Achse); „Gesteuert" (Bereich + Live-`<output>`, Wert von außen
  gelesen/gesetzt). **Nach Basecoat nachgezogen:** eigenes
  „Deaktiviert"-Beispiel (stand nur im Formularfeld-Beispiel) und die
  Wertanzeige (b) auf das Basecoat-Markup (`label`-Klasse + `grid gap-1` statt
  Roh-Utilities). **Skala-Kanon
  `[data-slider-scale]`**: Beschriftungen sitzen mittig unter ihrem Ankerpunkt
  (Position `--p` = value/max, rechnet den Thumb-Versatz ein — mit justify-between
  saßen die mittleren Werte links vom Anker). RTL-Demo entfernt (Galerie-Linie).
- **Separator (#50): drei neue Varianten nach shadcn-Base** — „Vertikal" (eigenes
  Beispiel), „Menü" (vertikale Linien zwischen mehrzeiligen Einträgen) und „Liste"
  (horizontale Linien zwischen `dl`-Zeilen); „Standard" zeigt jetzt rein horizontal
  zwei Textblöcke (die Vertikal-Zeile ist ins eigene Beispiel gewandert). Dabei Kanon-Fix: der Preflight setzt
  `hr { height: 0; border-top: 1px }` — die explizite Höhe schaltete
  `align-self: stretch` ab, vertikale Separatoren kollabierten in auto-hohen
  Flex-Zeilen auf den 1px-Border. `.separator[data-orientation='vertical']` ist
  jetzt wie im shadcn-Base-Original `w-px self-stretch` (+ `h-auto border-none`
  gegen den Preflight) statt `h-full` — füllt damit auch Zeilen ohne feste Höhe;
  die Werkzeugleisten-Linie behält ihre `h-5!`-Kappung (`self-center`).
- **Message-Fußzeile: Aktions-Elemente erst bei Hover** (SPOT): Kopieren und React-Knopf
  in `data-reactions`-Fußzeilen erscheinen erst beim Hover der Blase oder der Fußzeile
  (Deckkraft statt display — die Chips springen nicht); **Reaktions-Chips bleiben immer
  sichtbar**. Der Blasen-Chevron bekommt einen **großzügigen Halo in Blasenfarbe** —
  als Radial-Verlauf INNERHALB der Knopf-Box (`--bubble-bg` je Variante) statt
  box-shadow, damit er geometrisch nie über die Blase hinausläuft; die Blase hält zur
  Chevron-Seite etwas mehr Textabstand (24px, beidseitig symmetrisch), und der
  Ghost-Hover-Schleier ist auf dem Chevron-Knopf aus — Highlight kommt allein vom
  Chevron selbst (60 % → 100 %).
  **Reaktions-Zähler:** bei EINER Reaktion nur das Emoji, die Zahl erscheint ab zwei
  (`wireReactions` blendet den Zähler um, auch bei bestehenden Chips).
- **Message-Nachschliff:** Chevron-Knopf erbt die Blasen-Textfarbe auch beim Hover (der
  Ghost-Hover färbte sonst auf accent-foreground — schwarz auf dunkler Blase); die
  Fußzeile spannt in der Blasen-Spalte die **volle Blasenbreite** (Hover-Fläche zum
  Einblenden = ganze Breite; d/e beidseitig in `data-bubble-col`); der Datei-Anhang (f)
  hat einen **Download-Knopf**.
- **Scroll Area (#48) + Select (#49) auf den Scrollbar-Kanon** (SPOT-Fund): beide nutzten
  Basecoats `.scrollbar-sm` direkt statt des Kanons `.scrollbar` + `data-size="sm"`
  (Scrollbar #67) — vereinheitlicht. **Neue Kanon-Größe `data-size="thin"` (4px)**:
  48 zeigt sie als eigene Variante neben dem wiederhergestellten „Kompakt" (sm), das
  Kanon-Zuhause #67 führt sie ebenfalls (Firefox-Abbildung auf `scrollbar-width: thin`).
  RTL-Beispiele in beiden entfernt (Galerie-Linie).
- **Select (#49): der Trigger füllt die Hülle** — Vendor setzte `width: fit-content`
  (Knopfbreite folgte der Beschriftung, Position/Panel wirkten dagegen beliebig); jetzt
  bestimmt der `.select`-Container Knopf UND Panel gemeinsam, wie bei Input/Native
  Select (`.select:not(select) > button { w-full }`). Die Beispielhüllen waren mit
  `max-w-xs` (320px) überbreit — kompakte Demobreiten (w-48, Zeitzonen w-64;
  Formularfeld-Beispiele bleiben bewusst in voller Feldbreite).
- **Select (#49): Größen als S/M/L** — neue `data-size="lg"`-Ausführung (h-10, C22-Regel;
  der Vendor kennt nur Standard/sm), Reihenfolge Klein · Standard · Groß in einer Zeile.
  Das Zustände-Beispiel (e) tanzte aus der Reihe (`w-full`-Kinder rissen das Flex-Raster
  auseinander und klebten links) — feste Breiten, sauber zentriert.
- **Resizable (#47): Trennlinien-Varianten im shadcn-Stil** — `data-resize-handle`
  zwischen zwei Panels mit schlankem, dickerem Griff (`data-resize-grip`, 6×32px-Pill)
  in der Mitte. **Standard: nur der Griff zieht** (PO); die Variante
  `data-resize-handle="line"` zieht an der ganzen Linie (unsichtbar verbreiterte
  Greif-Fläche). Neue Verdrahtung `wireResizeHandle` (Pointer-Capture, ändert die
  flex-basis des Panels davor; Grenzen = dessen min-/max-Klassen, vertikal via
  flex-col automatisch). „Drei Panels" und „Verschachtelt" laufen jetzt ebenfalls über
  die Standard-Trennlinien (der innere Quer-Teiler via `aria-orientation="horizontal"`
  — der Kanon kann beide Ausrichtungen); das native Vertikal-Beispiel ist raus, ein
  CSS-`resize`-Beispiel bleibt als „Nativ"-Alternative.
- **Labels zeigen die Zeigehand** (PO 46a): `label[for]` und Labels mit eingebettetem
  (nicht deaktiviertem) Eingabefeld sind im Cursor-Kanon.
- **Popover (#44) nach der Basecoat-Quelle vervollständigt:** Standard (Titel +
  Beschreibung, w-72), **Ausrichtungs-Trio** (`data-align` start/center/end, w-56),
  **alle sechs Seiten** (`data-side` top/right/bottom/left/inline-start/inline-end,
  w-40), Formular mit vier Maß-Feldern; die Praxis-Beispiele Aktionen (align end)
  und Profilkarte (side right) bleiben. RTL nach Galerie-Linie ausgelassen.
- **42c:** geöffnete Untermenü-Chevrons zeigen nach **links** (zum Panel hin: zu = −90°,
  offen = 90°) statt nach unten.
- **Progress (#45):** RTL-Beispiel entfernt (Galerie-Linie).
- **Navigation Menu (#42) neu geschnitten:** a) **Standard ohne Container** — alle vier
  Menü-Bauformen in einer Leiste (Produkte einspaltig · Komponenten zweispaltig mit
  **unabhängigen Kartenhöhen** [zwei flex-Spalten im Grid statt ausgerichteter
  Grid-Zeilen, gemischt 1–3-zeilige Beschreibungen nach der shadcn-Vorlage] · Erkunden
  mit Bild · Lösungen als **horizontale Icon-Zeilen** mit 40px-Icon-Box) plus aktive
  Seite ohne Unterstrich; b) **mit Container und Unterstrich** (aktive Seite);
  c) **Vertikal ohne Container** mit aktiver Zeile und ALLEN Bauformen aus a
  (Untermenüs öffnen per `data-side="right"`). `data-rich` erzwingt `text-start`
  (der Beispiel-Wrapper vererbte sonst Zentrierung in mehrzeilige Beschreibungen).
- **Navigation Menu (#42) entschlackt:** neuer Kanon `data-rich` für mehrzeilige
  Menü-Einträge (Titel + Beschreibung, Icon-Grid, Bild-Karte) — ersetzt die
  `flex-col!`-Utility-Ketten aus der Vor-Layer-Entmachtungs-Zeit; einheitliches
  Abstands-Raster (py-2, gap-0.5, gemessen identisch über alle Einträge),
  **Beschreibungen dürfen mehrzeilig umbrechen** (der abgeschnittene Text unterm Bild
  ist damit vollständig) und **Link-Menü-Einträge zeigen die Zeigehand**
  (`a[role="menuitem"]` im Cursor-Kanon — der Vendor erzwang cursor:default).

- **Tippt-Indikator: Standard = gefüllte Punkte** in Seiten-Punkt-Größe (8px), sanft
  pulsierend; `data-typing="bounce"` = hüpfend, `"pulse"` = stark pulsierend. Dabei den
  9-vs-39-Unterschied (Ovale vs. Kreise) gefixt: die Punkte sind Flex-Kinder und wurden
  ohne `shrink-0` im schmalen Container horizontal gequetscht — jetzt im SPOT quetschfest. **Chronologie-Kanon:** der Verlauf liest sich von
  oben nach unten, die neueste Nachricht steht unten — Tippen daher immer als unterste
  Zeile (Status-Beispiel entsprechend umsortiert); die Blasen-Spitze zeigt weiterhin
  nach oben zum Absender.
- **Fußzeilen-Kanon für Nachrichten** (PO): erlaubte Aktionen sind Kopieren · Antworten ·
  Reagieren („+"/React-Knopf mit Schnellauswahl 👍 ❤️ 🎉) · Info · Löschen, plus
  „Erneut senden" nur bei Fehlschlag. **Zuordnung:** das Gegenüber bekommt Antworten ·
  Kopieren · Info (+ Reagieren), die eigene Seite Kopieren · Info · Löschen. Beispiele
  c–e folgen dem Kanon **beidseitig**: c) Aktionszeile bei Hover, d) Reaktions-Chips
  beidseitig immer sichtbar, e) **neu: Chevron-Menü AUF der Blase** — der Trigger liegt
  als Overlay über dem Inhalt (`data-bubble-menu`, SPOT: kein reservierter Platz), beim
  Gegenüber rechts oben, bei mir links oben; er erscheint beim Hover der Blase und wächst
  dabei deutlich auf (20px-Chevron, Scale 0.75 → 1.1). Menü-Inhalt Antworten/Info bzw.
  Info/Löschen (destruktiv, entfernt die Nachricht — `data-message-delete`, neue
  Verdrahtung). **Kopieren + React-Knopf sind dauerhaft sichtbar** (Größe = SPOT mit c,
  icon-sm; von außen 6px eingerückt), Fußzeilen-Reihenfolge auf BEIDEN Seiten gleich und
  links-nach-rechts: Kopieren · Reagieren · Chips. **Reaktions-Chips landen immer rechts
  vom React-Knopf** (auch neu hinzugefügte — `wireReactions` hängt ans Ende statt vor
  das „+"; d entsprechend umgestellt). Die Absender-Fußzeile ist **linksbündig an der
  Blasenkante** (neue SPOT-Spalte `data-bubble-col`; die 80%-Breitenbremse wandert dabei
  von der Blase auf die Spalte, sonst ragt die Fußzeile links raus). Chevron-Kontrast:
  Ruhe 60 % Deckkraft, beim Hover des Knopfs 100 % — auch auf der dunklen Primary-Blase
  klar sichtbar.
- **Bubble (#9) und Message (#39) sauber getrennt** (PO): Bubble ist jetzt das reine
  **Primitiv** (Form, Varianten, Gruppierung, Ghost, Tippt — 5 Beispiele); **Reaktionen
  und Fehlgeschlagen sind zu Message umgezogen**, denn sie sind Fußzeilen einer
  Nachricht, keine Eigenschaft der Blase.
- **Message hat jetzt EINE kanonische Zeilen-Anatomie** (`.message` in components.css,
  SPOT): Avatar oben verankert · `<header>` mit Name + `<time>` **immer oben** (beim
  Absender per `data-align="end"` gespiegelt) · Inhalt (`.bubble`/`.bubble-group`/
  `data-typing`) · `<footer>` als **einziger Fuß-Slot** für Status ODER Aktionen
  (`data-message-actions`) ODER Reaktionen (`data-reactions`). Alle Beispiele füllen
  nur noch Slots — die früheren Streuungen (Zeit mal oben/mal unten, wechselnde
  Flex-Ketten) sind strukturell unmöglich. Aktionszeilen blenden bei
  `.message:hover`/Fokus ein.

- **Pagination (#43) entschlackt:** „Am Rand ausgegraut" und „Mit Eingabe der Seitenzahl"
  entfernt — beides ist seit der Fensterlogik redundant (Standard graut am Rand
  automatisch aus; die Sprung-Variante hat das Eingabefeld). Übrig: Standard · Kompakt ·
  Sprung+Eingabe · Rand ausgeblendet · Punkte mit Knöpfen · Punkte s/m/l · Einfach.
- **Sprechblasen-Spitze zeigt jetzt nach OBEN** (Bubble #9 + Message #39, ein Kanon in
  components.css): fast komplett spitz (2px statt 4px), sitzt an der dem Absender
  zugewandten oberen Ecke; in `.bubble-group` behält nur die **oberste** Blase die
  Spitze (vorher unten/letzte). MessageGroup verankert den Avatar passend oben.
- **Tippt-Indikator ist SPOT** (`data-typing` auf `.bubble`, drei leere `<span>`):
  zwei Ausführungen mit kräftigerer eigener Animation — Standard hüpfend (Überhöhung +
  Aufhellen), `data-typing="pulse"` pulsierend (Größe + Deckkraft). Beide als Varianten
  bei Bubble 9g; Message 39e nutzt dasselbe Markup.
- **Message-Anhänge (39d) sind echte `.bubble`** (vorher handgerollte Divs ohne
  Ecken-Kanon) — Bild- und Datei-Anhang bekommen damit automatisch Spitze und Varianten.
- **Message-Aktionszeile ist SPOT** (`[data-message-actions]`): Hover-/Fokus-Einblendung
  aus einer Regel statt kopierter Utility-Ketten. **39c ist funktional:** Kopieren
  kopiert den Blasentext (`data-copy` + `data-copy-scope`, mit Haken-Feedback),
  Gut/Schlecht sind ein gegenseitig ausschließendes `aria-pressed`-Paar
  (`data-feedback`, neue Verdrahtung `wireFeedback`).

- **Pagination (#43) um vier Varianten erweitert:** Seitenzahl **eintippbar** (Zurück ·
  „Seite [Feld] von 12" · Weiter), **Punkte mit Richtungsknöpfen** (erste Seite, Zurück
  ausgegraut), **nur Punkte** in drei Größen (`data-size="sm"`/Standard/`"lg"`) und
  **Randfall „ausgeblendet"** — der Zurück-Knopf ist per `invisible` versteckt statt
  ausgegraut, der Platz bleibt reserviert (nichts springt).
- **Pagination ist jetzt funktional** (`wirePagination` in c22.js, Verdrahtung über
  `data-pagination`): Zahl-Listen laufen über die **Standard-Fensterlogik mit IMMER
  7 Elementen** — bis Seite 4 `1 2 3 4 5 … n`, ab n−3 gespiegelt, dazwischen
  `1 … i−1 i i+1 … n`; bei n ≤ 7 alle (Zahl-/Ellipsen-Knöpfe werden je Stand aus den
  Markup-Vorlagen neu erzeugt, die Ellipse ist ein typografisches „…" auf der
  Grundlinie statt des mittigen Icon-Punkte-Trios), Punkte wechseln die Seite,
  Richtungs-/Sprungknöpfe werden an ihren Chevron-Icons erkannt (±1 bzw. Anfang/Ende),
  Zahlenfeld und „Seite X von Y"-Zähler werden mitgepflegt (Eingabe klemmt auf 1…max).
  **Randverhalten an beiden Enden:** Knöpfe grauen aus — Links per `aria-disabled`
  (neue SPOT-Regel `.btn[aria-disabled='true']`, Links können kein `disabled` tragen) —
  bzw. ein anfangs unsichtbarer Knopf blendet sich aus/ein. Die Sprung-Variante (c)
  zeigt die Seitenzahl jetzt als **echtes Eingabefeld** (vorher ein Knopf, der wie ein
  Input aussah — Klick tat nichts). Das Seitenzahl-Feld ist schmaler (w-12).
- **Menü-Checkboxen/-Radios schalten um statt zu schließen** (`wireMenuChecks`, PO 38c):
  ein Klick auf `menuitemcheckbox`/`menuitemradio` togglet `aria-checked` (Radio räumt
  seine Gruppe) und lässt das Menü offen — Basecoats Schließ-Handler sieht den Klick
  nicht mehr (Capture-Phase). Normale Einträge schließen weiter. Menubar 38c nutzt
  jetzt den Indikator-Kanon (`data-mark="indicator"` — Haken/Punkt statt
  Hintergrund-Füllung, wie Dropdown 26c/d).
- **Punkt-Kanon verschmolzen (SPOT):** Carousel- und Pagination-Punkte teilen EINE Regel;
  der sichtbare Punkt ist jetzt ein `::before` im Zentrum eines **größeren, aneinander
  anschließenden Klickbereichs** (Punkt-Container ohne gap, Pitch = Knopfbreite; Standard
  8px Punkt / 16px Klick, sm 6/12, lg 12/24). Beim Carousel pixelgenau ohne optische
  Änderung verifiziert (Punktmitten identisch), Overlay-Punkte samt Schatten umgezogen.

- **Kalender (#12) neue Variante `data-clearable`:** ein „Löschen"-Knopf neben „Heute"
  entfernt die Auswahl (feuert `c22:calendar-change` mit `selected: null`; der Datums-Input
  leert dann sein Feld).
- **C22-Datumsfeld (31a):** Kalender-Icon rechts im Feld, das Kalender-Panel öffnet in
  **Eigenbreite** statt Feldbreite (`min-w-0` gegen Vendors `min-w-full`), und der Kalender
  ist `data-clearable`.
- **Suchfelder:** WebKits nativer Lösch-Knopf ist abgeschaltet — das C22-Lösch-X ist der
  Kanon (31b zeigte sonst zwei X).
- **Datums-Input:** das Kalender-Icon zeigt die Zeigehand und öffnet den Kalender (die
  Feld-Hülle zählt als Feldfläche, kein Außenklick mehr); **eine Datumswahl schließt den
  Kalender** — „Heute", Blättern und „Löschen" halten ihn offen. Gilt für alle
  `data-date-input`-Felder (31a, Date Picker e/h).
- **Marker (#37) ist jetzt eine echte SPOT-Component `.marker`** (Vorbild shadcn Base
  „Marker"): vorher waren alle Varianten rohe Utility-Ketten im Markup. Neu in
  components.css — Grundzeile (Icon-Größe aus der Klasse, wie bei `.btn`),
  `data-variant="bordered"` (Unterstrich), `data-variant="separator"` (zentriertes Label,
  Linien als `::before`/`::after` statt Span-Hack), `a.marker`/`button.marker` polymorph
  klickbar (Hover hebt Text + unterstreicht). Beispiele nach der shadcn-Demo aufgebaut:
  a) ist ein **komponierter Konversationsverlauf** (Branch-Wechsel · „Denkt nach …" mit
  Spinner/Shimmer · Trennlinie „Unterhaltung komprimiert" · „4 Dateien durchsucht"),
  dazu **Gestapelt** (`flex-col`, Icon über dem Inhalt — „Synchronisierung abgeschlossen"),
  Rahmen 3-zeilig, drei Trennlinien-Label, zwei Ladezustände, Link + Button. Der **Link**
  trägt seinen Unterstrich dauerhaft (Link-Konvention wie in der Quelle), der Button bleibt
  ohne; beide heben beim Hover die Textfarbe. Der **Stapel-Abstand ist SPOT**:
  `.marker + .marker` (48px) in components.css statt gap-Utilities im Markup,
  einheitlich für alle Varianten inklusive der gerahmten Zeilen.
  Vokabular um den Strukturwert `separator` erweitert (tests/test_conventions.py).
- **Native Select (#41):** RTL-Beispiel entfernt (gleiche Linie wie Item/Label); alle
  6 Basecoat-Quell-Varianten sind abgedeckt, dazu Feld- und Input-Gruppen-Einbau.
- **Label (#36):** RTL-Beispiel entfernt (Linie wie bei Item — für die deutsche Galerie ohne
  Mehrwert); das **schwebende Label** (`.field[data-float]`) ist von Field (#28) hierher
  umgezogen — es ist eine Label-Bauform, die CSS-Regel bleibt unverändert in components.css.
- **Kbd Sondertasten (35b) erweitert:** Umschalt (⇧ arrow-big-up), Windows-Taste (grid-2x2),
  Befehlstaste ⌘ (command), Optionstaste ⌥ (option) und „Entf" ergänzt.
- **Tastengruppen-Kanon `.kbd-group` (#35, SPOT):** Kombinationen benachbarter Tasten haben
  jetzt überall EINEN Abstand (4px, wie die Kürzelspalten der Menüs) — vorher streuten
  Sondertasten-Reihe und Eingabefeld-Span auf 8px (Vendor). „+"-Kombinationen rücken mit
  `data-join="plus"` enger zusammen (2px). Umgestellt: Kbd a–d, Input Group (kbd-Variante),
  Empty (Suchfeld).
- **Item (#34) mit allen Basecoat-Quell-Varianten vervollständigt** (basecoatui.com/components/item):
  neu sind Verifizierungs-Link (`a.item` klein mit Icon + Chevron), **Avatar-Gruppe**
  (`.avatar-group` in `figure`), **Medienliste** (Vorschaubild in `figure`, zweite `section`
  rechtsbündig für die Dauer), externer Link (`target="_blank"` + external-link-Icon) und
  **Item im Dropdown-Menü** (`span.item border-0 p-0 shadow-none` in `role="menuitem"`).
  Bewusst ausgelassen: die RTL-Demos der Quelle (arabische Beispiele — für die deutsche
  Galerie ohne Mehrwert). Vorgangsstatus (j): „Läuft"-Badge mit Spinner, „Fertig" mit
  Haken; `header`/`footer` grenzen sich per Trennlinie (`border-b`/`border-t`) vom
  Inhalt ab.
- **Input OTP (#33) ist jetzt interaktiv** (`wireOtp` in c22.js, SPOT über `.input-otp-slot`):
  Tippen springt automatisch ins nächste Feld; Backspace leert ein gefülltes Feld und
  bleibt dort (die nächste Eingabe gehört in die frei gewordene Stelle), erst in einem
  leeren Feld springt es zurück und leert das vorige. Fokus markiert den Inhalt — Tippen in ein
  beschriebenes Feld **überschreibt** den Wert. Zeichenfilter aus dem `pattern`-Attribut
  (Buchstaben prallen an Ziffern-Slots ab), Pfeiltasten navigieren, Einfügen verteilt den
  Code ab dem fokussierten Feld.
- **Input Group Suche mit Ergebnisanzahl (32b):** das Lösch-X steht jetzt **links** der
  Ergebnisanzahl, mit Abstand zum Zähler. Der Kanten-Kanon (Klickbereich wächst nach links) greift dabei nur noch
  für Icon-Knöpfe, die tatsächlich das letzte Element am Feldrand sind — mittige Knöpfe
  bleiben symmetrisch.

### Changed — Feinschliff-Runde 3 (PO)

- **Datumsfeld (31a):** das native `type="date"` ist ein geschlossenes Browser-Widget
  (Schatten-DOM-Segmente, verhält sich als EIN Block) — es zeigt jetzt den **Text-Cursor**;
  daneben steht ein **C22-Nachbau** aus Textfeld + C22-Kalender (`data-date-input` mit
  Monat/Jahr-Dropdown): tippen inklusive Vervollständigung, Kalender-Klick schreibt zurück.
- **Lösch-X auch in 31b** (Suche mit Icon, relative-Bauform): sichtbar sobald Text im Feld
  steht — **unabhängig vom Fokus** —, Klick leert und fokussiert; die geteilte Regel deckt
  jetzt `.input-group` und `.relative` ab.

### Changed — Feinschliff-Runde 2 (PO)

- 32h: In Aktionsgruppen (mehrere Icons) wächst der Klickbereich NICHT nach links — die
  Gruppe bleibt kompakt, nur der letzte Knopf trägt die Glyphen-Kante zum Rand.
- 31a: Cursor-Regel fürs native Kalender-Symbol zurückgenommen (Reset auf vorher).
- 32b: **Lösch-X** erscheint, sobald Text im Feld steht (`data-clear` + `:placeholder-shown`);
  Klick leert und fokussiert das Feld.
- 32d: Klick auf ein Text-Präfix/-Suffix fokussiert das Feld (Affixe gehören optisch zur
  Feldfläche, Text-Cursor inklusive) — gilt für alle input-groups.
- 32k: Senden-Knopf in Primärfarbe.

### Changed — Feinschliff-Runde (PO)

- Kontextmenü e): Untermenü-Schließverzögerung 300 → **400 ms**.
- Data Table: markierte Zeilen hovern mit **halbem** Schleier (vom Token abgeleitet — voll
  war zu kräftig).
- Uhr (22c): unmarkierte Kappen hovern per Schleier — accent ging auf dem muted-Zifferblatt
  farblich unter.
- Stepper (22d): **Durchschreiben** — zwei Stunden-Ziffern springen automatisch ins
  Minutenfeld (Inhalt vorgewählt, „0745" läuft in einem Zug durch); Rückwärtslöschen läuft
  vom leeren Minutenfeld ins Stundenfeld weiter.
- Affix-Strippen (32d) erst beim **Verlassen** des Feldes (change) — live wirkte es, als
  verschwänden Zeichen beim Tippen.
- **Knöpfe im input-group malten beim Hovern einen hellen Rahmen** zum Container: `.btn`
  clippt seinen Hintergrund auf die padding-box und trägt einen transparenten 1px-Rahmen —
  im Gruppenkontext jetzt `background-clip: border-box` (31e, 32h u. a.).
- Datumsfeld (31a): das native Kalender-Symbol zeigt den Zeiger-Cursor.
- Passwort-Auge (32f): **Standard zeigt nur, solange gedrückt wird** (Guckloch);
  `data-password-toggle="toggle"` ist die Klick-Toggle-Variante — beide im Beispiel.
- Spinner im Feld (32i) auf `size-8` (32 px — füllt die Feldzeile, kanonische lg-Stufe aus #62).
- Icon-Knöpfe im input-group (32f/g/h) einheitlich auf `data-size="icon-sm"` — dieselbe
  Größe wie der Kalender-Knopf des Date Pickers (SPOT für Feld-Icon-Knöpfe).
- **Rand-Icon-Knöpfe folgen dem optischen Ausrichtungs-Kanon** (PO): die Glyphe sitzt auf
  der Textkante des Feldes (pe-2.5 = Input-Padding, vorher klebte sie ~3 px am Rand), der
  Klickbereich wächst unsichtbar nach links (~40 px breit) und bleibt bündig bis zur Kante —
  auch für den letzten Knopf in Aktionsgruppen und die Zahl-Stepper. Der Lade-Spinner rückt
  auf dieselbe Kante.
- Textarea-Fußzeile (32k): der Zähler sitzt direkt links neben dem Senden-Knopf.

### Changed — Review-Runde: Kontextmenü, Data Table, Uhr, Input-Group-Paket (PO)

- **Kontextmenü:** d) Checkboxen & Radiogruppe nutzt wieder Haken-/Punkt-Indikatoren
  (`data-mark="indicator"`); e) das Hover-Untermenü schließt mit 300 ms Verzögerung
  (Diagonalweg zum Untermenü klappte sofort zu), Öffnen bleibt verzögerungsfrei.
- **Data Table (21):** markierte Zeilen (`data-state="selected"`) hovern per Schleier
  (muted über muted war stumm).
- **Date Picker Uhr (22c):** die markierte Kappe trägt `aria-pressed` und hovert per
  inversem Schleier. **Stepper (22d):** Stunden/Minuten sind echte Eingabefelder — Uhrzeit
  eintippbar (Ziffernfilter, Grenzwerte 23/59, Normalisierung beim Verlassen), die
  Hoch/Runter-Knöpfe arbeiten weiter.
- **Input Group (32):** c/k) Kopfzeilen-Label in primary, Fußzeilen-Zähler klein (text-xs);
  d) Text-Präfixe starten auf der Textkante UND das Feld streift mitgetippte Präfixe/Suffixe
  automatisch ab (`wireAffixStrip`, gilt für alle input-groups); f) das Passwort-Auge
  funktioniert (`data-password-toggle`: type-Umschaltung, Icon-Wechsel eye/eye-off über
  aria-pressed); g/h) Kopieren-Knöpfe kopieren wirklich und bestätigen mit Haken
  (`wireCopy` kann jetzt auch Feldwerte); h/j) Aktions-Gruppen und Dropdown-Hüllen am Ende
  sitzen bündig in der Ecke (Vendor zog mit −4px-Margin über die Kante, plus Block-Padding),
  minimaler Knopfabstand; i) der Spinner eierte — asymmetrisches Vendor-Padding verschob das
  Rotationszentrum, Abstand jetzt als Margin; j) Zahl mit Einheit ist rechtsbündig;
  l) aria-invalid ringt die GRUPPE statt des inneren Felds (wie der Fokus-Kanon).
- **Zahlfelder generell:** Standard ist OHNE native Hoch/Runter-Pfeile; neue Input-Variante
  „Zahl mit Steppern" mit eigenen Knöpfen (`data-number-step`, c22.js).

### Added — Date Picker: Android-Uhr, Zeit-Stepper, Datums-Eingabe

- **Uhr im Android-Stil (`data-clock`, c22.js):** Zifferblatt mit Stundenwahl in zwei Ringen
  (außen 1–12, innen 13–00), danach automatisch Minuten im 5er-Raster; Zeiger + gewählte
  Kappe in primary. Kopf wahlweise als klickbares HH:MM oder mit `data-input` als **echtes
  Eingabefeld**: nur Ziffern/`:` erlaubt, der `:` wird bei vier Ziffern automatisch gesetzt
  (`1100` → `11:00`, `11:00` geht ebenso), beim Verlassen wird normalisiert, und die
  Caret-Position wählt den Zifferblatt-Modus (vor dem `:` Stunden, dahinter Minuten).
  In c) „Mit Uhrzeit (Uhr)" steht die Uhr **immer** als zweite Spalte neben dem Kalender
  (gleiches Layout wie die Bereichsauswahl über 2 Monate), das Zeit-Feld sitzt über dem
  Zifferblatt — unter dem Kalender gibt es kein Uhrzeit-Feld mehr.
- **Zeit-Stepper (`data-time-stepper`, c22.js), neue Variante f):** je zwei Hoch/Runter-Knöpfe
  für Stunde und Minuten; Minuten springen immer auf 00/15/30/45 und tragen beim Umlauf in die
  Stunde über (±1), Stunden laufen 23↔0 um. Die Datumsauswahl im Kalender bleibt davon
  unberührt.
- **Geburtsdatum per Texteingabe (`data-date-input`, c22.js), neue Variante g):** ein
  Eingabefeld statt Button — Fokus/Klick öffnet das Kalender-Popover (eigene Verdrahtung,
  Basecoats Popover akzeptiert nur `<button>` als Trigger), Klick außerhalb/Escape schließt.
  Tippen übernimmt das Datum live in den Kalender und **vervollständigt unsichtbar** aus der
  aktuellen Auswahl: `12` → Tag 12 im Monat/Jahr der Auswahl, `1204`/`12.4` → 12. April im
  Jahr der Auswahl; dazu die vollen Formen `tt.mm.jjjj`, `tt.mm.jj`, `ttmmjjjj`, `ttmmjj`.
  Nur Ziffern und Punkte kommen durch, und bei reiner Ziffernfolge setzen sich die **Punkte
  automatisch** (`1204` → `12.04`, `150788` → `15.07.88`); beim Verlassen wird auf
  `tt.mm.jjjj` normalisiert. Zweistellige Jahre werden pivotiert (über dem aktuellen jj →
  19xx, sonst 20xx — `150788` → 15.07.1988). Ein Kalender-Klick schreibt das Datum
  formatiert zurück ins Feld. Neues Kalender-API dafür: `c22:calendar-set` (Auswahl setzen +
  Monat anzeigen) als Gegenstück zu `c22:calendar-change`.
- **„Per Texteingabe" in zwei Varianten:** e) das Feld trägt `data-date-input` — Fokus/Klick
  ins Feld öffnet den Kalender sofort, Tippen steuert ihn mit derselben Formatierung und
  Vervollständigung; f) klassisch — das Feld bleibt passiv, nur das Kalender-Symbol öffnet.
- **Varianten neu sortiert:** a) Einzeldatum · b) Zeitraum · c) Mit Uhrzeit (Uhr) ·
  d) Mit Uhrzeit (Stepper) · e) Per Texteingabe (Feld öffnet sofort) · f) Per Texteingabe
  (nur Symbol) · g) Geburtsdatum (Monat/Jahr-Dropdown) · h) Geburtsdatum per Texteingabe.

### Changed — Modal-Öffnen entzerrt (Entry-Jank-Gegenmittel)

- Beim `showModal()` hob der Browser Dialog + `::backdrop` aus `display:none` in den Top Layer
  und startete **im selben Frame** die Eintritts-Transition — Layer-Aufbau, Erst-Rasterung und
  Animationsstart kollidierten, der Einstieg ruckelte (der „warme" Exit lief glatt; PO-Befund
  an #23/#25, Recherche mit Quellen im Tower-Kontext). c22.js patcht `showModal` für
  `.dialog`/`.alert-dialog`/`.drawer` nach dem Muster von Material Components/Headless UI:
  ein per Doppel-`requestAnimationFrame` gehaltener Startzustand (`c22-open-hold`,
  `components.css`, `opacity: .001` — Deckkraft 0 dürfte der Browser beim Malen überspringen
  und der Erst-Raster fiele doch in den ersten sichtbaren Frame) gibt dem Browser erst einen
  committeten Frame für den Aufbau, dann läuft der Übergang regulär. Der `::backdrop` wird
  bewusst nicht festgehalten: die Abdunklung fadet sofort ab Frame 1 (Klick-Feedback ohne
  gefühlte Latenz), nur das teure Panel wartet den Aufbau ab. Öffnen ohne JS verhält sich
  unverändert wie vorher.

### Changed — Neuer Auswahl-Kanon: gewählte Einträge fett + primary-gefüllt (PO)

- **Der gewählte Eintrag wird überall gleich markiert** — fett + primary-gefüllte Zeile
  (vorher Dropdown-Variante `data-mark="bold bg"`, 26f): eine geteilte Kanon-Regel in
  `components.css` für Menü-Radios/-Checkboxen (dropdown/context-menu), Listbox-Optionen
  (select/combobox, ersetzt Basecoats Haken rechts) und das Kalender-Monat/Jahr-Dropdown
  (#12, dort entfällt auch der reservierte Haken-Platz). Haken-/Punkt-Indikatorspalten sind
  jetzt die **explizite Variante** `data-mark="indicator"` am Menü; die data-mark-Werte
  `bold`/`bg` entfallen. Dropdown-Menu-Galerie (#26) umgebaut: c) Checkboxen und
  d) Radiogruppe zeigen die Standard-Markierung, e) Haken- und f) Punkt-Indikator sind die
  Varianten. Zustands-Schautafel (#69d) und CLAUDE.md-Konvention entsprechend aktualisiert.

### Changed — Hover-Schleier-Rollout, Schritt 2: Big Bang

- **`--hover-veil-invers` auf 18 %** (PO: Primary-Hover etwas kräftiger).
- **Restliche Flächen-Hovers auf den Schleier umgestellt:** Link-/Button-Badges (primary →
  invers; secondary/outline/ghost → normal, outline/ghost ohne Vendor-Umfärbung von Fläche
  und Text), interaktive `.item`-Zeilen (statt Vendor-`bg-muted`) und **gedrückte Buttons**
  (`aria-pressed` — Toggles, Reaktions-Chips): die behalten beim Hovern ihre accent-
  Druckfläche plus Schleier, statt vom Varianten-Reset weggewischt zu werden.
- **Bewusst NICHT umgestellt:** accent-Hovers in Menüs/Listen/Kalender (dort IST accent der
  Hover-Effekt — er muss identisch zur Tastatur-Markierung bleiben), Link-Unterstreichungs-
  Hover, Carousel-Punkte (Deckkraft-Stufung).
- **Markierte (primary-gefüllte) Zeilen hovern jetzt auch** (PO 12e): Kalender-Monat/Jahr-
  Dropdown, Kanon-markierte Menü-Radios/-Checkboxen und Listbox-Optionen bekommen beim
  Hovern den inversen Schleier über der Markierung — vorher war die gewählte Zeile
  hover-stumm (`hover:bg-primary` war ein No-op).

### Changed — Hover-Schleier-Rollout, Schritt 1: Buttons

- **Alle Button-Varianten hovern jetzt per Schleier statt Prozentfarbe:** ein transparenter
  Schleier legt sich als `background-image` über die unveränderte Grundfläche (Text/Icons
  unberührt) — kontrastfarbige Flächen (primary) nehmen das neue Token
  `--hover-veil-invers` (background-basiert, 14 %: hellt Dunkles im Hellmodus auf, dunkelt
  Helles im Dark-Theme ab), neutrale Flächen (secondary, muted, outline, ghost — und
  destructive, dessen Grundfläche nur eine 10-/20-%-Tönung ist) den foreground-basierten
  `--hover-veil`. Vendor-Hover-Prozentfarben sind neutralisiert;
  `link` behält seinen Unterstreichungs-Hover, Menü-/Listen-Hover (accent) bleiben als
  eigener Kanon unangetastet. Verifiziert je Variante in hell UND dunkel (echter
  CDP-Maus-Hover).

### Changed — Layer-Entmachtung: Basecoat liegt jetzt in einer eigenen Kaskaden-Ebene

- Die Vendor-Komponentenregeln werden in eine **eigene `@layer vendor`-Ebene unterhalb von
  `components`** importiert (Build-Entry + `input.css`): jede C22-Regel gewinnt damit per
  Kaskaden-Layer gegen Basecoat — egal wie spezifisch der Vendor-Selektor ist. Die bisher
  nötigen Spezifitäts-Workarounds (verdoppelte/verdreifachte Selektoren gegen die
  `:is(…)`-Bomben) bleiben vorerst stehen und werden schrittweise zurückgebaut.
  `base/base.css` bleibt ungelayert (enthält `@custom-variant`/`@theme`, die Tailwind nicht
  in `layer(…)` schachteln kann; ihre Regeln stecken intern ohnehin in `@layer base/theme`).
  Verifiziert: 10 Galerie-Scrollabschnitte vorher/nachher pixelidentisch, Suiten grün.
- **Bau-Härtung:** Der Tailwind-CLI meldet Fehler bei Exit 0 — das stille `>/dev/null` in
  `build-gallery.sh` ließ kaputte Builds als Erfolg durchgehen (alte Pack-CSS blieben
  liegen). Der Bau bricht jetzt laut ab, wenn Tailwind einen Error meldet.

### Added — Hover-Schleier-Token + bündige Gruppenrand-Knöpfe (PO)

- **Neues Token `--hover-veil`** (`color-mix(in oklab, var(--foreground) 8%, transparent)`):
  ein theme-adaptiver, transparenter Hover-Schleier für Flächen, deren Hover sonst in der
  eigenen Farbe unterginge — macht Helles im hellen Theme dunkler und Dunkles im Dark-Theme
  heller; als `background-image` aufgetragen, die Grundfarbe bleibt darunter stehen.
  Erste Anwendung: der secondary-Chip des Datei-Uploads (31c).
- **Knöpfe am Gruppenrand sitzen bündig in der Ecke** (geteilte Regel): direkte `.btn`-Kinder
  einer input-group mit `data-align` am Anfang/Ende bekommen volle Höhe, Kante an Kante und
  die Gruppenrundung — Basecoat schob sie mit `margin-inline` von der Kante weg, die
  Hover-Fläche schwebte sichtbar im Feld (31e; gilt jetzt überall, auch Passwort-Auge und
  Kopieren-Knopf in #32).

### Changed — Input/Input-Group-Runde (PO)

- **Feld-Notizen noch dichter am Feld** (`-mt-1.5`) — und die Regel greift jetzt wirklich:
  Basecoats eigene Positions-Overrides (`.field > p:last-child { mt-0 }`, Spezifität 0,2,1)
  schluckten den negativen Margin bisher komplett; mit gespiegelten `last:`/`nth-last-2:`-
  Varianten nachgezogen.
- **Datei-Upload (31c): der native Auswahl-Knopf ist der LINKE TEIL des Feldes** — volle
  Höhe, secondary-Füllung, bündig an Rahmen und linker Rundung (wie ein integrierter
  Gruppen-Knopf, nur gefüllt; `::file-selector-button`, Selektoren verdoppelt — Basecoats
  Sammel-`:is(…)` setzt Padding/Hintergrund mit ~0,3,3).
- **Fokus-Kanon für Kombinationen:** Das Textfeld trägt den Fokus, aber OPTISCH ringt der
  Container — in jeder input-group (Suche integriert 31e, alle 32er). Der Kind-Reset ist
  dreifach geklasst, weil Basecoats `.input`-Fokusregel über ihr Sammel-`:is(…)` sonst
  gewinnt und das Feld zusätzlich ringte.
- **Input (31): RTL-Variante entfernt** (Rechts-nach-links zeigt #24 Direction); dafür zwei
  neue Such-Varianten — **integriert** (rahmenloser Ghost-Knopf in der input-group) und
  **separat** (Feld + eigenständiger Knopf daneben); der fehl am Platz wirkende
  Outline-„Suchen"-Knopf aus der Input-Group a) ist dorthin umgezogen.
- **Input Group (32) aufgefüllt** (nach Basecoat-/shadcn-Doku): a) wieder pur (Icon + Feld),
  neu **Suche mit Ergebnisanzahl** („12 Ergebnisse" als inline-end-Text) und **Label oben /
  Zeichenzähler unten** (`block-start`/`block-end` am einzeiligen Feld).

### Changed — Zweite Nachschärfung: Combobox fett, Field-Feinschliff, schwebendes Label (PO)

- **Combobox (#18): Haken UND fett** — die gewählte Option behält den Vendor-Haken und wird
  zusätzlich fett (weiterhin ohne Füllung).
- **Field-Notizen zusätzlich eingerückt** (`ps-2.5` = die Textkante des Inputs).
- **Fieldset-Legende hatte keinen Abstand zum ersten Feld** (28d gestapelt): Legends nehmen
  am Flex-Gap nicht teil und Basecoat nullt die Margin der label-Variante explizit — mit
  gleicher Spezifität auf `mb-2` nachgezogen.
- **Field i) neue Variante „Schwebendes Label"** (`.field[data-float]`, rein CSS über
  `:placeholder-shown`): das Label liegt im Feld und schiebt sich bei Fokus oder Inhalt auf
  den Rahmen (Hintergrund maskiert die Rahmenlinie); leer + unfokussiert wandert es zurück.

### Changed — Nachschärfungen am Auswahl-Kanon + Field-Runde (PO)

- **Combobox (#18) bleibt komplett bei der Häkchen-Markierung** — vom Auswahl-Kanon
  ausgenommen (`:not(.combobox *)`), dort gilt weiter Basecoats Haken rechts.
- **Dropdown-Menu (#26): c) Checkboxen und d) Radiogruppe wieder wie vorher** mit Haken- bzw.
  Punkt-Indikator (jetzt explizit via `data-mark="indicator"`); der Kanon (fett + gefüllt)
  wird in einer eigenen Variante e) gezeigt.
- **Date Picker c): das Uhrzeit-Feld sitzt mittig** über dem Zifferblatt (`.input` ist
  inline-block — ohne `block` griff `mx-auto` nicht).
- **Field: alle Notizen unterm Feld teilen eine Optik** — klein (`text-xs`, wie der
  Fehlertext) und dichter am Feld; der Fehlertext bleibt nur farblich die rote Ausnahme
  (geteilte Regel in `components.css`).
- **Field d) Responsiv ist jetzt testbar:** in einem per Griff ziehbaren Container
  (`resize-x`), und beide Inputs sind gleich breit (feste Label-Spalte statt Textbreite).
- **Field h) neue Variante „Mit Tabs":** drei Reiter mit unterschiedlichen Feld-Elementen
  (Profil: Text + Textarea · Mitteilungen: Switches · Zahlung: Select + IBAN-Feld) auf
  Basis der Tabs-Component.

### Fixed — input-group: Icongröße und Fokus-Sitz

- Nackte Icon-SVGs im input-group jetzt `size-4.5` (18 px — 16 px war in der Feldzeile zu
  zierlich, PO 27f).
- **Der Fokusring sitzt auf der GRUPPE, nicht auf dem inneren Feld** (ein Feld = ein Rahmen
  = ein Ring): `.input-group:has(:focus-visible)` übernimmt den kanonischen Fokuslook
  (`border-ring` + `ring-ring/50`), das Kind bleibt ring- und outlinefrei.

### Changed — Field (#28d): Labels einzeilig

- Die responsiven Adress-Labels „Straße & Hausnummer"/„PLZ & Ort" brachen in der
  Label-Spalte um — gekürzt auf „Straße"/„Ort" (die Platzhalter tragen das Detail).

### Fixed — Drawer: Scroll ist ab dem Schließen-Klick sofort frei

- Basecoats drawer.js überschreibt `close()` mit einer JS-Choreografie (erst `data-closing`,
  ~Animationsdauer warten, dann natives close) — der Drawer blieb dadurch die gesamte
  Ausfahranimation **modal**, die Seite inert und der Scroll gesperrt (PO: „nach dem Schließen
  bleibt der Scroll hängen"). c22.js **versiegelt** `close` auf Drawer-Dialogen wieder mit dem
  nativen close (nicht beschreibbare Property — Basecoat initialisiert nach uns, seine spätere
  Zuweisung prallt still ab; Esc/Backdrop-Klick rufen weiter `close()` und landen im nativen):
  Der Dialog verlässt den Modal-Zustand **sofort beim Klick**, die Ausfahranimation läuft rein
  in CSS weiter (`transition-discrete` + `overlay` halten Element und ::backdrop bis zum
  Animationsende sichtbar) — exakt das Muster, mit dem der Dialog es schon immer macht.

### Removed — Beta-Marker in der Galerie

- Die „Beta"-Badges an Komponenten-Überschriften (Chart #15, Drawer #25) sind entfernt —
  samt Beta-Flag in `gallery/build.py`; die Komponentenliste führt nur noch
  (title, basecoat, shadcn, custom).

### Changed — Dialog #23b: Sektion scrollt jetzt wirklich

- Der scrollbare Bedingungstext war mit acht Kurzzeilen so kurz, dass der Scrollweg nur
  wenige Pixel betrug — jeder Radtick schlug sofort am Ende an, was sich wie Ruckeln anfühlte.
  Jetzt 20 ausführliche Absätze (~1150 px Scrollweg), damit Rad-, Balken- und Schwungscrollen
  realistisch beurteilbar sind.

### Fixed — input-group: nackte Icon-SVGs wurden bildschirmbreit

- Ein Icon-SVG als direktes Kind eines `.input-group` ohne `size-*`-Klasse rendert in voller
  Breite über dem Feld (SVG ohne width/height dehnt sich im Flex-Container aus; aufgefallen
  in Empty 27f, betraf 7 Stellen in Empty/Combobox/Input Group). Neue geteilte Regel: die
  Gruppe dimensioniert nackte SVGs auf `size-4` — wie `.btn` es für seine Icons tut; eigene
  `size-*`-Klassen gewinnen weiterhin.

### Fixed — input-group: doppelter Rahmen der Kind-Inputs

- Trägt das Kind im `.input-group` wie in allen C22-Beispielen die Klasse `.input`, gewann
  dessen Rahmenregel (`.input[type='text']`, Spezifität 0,2,1) gegen Basecoats Entrahmung
  (`.input-group > input`, 0,1,1) — Gruppe UND Input zeichneten je einen Rahmen (aufgefallen
  im Date Picker e, betraf alle input-groups). Neue geteilte Regel in `components.css` zieht
  mit passender Spezifität nach: `.input`-Kinder im input-group sind wieder rahmen-, radius-
  und schattenlos, den Rahmen stellt die Gruppe.

### Fixed — Carousel-Autoplay tickt nur noch, wenn es sichtbar ist

- Autoplay setzte sein programmatisches Smooth-Scrolling (eine Main-Thread-Animation) alle
  paar Sekunden fort, auch wenn das Carousel längst aus dem Viewport gescrollt oder von einem
  modalen Dialog verdeckt war — auf der langen Galerie-Seite ließ das sichtbare Scroller
  periodisch ruckeln (gemeldet als Stottern im Dialog #23b; im echten Fenster gemessen:
  Frame-Ausreißer bis 133 ms im 3-Sekunden-Takt des Autoplays). Jetzt pausiert Autoplay
  außerhalb des Viewports (IntersectionObserver) und solange ein modaler Dialog offen ist,
  und läuft danach weiter.

### Changed — Date Picker auf den SPOT-Kalender umgestellt

- **Date Picker (#22) nutzt jetzt den Kalender aus #12** statt fünf handgebauter, statischer
  Kalendertabellen: jedes Popover enthält ein `<div data-calendar …>` (c22.js) — Blättern,
  Auswahl, Bereich mit Vorschau, „Heute"-Sprung und Monat/Jahr-Dropdown funktionieren damit
  auch im Date Picker; Kalender-Optik/-Logik lebt nur noch an EINER Stelle. Im Popover trägt
  der Kalender `p-3` statt `rounded-lg border p-3` — den Rahmen stellt das Panel.
- **Kalender-Klick schloss das Popover** (Fix in `c22.js`): `render()` ersetzt das Raster per
  `innerHTML`; beim Eintreffen des Klicks an `document` war der geklickte Button schon
  ausgehängt und Basecoats `panel.contains(e.target)`-Prüfung hielt den Klick für „außerhalb".
  Gerendert wird jetzt erst nach dem Bubbling (`setTimeout(0)`) — Tag wählen und Blättern
  lassen das Popover offen (dasselbe Detached-Node-Muster wie beim Kontextmenü).
- **Monat/Jahr-Dropdown wurde vom Popover abgeschnitten** (Fix in `components.css`): Basecoats
  `[data-popover]` scrollt (`overflow: hidden auto`) und clippte das absolut positionierte
  Menü; solange es offen ist (`:has([data-cal-menu])`), clippt das Panel nicht — analog zur
  Flyout-Regel des Kontextmenüs.

### Changed — PO-Review-Runde: Rollen komplettiert, Zustands-Marker, Carousel-Feinschliff

- **Grund-Ausführungen vervollständigt** (Button/Bubble/Badge bieten jetzt alle sechs:
  primär/sekundär/outline/muted/ghost/destruktiv; Bubble+Badge zusätzlich die drei Statusrollen):
  neu sind `.btn[data-variant="muted"]` (gedämpft, aber bedienbar — „deaktiviert" bleibt das
  `disabled`-Attribut), `.badge[data-variant="muted"]` und die getönten Bubble-Statusrollen
  `success`/`warning`/`info` (analog zur destructive-Bubble). Galerie-Beispiele von Button (#10),
  Badge (#7) und Bubble (#9b) entsprechend ergänzt; die „Wer nutzt was"-Reihen in Color Roles
  (#69c) zeigen jetzt je Komponente den vollen Satz.
- **Color Roles: neues Beispiel „Zustands-Marker"** — der Interaktions-Kanon als Schautafel:
  Hover/Aktiv in Menüs (`accent`-Paar, nie bg-muted), ausgewählte Option (Haken rechts,
  `--check-icon` via Basecoats `[role=option][aria-selected]`), Fokusring (`ring`/`border-ring`)
  und Gedrückt (`aria-pressed` → accent).
- **Reaktions-Chips (9e):** die eigene (gedrückte) Reaktion trägt zusätzlich zum accent-Grund
  einen dunklen Rahmen (`border-primary`, themefolgend — geteilte Regel in `components.css`).
- **Progress „In einer Karte" (45e) auf die Foundation umgebaut:** statt der rohen
  Utility-Karte jetzt eine `.item`-Zeile mit `item-media`, `btn-close` und dem geteilten
  `data-actions="corner"`-Fortschrittslayout — identisches SPOT-Konstrukt wie Attachment.
- **Carousel (#14):** a) zweite Variante `data-carousel-nav="auto-hide"` — deaktivierte
  Randpfeile werden komplett ausgeblendet statt ausgegraut (visibility, Layout bleibt ruhig);
  b) Rahmen-Pfeile über die neue geteilte Regel `data-carousel-frame` — nur noch Position +
  Schatten (SPOT), die Farben kommen ganz normal vom themefolgenden outline-Button
  (keine Overlay-Sonderoptik, PO);
  d) „Zähler im Bild" hat die Pfeile jetzt IM Bild wie bei c; neue letzte Variante
  **Endlos** (`data-carousel-loop`, `c22.js`): „Weiter" auf der letzten Folie springt zum
  Anfang, „Zurück" am Anfang ans Ende, die Pfeile bleiben immer bedienbar.
- **Kontextmenü (#20): Standard ist jetzt „bleibt offen"** — ohne `data-close` schließt das
  Menü erst bei Klick/Rechtsklick woanders, Escape oder Scroll (wie native Kontextmenüs);
  `leave`/`leave-delay` sind explizite Varianten (Galerie-Beispiele/Labels umsortiert).
- **`.kbd` mit Mindestbreite** (`min-w-5`): Einzelzeichen-Kappen ([ ] R …) sind jetzt gleich
  breite Quadrate — vorher standen die „Strg"-Kappen der Kürzelspalte je nach Zweittaste
  versetzt (ungleiche Abstände im Kontextmenü).
- **Ghost-Badge ohne Hover**, wenn es kein Link/Button ist: Basecoats Ghost-Hover (bg-muted)
  ist für interaktive Badges gedacht — statische `span`-Badges reagieren nicht mehr auf die
  Maus (`:not(a):not(button)`-Override).
- **Galerie: Cache-Busting für CSS/JS** (`gallery/build.py`): alle Asset-URLs tragen die mtime
  als `?v=` — der lokale http.server sendet keine Cache-Header, Browser cachten heuristisch und
  zeigten nach einem Rebuild altes Aussehen/Verhalten, bis man hart neu lud. Nach einmaligem
  Hart-Reload holt der Browser Änderungen jetzt immer automatisch.
- **Outline-Buttons im Dunkelmodus deckend** (PO, SPOT, global): Basecoats Dark-Regel malt sie
  mit `color-mix(--input 30%, transparent)` — über Bildern (Carousel-Rahmen-Pfeile) schien das
  Motiv durch. **Falle dabei:** `--input` ist im Dark-Theme SELBST halbtransparent (weiß /0.15),
  ein Mix über `--input` erbt dieses Alpha und bleibt durchscheinend. Die gleiche wahrgenommene
  Farbe (aufgehelltes Schwarz) wird deshalb aus den beiden DECKENDEN Tokens gemischt:
  `--foreground` 5% über `--background` (Hover 8%). Pixel-verifiziert: Button über Weiß =
  Button über Schwarz, null Durchsicht.
- **Carousel-Standard: Randpfeile ausblenden** (PO): deaktivierte Pfeile am Anfang/Ende sind
  jetzt STANDARD-mäßig unsichtbar (visibility, Layout ruhig) — für alle Carousels ohne
  Zusatzattribut; die frühere `data-carousel-nav="auto-hide"`-Variante entfällt (Galerie-
  Beispiel a wieder eines). Der Endlos-Modus deaktiviert nie und zeigt immer beide Pfeile.
- **Kontextmenü: Untermenü per Klick ist Standard** (neue Galerie-Variante): ein verschachteltes
  Panel mit `hidden` im Markup wird per Klick auf seinen `aria-haspopup`-Eintrag geöffnet/
  geschlossen (`aria-expanded` gepflegt, Geschwister-Untermenüs schließen sich, beim Schließen
  des Menüs klappen Untermenüs zu); Auswahl im Untermenü schließt das ganze Menü. Die
  Hover-Variante (CSS `group-hover`, ohne `hidden`) bleibt als explizite Ausführung erhalten.
- **Kontextmenü-Fix Untermenü:** das Flyout-Untermenü (20e) erschien IM Mutter-Menü statt
  daneben — das `overflow-y-auto` des Panels (für lange Menüs) clippte den absolut
  positionierten Flyout bzw. machte ihn zur Scrollfläche. Fix per `:has()`: ein Panel, das ein
  Unter-Panel enthält, bekommt `overflow-visible` (lange Menüs und Flyouts schließen sich aus).
- **Galerie-Server ohne Browser-Cache** (`scripts/serve-gallery.py`): sendet
  `Cache-Control: no-store` für alles — der nackte http.server ließ Browser sogar die
  index.html heuristisch cachen, wodurch trotz `?v=`-Buster alter Stand sichtbar blieb.
- **Kontextmenü-Fix „schließt von selbst":** der globale Scroll-Schließer lief im Capture-Modus
  über ALLE Scroll-Events der Seite — das Autoplay-Carousel scrollt alle 3s programmatisch und
  schloss damit jedes offene Menü, egal wo die Maus war. Jetzt schließt ein Scroll nur noch,
  wenn der gescrollte Container das Menü wirklich bewegt (Dokument/Fenster oder ein Vorfahr des
  Panels); Scrollen im Menü selbst schließt ebenfalls nicht. Headless verifiziert: Menü bleibt
  auf der echten Galerie-Seite trotz laufendem Autoplay offen, Außenklick schließt weiter.

### Changed — Bubble-Beispiel „Mit Reaktionen" interaktiv

- Das Reaktions-Beispiel der **Bubble** (`c22/components/bubble.html`, Galerie-Nr. 9e) ist jetzt
  funktional: **Klick auf einen Reaktions-Chip** setzt/entfernt die eigene Reaktion (Zähler ±1,
  `aria-pressed` → Accent-Look aus `.btn[aria-pressed]`); **fällt der Zähler auf 0, verschwindet der
  Chip** (Chat-Konvention). Der **„+"-Button** öffnet ein kleines Emoji-Popover (Basecoat-`.popover`);
  die Auswahl erhöht einen vorhandenen Chip (nur einmal je Nutzer) bzw. legt einen neuen (Zähler 1) an
  und schließt das Popover.
- Chips auf Foundation umgestellt: Emoji sind **Text** (keine Icons, kein `data-icon-lu`), der Chip ist
  ein `.btn[data-variant="outline"][data-size="xs"]` mit `data-reaction="<emoji>"` und Zähler in
  `[data-reaction-count]`; die eigene Reaktion steckt in `aria-pressed`.
- Neuer c22.js-Baustein **`wireReactions`** (`[data-reactions]`, in `init()` registriert, idempotent
  via dataset-Flag): reine Demo-/UI-Logik ohne Persistenz — die echte Anbindung (wer hat womit reagiert)
  bleibt Sache der App. Ohne JS bleibt das statische Markup gültig (Chips sichtbar, nur ohne Klick).

### Added — „Code Block"-Komponente (Nr. 70)

- Neue Komponente **Code Block** (`c22/components/code-block.html`, Galerie-Nr. 70 — ans Ende
  gehängt, Nummern 1–69 stabil, Kategorie „Anzeige"): der mehrzeilige Codeblock ist jetzt eine
  eigene Komponente statt nur eines Typography-Beispiels. Neue SPOT-Klasse **`.code-block`**
  (`components.css`) bündelt die bisherige Optik (Muted-Fläche, `rounded-lg`, `p-4`, `text-sm`,
  `overflow-x-auto`, Mono im `<code>`) an EINEM Ort; `typography.html` nutzt sie jetzt statt der
  rohen Utility-Kette (die Optik kommt aus einer Quelle, der Block bleibt dort als Auftritt sichtbar).
- Fünf Varianten: (a) **Standard**, (b) **Copy-Button** oben rechts (`.btn` ghost + `.code-block-copy`),
  (c) **Zeilenanzahl** als dezente Fußzeile, (d) **Zeilennummerierung** über das Feature-Attribut
  **`data-line-numbers`** (bewusst kein `data-variant` — Zeilennummern sind keine Farb-Rolle,
  Suite-Regel 12), (e) **ausklappbarer Container-Code** (gerendertes Demo + `<details>` mit escaptem
  Quelltext, reines HTML ohne JS).
- **Optische Ausrichtung des Copy-Buttons** nach dem Modell `.btn-close[data-corner]`: die Glyphe
  sitzt auf dem `p-4`-Content-Raster, die 32er-Klickfläche bleedet in den Innenabstand — SPOT als
  `.btn.code-block-copy` in `components.css`; der Button hängt in einem relativen Wrapper, damit er
  nicht im `overflow-x-auto` mitscrollt.
- **Zeilennummern werden nicht mitkopiert:** Nummern sind reiner CSS-Counter (`::before`) und damit
  weder Teil von `code.textContent` noch der Selektion, zusätzlich `user-select: none`.
- Neuer c22.js-Baustein **`wireCopy`** (`[data-copy]`, in `init()` registriert): kopiert den Textinhalt
  des zugehörigen `<code>` per `navigator.clipboard`, Feedback = Icon wechselt ~2s auf ein Häkchen
  (aria-label „Code kopieren" → kurzzeitig „Kopiert", via `data-copy-done` überschreibbar). Ohne JS
  bzw. ohne Clipboard-API ist der Button wirkungslos, das Markup bleibt gültig.

### Added — „Color Roles"-Komponente (Nr. 69) + Status-Rollen als vollwertige Paare

- Neue Komponente **Color Roles** (`c22/components/color-roles.html`, Galerie-Nr. 69 — ans Ende
  gehängt, Nummern 1–68 stabil, Kategorie „Anzeige"): macht das Token-Rollen-System sichtbar und
  verbindlich. Zeigt (a) die **Kernpaare** (background/foreground, primary, secondary, muted, accent,
  destructive, card, popover) als Fläche + zugehöriger Foreground-Text, (b) die **Statuspaare**
  success/warning/info je als Fläche+Foreground UND getönte Ausführung, (c) **„Wer nutzt was"** —
  Live-Demos (Button-/Bubble-Varianten, Badge-Status) mit dem Kernsatz: die Rollen-Paare sind der
  SPOT, `data-variant` greift sie ab, umfärben = Tokens ändern, nie die Komponente. Nur
  Token-Utilities, keine Hex-Werte.
- **Status-Rollen success/warning/info sind jetzt vollwertige Farbrollen-Paare** wie primary/secondary:
  die Foregrounds (`--success-foreground`/`--warning-foreground`) und die `@theme inline`-Mappings
  (`--color-success` …) existierten bereits; die Flächen bleiben themeunabhängig (Foreground liest in
  beiden Themes), darum kein `.dark`-Wert. Badge-Status (`badge.html`) von der Inline-Kette
  `bg-success text-success-foreground border-transparent` auf `data-variant="success/warning/info"`
  umgestellt (SPOT `.badge[data-variant=…]` in `components.css` war schon da). **Buttons bekommen
  bewusst KEINE Status-Varianten** (PO — passt dort nicht).
- **Destructive-Rollen-Paar vervollständigt:** vega definierte nur `--destructive` ohne Foreground —
  jetzt `--destructive-foreground` (+ `@theme inline`-Mapping), damit `text-destructive-foreground`
  existiert und destructive ein echtes Paar ist. Themeabhängig: weiß im Hellen (dunkles Rot), dunkel
  im `.dark` (helles Lachs-Rot) — beide Themes lesbar (headless-Chrome geprüft).

### Changed — Varianten-Vokabular geschlossen + Bubble-default normalisiert

- **Bubble `data-variant="default"` → `"primary"`** normalisiert (Markup, `components.css`,
  Galerie-Label): der explizite Variantenname heißt jetzt `primary`; die attributlose Blase bleibt
  über `.bubble:not([data-variant])` die primary-Blase. Angleichung an das gemeinsame Rollen-Vokabular.
- **Konventions-Suite Regel 12** (`tests/test_conventions.py`): jedes `data-variant` in
  `c22/components/*.html` muss aus dem festgeschriebenen Vokabular stammen (Konstante
  `ERLAUBTE_VARIANTEN`: Farb-Rollen primary/secondary/muted/accent/tinted/outline/ghost/link/
  destructive/success/warning/info + die Nicht-Farb-Ausführungen line/label/elevated/card/bordered).
  Regel 4 prüft die Form, Regel 12 die Mitgliedschaft; inkl. Selbsttest (Regex schlägt bei einem
  erfundenen Wert an, gültige Werte nicht) — analog zu Regel 6 gegen das Wegrefactoren.

### Added — Close-Button-Komponente (Nr. 68)

- Neue Komponente **Close Button** (`c22/components/close-button.html`, Galerie-Nr. 68 — ans Ende
  gehängt, die Nummern 1–67 bleiben stabil): der repo-weite Schließbutton (X) als SPOT-Klasse
  `.btn-close`, aufgebaut auf `.btn` (`class="btn btn-close" data-variant="ghost"` +
  `data-icon-lu="x"`, `aria-label` Pflicht). Normiert an EINEM Ort statt per Utility-Kette je
  Einsatzstelle:
  - **Größen** über `data-size` — `sm` (24px/12px-X), Default `m` (32px/16px-X), `lg` (40px/20px-X);
    bilden die bestehenden `.btn`-Icon-Kacheln ab. Selektor `.btn.btn-close` (0,2,0) schlägt
    Basecoats `.btn:not([data-size])`/`.btn[data-size=…]` über die spätere Quellreihenfolge, sonst
    erzwänge Basecoat seine Pillen-Höhe. Im Bestand wird überall **m** genutzt; s/l sind ein
    Angebot in der Galerie.
  - **Ecken-Einsatz** über `data-corner` nach dem Modell der optischen Ausrichtung: die Glyphe
    sitzt auf dem Content-Raster des Containers, die Klickfläche bleedet (Inset = Padding −
    Ring). `data-corner` → p-4-Raster (Inset 8, Glyphe bei 16), `data-corner="panel"` →
    p-6-Raster (Inset 16, Glyphe bei 24, Dialog-/Sheet-Panels). Basecoats `.dialog`
    positioniert seinen Schließknopf selbst — dort **kein** `data-corner`, nur Klasse +
    Variante (kein Doppel-Styling).
  - **Auf Bild** über `data-on-image` (frosted: getönter `bg-background`-Grund + Backdrop-Blur,
    kräftiger beim Hover) — ersetzt die rohe Overlay-Utility-Kette aus `attachment.html`,
    theme-fähig aus Tokens. PO-Ausnahme: die X-Glyphe bleibt m (16px), nur der sichtbare
    Container ist kleiner (24px-Fläche, Ring 4).
- **Repo-weit auf `.btn-close` umgestellt** (durchgängig Größe **m**, icon-xs/icon-sm-Streuung
  vereinheitlicht): `attachment.html` (alle X), `dialog.html` (3×, Basecoat-positioniert),
  `sheet.html` (4×, `data-corner="panel"` statt `absolute top-4 end-4`), `progress.html` (Upload
  abbrechen). Nicht umgestellt, weil **keine** Schließ-X: `drawer.html` (Papierkorb-„Entfernen",
  eigenes Löschen-Icon) und `combobox.html` (`data-clear`-Eingabe-Löscher im Input).

### Changed — Attachment (Nr. 5) Feinschliff + optische Ausrichtung (repo-weites Modell)

- **Optische Ausrichtung (PO-Modell, SPOT):** Das Content-Raster bleibt die eine Wahrheit — die
  **sichtbare Glyphe** (16px-X, Pause, Retry) sitzt exakt auf den normalen Innenabständen des
  Containers (Item default 16/14, sm 12/10, xs 10/8), genau wie Text und Icon-Kachel. Die
  **Ausnahme ist die unsichtbare Klickfläche**: sie ist um die Glyphe zentriert und bleedet in
  den Innenabstand (Flächen-Inset = Content-Padding − Ring). In `data-actions="corner"` ist die
  Fläche 24px bei voller m-Glyphe (Ring 4) — dadurch passen zwei Aktionen in die **natürliche
  Zeilenhöhe** (die frühere Mindesthöhe `5.25rem` ist gestrichen, der Container wächst nicht
  mehr). Der Aktions-Stapel ist **von oben gerechnet** (X auf dem Raster, Zweitaktion direkt
  darunter, Glyphen ~8px auseinander) — die Position ist damit in jeder Zeilenhöhe identisch,
  auch wenn ein Fortschrittsbalken die Karte nach unten verlängert. In einzeiligen Zeilen ohne
  Ecken-Modus bleedet der Schließbutton um seinen Ring (`-me-2`), damit die Glyphe ebenfalls
  auf dem Raster sitzt.
- **Stop-Icon (SPOT):** gefülltes Stop-Viereck (PO-Wunsch: Fläche, kein Rahmen) in
  Lucide-Geometrie-Anmutung (14px-Rect, rx 2) — optisches Gewicht passend zu `rotate-ccw`,
  keine Icon-Größen-Streuung mehr (der alte 12px-Rect war zu klein).
- **Scroll-Kanten-Fade** für die scrollbare Gruppe: neuer Baustein `data-scroll-fade`
  (Maske in `components.css`, Zustandspflege `data-at-start`/`-end` in `c22.js`) — der Inhalt
  läuft an der Kante weich aus, an der es weiterscrollt; am Anfang/Ende fällt der jeweilige
  Fade weg. Wiederverwendbar für jede horizontale Scrollreihe (LTR).
- **Bubble `muted`** jetzt mit ausgegrautem Text (`text-muted-foreground`) — war sonst optisch
  identisch mit `secondary`; die Unterscheidung trägt jetzt der Text, nicht nur die Fläche.
- **Neue Bilder-Variante „Kopfzeile"** (eigener Galerie-Buchstabe, nachfolgende Buchstaben
  verschieben sich um eins): Titel + Schließbutton ÜBER dem Bild, keine Details unten. Der
  Titel läuft nach rechts weich in Transparenz aus statt mit „…" abzuschneiden — neue
  wiederverwendbare Regel **`.truncate-fade`** (Maskenverlauf über die letzten 2rem,
  `components.css`; physisch „to right", in RTL nicht einsetzen). Der X bleedet horizontal um
  seinen Ring und vertikal minimal (`-my-1`), damit die Glyphe auf dem Content-Raster sitzt
  und die 32px-Klickfläche die Titelzeile nicht aufbläht (geteilte Regel in `components.css`).
- **Größen-Beispiel neu geordnet:** Container-Raster in allen drei Zeilen einheitlich (kein
  `data-size` mehr am Item) — nur die Icon-Kachel skaliert, dafür kann `.item-media` ihre
  Größe jetzt auch direkt als eigene Variante tragen (`data-size="sm"/"xs"` auf der Kachel).
  Erste Zeile zweizeilig, zweite und dritte einzeilig (Name · Größe · X mittig).
- **Fortschrittsbalken (Zustand „lädt hoch"):** liegt im Content-Raster — links UND rechts
  gleich weit vom Rahmen (16px, bündig mit Icon-Kachel) und mit bewusst minimaler Luft zum
  unteren Rand (4px, sanktionierte Raster-Ausnahme, einmal in `components.css` definiert).
- **Neue Progress-Variante `.progress-surface`** (in Progress Nr. 45 gebaut, in Attachment 5c
  als weitere Zustandszeile genutzt): der **Container-Hintergrund selbst** ist der Fortschritt —
  primär-getönte Füllung bis `--progress` (Inline-Style wie beim Füllspan), Farbe per
  `color-mix` aus Tokens, dark-fähig.
- **Größenzeilen:** der Schließbutton ist in allen drei Zeilen (default/sm/xs) homogen **m**
  (gleiche Glyphe) — skaliert nicht mit der Icon-Kachel mit.

### Changed — Scrollbar: globaler Standard + Puffer an Rundungen

- **Der pfeillose Token-Balken ist jetzt der globale Standard** für jede Scrollfläche der Seite
  (SPOT): nackte `::-webkit-scrollbar`-Pseudos in `components.css` matchen universell, Firefox
  erbt `scrollbar-color` von `:root` (die Property erbt) im bestehenden `@supports`-Zweig. Die
  Klasse `.scrollbar` braucht es nur noch als Hook für die Varianten (`data-size`/`data-track`/
  `data-buttons`); Aussteiger bleiben `data-buttons="arrows"` (native Route), `.no-scrollbar`
  und Vendor-Sonderfälle (Command-Liste). Damit sind auch bisher native Balken (z.B. die
  Galerie-Seitenleiste) automatisch im C22-Look.
- **Neues Token `--scrollbar-inset`** (an `--radius` gekoppelt): der Track endet um diesen
  Puffer vor den Ecken, damit der Daumen nicht über die Container-Rundung läuft. Greift
  **automatisch**, sobald die Scrollfläche selbst eine `rounded-*`-Utility trägt (berechnetes
  `border-radius` kann CSS nicht abfragen; im kanonischen Markup ist die Klasse der
  verlässliche Marker, und Track-Pseudos existieren nur auf echten Scrollflächen). Explizit
  erzwingen per `data-scrollbar-inset` (Rundung auf dem Eltern-Container), abschalten per
  `data-scrollbar-inset="false"`. Nur `::-webkit`-Route — Firefox kennt keine Track-Ränder.
  Neues Galerie-Beispiel 67i zeigt den Vergleich mit/ohne Puffer.

### Added — Scrollbar-Komponente (Nr. 67)

- Neue Komponente **Scrollbar** (`c22/components/scrollbar.html`, Galerie-Nr. 67 — ans Ende gehängt,
  die Nummern 1–66 bleiben stabil): eigene, themefolgende Scrollbalken auf Basis von Basecoats
  `.scrollbar`/`.scrollbar-sm`. Die fünf Tokens `--scrollbar-width`/`-sm-width`/`-thumb`/`-track`/
  `-radius` sind jetzt ein sichtbarer C22-Seam in `tokens.css` (Thumb bewusst kräftiger als der
  Vendor-Default `var(--border)`: `color-mix` aus `--muted-foreground`, folgt beiden Themes
  automatisch; Track transparent). **Pfeillos ist der C22-Standard** (PO-Entscheid):
  `.scrollbar`/`.scrollbar-sm` fahren die `::-webkit`-Custom-Route mit explizit
  ausgeblendeten Schrittknöpfen; Firefox behält die Token-Farben über einen eigenen
  `@supports (-moz-appearance: none)`-Zweig. Varianten per Variant-Contract in
  `components.css`: `data-size="sm"/"lg"` (Breite als Token-Override; „sm" = Basecoats
  `.scrollbar-sm`), `data-track="visible"` (sichtbare Rinne), `data-buttons="arrows"`
  (native `scrollbar-color`-Route: Token-Farben + native Systempfeile unter Chromium/Linux,
  bewusst ohne eigene Pfeil-Grafiken). Die `.no-scrollbar`-Utility bleibt der Weg zum
  kompletten Ausblenden.
- Dokumentierte Engine-Grenzen: Firefox kennt bei `scrollbar-width` nur auto/thin/none
  („sm" wird thin, „lg" wirkt dort nicht) und rendert grundsätzlich keine Pfeile. Modernes
  Chromium ignoriert `::-webkit-scrollbar`-Styles, sobald `scrollbar-color`/`scrollbar-width`
  gesetzt sind — der Default setzt sie deshalb auf `auto` zurück, die Pfeil-Variante nutzt
  genau diesen Effekt für die native Route. `::-webkit-scrollbar-button` matcht je Ende
  mehrere Slots (single + double button) — ungefiltert ergäbe das Doppelpfeile, weshalb es
  keine eigenen `::-webkit`-Pfeil-Grafiken gibt. Die Firefox-Weiche läuft bewusst über
  `-moz-appearance` statt `@supports selector(::-webkit-scrollbar)` (Firefox parst unbekannte
  `::-webkit`-Pseudos aus Webkompat-Gründen als gültig).

### Changed — Attachment: Ecken-Aktionen, größere Icon-Kachel, Upload mit Fortschritt

- Attachment (Nr. 5) nach PO-Feedback überarbeitet: Aktionen sitzen per neuem
  `data-actions="corner"` (geteilte Regel in `components.css`, Variant-Contract) oben rechts in
  der Ecke und stapeln vertikal — Schließen-X immer oben, Zweitaktion (Pause/Retry) darunter;
  absolut positioniert (mit reservierter `pe-10`-Spalte), weil `.item` flex-wrap ist und das
  aside in schmalen Karten sonst unter den Text fiele. Die generische `.item`-Komponente bleibt
  unverändert.
- Die geteilte `.item-media`-Kachel schließt jetzt mit dem zweizeiligen Textblock ab
  (size-9 → size-10, inneres SVG size-4 → size-5; sm behält size-8 mit explizitem size-4-SVG) —
  gilt bewusst überall, auch in der Progress-Karte.
- Beispiel „Zustände": zweite Upload-Variante mit Fortschrittsbalken (`.progress`-Foundation)
  und Meta-Zeile „64 % · 12,4 MB / 19,3 MB"; Beispiel „Größen" mit einzeiliger xs-Zeile
  (Dateiname · Größe · X) und X in allen drei Größen; Beispiel „Gruppe" mit X pro Karte.

### Fixed — Item-Größenabstufung sm und Fehlertext-Kanon

- `.item[data-size='sm']` änderte nur gap/padding, nicht die Typo (Basecoat stuft nur `xs` ab) —
  default und sm sahen praktisch gleich aus und der sm-Text wirkte durch das knappere Padding
  sogar größer. Neue Mittelstufe in `components.css`: die Meta-Zeile (`p`) wird `text-xs`,
  explizite `text-*`-Utilities im Markup gewinnen weiterhin.
- Fehlertext im `.item`-Kontext vereinheitlicht: `p[role='alert']` trägt den Kanon
  `text-destructive text-xs` über eine geteilte Regel (analog `.field[data-invalid]`),
  statt gestreuter Utilities pro Zeile.

### Added — theming axes (phase A) and the Phosphor icon set

- Five more token axes, each a documented override seam a future theme generator can drive
  (see `docs/theming.md`, now fifteen axes plus the normative **variant contract**): icon stroke
  width (`--icon-stroke`, scoped so chart lines stay untouched), shadows as runtime tokens
  (`--shadow-2xs…2xl`; `shadow-md`/`shadow-lg` now resolve at runtime), motion
  (`--default-transition-duration`/easing seam plus a global `prefers-reduced-motion` fallback),
  heading weight (`--font-weight-heading`), and a named z-index ladder (`--z-popover`/`--z-context`)
  replacing the last magic number.
- The Phosphor icon subset (MIT) from C22 0.2.0 returns as the second icon library: 21 icons ×
  6 weights in `c22/static/js/icons.js`, a declarative `data-icon-ph`/`data-weight` host filled by
  `c22.js` (plus `window.C22.phIcon(name, weight)`), and a new **Icon** gallery component — the
  gallery now shows 66 components. Weights double as the icon-weight axis for fill-based icons.

### Added — icon names (`data-icon-lu`), the foundation of the icon-library axis

- Every inline lucide `<svg>` in the partials (419 across 51 files) now carries its machine-readable
  name as `data-icon-lu="<lucide-name>"` — the prerequisite for the generation-time library switch
  (axis 8): a tool can only swap icon markup by *name*. Names are the **canonical** lucide-static
  1.25.0 ones (aliases like `x-circle`/`bar-chart-3` resolved to `circle-x`/`chart-column`); the
  four icon strings in `c22.js` (calendar chevrons/nav) are named by hand. `data-icon` itself stays
  Basecoat's `inline-start`/`inline-end` padding hint — untouched, hence the separate attribute.
- `tools/annotate-icons.py`: repeatable annotator — downloads the pinned `lucide-static` npm tarball
  to a cache outside the repo, builds a geometry signature per icon (normalised, sorted child
  elements), matches every lucide-like `<svg>` in the partials and writes/corrects `data-icon-lu`
  idempotently (second run: zero changes). Older redesigned lucide forms and the one custom glyph
  (GitHub logo in `badge.html` → `data-icon-lu="github"`) live in a curated override table;
  anything unmatched is reported with file:line instead of guessed.
- `docs/icons.md`: the icon registry — the two-library situation, the semantic → lucide → Phosphor
  name mapping for the 21 vendored Phosphor icons (lucide side verified against the pinned
  download), the custom-icon list, and how the table grows. Suite rule 11 enforces that every
  lucide-like `<svg>` carries a non-empty `data-icon-lu`.

### Added — convention hygiene suite

- `tests/test_conventions.py` enforces the design-system contract mechanically over all
  `c22/components/*.html` and the class strings in `c22/static/js/c22.js`: no literal colours in
  markup, no Tailwind palette classes (tokens only), no arbitrary sizes (only the sanctioned
  `text-[11px]`), a lowercase-hyphen `data-variant`/`-size`/`-align`/`-side` vocabulary, one `.kbd`
  cap per key, and the presence of the token axes in `tokens.css` (`--font-heading`, `--chart-1…5`,
  `--info`, `--overlay-control`). Auto-discovered by `run_all.py`.
- Two icon-sizing rules extend the suite: no `width`/`height` on **any** `<svg>` in the partials
  (blanket — every icon is sized by a `size-*` class or by its component CSS) and — via a real HTML
  parser, not line-guessing — a 24px `<svg>` without a `size-*` class must sit under an ancestor whose
  component CSS sets the icon size (whitelist: `.btn`, `.kbd`, `.badge`, `.item-media`, `.avatar-badge`,
  `.alert`, `.select`, `<figure>`, carousel arrows/dots, `combobox-trigger-icon`, the `.command`
  header, `.input-group` `data-align` slots, `role=menuitem`/`option`/`heading`, and
  `<summary>`/`.accordion`/`.collapsible`) — for `.item` only `<figure>` counts, not `<aside>`.
- Two regression rules close out the audit: no stray generation artifacts (`</content>`/`</invoke>`/
  `<content`) in the partials, and no `aria-pressed:`/`aria-checked:` arbitrary-variant utilities in
  markup (the pressed/checked look now comes from the `.btn[aria-pressed='true']` foundation rule).

### Fixed — token/variant contract violations the suite surfaced

- The badge `Info` variant now uses the `--info` token (`bg-info text-info-foreground
  border-transparent`, solid like OK/Warnung) instead of literal `blue-*` palette classes.
- Keyboard shortcuts in `menubar`, `input-group` and `empty` now render one `.kbd` cap per key
  (e.g. `Strg` + `T`) instead of a single box with a space (`Strg T`).
- Icon sizing brought in line with the `.btn`/`size-*` convention: error micro-text in `radio-group`
  and `switch` is now `text-destructive text-xs`; standalone 24px icons that dwarfed adjacent small
  text got a `size-*` class (`hover-card` calendar → `size-3.5`; `item` link-row chevrons and the
  `message` file-tile icon → `size-4`; `message` error micro-icon → `size-3.5`); and
  `width="24" height="24"` was stripped from **every** `<svg>` root whose size is set otherwise (all
  66 across the partials, incl. `.btn`, figure/media icons, `.alert`, carousel, the `.command` header
  and the `toast` runtime-icon string), leaving `grep width="24"` at zero.
- Final polish batch: stray `</content>`/`</invoke>` generation artifacts removed from `dropdown-menu`,
  `collapsible` and `select`; the `.btn` dropdown-trigger chevrons in `data-table` and `input-group`
  now carry `opacity-50` (the muted-50 canon `.select` triggers already get via CSS); the redundant
  `text-muted-foreground` dropped from `select`'s chevrons (CSS already colours them); `sidebar`
  `<details>` submenu links got `role="menuitem"` (matching the top level); and an ineffective
  `data-active="true"` was removed from the `message-scroller` scroll-to-bottom `.btn`.

### Changed — foundation/SPOT consolidation (component audit)

- Toggle state is now one rule (`components.css`): `.btn[aria-pressed='true']`/`[aria-checked='true']`
  → `bg-accent text-accent-foreground`, replacing ~35 inline `aria-pressed:…`/`aria-checked:…` chains
  across `toggle`, `toggle-group` and `theme-switcher`.
- `toggle-group`'s exclusive (single-select) groups are now `role="radiogroup"`/`role="radio"` +
  `aria-checked` — a11y-correct like `theme-switcher`; multi-select groups keep `aria-pressed`.
- `message-scroller` now uses the `.bubble` foundation (`muted` = received, default = sent via
  `data-align="end"`) instead of raw `bg-muted`/`bg-primary … rounded-lg` chains — one bubble look
  system-wide (rounded-2xl + tail).
- New shared classes in `components.css` replace duplicated utility chains: `.hover-card` (the popover
  surface, was 4× identical in `hover-card`), `.badge[data-variant='success'|'warning'|'info']`
  (status chains → `data-variant` in `badge`, `data-table`, `item`, `table`, `message-scroller`),
  and `.input-otp-slot` (~30 repeated OTP-cell chains).
- `progress` icon tile → `.item-media`; `drawer` nav links → `.btn` `data-variant="ghost"`;
  `direction` initials avatars → `.avatar`; `navigation-menu` active page now uses the `bg-accent`
  state canon instead of `bg-muted`.

### Fixed — missing `.separator` foundation and error micro-text canon

- `.separator` (listed as a foundation in `CLAUDE.md`) had no CSS and lived as a repeated utility
  chain in the markup — now a real class (`bg-border shrink-0` + `data-orientation` for thickness);
  `separator.html` and its ad-hoc dividers use it.
- Error micro-text canon `.field[data-invalid] > p[role='alert'] { text-xs }` — `select` and
  `textarea` field errors now render at `text-xs` like the explicit `checkbox`/`radio-group`/`switch`
  ones (colour already comes from Basecoat's `data-invalid` rule).

### Changed — rebuilt on Basecoat + Tailwind CSS v4 (shadcn look)

C22's own component CSS/JS is superseded by a vendored, pinned copy of
[Basecoat](https://basecoatui.com/) (MIT), driven by the Tailwind CSS v4 standalone CLI. The design
system is now shadcn-flavoured semantic HTML + Basecoat classes + C22 tokens, with app-side adapters
kept thin. Basecoat is vendored under `c22/vendor/basecoat/` (reproducible via
`scripts/vendor-basecoat.sh`); the Tailwind binary is fetched, not committed.

### Added — component gallery (the single point of truth)

- A generated gallery (`gallery/build.py` → `gallery/index.html`) showing all 65 components, each in
  its variants — numbered per component, lettered per variant — with an eight-pack style switcher and
  a light/dark toggle. Every component links its Basecoat and shadcn source docs.
- Canonical HTML partials for all 65 components under `c22/components/`, each carrying its variants via
  one reusable `c22-examples` pattern (full-width dividers and spacing defined once in `components.css`).
- Reusable C22 component rules in `components.css`: `badge-split` (shields-style two-part badges),
  `bubble`/`bubble-group` (chat bubbles), avatar shapes (`data-shape`), accordion `bordered`/`card`,
  a text shimmer for in-progress states, context-menu and resizable skins, and slider status colours.
- A minimal own behaviour layer (`c22/static/js/c22.js`) for what Basecoat's JS does not cover:
  the context menu — right-click to open, viewport-aware placement that flips left/up near the edges,
  close on leave / after a short delay / manually (`data-close`), and a right-click inside the menu
  acting like a normal click. Apps embed it alongside `basecoat.all.min.js`.
- Example imagery sourced from Unsplash; a global `cursor: pointer` on interactive buttons.
- The behaviour layer now also renders interactive calendars (`data-calendar`: single/range selection,
  multiple months, month/year dropdown, disabled days, today/weekend/holiday styling), carousels and
  charts.
- Menu components share one hover/active state (`accent`) across command, dropdown-menu, context-menu,
  combobox and the calendar dropdown. Keyboard-shortcut keys render as `.kbd` key-caps (a single point
  of truth with `kbd`/`dropdown-menu`), one cap per key, that keep a constant border and only lighten
  their background on the highlighted row. The calendar's month/year dropdown marks the current choice
  with a check like a selected `select` option instead of a filled row. The command palette gains
  popover- and dialog-triggered variants plus a scrollable list, and opens without a pre-highlighted
  first row. Combobox `auto-highlight` is limited to its dedicated variant.
- Consistency pass across components 1–20: keyboard shortcuts in `context-menu` render as one `.kbd`
  key-cap per key (was a single combined box); `alert` gains a token-based `data-variant="warning"`
  instead of hardcoded `amber-*`; shields-style split badges use a new `--info` token instead of
  `bg-blue-600`; carousel photo-overlay controls use new `--overlay-control`/`--overlay-shadow-*` tokens
  instead of literal white/black — the sanctioned way to keep a deliberately theme-independent colour a
  token; the breadcrumb dropdown trigger inherits the `.breadcrumb` link hover via a shared rule; the
  calendar trigger chevron and an avatar check-icon follow the icon conventions (opacity-50, stroke-2).
- `attachment` is rebuilt on the `.item` row primitive plus a shared `.item-media` icon-tile class,
  instead of repeating the row/tile utility chains per entry.
- A repo `CLAUDE.md` documenting the build-on-the-foundation (SPOT) rule, the foundation blocks, the
  token/state/icon/typography conventions, and how to add or change a component.
- `docs/theming.md`: the theming concept — independent axes (style, base color, accent, chart
  colors, heading font, base font, typography scale, icon library, radius, menu, menu accent, and
  later density, shadows, motion and icon weight) that a future generator drives through tokens only. Phase A lands in this release: a `--font-heading` token
  (headings follow it via one base rule; default = body font), the chart palette moved from hex to
  oklch (same colours, generator-settable), and the documented override seam for the Tailwind v4
  `--text-*` type-scale tokens.

## [0.2.0] - 2026-07-12

### Added — component library and pattern book

The first design release: a framework-free component library (vanilla CSS + minimal vanilla JS,
no build step, no runtime dependency, single-file friendly) with a live pattern book at
`examples/musterbuch.html`.

- **Four independent look axes**, switchable without touching behaviour: colour theme
  (`data-theme`: hell/ambient/dunkel), size/density (`data-size`), corner shape
  (`--radius-scale`, a free value, plus per-corner `--rc-*`), and icon weight
  (`data-icon-weight`) over an inlined [Phosphor](https://phosphoricons.com/) subset.
- **Components**: buttons and segmented switches (including click-anywhere toggle chips and an
  icon toggle with a split thumb), forms with floating labels and `:user-invalid` validation
  timing, tabs (sliding underline and a browser-style variant), accordion, cards, navigation,
  chips, list, table, divider, media, single- and dual-thumb sliders, combobox/autocomplete,
  an ARIA menu, tooltip and popover, and custom scrollbars.
- **Notification system** from a single source of truth (the `KIND` registry) feeding banner,
  toast, centred popup and a notification centre/history — with grouped per-app notifications,
  a history filter by app, and an ARIA-live announcer for screen readers.
- Design principles (`docs/prinzipien.md`) and a BeerCSS-parity component checklist
  (`docs/komponenten-checkliste.md`).

Interaction patterns (combobox, menu, tabs, dual-thumb slider, live announcer) follow the
[WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/). Brand/app logos come from
[selfh.st/icons](https://selfh.st/icons/) (CC BY 4.0), bundled and self-hosted — never via CDN.

### Changed — unified layout of the documentation subpages

`CONTRIBUTING`, `SECURITY` and the German `i18n/` versions now carry the language switcher directly
below the heading and the logo bottom-right — the same pattern across all own repos. The English
`CODE_OF_CONDUCT.md` stays untouched and **pure** so GitHub recognises it as Contributor Covenant
rather than "Other".

The Flaticon credit now links straight to the author page (Iconjam) and opens in a new tab, in the
format shared across the repos: `Icon: … PNG Image by … - flaticon.com`.

## [0.1.0] - 2026-07-10

### Added
- Repository skeleton: package layout (`c22/static/{css,js}`, `c22/macros`),
  the `static_path()` and `macros_path()` helpers, a `Report`-based test harness,
  the shared hygiene kit via `repokit`, and a hardened CI workflow.
- Bilingual community files (README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT).
- Project logo (`docs/logo.png`) in both README versions, with Flaticon attribution.

No design assets are included yet; they follow once the layout foundation is settled.
