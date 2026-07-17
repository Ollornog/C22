// C22 — eigenes, minimales Verhalten für Components, die Basecoat NICHT mitbringt.
// Ergänzt basecoat.all.min.js (das die übrigen Components live macht). Kein Build-Schritt,
// keine Abhängigkeit: eine Datei einbinden, fertig. Alles hängt an data-Attributen im Markup.
(function () {
  'use strict';

  // ---- Phosphor-Icons (zweite Icon-Bibliothek neben den Lucide-Inline-SVGs) --
  // Subset in icons.js (window.C22_ICONS = {name: {gewicht: "<path …>"}}), MUSS vor c22.js
  // eingebunden sein. Deklarativ: <span data-icon-ph="name" data-weight="thin|light|regular|
  // bold|fill|duotone" class="size-4">, befüllt von init()/wirePhIcons(). Programmatisch:
  // window.C22.phIcon(name, weight) -> SVG-String. Unbekannter Name/Gewicht: console.warn + leer,
  // damit ein Tippfehler nicht die ganze Seite zerlegt.
  var PH_WEIGHTS = ['thin', 'light', 'regular', 'bold', 'fill', 'duotone'];
  function phIcon(name, weight) {
    var set = window.C22_ICONS && window.C22_ICONS[name];
    if (!set) { console.warn('C22.phIcon: unbekanntes Icon "' + name + '"'); return ''; }
    var w = PH_WEIGHTS.indexOf(weight) >= 0 ? weight : 'regular';
    var inner = set[w] || set.regular;
    if (!inner) { console.warn('C22.phIcon: unbekanntes Gewicht "' + weight + '" bei "' + name + '"'); return ''; }
    return '<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">' + inner + '</svg>';
  }
  function wirePhIcons(root) {
    (root || document).querySelectorAll('[data-icon-ph]').forEach(function (el) {
      el.innerHTML = phIcon(el.dataset.iconPh, el.dataset.weight);
    });
  }

  // ---- Context-Menu (Basecoat hat kein Rechtsklick-JS) ---------------------
  // Markup:  <div class="context-menu" data-close="leave|leave-delay|manual">
  //            <div … oncontextmenu-Ziel …>Rechtsklick-Fläche</div>
  //            <div data-cm-panel role="menu" hidden> … Einträge … </div>
  //          </div>
  // Untermenüs (verschachtelte [data-cm-panel]) laufen weiter rein über CSS-Hover.
  var CLOSE_DELAY = 500; // ms für data-close="leave-delay" ("kurze Verzögerung")
  var MARGIN = 8;        // Mindestabstand zum Fensterrand
  var HIT_SLOP = 24;     // Toleranzsaum ums Panel, der noch als "auf dem Menü" zählt

  // Registry aller verdrahteten Wurzelmenüs; `active` ist das gerade offene (max. eines, weil
  // jeder Rechtsklick zuerst alle schließt). Ein Ereignis (Rechtsklick woanders, Scroll, Escape,
  // Zeiger verlässt das Panel) kann so ALLE bzw. das aktive schließen.
  var registry = [];
  var active = null;
  function closeAll() { registry.forEach(function (m) { m.close(); }); }

  // Panel ist position:fixed -> Koordinaten sind Viewport-Koordinaten. Es zählt allein das
  // Fenster, nicht der Container: standardmäßig rechts/unter dem Zeiger, sonst nach links bzw.
  // über den Zeiger gekippt, damit es nie aus dem Fenster ragt.
  function positionPanel(panel, ev) {
    panel.hidden = false;               // erst sichtbar, dann messbar
    var pw = panel.offsetWidth, ph = panel.offsetHeight;
    var vw = window.innerWidth;         // echte Fenstergröße — nur sie zählt, nicht der Container
    var vh = window.innerHeight;
    var x = ev.clientX, y = ev.clientY;
    if (x + pw > vw - MARGIN) x = x - pw;                       // rechts kein Platz -> nach links
    if (y + ph > vh - MARGIN) y = y - ph;                       // unten kein Platz -> nach oben
    panel.style.left = Math.min(Math.max(MARGIN, x), vw - pw - MARGIN) + 'px';
    panel.style.top = Math.min(Math.max(MARGIN, y), vh - ph - MARGIN) + 'px';
  }

  function wireContextMenu(menu) {
    if (menu.dataset.c22Wired) return;  // idempotent (mehrfaches Init schadet nicht)
    menu.dataset.c22Wired = '1';
    var panel = menu.querySelector(':scope > [data-cm-panel]');
    if (!panel) return;
    var trigger = panel.previousElementSibling;
    var obj = { panel: panel, mode: menu.dataset.close || 'leave-delay', timer: null, close: null };

    function close() { clearTimeout(obj.timer); obj.timer = null; panel.hidden = true; if (active === obj) active = null; }
    function open(ev) { ev.preventDefault(); clearTimeout(obj.timer); obj.timer = null; positionPanel(panel, ev); active = obj; }
    obj.close = close;
    registry.push(obj);

    if (trigger) trigger.addEventListener('contextmenu', open);

    // Links- UND Rechtsklick auf einen Eintrag verhalten sich gleich (wie native Kontextmenüs).
    panel.addEventListener('click', function (e) { activateItem(e.target, close); });
  }

  // Einen Eintrag "aktivieren" — geteilt von Links- und Rechtsklick: Checkbox/Radio togglen und
  // offen bleiben; ein echter Eintrag schließt; ein Untermenü-Öffner (aria-haspopup) macht nichts.
  function activateItem(target, close) {
    var cb = target.closest('[role=menuitemcheckbox]');
    if (cb) { cb.setAttribute('aria-checked', cb.getAttribute('aria-checked') !== 'true'); return; }
    var rd = target.closest('[role=menuitemradio]');
    if (rd) {
      rd.closest('[role=group]').querySelectorAll('[role=menuitemradio]')
        .forEach(function (el) { el.setAttribute('aria-checked', el === rd ? 'true' : 'false'); });
      return;
    }
    if (target.closest('[role=menuitem]:not([aria-haspopup])')) close();
  }

  // Globale Schließ-Auslöser — einmal fürs ganze Dokument, wirken auf ALLE Menüs.
  var globalsWired = false;
  function wireGlobals() {
    if (globalsWired) return;
    globalsWired = true;
    // Linksklick außerhalb eines Panels schließt alles (ein Rechtsklick feuert KEIN click-Event).
    document.addEventListener('click', function (e) {
      if (!e.target.closest('[data-cm-panel]')) closeAll();
    });
    // Rechtsklick INS offene Menü = normaler Klick auf den Eintrag (wie native Kontextmenüs),
    // ohne natives Browsermenü. Sonst: Rechtsklick woanders schließt zuerst alle (capture, also
    // VOR dem Auslöser); liegt er auf einer Auslöserfläche, öffnet deren Handler danach sein
    // eigenes — so bleibt nie mehr als ein Menü offen, auch während eines Schließ-Timers.
    document.addEventListener('contextmenu', function (e) {
      if (active && !active.panel.hidden && active.panel.contains(e.target)) {
        e.preventDefault();
        activateItem(e.target, active.close);
        return;
      }
      closeAll();
    }, true);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeAll(); });
    window.addEventListener('scroll', closeAll, true);  // fixes Menü soll nicht mitschweben

    // Auto-Schließen beim Verlassen: bewusst NICHT über mouseleave am Panel — das Panel öffnet
    // unter dem Zeiger (fixed), da feuert kein zuverlässiges mouseenter/leave. Stattdessen prüfen
    // wir bei jeder Zeigerbewegung DOM-basiert, ob der Zeiger noch im Panel ist (elementFromPoint
    // + panel.contains -> Untermenüs zählen mit, weil sie DOM-Kinder des Panels sind).
    document.addEventListener('pointermove', function (e) {
      var m = active;
      if (!m || m.panel.hidden || (m.mode !== 'leave' && m.mode !== 'leave-delay')) return;
      var x = e.clientX, y = e.clientY;
      // "auf dem Menü" = über dem Panel bzw. seinen DOM-Kindern (Untermenü zählt mit) ODER
      // innerhalb eines Toleranzsaums um das Panel-Rechteck. Der Saum federt ab, dass der Zeiger
      // beim Öffnen an der gerundeten Ecke knapp außerhalb sitzt und dass man die Kante kurz
      // übersteuert.
      var el = document.elementFromPoint(x, y);
      var r = m.panel.getBoundingClientRect();
      var inside = (el && m.panel.contains(el)) ||
                   (x >= r.left - HIT_SLOP && x <= r.right + HIT_SLOP &&
                    y >= r.top - HIT_SLOP && y <= r.bottom + HIT_SLOP);
      if (inside) {
        clearTimeout(m.timer); m.timer = null;                 // wieder drin -> Schließen abbrechen
      } else if (m.mode === 'leave') {
        m.close();                                             // sofort schließen
      } else if (m.timer === null) {
        m.timer = setTimeout(m.close, CLOSE_DELAY);            // leave-delay: verzögert
      }
    });
  }

  // ---- Kalender (Basecoat bringt keinen) ------------------------------------
  // Markup (alles über data-*): <div data-calendar class="w-fit rounded-lg border p-3"
  //   data-mode="single|range" data-month="YYYY-MM" data-months="1|2"
  //   data-selected="YYYY-MM-DD" | "YYYY-MM-DD/YYYY-MM-DD"
  //   [data-dropdown] [data-abbrev] [data-today="ring|bold"] [data-weekend="bold|color"]
  //   [data-holidays="YYYY-MM-DD,…"] [data-disabled="weekends|YYYY-MM-DD,…"]></div>
  // c22.js rendert Kopf + Raster (IMMER 6 Zeilen -> feste Höhe; "Heute" sitzt in der nie vollen
  // 6. Zeile), blättert Monate, wählt Tag/Bereich (auch über mehrere Monate). Datum-Rechnen macht
  // `Date`; Auswahl als 'YYYY-MM-DD'-String -> Vergleich per String.
  var CAL_MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
  var CAL_WEEKDAYS = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'];
  var CAL_ICO = 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"';
  var CAL_PREV = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" ' + CAL_ICO + '><path d="m15 18-6-6 6-6"/></svg>';
  var CAL_NEXT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" ' + CAL_ICO + '><path d="m9 18 6-6-6-6"/></svg>';
  var CAL_DOWN = '<svg class="ms-1 opacity-50" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" ' + CAL_ICO + '><path d="m6 9 6 6 6-6"/></svg>';
  var CAL_TODAY = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="13" height="13" ' + CAL_ICO + '><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="M8 2v4"/><path d="M16 2v4"/></svg>';
  var CAL_LEGEND_BG = { destructive: 'bg-destructive', warning: 'bg-warning', success: 'bg-success', primary: 'bg-primary', accent: 'bg-accent', 'muted-foreground': 'bg-muted-foreground' };

  function calPad(n) { return (n < 10 ? '0' : '') + n; }
  function calKey(y, m, d) { return y + '-' + calPad(m + 1) + '-' + calPad(d); }      // 'YYYY-MM-DD'
  function calNorm(str) { var p = String(str).split('-'); return calKey(+p[0], +p[1] - 1, +p[2]); }
  function calTrim(x) { return x.trim(); }
  function calEsc(x) { return String(x).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

  function wireCalendar(el) {
    if (el.dataset.c22CalWired) return;
    el.dataset.c22CalWired = '1';
    var mode = el.dataset.mode || 'single';
    var nMonths = Math.max(1, +(el.dataset.months || 1));
    var hasDropdown = el.hasAttribute('data-dropdown');
    var abbrev = el.hasAttribute('data-abbrev');
    var todayStyle = el.dataset.today || 'ring';
    var weekendStyle = el.dataset.weekend || '';
    var legend = el.dataset.legend || '';   // "farbe:Label,farbe:Label" -> Punkt-Legende im Container
    var holidays = (el.dataset.holidays || '').split(',').map(calTrim).filter(Boolean);
    var disRaw = (el.dataset.disabled || '').split(',').map(calTrim).filter(Boolean);
    var disWeekends = disRaw.indexOf('weekends') >= 0;
    var disDates = disRaw.filter(function (x) { return x !== 'weekends'; });
    var now = new Date();
    var todayKey = calKey(now.getFullYear(), now.getMonth(), now.getDate());
    var s = { vy: now.getFullYear(), vm: now.getMonth(), sel: null, start: null, end: null, hover: null, ddOpen: false };
    if (el.dataset.month) { var mp = el.dataset.month.split('-'); s.vy = +mp[0]; s.vm = +mp[1] - 1; }
    if (mode === 'single' && el.dataset.selected) { s.sel = calNorm(el.dataset.selected); }
    if (mode === 'range' && el.dataset.selected) {
      var rp = el.dataset.selected.split('/'); s.start = calNorm(rp[0]); s.end = calNorm(rp[1] || rp[0]);
    }

    function monthName(m) { return abbrev ? CAL_MONTHS[m].slice(0, 3) : CAL_MONTHS[m]; }
    function navBtn(dir) {
      return '<button type="button" data-cal-' + dir + ' class="btn" data-variant="outline" data-size="icon-sm" aria-label="' +
        (dir === 'prev' ? 'Vorheriger' : 'Nächster') + ' Monat">' + (dir === 'prev' ? CAL_PREV : CAL_NEXT) + '</button>';
    }
    function ddItem(label, attr, current) {
      // Gewählte Zeile im normalen Dropdown-Stil: Haken rechts (aria-selected, via components.css
      // wie .select), Hover accent — NICHT als gefüllte primary-Zeile (SPOT mit select/dropdown).
      var cls = 'flex w-full cursor-pointer items-center rounded-sm ps-2 pe-7 py-1.5 text-start text-sm hover:bg-accent';
      return '<button type="button" ' + attr + (current ? ' aria-selected="true"' : '') + ' class="' + cls + '">' + label + '</button>';
    }
    function heute() {
      return '<div class="flex h-full items-center justify-end pe-1"><button type="button" data-cal-today class="text-muted-foreground hover:text-foreground inline-flex cursor-pointer items-center gap-1 text-xs font-medium">' + CAL_TODAY + 'Heute</button></div>';
    }
    function legendHtml() {   // Punkt-Legende im Container: data-legend="destructive:Wochenende,warning:Feiertag"
      if (!legend) return '';
      var items = legend.split(',').map(calTrim).filter(Boolean).map(function (it) {
        var i = it.indexOf(':'), bg = CAL_LEGEND_BG[it.slice(0, i).trim()] || 'bg-muted-foreground';
        return '<span class="flex items-center gap-1.5"><span class="' + bg + ' size-2 rounded-full"></span>' + calEsc(it.slice(i + 1).trim()) + '</span>';
      });
      return '<div class="text-muted-foreground mt-3 flex flex-wrap justify-center gap-x-4 gap-y-1 px-1 text-xs">' + items.join('') + '</div>';
    }

    function head() {
      var h = '<div class="flex items-center justify-between gap-2 px-1 pb-3">' + navBtn('prev');
      if (hasDropdown) {
        h += '<div class="relative"><button type="button" data-cal-dd class="btn" data-variant="outline" data-size="sm" aria-expanded="' + (s.ddOpen ? 'true' : 'false') + '">' + monthName(s.vm) + ' ' + s.vy + CAL_DOWN + '</button>';
        if (s.ddOpen) {
          h += '<div data-cal-menu class="bg-popover text-popover-foreground ring-foreground/10 absolute left-1/2 top-full z-50 mt-1 flex -translate-x-1/2 gap-1 rounded-md p-1 shadow-md ring-1"><div class="pe-1">';
          for (var mi = 0; mi < 12; mi++) h += ddItem(CAL_MONTHS[mi], 'data-cal-month="' + mi + '"', mi === s.vm);
          h += '</div><div class="bg-border w-px self-stretch"></div><div class="ps-1">';
          for (var yy = s.vy - 3; yy <= s.vy + 3; yy++) h += ddItem(String(yy), 'data-cal-year="' + yy + '"', yy === s.vy);
          h += '</div></div>';
        }
        h += '</div>';
      } else {
        h += '<div class="text-sm font-medium">' + monthName(s.vm) + ' ' + s.vy + '</div>';
      }
      return h + navBtn('next') + '</div>';
    }

    function cell(y, m, day) {
      var key = calKey(y, m, day);
      var dow = new Date(y, m, day).getDay();
      var wknd = dow === 0 || dow === 6;
      if ((disWeekends && wknd) || disDates.indexOf(key) >= 0) {
        return '<td><button type="button" disabled aria-disabled="true" class="text-muted-foreground size-9 cursor-not-allowed rounded-md line-through opacity-50">' + day + '</button></td>';
      }
      var SEL = '<button type="button" data-cal-day="' + key + '" aria-selected="true" class="size-9 rounded-md bg-primary text-primary-foreground hover:bg-primary/90">' + day + '</button>';
      if (mode === 'range') {
        // Band-Grenzen: fertiger Bereich (start..end) ODER Vorschau bis zum Zeiger (start..hover).
        var lo = null, hi = null, other = s.end || s.hover;
        if (s.start && other) { lo = s.start < other ? s.start : other; hi = s.start < other ? other : s.start; }
        var inBand = lo && lo !== hi && key >= lo && key <= hi;
        var tdc = inBand ? ('bg-foreground/10' + (key === lo ? ' rounded-l-md' : '') + (key === hi ? ' rounded-r-md' : '')) : '';
        if (key === s.start || key === s.end) return '<td class="' + tdc + '">' + SEL + '</td>';   // schwarze Endpunkte
        if (inBand) return '<td class="' + tdc + '"><button type="button" data-cal-day="' + key + '" class="size-9">' + day + '</button></td>';
      } else if (s.sel === key) {
        return '<td>' + SEL + '</td>';
      }
      var x = 'size-9 rounded-md hover:bg-accent';
      if (key === todayKey) x += todayStyle === 'bold' ? ' font-bold underline underline-offset-2' : ' ring-1 ring-inset ring-foreground/30';
      if (weekendStyle === 'bold' && wknd) x += ' font-bold';
      if (weekendStyle === 'color' && wknd) x += ' text-destructive';
      if (holidays.indexOf(key) >= 0) x += ' text-warning font-semibold';
      return '<td><button type="button" data-cal-day="' + key + '" class="' + x + '">' + day + '</button></td>';
    }

    function grid(y, m, withHeute) {
      var h = '<table class="text-sm [&_td]:p-0"><thead><tr class="text-muted-foreground">';
      for (var w = 0; w < 7; w++) h += '<th class="size-9 font-normal">' + CAL_WEEKDAYS[w] + '</th>';
      h += '</tr></thead><tbody>';
      var startCol = (new Date(y, m, 1).getDay() + 6) % 7;
      var days = new Date(y, m + 1, 0).getDate();
      var day = 1;
      for (var row = 0; row < 6; row++) {           // IMMER 6 Zeilen -> feste Höhe
        h += '<tr>';
        for (var col = 0; col < 7; col++) {
          var blank = (row === 0 && col < startCol) || day > days;
          if (row === 5 && blank) {                 // 6. Zeile ist nie voll -> "Heute" rechts hinein
            h += '<td colspan="' + (7 - col) + '" class="h-9">' + (withHeute ? heute() : '') + '</td>';
            break;
          }
          if (blank) h += '<td class="h-9"></td>';
          else { h += cell(y, m, day); day++; }
        }
        h += '</tr>';
      }
      return h + '</tbody></table>';
    }

    function render() {
      if (nMonths > 1) {
        var h = '<div class="flex flex-col gap-4 sm:flex-row sm:gap-6">';
        for (var i = 0; i < nMonths; i++) {
          var dt = new Date(s.vy, s.vm + i, 1), y = dt.getFullYear(), m = dt.getMonth(), last = i === nMonths - 1;
          h += '<div><div class="flex items-center justify-between px-1 pb-3">' +
            (i === 0 ? navBtn('prev') : '<div class="size-8"></div>') +
            '<div class="text-sm font-medium">' + monthName(m) + ' ' + y + '</div>' +
            (last ? navBtn('next') : '<div class="size-8"></div>') +
            '</div>' + grid(y, m, last) + '</div>';
        }
        el.innerHTML = h + '</div>' + legendHtml();
      } else {
        el.innerHTML = head() + grid(s.vy, s.vm, true) + legendHtml();
      }
    }

    function shift(delta) { var d = new Date(s.vy, s.vm + delta, 1); s.vy = d.getFullYear(); s.vm = d.getMonth(); }
    function pick(key) {
      if (mode === 'range') {
        if (!s.start || s.end) { s.start = key; s.end = null; }
        else if (key < s.start) { s.end = s.start; s.start = key; }
        else { s.end = key; }
      } else { s.sel = key; }
      el.dispatchEvent(new CustomEvent('c22:calendar-change', { bubbles: true, detail: { mode: mode, selected: s.sel, start: s.start, end: s.end } }));
    }

    el.addEventListener('click', function (e) {
      var t = e.target.closest('button');
      if (!t || !el.contains(t)) return;
      if (t.hasAttribute('data-cal-prev')) { shift(-1); render(); }
      else if (t.hasAttribute('data-cal-next')) { shift(1); render(); }
      else if (t.hasAttribute('data-cal-dd')) { e.stopPropagation(); s.ddOpen = !s.ddOpen; render(); }
      else if (t.hasAttribute('data-cal-month')) { s.vm = +t.getAttribute('data-cal-month'); s.ddOpen = false; render(); }
      else if (t.hasAttribute('data-cal-year')) { s.vy = +t.getAttribute('data-cal-year'); s.ddOpen = false; render(); }
      else if (t.hasAttribute('data-cal-today')) { var td = new Date(); s.vy = td.getFullYear(); s.vm = td.getMonth(); s.ddOpen = false; render(); }
      else if (t.hasAttribute('data-cal-day')) { pick(t.getAttribute('data-cal-day')); render(); }
    });
    // Bereich-Vorschau: nach dem Start-Klick das graue Band live bis zum Zeiger ziehen.
    el.addEventListener('mouseover', function (e) {
      if (mode !== 'range' || !s.start || s.end) return;
      var t = e.target.closest('[data-cal-day]');
      var key = t ? t.getAttribute('data-cal-day') : null;
      if (key !== s.hover) { s.hover = key; render(); }
    });
    el.addEventListener('mouseleave', function () {
      if (mode === 'range' && s.hover != null) { s.hover = null; render(); }
    });
    document.addEventListener('click', function (e) { if (s.ddOpen && !el.contains(e.target)) { s.ddOpen = false; render(); } });

    render();
  }

  // ---- Carousel (Basecoat hat keins) ----------------------------------------
  // Aufbauend auf nativem Snap-Scrolling (funktioniert auch ohne JS per Wisch/Trackpad/
  // Pfeiltasten). c22.js macht zusätzlich Prev/Next-Buttons + Punkt-Navigation funktional,
  // markiert JEDE sichtbare Folie (Einzel- wie Mehrfachansicht), pflegt einen "x von y"-Zähler,
  // den Endzustand (Button am Rand deaktiviert) und optionales Autoplay.
  // Markup:  <div data-carousel[="vertical"] [data-carousel-autoplay="4000"] class="relative …">
  //            <div data-carousel-viewport class="… snap-x/​snap-y overflow-…-auto">…Folien…</div>
  //            <button data-carousel-prev …>  <button data-carousel-next …>
  //            <a|button data-carousel-dot …> …          (optional, eine je Folie)
  //            <span data-carousel-counter></span>       (optional, füllt sich mit "x von y")
  //          </div>
  function wireCarousel(root) {
    if (root.dataset.c22CarWired) return;
    root.dataset.c22CarWired = '1';
    var vertical = root.dataset.carousel === 'vertical';
    var autoplay = +root.dataset.carouselAutoplay || 0;
    var vp = root.querySelector('[data-carousel-viewport]');
    if (!vp) return;
    var slides = [].slice.call(vp.children);
    var prev = root.querySelector('[data-carousel-prev]');
    var next = root.querySelector('[data-carousel-next]');
    var dots = [].slice.call(root.querySelectorAll('[data-carousel-dot]'));
    var counter = root.querySelector('[data-carousel-counter]');

    // Schrittweite = Abstand zweier Folien (deckt gap UND Innen-padding ab); sonst Viewport-Maß.
    function step() {
      if (slides.length > 1) {
        return vertical ? slides[1].offsetTop - slides[0].offsetTop
                        : slides[1].offsetLeft - slides[0].offsetLeft;
      }
      return vertical ? vp.clientHeight : vp.clientWidth;
    }
    function maxScroll() { return vertical ? vp.scrollHeight - vp.clientHeight : vp.scrollWidth - vp.clientWidth; }
    function curPos() { return vertical ? vp.scrollTop : vp.scrollLeft; }
    function atEnd() { return (target != null ? target : curPos()) >= maxScroll() - 1; }
    function setEnds(pos) {
      if (prev) prev.disabled = pos <= 1;
      if (next) next.disabled = pos >= maxScroll() - 1;
    }

    // `target` = zuletzt per Button/Punkt beabsichtigte Zielposition. Solange sie gesetzt ist,
    // richtet sich der Endzustand danach — so wird der Rand-Button SOFORT beim Klick grau (die
    // smooth-Animation läuft noch) und flackert währenddessen nicht zurück; aufeinanderfolgende
    // Klicks addieren sich korrekt (Ist-Position hinkt sonst hinterher). `programmatic` markiert das
    // Zeitfenster unserer eigenen Scrolls; ein Scroll außerhalb davon = der Nutzer hat selbst
    // gewischt -> Ziel loslassen, damit wieder die Ist-Position zählt. Nur der Viewport scrollt
    // (kein Seiten-Sprung wie bei einem blanken #anker).
    var target = null, programmatic = 0, ticking = false;
    function scrollToPos(pos) {
      pos = Math.max(0, Math.min(maxScroll(), pos));
      target = pos; programmatic = Date.now() + 700;
      vp.scrollTo(vertical ? { top: pos, behavior: 'smooth' } : { left: pos, behavior: 'smooth' });
      setEnds(pos);
    }
    function go(sign) { scrollToPos((target != null ? target : curPos()) + sign * step()); }
    function goToSlide(i) {
      var vr = vp.getBoundingClientRect(), r = slides[i].getBoundingClientRect();
      scrollToPos(curPos() + (vertical ? r.top - vr.top : r.left - vr.left));
    }

    // Sichtbarer Anteil jeder Folie -> markiert werden ALLE hinreichend sichtbaren (>60 %).
    // Bei 1-je-Ansicht ist das genau eine, bei 3-je-Ansicht drei — dieselbe Logik.
    function update() {
      var vr = vp.getBoundingClientRect(), firstVisible = -1;
      slides.forEach(function (sl, di) {
        var r = sl.getBoundingClientRect();
        var vis = vertical
          ? (Math.min(r.bottom, vr.bottom) - Math.max(r.top, vr.top)) / (r.height || 1)
          : (Math.min(r.right, vr.right) - Math.max(r.left, vr.left)) / (r.width || 1);
        var on = vis > 0.6;
        if (on && firstVisible < 0) firstVisible = di;
        if (dots[di]) dots[di].setAttribute('aria-current', on ? 'true' : 'false');
      });
      if (firstVisible < 0) firstVisible = 0;
      if (counter) counter.textContent = (firstVisible + 1) + ' von ' + slides.length;
      setEnds(target != null ? target : curPos());
    }

    if (prev) prev.addEventListener('click', function () { go(-1); });
    if (next) next.addEventListener('click', function () { go(1); });
    dots.forEach(function (dot, di) {
      dot.addEventListener('click', function (e) { e.preventDefault(); goToSlide(di); });
    });

    vp.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        if (Date.now() > programmatic) target = null;   // Nutzer hat selbst gewischt -> Ziel los
        update();
      });
    });
    update();

    // Autoplay: eine Folie weiter, am Ende zurück auf Anfang (Endlosschleife). Pausiert, solange
    // der Zeiger auf dem Carousel liegt, damit man in Ruhe schauen/bedienen kann.
    if (autoplay > 0) {
      var timer = null;
      function play() { if (!timer) timer = setInterval(function () { atEnd() ? goToSlide(0) : go(1); }, autoplay); }
      function stop() { clearInterval(timer); timer = null; }
      root.addEventListener('pointerenter', stop);
      root.addEventListener('pointerleave', play);
      play();
    }
  }

  // ---- Charts (datengetrieben, SVG) -----------------------------------------
  // Basecoat-Charts nutzen Chart.js auf <canvas> (nicht vendored); shadcn/Recharts nutzt SVG.
  // C22 geht den SVG-Weg: jedes Element ist ein DOM-Knoten -> Highlight/Hover/Tokens/a11y ohne
  // Neuzeichnen. Aus EINER Config (Daten-Array) kommen Skala, Achse, Formen, Legende UND Tooltip
  // -> eine Quelle der Wahrheit (SPOT), keine handberechneten Koordinaten.
  // Markup:  <div data-chart='{ "type":"bar", "labels":["Jan",…],
  //            "series":[{"name":"Besuche","data":[…],"color":"chart-1"}],
  //            "axis":true, "grid":true, "legend":false, "area":false, "max":1000, "unit":"" }'></div>
  // type: bar | bars | stacked | line | lines | step | smooth | donut | radar
  // SVG-Teile werden mit inline var(--token) gefärbt (NICHT mit Tailwind-Utilities) — Tailwind
  // scannt Quellen, JS-generierte Klassen kämen nicht in den Build. Der Tooltip wird in ECHTEN
  // Pixeln (getBoundingClientRect) gesetzt -> skalierungsunabhängig/responsiv.
  var CH_W = 320, CH_H = 180;
  function chCol(c, i) { return 'var(--' + (c || ('chart-' + ((i % 5) + 1))) + ')'; }
  function chNum(n) { return Number(n).toLocaleString('de-DE'); }
  function chNiceMax(v) {
    if (v <= 0) return 1;
    var mag = Math.pow(10, Math.floor(Math.log10(v)));
    var f = v / mag;
    var s = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
    return s * mag;
  }
  function chText(x, y, str, anchor, size, color) {
    return '<text x="' + x + '" y="' + y + '" text-anchor="' + anchor + '" fill="' + chCol(color || 'muted-foreground', 0) +
      '" font-size="' + size + '" style="font-variant-numeric:tabular-nums">' + calEsc(str) + '</text>';
  }
  // Catmull-Rom -> kubische Bézier (weiche Kurve durch alle Punkte).
  function chSmooth(p) {
    var d = 'M' + p[0][0].toFixed(1) + ',' + p[0][1].toFixed(1);
    for (var i = 0; i < p.length - 1; i++) {
      var p0 = p[i - 1] || p[i], p1 = p[i], p2 = p[i + 1], p3 = p[i + 2] || p[i + 1];
      var c1x = p1[0] + (p2[0] - p0[0]) / 6, c1y = p1[1] + (p2[1] - p0[1]) / 6;
      var c2x = p2[0] - (p3[0] - p1[0]) / 6, c2y = p2[1] - (p3[1] - p1[1]) / 6;
      d += 'C' + c1x.toFixed(1) + ',' + c1y.toFixed(1) + ' ' + c2x.toFixed(1) + ',' + c2y.toFixed(1) + ' ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1);
    }
    return d;
  }
  function chTooltip(root) {
    var tip = document.createElement('div');
    tip.className = 'chart-tooltip';
    // WICHTIG: .chart-tooltip (Basecoat) setzt eine eigene CSS-translate-Property (-50% X / 8px Y),
    // die sich zu unserem transform ADDIEREN würde -> alles wandert nach links. Mit translate:none
    // ausschalten, dann steuert allein unser transform die Ausrichtung. Ebenso position:absolute
    // (Klasse ist fixed) -> wir positionieren relativ zum root.
    tip.style.cssText = 'position:absolute;left:0;top:0;opacity:0;pointer-events:none;translate:none;transform:translate(-50%,-100%);transition:opacity .12s;z-index:20';
    root.appendChild(tip);
    return tip;
  }
  function chTipHtml(title, rows) {
    var items = rows.map(function (r) {
      return '<div class="chart-tooltip-item"><span class="chart-tooltip-indicator" style="--chart-indicator-color:' + r.color +
        '"></span><span class="chart-tooltip-label">' + calEsc(r.label) + '</span><span class="chart-tooltip-value">' + calEsc(r.value) + '</span></div>';
    }).join('');
    return '<div class="chart-tooltip-title">' + calEsc(title) + '</div><div class="chart-tooltip-items">' + items + '</div>';
  }
  // Tooltip in echten Pixeln über einem SVG-Punkt (viewBox-Koordinaten) platzieren.
  function chPlace(tip, svgEl, root, vx, vy, vbW, vbH) {
    var sr = svgEl.getBoundingClientRect(), rr = root.getBoundingClientRect();
    tip.style.left = (sr.left - rr.left + vx / vbW * sr.width) + 'px';
    tip.style.top = (sr.top - rr.top + vy / vbH * sr.height - 10) + 'px';
    tip.style.opacity = '1';
  }
  // Tortenstück (Keil vom Mittelpunkt bis Radius r über den Winkelbereich a0..a1) — als volle,
  // transparente Trefferfläche für runde Charts, damit die Maus sauber je Segment/Achse zählt.
  function chWedge(cx, cy, r, a0, a1) {
    var x0 = cx + r * Math.cos(a0), y0 = cy + r * Math.sin(a0);
    var x1 = cx + r * Math.cos(a1), y1 = cy + r * Math.sin(a1);
    var large = (a1 - a0) > Math.PI ? 1 : 0;
    return 'M' + cx + ',' + cy + 'L' + x0.toFixed(1) + ',' + y0.toFixed(1) +
      'A' + r + ' ' + r + ' 0 ' + large + ' 1 ' + x1.toFixed(1) + ',' + y1.toFixed(1) + 'Z';
  }
  // Runde Charts: Tooltip radial (Richtung angle) ab dem Basispunkt (baseX,baseY in viewBox) nach außen
  // setzen, so dass sein EUKLIDISCH nächster Punkt konstanten Abstand (extraR + gap) zum Basispunkt hält.
  // Die Referenz ist ein Kreis mit Radius extraR um den Basispunkt — das deckt beide Geometrien mit einer
  // Formel ab:
  //   Donut  = durchgehender Ring: base = Kreismittelpunkt, extraR = Ringradius -> Abstand zur Ringkurve
  //            konstant (kürzeste Distanz, überall gleicher Spalt zum Ring).
  //   Radar  = diskreter Vertex:   base = Vertex, extraR = 0 -> Abstand direkt zum Punkt konstant.
  // Nur so ist es oben wie unten gleich; das Radar-Polygon ist nicht vertikal zentriert, also darf hier
  // NICHT gegen den Mittelpunkt gerechnet werden. Abstand wächst monoton mit dem Vorschub t -> Bisektion.
  function chPlaceRadial(tip, svgEl, root, baseX, baseY, angle, vbW, extraR) {
    var sr = svgEl.getBoundingClientRect(), rr = root.getBoundingClientRect();
    var scale = sr.width / vbW;                        // uniform (svg behält viewBox-Seitenverhältnis)
    var dx = Math.cos(angle), dy = Math.sin(angle);
    tip.style.transform = 'translate(-50%,-50%)';
    var w = tip.offsetWidth, h = tip.offsetHeight, target = (extraR || 0) * scale + 10;   // +10px Spalt
    function nearest(t) {                              // Abstand Basispunkt -> nächster Rechteckpunkt (Mitte bei base + t*dir)
      var ncx = dx * t, ncy = dy * t;
      var nx = Math.max(ncx - w / 2, Math.min(0, ncx + w / 2));
      var ny = Math.max(ncy - h / 2, Math.min(0, ncy + h / 2));
      return Math.sqrt(nx * nx + ny * ny);
    }
    var lo = 0, hi = target + Math.max(w, h);
    for (var k = 0; k < 32; k++) { var mid = (lo + hi) / 2; if (nearest(mid) < target) lo = mid; else hi = mid; }
    tip.style.left = (sr.left - rr.left + baseX * scale + dx * hi) + 'px';
    tip.style.top = (sr.top - rr.top + baseY * scale + dy * hi) + 'px';
    tip.style.opacity = '1';
  }
  function chLegItem(label, color) {
    return '<li><span class="chart-legend-item"><span class="chart-legend-indicator" style="--chart-indicator-color:' + color +
      '"></span><span>' + calEsc(label) + '</span></span></li>';
  }
  function chLegend(cfg) {
    if (!cfg.legend) return '';
    var items;
    if (cfg.type === 'donut') {
      items = (cfg.labels || []).map(function (l, i) { return chLegItem(l, chCol(((cfg.series[0] || {}).colors || [])[i], i)); });
    } else {
      items = (cfg.series || []).map(function (se, i) { return chLegItem(se.name || '', chCol(se.color, i)); });
    }
    return '<ul class="chart-legend" style="margin-top:12px">' + items.join('') + '</ul>';
  }
  // Serien -> Tooltip-Zeilen (Farbe/Name/Wert+Einheit); geteilt von kartesischen Charts und Radar.
  function chRows(series, i, unit) {
    return series.map(function (se, si) {
      return { color: chCol(se.color, si), label: se.name || '', value: chNum(se.data[i] || 0) + (unit || '') };
    });
  }
  // Skalen-Maximum aus allen Serienwerten (schön gerundet), oder cfg.max wenn gesetzt.
  function chSeriesMax(cfg, series) {
    return cfg.max || chNiceMax(Math.max.apply(null, series.map(function (se) { return Math.max.apply(null, se.data); })) || 1);
  }
  // SVG + Legende in root setzen, Tooltip anlegen; root wird relativ (Tooltip liegt absolut darüber).
  function chMount(root, cfg, svg) {
    root.style.position = 'relative';
    root.innerHTML = svg + chLegend(cfg);
    return { svgEl: root.querySelector('svg'), tip: chTooltip(root) };
  }
  // Hover verdrahten: pointerenter je [data-hit] -> show(i), Zeiger verlässt das SVG -> hide().
  function chHover(svgEl, show, hide) {
    [].slice.call(svgEl.querySelectorAll('[data-hit]')).forEach(function (h, i) {
      h.addEventListener('pointerenter', function () { show(i); });
    });
    svgEl.addEventListener('pointerleave', hide);
  }

  function chartCartesian(root, cfg) {
    var type = cfg.type;
    var labels = cfg.labels || [];
    var series = cfg.series || [];
    var N = labels.length;
    var grid = cfg.grid !== false;
    var axis = !!cfg.axis;
    var padL = axis ? 42 : 14, padR = 14, padT = 14, padB = 26;
    var x0 = padL, x1 = CH_W - padR, y0 = padT, y1 = CH_H - padB;
    var band = (x1 - x0) / N;
    function xc(i) { return x0 + band * (i + 0.5); }

    var max = type === 'stacked'
      ? (cfg.max || chNiceMax(Math.max.apply(null, labels.map(function (_, i) { return series.reduce(function (a, se) { return a + (se.data[i] || 0); }, 0); })) || 1))
      : chSeriesMax(cfg, series);
    function yv(v) { return y1 - (v / max) * (y1 - y0); }

    var ticks = cfg.ticks || 4, s = '';
    for (var t = 0; t <= ticks; t++) {
      var val = max * t / ticks, gy = yv(val);
      if (grid) s += '<line x1="' + x0 + '" y1="' + gy.toFixed(1) + '" x2="' + x1 + '" y2="' + gy.toFixed(1) + '" stroke="var(--border)" stroke-width="1"/>';
      if (axis) s += chText(padL - 6, gy + 3, chNum(val), 'end', 10);
    }
    if (axis) s += '<line x1="' + x0 + '" y1="' + y0 + '" x2="' + x0 + '" y2="' + y1 + '" stroke="var(--muted-foreground)" stroke-width="1"/>';

    if (type === 'bar' || type === 'bars') {
      var m = type === 'bar' ? 1 : series.length, bw = band * 0.62 / m;
      series.forEach(function (se, si) {
        var g = '<g fill="' + chCol(se.color, si) + '">';
        for (var i = 0; i < N; i++) {
          var v = se.data[i] || 0, by = yv(v), bh = y1 - by;
          var cx = type === 'bar' ? xc(i) : (xc(i) - band * 0.31 + bw * (si + 0.5));
          g += '<rect data-cat="' + i + '" x="' + (cx - bw / 2).toFixed(1) + '" y="' + by.toFixed(1) + '" width="' + bw.toFixed(1) + '" height="' + Math.max(0, bh).toFixed(1) + '" rx="3"/>';
        }
        s += g + '</g>';
      });
    } else if (type === 'stacked') {
      var w = band * 0.62;
      for (var i = 0; i < N; i++) {
        var acc = 0;
        for (var si = 0; si < series.length; si++) {
          var v = series[si].data[i] || 0, yTop = yv(acc + v), yBot = yv(acc);
          s += '<rect data-cat="' + i + '" fill="' + chCol(series[si].color, si) + '" x="' + (xc(i) - w / 2).toFixed(1) + '" y="' + yTop.toFixed(1) +
            '" width="' + w.toFixed(1) + '" height="' + Math.max(0, yBot - yTop).toFixed(1) + '" rx="' + (si === series.length - 1 ? '3' : '0') + '"/>';
          acc += v;
        }
      }
    } else { // line | lines | step | smooth
      series.forEach(function (se, si) {
        var col = chCol(se.color, si);
        var pts = se.data.map(function (v, i) { return [xc(i), yv(v)]; });
        var d;
        if (type === 'step') { d = 'M' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1); for (var k = 1; k < pts.length; k++) d += 'H' + pts[k][0].toFixed(1) + 'V' + pts[k][1].toFixed(1); }
        else if (type === 'smooth') { d = chSmooth(pts); }
        else { d = 'M' + pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join('L'); }
        if (cfg.area && series.length === 1 && type !== 'step') {
          s += '<path d="' + d + 'L' + pts[pts.length - 1][0].toFixed(1) + ',' + y1 + 'L' + pts[0][0].toFixed(1) + ',' + y1 + 'Z" fill="' + col + '" fill-opacity="0.12"/>';
        }
        s += '<path d="' + d + '" fill="none" stroke="' + col + '" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>';
      });
      s += '<line data-focus-line x1="0" y1="' + y0 + '" x2="0" y2="' + y1 + '" stroke="var(--muted-foreground)" stroke-width="1" stroke-dasharray="4 3" opacity="0"/>';
      series.forEach(function (se, si) { s += '<circle data-focus-dot="' + si + '" r="4.5" fill="var(--background)" stroke="' + chCol(se.color, si) + '" stroke-width="2.5" opacity="0"/>'; });
    }

    if (cfg.xLabels !== false) for (var i = 0; i < N; i++) s += chText(xc(i), y1 + 16, labels[i], 'middle', 10);
    for (var i = 0; i < N; i++) s += '<rect data-hit="' + i + '" x="' + (x0 + band * i).toFixed(1) + '" y="' + y0 + '" width="' + band.toFixed(1) + '" height="' + (y1 - y0) + '" fill="transparent"/>';

    var m = chMount(root, cfg, '<svg viewBox="0 0 ' + CH_W + ' ' + CH_H + '" style="display:block;width:100%" fill="none">' + s + '</svg>');
    var svgEl = m.svgEl, tip = m.tip;
    var catRects = [].slice.call(svgEl.querySelectorAll('rect[data-cat]'));
    var focusLine = svgEl.querySelector('[data-focus-line]');
    var focusDots = [].slice.call(svgEl.querySelectorAll('[data-focus-dot]'));

    function show(i) {
      var rows = chRows(series, i, cfg.unit);
      if (type === 'stacked') rows.reverse();
      tip.innerHTML = chTipHtml(labels[i], rows);
      var topVal = type === 'stacked'
        ? series.reduce(function (a, se) { return a + (se.data[i] || 0); }, 0)
        : Math.max.apply(null, series.map(function (se) { return se.data[i] || 0; }));
      chPlace(tip, svgEl, root, xc(i), yv(topVal), CH_W, CH_H);
      catRects.forEach(function (r) { r.style.opacity = (+r.getAttribute('data-cat') === i) ? '1' : '0.3'; });
      if (focusLine) { focusLine.setAttribute('x1', xc(i)); focusLine.setAttribute('x2', xc(i)); focusLine.setAttribute('opacity', '0.5'); }
      focusDots.forEach(function (d, si) { d.setAttribute('cx', xc(i)); d.setAttribute('cy', yv(series[si].data[i] || 0)); d.setAttribute('opacity', '1'); });
    }
    function hide() {
      tip.style.opacity = '0';
      catRects.forEach(function (r) { r.style.opacity = '1'; });
      if (focusLine) focusLine.setAttribute('opacity', '0');
      focusDots.forEach(function (d) { d.setAttribute('opacity', '0'); });
    }
    chHover(svgEl, show, hide);
  }

  function chartDonut(root, cfg) {
    var labels = cfg.labels || [];
    var se0 = (cfg.series && cfg.series[0]) || { data: [] };
    var data = se0.data || [], colors = se0.colors || [];
    var total = data.reduce(function (a, b) { return a + b; }, 0) || 1;
    var cx = 70, cy = 70, R = 52, sw = 20, C = 2 * Math.PI * R, VB = 140, gap = 1.5;
    var rHit = R + sw / 2 + 2;                 // Keil bis knapp über den Ring
    var off = 0, segs = '', hits = '', midAngles = [];
    data.forEach(function (v, i) {
      var len = v / total * C;
      segs += '<circle data-seg="' + i + '" cx="' + cx + '" cy="' + cy + '" r="' + R + '" fill="none" stroke="' + chCol(colors[i], i) +
        '" stroke-width="' + sw + '" stroke-dasharray="' + Math.max(0, len - gap).toFixed(2) + ' ' + (C - Math.max(0, len - gap)).toFixed(2) +
        '" stroke-dashoffset="' + (-off).toFixed(2) + '" transform="rotate(-90 ' + cx + ' ' + cy + ')"/>';
      var a0 = -Math.PI / 2 + off / C * 2 * Math.PI, a1 = -Math.PI / 2 + (off + len) / C * 2 * Math.PI;
      midAngles.push((a0 + a1) / 2);
      hits += '<path data-hit="' + i + '" d="' + chWedge(cx, cy, rHit, a0, a1) + '" fill="transparent"/>';
      off += len;
    });
    var center = cfg.center || {}, ctext = '';
    if (center.value != null) ctext += '<text x="' + cx + '" y="' + (cy - 2) + '" text-anchor="middle" fill="var(--foreground)" style="font-size:17px;font-weight:600">' + calEsc(center.value) + '</text>';
    if (center.label != null) ctext += '<text x="' + cx + '" y="' + (cy + 13) + '" text-anchor="middle" fill="var(--muted-foreground)" style="font-size:9px">' + calEsc(center.label) + '</text>';
    var m = chMount(root, cfg, '<svg viewBox="0 0 ' + VB + ' ' + VB + '" style="display:block;margin:0 auto;width:160px" fill="none">' + segs + ctext + hits + '</svg>');
    var svgEl = m.svgEl, tip = m.tip;
    var segEls = [].slice.call(svgEl.querySelectorAll('[data-seg]'));
    function show(i) {
      tip.innerHTML = chTipHtml(labels[i] || '', [{ color: chCol(colors[i], i), label: cfg.unit || 'Anteil', value: Math.round(data[i] / total * 100) + ' %' }]);
      chPlaceRadial(tip, svgEl, root, cx, cy, midAngles[i], VB, R + sw / 2);   // Kreis-Referenz: Ring um Mitte
      segEls.forEach(function (e, j) { e.style.opacity = j === i ? '1' : '0.3'; });
    }
    function hide() { tip.style.opacity = '0'; segEls.forEach(function (e) { e.style.opacity = '1'; }); }
    chHover(svgEl, show, hide);
  }

  function chartRadar(root, cfg) {
    var labels = cfg.labels || [], series = cfg.series || [], n = labels.length;
    var VBW = 240, VBH = 188, cx = VBW / 2, cy = 94, R = 62;   // breite viewBox -> Achsenlabels ragen nicht raus
    var max = chSeriesMax(cfg, series);
    function ang(i) { return -Math.PI / 2 + i * 2 * Math.PI / n; }
    function pt(i, frac) { var a = ang(i); return [cx + R * frac * Math.cos(a), cy + R * frac * Math.sin(a)]; }
    function ring(k) { var p = []; for (var i = 0; i < n; i++) { var q = pt(i, k); p.push(q[0].toFixed(1) + ',' + q[1].toFixed(1)); } return p.join(' '); }
    var s = '';
    [0.33, 0.66, 1].forEach(function (k) { s += '<polygon points="' + ring(k) + '" stroke="var(--border)" stroke-width="1" fill="none"/>'; });
    for (var i = 0; i < n; i++) { var p = pt(i, 1); s += '<line x1="' + cx + '" y1="' + cy + '" x2="' + p[0].toFixed(1) + '" y2="' + p[1].toFixed(1) + '" stroke="var(--border)" stroke-width="1"/>'; }
    series.forEach(function (se, si) {
      var col = chCol(se.color, si);
      var pts = se.data.map(function (v, i) { return pt(i, v / max); });
      s += '<polygon points="' + pts.map(function (p) { return p[0].toFixed(1) + ',' + p[1].toFixed(1); }).join(' ') + '" fill="' + col + '" fill-opacity="0.2" stroke="' + col + '" stroke-width="2.5" stroke-linejoin="round"/>';
      pts.forEach(function (p, i) { s += '<circle data-dot="' + si + '-' + i + '" cx="' + p[0].toFixed(1) + '" cy="' + p[1].toFixed(1) + '" r="3" fill="' + col + '"/>'; });
    });
    for (var i = 0; i < n; i++) {
      var p = pt(i, 1.16), dx = Math.cos(ang(i));
      var anchor = Math.abs(dx) < 0.3 ? 'middle' : (dx > 0 ? 'start' : 'end');
      s += chText(p[0].toFixed(1), (p[1] + 3).toFixed(1), labels[i], anchor, 9);
    }
    for (var i = 0; i < n; i++) { s += '<path data-hit="' + i + '" d="' + chWedge(cx, cy, R * 1.12, ang(i) - Math.PI / n, ang(i) + Math.PI / n) + '" fill="transparent"/>'; }
    var m = chMount(root, cfg, '<svg viewBox="0 0 ' + VBW + ' ' + VBH + '" style="display:block;margin:0 auto;width:230px" fill="none">' + s + '</svg>');
    var svgEl = m.svgEl, tip = m.tip;
    function show(i) {
      tip.innerHTML = chTipHtml(labels[i], chRows(series, i, cfg.unit));
      var vtx = pt(i, 1);                              // Punkt-Referenz: Polygon-Vertex auf der Achse (extraR=0)
      chPlaceRadial(tip, svgEl, root, vtx[0], vtx[1], ang(i), VBW);
      series.forEach(function (se, si) { var d = svgEl.querySelector('[data-dot="' + si + '-' + i + '"]'); if (d) d.setAttribute('r', '5'); });
    }
    function hide() { tip.style.opacity = '0'; [].slice.call(svgEl.querySelectorAll('[data-dot]')).forEach(function (d) { d.setAttribute('r', '3'); }); }
    chHover(svgEl, show, hide);
  }

  function wireChart(root) {
    if (root.dataset.c22ChartWired) return;
    root.dataset.c22ChartWired = '1';
    var cfg;
    try { cfg = JSON.parse(root.dataset.chart || '{}'); } catch (e) { return; }
    if (cfg.type === 'donut') return chartDonut(root, cfg);
    if (cfg.type === 'radar') return chartRadar(root, cfg);
    chartCartesian(root, cfg);
  }

  function init(root) {
    wirePhIcons(root);
    (root || document).querySelectorAll('.context-menu').forEach(wireContextMenu);
    (root || document).querySelectorAll('[data-calendar]').forEach(wireCalendar);
    (root || document).querySelectorAll('[data-carousel]').forEach(wireCarousel);
    (root || document).querySelectorAll('[data-chart]').forEach(wireChart);
    wireGlobals();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
  window.C22 = window.C22 || {};
  window.C22.init = init;             // Context-Menu + Kalender + Carousel (für dynamisch nachgeladenes Markup)
  window.C22.initContextMenus = init;
  window.C22.wireChart = wireChart;   // einzelnes [data-chart]-Element gezielt verdrahten
  window.C22.phIcon = phIcon;         // Phosphor-SVG als String: phIcon(name, gewicht)
})();

/* C22: Command-Palette ohne initiale Vorauswahl (weder eingebettet noch im Popover/Dialog).
   basecoat markiert beim Init IMMER den ersten Treffer aktiv (das Enter-Ziel einer Palette) — das
   wirkt wie eine feste Auswahl, auch in einer frisch geöffneten Palette. Hier wird diese INITIALE
   Markierung entfernt; Maus/Tastatur setzen sie bei der ersten Interaktion normal wieder (basecoat
   mousemove/keydown). Capture, weil basecoat:initialized nicht bubbelt. */
document.addEventListener('basecoat:initialized', function (e) {
  var el = e.target;
  if (!el || !el.classList || !el.classList.contains('command')) return;
  var active = el.querySelector('[role="menuitem"].active');
  if (!active) return;
  active.classList.remove('active');
  var input = el.querySelector('header input');
  if (input) input.removeAttribute('aria-activedescendant');
}, true);
