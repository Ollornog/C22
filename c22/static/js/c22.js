// C22 — eigenes, minimales Verhalten für Components, die Basecoat NICHT mitbringt.
// Ergänzt basecoat.all.min.js (das die übrigen Components live macht). Kein Build-Schritt,
// keine Abhängigkeit: eine Datei einbinden, fertig. Alles hängt an data-Attributen im Markup.
(function () {
  'use strict';

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

  function init(root) {
    (root || document).querySelectorAll('.context-menu').forEach(wireContextMenu);
    wireGlobals();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { init(); });
  } else {
    init();
  }
  window.C22 = window.C22 || {};
  window.C22.initContextMenus = init; // für dynamisch nachgeladenes Markup
})();
