/* ============================================================
   C22 · c22.js — Verhalten der Bausteine (framework-frei, kein Build).
   - Umschalter: gleitender Daumen + ARIA; koppelbar an Theme / Größe / Toast-Position
   - Dropdown: <details class="menu"> schließt bei Escape / Klick außerhalb
   - Toasts: window.c22Toast(text, art)  → Icon+Farbe je Art (Farbsehschwäche-fest),
             identische Meldungen werden gebündelt (Zähler statt Flut),
             ab 2 Meldungen erscheint „Alle schließen".
             window.c22ToastPosition(pos) · window.c22ToastCloseAll()
   Anti-FOUC (Theme vor dem ersten Paint) gehört INLINE in den <head>.
   ============================================================ */
(function () {
  "use strict";
  var THEMES = ["hell", "ambient", "dunkel"];
  var STORE = "c22-theme";

  /* ---------- SPOT: Meldungsarten an EINER Stelle ----------
     Pro Art: Icon (Phosphor-NAME — eigene FORM, farbsehschwäche-fest), Filter-Gruppe, Anzeige-
     Priorität, Label. Genutzt von Banner + Toast + Popup + Historie. Die FARBE liefert das
     gleichnamige CSS-Token (--bad/--warn/--info/--ok/--status/--app/--progress) über die Klasse .<kind>. */
  var KIND = {
    bad:      { label: "Fehler",      group: "fehler",     prio: 6, icon: "x-circle" },
    warn:     { label: "Warnung",     group: "fehler",     prio: 5, icon: "warning" },
    progress: { label: "Fortschritt", group: "status",     prio: 4, icon: "circle-notch" },
    info:     { label: "Info",        group: "mitteilung", prio: 3, icon: "info" },
    ok:       { label: "Erfolg",      group: "mitteilung", prio: 2, icon: "check-circle" },
    status:   { label: "Status",      group: "status",     prio: 1, icon: "pulse" },
    app:      { label: "App",         group: "app",        prio: 0, icon: "squares-four" }
  };

  /* ---------- Icons: Phosphor-Subset (icons.js) + schaltbares Gewicht ----------
     Vierte Look-Achse `data-icon-weight` (thin/light/regular/bold/fill/duotone). EINE Quelle
     (window.C22_ICONS), ein Rahmen; das Gewicht wird zur Renderzeit gelesen. Elemente mit
     [data-c22-ico="<name>"] werden befüllt und bei Achsenwechsel neu gerendert (renderIcons). */
  var ICON_WEIGHTS = ["thin", "light", "regular", "bold", "fill", "duotone"];
  function iconWeight() {
    var w = document.documentElement.dataset.iconWeight;
    return ICON_WEIGHTS.indexOf(w) >= 0 ? w : "regular";
  }
  function iconInner(name) {
    var ic = window.C22_ICONS && window.C22_ICONS[name];
    if (!ic) return "";
    return ic[iconWeight()] || ic.regular || "";
  }
  function svgFor(name) {
    return '<svg viewBox="0 0 256 256" fill="currentColor" aria-hidden="true">' + iconInner(name) + '</svg>';
  }
  function iconSVG(kind) {   // KIND-Schlüssel → SVG im aktuellen Gewicht (Signatur bleibt kompatibel)
    return svgFor((KIND[kind] || KIND.info).icon);
  }
  // Icon-Host: <span class="…" data-c22-ico="name">…</span> — teilnahmefähig am Gewichts-Wechsel
  function iconSpan(cls, name) {
    return '<span class="' + cls + '" data-c22-ico="' + name + '">' + svgFor(name) + '</span>';
  }
  function renderIcons(root) {
    (root || document).querySelectorAll("[data-c22-ico]").forEach(function (el) {
      el.innerHTML = svgFor(el.dataset.c22Ico);
    });
  }
  window.c22RenderIcons = renderIcons;

  /* ---------- Umschalter ---------- */
  function applyEffect(sw, val) {
    if (!val) return;
    if (sw.hasAttribute("data-theme-switch") && THEMES.indexOf(val) >= 0) {
      document.documentElement.dataset.theme = val;
      try { localStorage.setItem(STORE, val); } catch (e) {}
    }
    if (sw.hasAttribute("data-size-switch")) document.documentElement.dataset.size = val;
    if (sw.hasAttribute("data-shape-switch")) document.documentElement.dataset.shape = val;   // Form/Ecken: Mechanik bleibt, nur der Look ändert sich
    if (sw.hasAttribute("data-icon-switch")) { document.documentElement.dataset.iconWeight = val; renderIcons(); }   // Icon-Gewicht (Phosphor) live umstellen
    if (sw.hasAttribute("data-toast-switch")) setToastPosition(val);
  }
  function selectSegment(sw, btn) {
    var btns = Array.prototype.slice.call(sw.querySelectorAll("button"));
    var i = btns.indexOf(btn);
    if (i < 0) return;
    sw.style.setProperty("--i", i);
    btns.forEach(function (b, bi) { b.setAttribute("aria-checked", bi === i ? "true" : "false"); });
    applyEffect(sw, btn.getAttribute("data-value"));
  }
  function initSwitches() {
    document.querySelectorAll(".switch").forEach(function (sw) {
      var btns = Array.prototype.slice.call(sw.querySelectorAll("button"));
      var start = 0;
      btns.forEach(function (b, i) { if (b.getAttribute("aria-checked") === "true") start = i; });
      if (sw.hasAttribute("data-theme-switch")) {
        var ci = THEMES.indexOf(document.documentElement.dataset.theme || "hell");
        if (ci >= 0) start = ci;
      }
      if (sw.hasAttribute("data-shape-switch")) {
        var si = ["eckig", "normal", "rund"].indexOf(document.documentElement.dataset.shape || "normal");
        if (si >= 0) start = si;
      }
      if (sw.hasAttribute("data-icon-switch")) {
        var wi = ICON_WEIGHTS.indexOf(document.documentElement.dataset.iconWeight || "regular");
        if (wi >= 0) start = wi;
      }
      sw.style.setProperty("--i", start);
      btns.forEach(function (b, i) { b.setAttribute("aria-checked", i === start ? "true" : "false"); });
      applyEffect(sw, btns[start] && btns[start].getAttribute("data-value"));
      sw.addEventListener("click", function (e) {
        if (sw.classList.contains("cycle")) {          // Klick irgendwo → nächster Eintrag
          var cur = btns.findIndex(function (b) { return b.getAttribute("aria-checked") === "true"; });
          selectSegment(sw, btns[(cur + 1) % btns.length]);
          return;
        }
        var btn = e.target.closest("button");
        if (btn && sw.contains(btn)) selectSegment(sw, btn);
      });
      sw.addEventListener("keydown", function (e) {
        if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].indexOf(e.key) < 0) return;
        var cur = btns.findIndex(function (b) { return b.getAttribute("aria-checked") === "true"; });
        var fwd = e.key === "ArrowRight" || e.key === "ArrowDown";
        var next = fwd ? Math.min(btns.length - 1, cur + 1) : Math.max(0, cur - 1);
        selectSegment(sw, btns[next]); btns[next].focus(); e.preventDefault();
      });
    });
  }

  /* ---------- Dropdown / Menü ---------- */
  /* Rand-Kollision: ragt das Panel raus, nach oben klappen / rechtsbündig ziehen.
     Feste Richtungen (drop-up/left/right vom Autor gesetzt) bleiben unangetastet. */
  function placePanel(d) {
    var panel = d.querySelector(".menu-panel");
    if (!panel || panel.dataset.fixed) return;
    panel.classList.remove("drop-up", "align-end");
    var r = panel.getBoundingClientRect();
    if (r.bottom > window.innerHeight - 8 && (r.top - r.height) > 8) panel.classList.add("drop-up");
    if (r.right > window.innerWidth - 8) panel.classList.add("align-end");
  }
  function initMenus() {
    document.querySelectorAll("details.menu").forEach(function (d) {
      var panel = d.querySelector(".menu-panel");
      if (panel && /drop-(up|left|right)/.test(panel.className)) panel.dataset.fixed = "1";
      d.addEventListener("toggle", function () {
        if (d.open) placePanel(d);
        else if (panel && !panel.dataset.fixed) panel.classList.remove("drop-up", "align-end");   // sonst flackert das nächste Öffnen
      });
      if (d.classList.contains("hover")) {          // Auto-open mit kurzem Delay; Klick öffnet sofort
        var openT, closeT, sum = d.querySelector("summary");
        d.addEventListener("mouseenter", function () { clearTimeout(closeT); openT = setTimeout(function () { d.open = true; }, 220); });
        d.addEventListener("mouseleave", function () { clearTimeout(openT); closeT = setTimeout(function () { d.open = false; }, 500); });
        if (sum) sum.addEventListener("click", function (e) { clearTimeout(openT); if (d.open) e.preventDefault(); });   // Klick = sofort, Hover-Delay abbrechen
      }
    });
    document.addEventListener("click", function (e) {
      document.querySelectorAll("details.menu[open]").forEach(function (d) {
        if (!d.contains(e.target)) d.removeAttribute("open");
      });
    });
    // Escape für Menüs läuft über den EINEN Overlay-Koordinator (initPopups) — kein eigener Handler mehr,
    // sonst würde ein Escape gleichzeitig Menü UND Popup schließen (dismissible-stack).
  }

  /* ---------- Banner (im Layout; Stickyness folgt der Titelleiste) ---------- */
  function bannerHost() {
    var host = document.getElementById("c22-banners");
    if (host) return host;
    host = document.createElement("div"); host.id = "c22-banners";
    document.body.insertBefore(host, document.body.firstChild);   // ÜBER allem — auch über der Titelleiste
    // Klebt die Titelleiste oben (sticky/fixed), soll der Banner mit oben bleiben und die Titelleiste
    // unter sich schieben: Banner sticky top:0, und der sticky-Top der Titelleiste wird live auf die
    // Banner-Höhe nachgeführt (Banner zu → zurück). Titelleiste = [data-c22-titlebar] oder erstes <header>.
    var bar = document.querySelector("[data-c22-titlebar]") || document.querySelector("header");
    var pos = bar ? getComputedStyle(bar).position : "";
    if (bar && (pos === "sticky" || pos === "fixed")) {
      host.style.position = "sticky"; host.style.insetBlockStart = "0"; host.style.zIndex = "55";
      var barTop0 = getComputedStyle(bar).top;   // Original merken
      var sync = function () {
        var h = host.offsetHeight;
        bar.style.top = h ? h + "px" : (barTop0 === "auto" ? "" : barTop0);
      };
      if (window.ResizeObserver) new ResizeObserver(sync).observe(host);
      sync();
    }
    return host;
  }
  function banner(msg, kind, opts) {
    opts = opts || {};
    var el = document.createElement("div");
    el.className = "banner slide-in" + (kind ? " " + kind : "");
    // KEIN role=alert/status mehr — die Ansage übernimmt der Announcer (sonst Doppelansage)
    var h = iconSpan("banner-icon", (KIND[kind] || KIND.info).icon) + '<div class="banner-msg"></div><div class="banner-actions">';
    if (opts.action) h += '<button class="btn ghost banner-act" type="button"></button>';
    h += '<button class="banner-x" type="button" aria-label="Schließen">×</button></div>';
    el.innerHTML = h;
    el.querySelector(".banner-msg").textContent = msg;
    if (opts.action) {
      var a = el.querySelector(".banner-act"); a.textContent = opts.action;
      if (opts.onAction) a.addEventListener("click", opts.onAction);
    }
    el.querySelector(".banner-x").addEventListener("click", function () { el.remove(); });
    bannerHost().appendChild(el);
    announce(msg, kind === "bad" || kind === "warn");
    pushHistory(msg, kind || "info", "", "", "", "", "");   // Banner landen IMMER in der Historie (wie Toasts)
    return el;
  }
  window.c22Banner = banner;

  /* ---------- Benachrichtigungs-Center (stille Oberfläche / Historie) ---------- */
  var HIST = [];
  var centerFilter = "all";
  var appFilter = [];   // Feinfilter innerhalb „Apps": leere Liste = alle Apps, sonst nur die gewählten App-Keys (Mehrfachauswahl)
  // Filter-Gruppen als Wechsler — IMMER alle sichtbar; „Apps" nimmt spätere App-Benachrichtigungen (item.group === "app").
  var GROUPS = [
    { key: "all",        label: "Alle" },
    { key: "fehler",     label: "Fehler" },
    { key: "mitteilung", label: "Mitteilungen" },
    { key: "status",     label: "Status" },
    { key: "app",        label: "Apps" }
  ];
  function groupOf(item) {
    if (item.group) return item.group;                                        // explizit (App-Benachrichtigung)
    return (KIND[item.kind] && KIND[item.kind].group) || "mitteilung";        // sonst aus der SPOT-Registry
  }
  // title + kind + Untertitel(text) + optionale Notiz(HTML, aufklappbar) + eigenes Icon + Gruppe + App-Key + Zeitstempel
  function pushHistory(title, kind, text, note, icon, group, app) {
    HIST.push({ title: title, kind: kind, text: text || "", note: note || "", icon: icon || "", group: group || "", app: app || "", time: Date.now() });
    updateBells();
  }
  function updateBells() {   // kein Zähler mehr — Meldungen erschienen bereits als Toast, gelten als gelesen
    document.querySelectorAll(".bell .bell-badge").forEach(function (b) { b.remove(); });
  }
  // Zeitinfo für die History: absolute Zeit + (nur heute, solange KEIN Datum nötig ist) „vor X Min/Std".
  function timeInfo(ts) {
    if (!ts) return { time: "", rel: "" };
    var now = new Date(), d = new Date(ts), diffS = (now - d) / 1000, p = function (n) { return (n < 10 ? "0" : "") + n; };
    var hhmm = p(d.getHours()) + ":" + p(d.getMinutes());
    var sameDay = d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth() && d.getDate() === now.getDate();
    if (!sameDay) return { time: p(d.getDate()) + "." + p(d.getMonth() + 1) + "." + d.getFullYear() + ", " + hhmm, rel: "" };   // Datum → keine vergangene Zeit
    if (diffS < 60) return { time: "gerade", rel: "" };
    var mins = Math.floor(diffS / 60);
    return { time: hhmm, rel: mins < 60 ? "vor " + mins + " Min" : "vor " + Math.floor(mins / 60) + " Std" };
  }
  function centerItem(item) {
    var row = document.createElement("div");
    row.className = "center-item " + item.kind + (item.note ? " has-note" : "");
    var ti = timeInfo(item.time);
    row.innerHTML =
      (item.icon ? '<span class="ci-icon">' + item.icon + '</span>' : iconSpan("ci-icon", (KIND[item.kind] || KIND.info).icon)) +   // App darf eigenes Icon liefern
      '<div class="ci-body">' +
        '<div class="ci-head"><span class="ci-msg"></span>' +               // Titel links, Zeit rechts (wie vorher)
          '<span class="ci-timeblock"><span class="ci-time"></span>' +
            (ti.rel ? '<span class="ci-rel"><span class="ci-clock" data-c22-ico="clock" aria-hidden="true">' + svgFor("clock") + '</span><span class="ci-reltext"></span></span>' : '') +
          '</span></div>' +
        (item.text ? '<span class="ci-sub"></span>' : '') +                 // Untertitel — immer sichtbar
        (item.note ? '<div class="ci-note"></div>' : '') +                  // Notiz INLINE sichtbar → Link/Button direkt klickbar
      '</div>';
    row.querySelector(".ci-msg").textContent = item.title;
    row.querySelector(".ci-time").textContent = ti.time;
    if (ti.rel) row.querySelector(".ci-reltext").textContent = ti.rel;
    if (item.text) row.querySelector(".ci-sub").textContent = item.text;
    if (item.note) row.querySelector(".ci-note").innerHTML = item.note;   // Rich-Content (Link/Button …), direkt sichtbar & klickbar
    return row;
  }
  function renderList(panel) {
    var list = panel.querySelector(".center-list");
    if (!list) return;
    list.innerHTML = "";
    var items = HIST.filter(function (it) { return centerFilter === "all" || groupOf(it) === centerFilter; });
    if (centerFilter === "app" && appFilter.length) {   // Feinfilter: nur die gewählten Apps
      items = items.filter(function (it) { return appFilter.indexOf(it.app) !== -1; });
    }
    if (!items.length) { list.innerHTML = '<div class="center-empty">Keine Benachrichtigungen.</div>'; return; }
    items.slice().reverse().forEach(function (item) { list.appendChild(centerItem(item)); });   // neueste zuerst
  }
  // Distinkte Apps, die in der Historie liegen (nur App-Meldungen mit App-Key) — Icon = erstes gesehenes Logo.
  function appsInHistory() {
    var seen = {}, out = [];
    HIST.forEach(function (it) {
      if (groupOf(it) === "app" && it.app && !seen[it.app]) { seen[it.app] = true; out.push({ app: it.app, icon: it.icon }); }
    });
    return out;
  }
  // Feinfilter-Chips „nach App": nur sichtbar im Apps-Tab und nur, wenn Apps in der Historie liegen. Mehrfachauswahl (Toggle).
  function renderAppFilter(panel) {
    var apps = appsInHistory();
    appFilter = appFilter.filter(function (a) { return apps.some(function (x) { return x.app === a; }); });   // verwaiste Auswahl (z.B. nach Leeren) entfernen
    var row = panel.querySelector(".center-appfilter");
    var show = centerFilter === "app" && apps.length > 0;
    if (!show) { if (row) row.hidden = true; return; }
    if (!row) {
      row = document.createElement("div"); row.className = "center-appfilter"; row.setAttribute("aria-label", "Nach App filtern");
      var sw = panel.querySelector(".center-filter") || panel.querySelector(".center-list");
      sw.insertAdjacentElement("afterend", row);
    }
    row.hidden = false; row.innerHTML = "";
    apps.forEach(function (a) {
      var on = appFilter.indexOf(a.app) !== -1;
      var b = document.createElement("button");
      b.type = "button"; b.className = "chip ci-appchip"; b.dataset.app = a.app;
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.innerHTML = (a.icon ? '<span class="ci-appchip-logo">' + a.icon + '</span>' : '') +
        '<span>' + (a.app.charAt(0).toUpperCase() + a.app.slice(1)) + '</span>';
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var i = appFilter.indexOf(a.app);
        if (i === -1) appFilter.push(a.app); else appFilter.splice(i, 1);
        renderAppFilter(panel); renderList(panel);
      });
      row.appendChild(b);
    });
  }
  function updateFilter(sw) {
    var i = 0; GROUPS.forEach(function (g, gi) { if (g.key === centerFilter) i = gi; });
    sw.style.setProperty("--i", i);
    Array.prototype.slice.call(sw.querySelectorAll("button")).forEach(function (b, bi) {
      b.setAttribute("aria-checked", bi === i ? "true" : "false");
    });
  }
  function renderCenter(panel) {
    var list = panel && panel.querySelector(".center-list");
    if (!list) return;
    var sw = panel.querySelector(".center-filter");
    if (!sw) {   // Filter als Wechsler (immer alle Gruppen); EINMAL bauen, danach nur Daumen/Aria updaten —
                 // sonst würde der Klick den geklickten Knopf abhängen und das <details> schließen.
      sw = document.createElement("div");
      sw.className = "switch center-filter"; sw.setAttribute("role", "radiogroup"); sw.setAttribute("aria-label", "Filter");
      sw.style.setProperty("--n", GROUPS.length);
      var thumb = document.createElement("span"); thumb.className = "thumb"; thumb.setAttribute("aria-hidden", "true"); sw.appendChild(thumb);
      GROUPS.forEach(function (g) {
        var b = document.createElement("button");
        b.type = "button"; b.setAttribute("role", "radio"); b.dataset.filter = g.key; b.textContent = g.label;
        b.addEventListener("click", function (e) { e.stopPropagation(); centerFilter = g.key; updateFilter(sw); renderAppFilter(panel); renderList(panel); });
        sw.appendChild(b);
      });
      list.parentNode.insertBefore(sw, list);
    }
    updateFilter(sw);
    renderAppFilter(panel);
    renderList(panel);
  }
  function initCenter() {
    document.querySelectorAll("[data-center]").forEach(function (d) {
      var panel = d.querySelector(".center-panel");
      d.addEventListener("toggle", function () { if (d.open) renderCenter(panel); });
      var clr = d.querySelector("[data-center-clear]");
      if (clr) clr.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); HIST.length = 0; centerFilter = "all"; appFilter = []; updateBells(); renderCenter(panel); });
    });
    updateBells();
  }

  /* ---------- Toasts (Gruppen-Karte je Art) ----------
     EIN Toast je Art sammelt mehrere Meldungen als Zeilen — statt einer Flut
     einzelner Toasts (Alarm-Bündelung). Identische Zeilen → Zähler. */
  var TOAST_LIFE = 4500;   // ms, Auto-Dismiss (ok/info/status/app)
  var reduceMotion = false;
  try {
    var rmq = window.matchMedia("(prefers-reduced-motion: reduce)");
    reduceMotion = rmq.matches;
    rmq.addEventListener("change", function (e) { reduceMotion = e.matches; });   // live nachziehen, sonst warten armierte Timer auf eine abgeschaltete Animation
  } catch (e) {}

  /* ---------- ARIA-Live-Announcer (Screenreader-Ansage für Toasts/Banner/Status) ----------
     Zwei PERSISTENTE Regionen (polite/assertive), ab Bedarf leer im DOM. Clear-then-set mit
     Frame-Abstand (sonst sagt der SR identischen Text nicht erneut an), Queue staffelt Bursts,
     Markup wird gestrippt. Toasts/Banner tragen KEIN role=alert/status mehr → EIN Mechanismus. */
  var ANN = null;
  function ensureAnnouncers() {
    if (ANN) return ANN;
    function mk(live) {
      var d = document.createElement("div");
      d.className = "c22-sr-only"; d.setAttribute("aria-live", live);
      d.setAttribute("aria-atomic", "true"); d.setAttribute("aria-relevant", "additions text");
      document.body.appendChild(d); return d;
    }
    ANN = { polite: mk("polite"), assertive: mk("assertive"), q: { polite: [], assertive: [] }, busy: { polite: false, assertive: false } };
    return ANN;
  }
  function pumpAnnounce(pr) {
    var a = ANN; if (!a || a.busy[pr]) return;
    if (!a.q[pr].length) return;
    var msg = a.q[pr].shift(); a.busy[pr] = true;
    var region = a[pr]; region.textContent = "";
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        region.textContent = msg;
        setTimeout(function () { a.busy[pr] = false; pumpAnnounce(pr); }, 350);   // Bursts staffeln
      });
    });
  }
  function announce(text, assertive) {
    if (text == null) return;
    var t = String(text).replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
    if (!t) return;
    var a = ensureAnnouncers(), pr = assertive ? "assertive" : "polite";
    a.q[pr].push(t); pumpAnnounce(pr);
  }
  window.c22Announce = announce;

  function ensureWrap() {
    var w = document.getElementById("c22-toasts");
    if (!w) { w = document.createElement("div"); w.id = "c22-toasts"; document.body.appendChild(w); }
    return w;
  }
  function liveCards(wrap) {
    return Array.prototype.slice.call(wrap.querySelectorAll(".toast-slot:not(.out) > .toast-inner > .toast"));
  }
  function slideIn(slot) {   // grid 0fr→1fr im nächsten Frame → Höhen-Slide
    requestAnimationFrame(function () { requestAnimationFrame(function () { slot.classList.add("in"); }); });
  }
  function slideOut(slot, done) {
    slot.classList.remove("in"); slot.classList.add("out");
    setTimeout(function () { slot.remove(); if (done) done(); }, 340);
  }

  function makeCard(wrap, kind) {
    var slot = document.createElement("div");
    slot.className = "toast-slot c22-slide";
    slot.style.order = String(10 - ((KIND[kind] || {}).prio || 0));   // Wichtigkeit: Fehler oben
    var inner = document.createElement("div"); inner.className = "toast-inner";
    var card = document.createElement("div");
    card.className = "toast " + kind;
    card.dataset.kind = kind;
    // KEIN role=alert/status mehr auf der Karte — Ansage übernimmt der Announcer (in toast()); sonst Doppelansage.
    // App-Karte: KEIN Einzel-Wasserzeichen — die App-Logos je Gruppe ersetzen es (PO 2026-07-12).
    var iconHtml = (kind === "app") ? "" : iconSpan("toast-icon", (KIND[kind] || KIND.info).icon);
    card.innerHTML =
      '<div class="toast-fill"></div>' + iconHtml +
      '<div class="toast-body"><div class="toast-list"></div></div>';
    inner.appendChild(card); slot.appendChild(inner);
    // „Alle schließen" hängt am SLOT (außerhalb des Karten-/Inner-overflow) → kann als Reiter unten raushängen
    var foot = document.createElement("div"); foot.className = "toast-foot";
    var fbtn = document.createElement("button"); fbtn.className = "toast-closeall"; fbtn.type = "button"; fbtn.textContent = "Alle schließen";
    fbtn.addEventListener("click", function () { removeCard(card); });
    foot.appendChild(fbtn); slot.appendChild(foot);
    wrap.appendChild(slot);
    slideIn(slot);
    return card;
  }

  function updateMulti(card) {
    var n = card.querySelectorAll(".toast-row-slot:not(.out) .toast-row").length;   // Zeilen im Abgang nicht mitzählen
    var multi = n >= 2;
    card.classList.toggle("multi", multi);
    var slot = card.closest(".toast-slot");
    var foot = slot && slot.querySelector(".toast-foot");
    if (foot) foot.classList.toggle("in", multi);   // „Alle schließen"-Reiter erscheint ab 2 Einträgen
  }

  function removeRow(card, slot) {
    if (slot.classList.contains("out")) return;   // schon im Abgang (z.B. Doppelklick aufs ×) → nicht doppelt zählen/schließen
    // War das die letzte Zeile? Dann NICHT erst Zeile, dann Karte animieren (Ruckler),
    // sondern gleich die ganze Karte in EINER Bewegung schließen.
    var remaining = card.querySelectorAll(".toast-row-slot:not(.out) .toast-row").length - 1;
    if (remaining <= 0) { removeCard(card); return; }
    slot.classList.remove("in"); slot.classList.add("out");   // sofort aus der Zählung → Fußzeile/Icon passen sich parallel an
    updateMulti(card);
    setTimeout(function () {
      var group = slot.closest(".toast-appgroup");
      slot.remove();
      if (group && !group.querySelector(".toast-row-slot")) group.remove();   // leere App-Gruppe (samt Logo) entfernen
    }, 340);
  }
  function addRow(card, title, text, note, icon, app) {
    var list = card.querySelector(".toast-list");
    var rows = Array.prototype.slice.call(list.querySelectorAll(".toast-row-slot:not(.out) .toast-row"));   // ausblendende Zeilen NICHT als Duplikat matchen (sonst geht die neue Meldung verloren)
    var same = rows.filter(function (r) { return r.dataset.title === title && r.dataset.text === (text || "") && (r.dataset.app || "") === (app || ""); })[0];
    if (same) {                                   // identische Meldung → Zähler + Bump
      var c = parseInt(same.dataset.count || "1", 10) + 1;
      same.dataset.count = c;
      var badge = same.querySelector(".row-count");
      if (!badge) { badge = document.createElement("span"); badge.className = "row-count"; same.querySelector(".row-x").before(badge); }
      badge.textContent = "×" + c;
      same.classList.remove("bump"); void same.offsetWidth; same.classList.add("bump");
      return;
    }
    var slot = document.createElement("div");
    slot.className = "toast-row-slot c22-slide";
    var inner = document.createElement("div"); inner.className = "toast-row-inner";
    var row = document.createElement("div"); row.className = "toast-row" + (note ? " has-note" : "");
    row.dataset.title = title; row.dataset.text = text || ""; row.dataset.count = "1";
    if (app) row.dataset.app = app;
    row.innerHTML =
      '<div class="row-main"><span class="row-title"></span>' +
        (text ? '<span class="row-text"></span>' : '') +
        (note ? '<div class="row-note"></div>' : '') +   // Notiz INLINE sichtbar → Link/Button direkt klickbar (kein Aufklappen, kein role=button)
      '</div>' +
      '<button class="row-x" type="button" aria-label="Schließen">×</button>';
    row.querySelector(".row-title").textContent = title;
    if (text) row.querySelector(".row-text").textContent = text;
    if (note) row.querySelector(".row-note").innerHTML = note;   // Notiz = Rich-Content (autorseitig, z.B. Link/Button)
    row.querySelector(".row-x").addEventListener("click", function (e) { e.stopPropagation(); removeRow(card, slot); });
    inner.appendChild(row); slot.appendChild(inner);
    if (app) {
      // App-Gruppe: EIN Logo pro App (nicht je Zeile), Gruppen mit Trennlinie abgegrenzt
      var group = null;
      list.querySelectorAll(".toast-appgroup").forEach(function (g) { if (g.dataset.app === app) group = g; });
      if (!group) {
        group = document.createElement("div"); group.className = "toast-appgroup"; group.dataset.app = app;
        group.innerHTML = '<span class="tg-icon" aria-hidden="true">' + (icon || "") + '</span><div class="tg-body"></div>';
        list.appendChild(group);
      }
      group.querySelector(".tg-body").appendChild(slot);
    } else {
      list.appendChild(slot);
    }
    slideIn(slot);
  }

  function removeCard(card) {
    var slot = card.closest(".toast-slot"); if (!slot) return;
    var wrap = slot.parentNode;
    if (card._t) clearTimeout(card._t);
    slideOut(slot);
    if (wrap) updateBar(wrap);   // sofort neu bewerten → „Alle schließen" gleitet parallel, nicht verzögert
  }
  function closeAll() {
    var wrap = document.getElementById("c22-toasts"); if (!wrap) return;
    liveCards(wrap).forEach(removeCard);
  }

  /* „Alle schließen" erscheint ab 2 Karten — UNTER den Karten, mit Höhen-Slide. */
  function updateBar(wrap) {
    var n = liveCards(wrap).length;
    var slot = wrap.querySelector(".toasts-bar-slot:not(.out)");
    if (n >= 2 && !slot) {
      slot = document.createElement("div"); slot.className = "toasts-bar-slot c22-slide";
      var inner = document.createElement("div"); inner.className = "toast-inner";
      var bar = document.createElement("div"); bar.className = "toasts-bar";
      var b = document.createElement("button"); b.type = "button"; b.textContent = "Alles schließen";
      b.addEventListener("click", function () { closeAll(); });
      bar.appendChild(b); inner.appendChild(bar); slot.appendChild(inner);
      wrap.appendChild(slot);
      slideIn(slot);
    } else if (n < 2 && slot) {
      slideOut(slot);
    }
  }

  /* Auto-Dismiss (ok/info): ablaufende Hintergrund-Füllung; Hover pausiert (CSS).
     Bei reduzierter Bewegung greift ein JS-Timer als Ersatz. */
  function armTimer(card, kind) {
    if (kind !== "ok" && kind !== "info" && kind !== "status" && kind !== "app") return;   // Fehler/Warnung/Fortschritt bleiben stehen
    card.classList.remove("auto"); void card.offsetWidth; card.classList.add("auto");
    if (reduceMotion) {
      if (card._t) clearTimeout(card._t);
      card._t = setTimeout(function () { removeCard(card); }, TOAST_LIFE);
      return;
    }
    var fill = card.querySelector(".toast-fill");
    if (fill && !fill._bound) {
      fill._bound = true;
      fill.addEventListener("animationend", function (e) {
        if (e.animationName === "c22-shrink") removeCard(card);
      });
    }
  }
  /* Fehler wackelt heftig, sonst kurzer Bump — bei jeder neuen wie gebündelten Meldung. */
  function punch(card, kind) {
    var cls = kind === "bad" ? "shake" : "bump";
    card.classList.remove("shake", "bump"); void card.offsetWidth; card.classList.add(cls);
  }

  function toast(title, kind, text, note, icon, group, app) {
    kind = kind || "info"; text = text || ""; note = note || "";
    var wrap = ensureWrap();
    var card = liveCards(wrap).filter(function (c) { return c.dataset.kind === kind; })[0];   // EINE Karte je Art — App-Meldungen landen alle in der App-Karte, nach App gruppiert
    if (!card) card = makeCard(wrap, kind);
    addRow(card, title, text, note, icon, app);   // icon = App-Logo je Zeile, app = Gruppierungsschlüssel innerhalb der Karte
    updateMulti(card);
    updateBar(wrap);
    punch(card, kind);
    armTimer(card, kind);
    announce(title + (text ? ". " + text : ""), kind === "bad" || kind === "warn");   // Screenreader-Ansage (Fehler/Warnung assertiv)
    pushHistory(title, kind, text, note, icon, group, app);   // icon = Marken-/App-Logo (selfh.st), group z.B. "app", app = App-Key für den Historie-Feinfilter
    return card;
  }
  window.c22Toast = toast;
  window.c22ToastPosition = setToastPosition;
  window.c22ToastCloseAll = closeAll;
  function setToastPosition(pos) {
    var w = ensureWrap();
    w.className = pos ? "pos-" + pos : "";   // .pos-*-Klasse am Wrapper; Slots bleiben Kinder
  }

  /* ---------- Popup: Klick auf den Hintergrund schließt ---------- */
  function initDialogs() {
    document.querySelectorAll("dialog.c22-dialog").forEach(function (d) {
      d.addEventListener("click", function (e) { if (e.target === d) d.close(); });   // Klick auf den Backdrop
    });
  }

  /* ---------- Mittige Popup-Meldung + Scrim (NON-modal — blockiert nichts) ----------
     Anders als das <dialog>-Popup (Entscheidung, modal, sperrt die Seite): eine mittige
     Ankündigung, die Aufmerksamkeit holt, aber die Seite bedienbar lässt. Dahinter liegt der
     SCRIM — rein visuell (pointer-events:none), Blur + weicher Vignetten-Rand, blendet mit ein.
     Reduziert auf ein Fokus-Mittel, kein Klick-Fänger. Nutzt dieselbe Notiz-/Rich-Content-Basis. */
  function ensurePopups() {
    var w = document.getElementById("c22-popups");
    if (!w) {
      var scrim = document.createElement("div"); scrim.id = "c22-popup-scrim"; scrim.setAttribute("aria-hidden", "true");
      document.body.appendChild(scrim);
      w = document.createElement("div"); w.id = "c22-popups";   // KEIN aria-live am Container: jede Popup-Karte ist selbst role=status/alert (sonst geschachtelte Live-Regionen → bad/warn verliert Assertivität)
      document.body.appendChild(w);
    }
    return w;
  }
  function livePopups(w) { return Array.prototype.slice.call(w.querySelectorAll(".c22-popup:not(.out)")); }
  function updateScrim() {
    var w = document.getElementById("c22-popups"), scrim = document.getElementById("c22-popup-scrim");
    if (w && scrim) scrim.classList.toggle("in", livePopups(w).length > 0);
  }
  function removePopup(pop) {
    if (pop.classList.contains("out")) return;
    if (pop._t) clearTimeout(pop._t);
    if (pop._ld) document.removeEventListener("pointerdown", pop._ld, true);   // Light-Dismiss-Listener lösen
    pop.classList.remove("in"); pop.classList.add("out");
    setTimeout(function () { pop.remove(); updateScrim(); }, 260);
    updateScrim();   // war das das letzte? → Scrim blendet parallel aus, nicht verzögert
  }
  // Selbst-schließendes Popup: sichtbarer Hintergrund-Countdown (wie beim Toast), Hover pausiert.
  // Bei reduzierter Bewegung greift ein schlichter Timer.
  function autoClosePopup(pop) {
    if (reduceMotion) { pop._t = setTimeout(function () { removePopup(pop); }, 2600); return; }
    pop.classList.add("auto");
    var f = pop.querySelector(".pop-fill");
    if (!f) { f = document.createElement("div"); f.className = "pop-fill"; pop.appendChild(f); }
    f.addEventListener("animationend", function (e) { if (e.animationName === "c22-shrink") removePopup(pop); });
  }
  function popup(title, kind, text, note, opts) {
    kind = kind || "info"; title = title || ""; text = text || ""; note = note || ""; opts = opts || {};
    var w = ensurePopups();
    // SPOT: dieselbe Karte + Scrim, nur die POSITION unterscheidet sich (mitte | oben | unten).
    var pos = opts.pos || "mitte";
    w.dataset.pos = pos;
    var scrimEl = document.getElementById("c22-popup-scrim"); if (scrimEl) scrimEl.dataset.pos = pos;
    var big = opts.size && /gro|big/i.test(opts.size);   // „groß"/"gross"/"big" → breite Variante
    var pop = document.createElement("div");
    pop.className = "c22-popup " + kind + (big ? " big" : "") + (opts.locked ? " locked" : "");
    if (opts.locked) pop.dataset.locked = "1";           // gesperrt: kein ×/Esc/Klick-weg (läuft ein Status)
    pop.setAttribute("role", (kind === "bad" || kind === "warn") ? "alert" : "status");
    pop.innerHTML =
      '<button class="pop-x" type="button" aria-label="Schließen">×</button>' +
      iconSpan("pop-icon", (KIND[kind] || KIND.info).icon) +
      (title ? '<div class="pop-title"></div>' : '') +
      (text ? '<div class="pop-text"></div>' : '') +
      (note ? '<div class="pop-note"></div>' : '');
    if (title) pop.querySelector(".pop-title").textContent = title;
    if (text) pop.querySelector(".pop-text").textContent = text;
    if (note) pop.querySelector(".pop-note").innerHTML = note;   // Custom-Popup: Autor-HTML (Link/Button …), direkt sichtbar
    pop.querySelector(".pop-x").addEventListener("click", function () { removePopup(pop); });
    pop.close = function () { removePopup(pop); };   // programmatisch schließbar (auch gesperrte)
    w.appendChild(pop);
    requestAnimationFrame(function () { requestAnimationFrame(function () { pop.classList.add("in"); }); });
    updateScrim();
    if (opts.autoclose) autoClosePopup(pop);   // opt-in: schließt sich mit sichtbarem Countdown (z.B. Erfolg)
    if (!opts.locked) {   // Light-Dismiss: Klick auf den Hintergrund schließt (Scrim ist pointer-events:none)
      pop._ld = function (e) { if (!pop.contains(e.target)) removePopup(pop); };
      setTimeout(function () { document.addEventListener("pointerdown", pop._ld, true); }, 0);   // nächster Tick → der öffnende Klick schließt nicht sofort
    }
    return pop;   // sonst blenden Popups NIE von selbst aus — nur × / Esc / Klick-weg / .close()
  }
  // ---------- Body-Scroll-Lock (iOS-tauglich, refcount) ----------
  // <dialog>.showModal() macht den Hintergrund inert, sperrt auf iOS Safari aber NICHT den Scroll
  // (overflow:hidden am body versagt dort). position:fixed + scrollY-Restore + Scrollbar-Gutter.
  var scrollLocks = 0, savedScrollY = 0;
  function lockScroll() {
    if (scrollLocks++ > 0) return;
    savedScrollY = window.scrollY || 0;
    var gut = window.innerWidth - document.documentElement.clientWidth;   // Scrollbar-Breite gegen Layout-Shift
    var s = document.body.style;
    s.position = "fixed"; s.top = -savedScrollY + "px"; s.insetInlineStart = "0"; s.insetInlineEnd = "0"; s.width = "100%";
    if (gut > 0) s.paddingInlineEnd = gut + "px";
  }
  function unlockScroll() {
    if (scrollLocks <= 0 || --scrollLocks > 0) return;
    var s = document.body.style;
    s.position = ""; s.top = ""; s.insetInlineStart = ""; s.insetInlineEnd = ""; s.width = ""; s.paddingInlineEnd = "";
    window.scrollTo(0, savedScrollY);
  }
  window.c22LockScroll = lockScroll; window.c22UnlockScroll = unlockScroll;

  function initPopups() {
    // EIN Overlay-Escape-Koordinator statt je Typ ein eigener document-Handler → schließt nur das
    // OBERSTE (dismissible-stack). Reihenfolge: modaler <dialog> nativ (cancel) → Popup → Menü.
    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (document.querySelector("dialog.c22-dialog[open]")) return;   // modaler Dialog schließt sich selbst (cancel)
      var w = document.getElementById("c22-popups");
      var pops = w ? livePopups(w).filter(function (p) { return !p.dataset.locked; }) : [];
      if (pops.length) { removePopup(pops[pops.length - 1]); e.stopPropagation(); return; }   // Popup liegt über dem Menü
      var openMenu = document.querySelector("details.menu[open]");
      if (openMenu) openMenu.removeAttribute("open");
    });
  }
  window.c22Popup = function (title, kind, text, note, opts) { return popup(title, kind, text, note, opts); };

  /* ---------- Auswahl-Popup: modale Entscheidung (nativ <dialog>, Fokus-Falle, sperrt die Seite) ---------- */
  function confirmDialog(title, opts) {
    opts = opts || {};
    var danger = opts.kind === "bad" || opts.danger;
    var d = document.createElement("dialog");
    d.className = "c22-dialog";
    d.innerHTML =
      '<div class="dialog-head"><h3></h3><button class="banner-x" type="button" aria-label="Schließen" data-x>×</button></div>' +
      (opts.text ? '<div class="dialog-body"></div>' : '') +
      '<div class="dialog-actions">' +
        (opts.cancel === false ? '' : '<button class="btn ghost" type="button" data-cancel></button>') +
        '<button class="btn ' + (danger ? "danger" : "accent") + '" type="button" data-confirm></button>' +
      '</div>';
    d.querySelector("h3").textContent = title;
    if (opts.text) d.querySelector(".dialog-body").textContent = opts.text;
    d.querySelector("[data-confirm]").textContent = opts.confirm || "OK";
    var cancelBtn = d.querySelector("[data-cancel]"); if (cancelBtn) cancelBtn.textContent = (typeof opts.cancel === "string" ? opts.cancel : "Abbrechen");
    var settled = false;
    function fin(ok) {
      if (settled) return; settled = true;
      unlockScroll();
      d.close(); setTimeout(function () { d.remove(); }, 220);
      if (ok && opts.onConfirm) opts.onConfirm();
      else if (!ok && opts.onCancel) opts.onCancel();
    }
    d.querySelector("[data-confirm]").addEventListener("click", function () { fin(true); });
    if (cancelBtn) cancelBtn.addEventListener("click", function () { fin(false); });
    d.querySelector("[data-x]").addEventListener("click", function () { fin(false); });
    d.addEventListener("click", function (e) { if (e.target === d) fin(false); });   // Klick auf den Backdrop
    d.addEventListener("cancel", function (e) { e.preventDefault(); fin(false); });    // Escape
    document.body.appendChild(d);
    lockScroll();       // iOS: Hintergrund-Scroll sperren, solange der modale Dialog offen ist
    d.showModal();
    return d;
  }
  window.c22Confirm = confirmDialog;

  /* ---------- Fortschritt-Popup: läuft GESPERRT, löst dann zu Erfolg/Fehler auf ----------
     var p = c22Progress("Export läuft", {text:"…"});  p.set(0.4);  p.done("Fertig","…") / p.fail("…").
     Vorgabe autoclose: Erfolg schließt nach ~1,5 s, Fehler bleibt (mit ×). {autoclose:bool} überstimmt. */
  function progressPopup(title, opts) {
    opts = opts || {};
    var big = opts.size && /gro|big/i.test(opts.size);
    var pop = popup(title || "", "progress", opts.text || "", "", { locked: true, size: opts.size, pos: opts.pos });
    var svg = pop.querySelector(".pop-icon svg"); if (svg) svg.classList.add("pop-spin");
    var track = document.createElement("div"); track.className = "pop-progress indet";
    var fill = document.createElement("div"); fill.className = "pop-progress-fill";
    track.appendChild(fill);
    var titleEl = pop.querySelector(".pop-title"), textEl = pop.querySelector(".pop-text");
    (textEl || titleEl || pop.querySelector(".pop-icon")).insertAdjacentElement("afterend", track);
    function morph(kind, t, tx) {
      delete pop.dataset.locked;
      pop.className = "c22-popup in " + kind + (big ? " big" : "");   // „in" behalten (sonst blendet die Karte aus), entsperren → × sichtbar
      pop.setAttribute("role", kind === "bad" ? "alert" : "status");
      var pIcon = pop.querySelector(".pop-icon"); pIcon.dataset.c22Ico = (KIND[kind] || KIND.info).icon; pIcon.innerHTML = iconSVG(kind);
      if (titleEl) titleEl.textContent = t;
      if (tx != null && tx !== "") {
        if (!textEl) { textEl = document.createElement("div"); textEl.className = "pop-text"; (titleEl || pop.querySelector(".pop-icon")).insertAdjacentElement("afterend", textEl); }
        textEl.textContent = tx;
      }
      track.remove();
      var autoclose = ("autoclose" in opts) ? opts.autoclose : (kind === "ok");   // Vorgabe: Erfolg schließt (mit Countdown), Fehler bleibt
      if (autoclose) autoClosePopup(pop);
    }
    function clamp(f) { return Math.max(0, Math.min(1, +f || 0)); }
    var api = {
      el: pop,
      // diskreter Sprung (weiche .35s-Transition aus dem CSS)
      set: function (frac) { fill.style.transition = ""; track.classList.remove("indet"); fill.style.transform = "scaleX(" + clamp(frac) + ")"; return api; },
      // kontinuierlich über ms fahren — EIN GPU-Übergang, absolut glatt (kein Frame-für-Frame-JS)
      run: function (toFrac, ms) {
        track.classList.remove("indet");
        var v = clamp(toFrac);
        // SAUBERER Startpunkt: die indeterminate-Animation hinterlässt ein translateX-Transform;
        // ohne Reset interpoliert der Balken von translateX → scaleX (sliden UND scalen = Ruckeln).
        fill.style.animation = "none";
        fill.style.transition = "none";
        fill.style.width = "100%";
        fill.style.transform = "scaleX(0)";
        void fill.offsetWidth;   // Reflow erzwingen, damit der Startzustand „einrastet"
        fill.style.transition = "transform " + (ms || 1200) + "ms linear";
        requestAnimationFrame(function () { fill.style.transform = "scaleX(" + v + ")"; });
        return api;
      },
      done: function (t, tx) { morph("ok", t || "Fertig", tx); return api; },
      fail: function (t, tx) { morph("bad", t || "Fehlgeschlagen", tx); return api; }
    };
    return api;
  }
  window.c22Progress = progressPopup;

  /* ---------- c22Notify: EIN Einstieg, drei Ziele (toast | popup | banner) ----------
     msg = Titel/Kopfzeile; opts.text = Untertitel; opts.note = Rich-HTML (Link/Button).
     target wählt die Darstellung, sticky hält die mittige Meldung offen (Toast/Banner ohnehin). */
  function notify(msg, opts) {
    opts = opts || {};
    var kind = opts.kind || "info", target = opts.target || "toast";
    var title = opts.title || msg || "", text = opts.text || "", note = opts.note || "";
    if (target === "popup")  return popup(title, kind, text, note, { sticky: opts.sticky, pos: opts.pos, size: opts.size, locked: opts.locked, autoclose: opts.autoclose });
    if (target === "banner") return banner(text ? title + " — " + text : title, kind, { action: opts.action, onAction: opts.onAction });
    return toast(title, kind, text, note, opts.icon, opts.group, opts.app);   // Vorgabe: Toast; icon = Marken-Logo, app = Bündel je App, group = Center-Filter
  }
  window.c22Notify = notify;

  /* ---------- Formulare: Timing via :user-invalid (CSS), Semantik via JS ----------
     Der Browser entscheidet über die Pseudoklasse `:user-invalid`, WANN ein Fehler sichtbar wird
     (nach Blur/Submit, NIE bei unberührten required-Feldern) — das CSS koppelt Rahmen/Label/Fehlerzeile
     daran (kein JS-Timing mehr). JS spiegelt nur die SEMANTIK: aria-invalid + Fehlertext
     (validationMessage / data-error) + dauerhaftes aria-describedby. Opt-in über `.field[data-validate]`. */
  function escHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function autoGrow(ta) {
    ta.style.height = "auto";
    ta.style.height = ta.scrollHeight + "px";
  }
  var formSeq = 0;
  function syncField(ctrl, errEl, force) {
    var bad = force || (ctrl.matches && ctrl.matches(":user-invalid"));
    ctrl.setAttribute("aria-invalid", bad ? "true" : "false");
    if (!errEl) return;
    if (bad) {
      var msg = ctrl.getAttribute("data-error") || ctrl.validationMessage;
      if (errEl.dataset.c22Msg !== msg) {   // nur bei GEÄNDERTER Meldung neu schreiben → keine Live-Region-Ansage pro Tastendruck
        errEl.dataset.c22Msg = msg;
        errEl.innerHTML = iconSpan("fe-ico", "x-circle") + "<span>" + escHtml(msg) + "</span>";
      }
    } else if (errEl.dataset.c22Msg) { errEl.dataset.c22Msg = ""; errEl.textContent = ""; }
  }
  function initForms(root) {
    var scope = root || document;
    scope.querySelectorAll(".field[data-validate]").forEach(function (field) {
      if (field.dataset.c22Form) return; field.dataset.c22Form = "1";
      var ctrl = field.querySelector("input, select, textarea"); if (!ctrl) return;
      var errEl = field.querySelector(".field-error");
      if (errEl) {   // aria-describedby DAUERHAFT verdrahten (Sichtbarkeit des Textes steuert CSS)
        if (!errEl.id) errEl.id = "c22-err-" + (++formSeq);
        var db = (ctrl.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean);
        if (db.indexOf(errEl.id) < 0) { db.push(errEl.id); ctrl.setAttribute("aria-describedby", db.join(" ")); }
      }
      var sync = function () { syncField(ctrl, errEl); };
      ctrl.addEventListener("input", sync);
      ctrl.addEventListener("change", sync);
      ctrl.addEventListener("blur", function () { setTimeout(sync, 0); });   // :user-invalid greift beim Blur → danach spiegeln
      // Submit-Versuch: native Bubble unterdrücken, eigenen Fehlertext setzen, ersten Fehler fokussieren
      ctrl.addEventListener("invalid", function (e) {
        e.preventDefault();   // native Bubble immer unterdrücken
        requestAnimationFrame(function () {
          // nur ein ECHTER Submit-Versuch aktiviert :user-invalid — reines checkValidity()/reportValidity() nicht;
          // so stiehlt ein Status-Check keinen Fokus und erzeugt keinen Semantik/Optik-Desync
          if (!(ctrl.matches && ctrl.matches(":user-invalid"))) return;
          syncField(ctrl, errEl, true);
          var form = ctrl.form;
          if (form && !form._c22Focusing) { form._c22Focusing = true; ctrl.focus(); requestAnimationFrame(function () { form._c22Focusing = false; }); }
        });
      });
    });
    // Reset: aria + Fehlertext abräumen (die :user-invalid-Optik setzt der Browser beim Reset selbst zurück)
    var forms = [];
    scope.querySelectorAll(".field[data-validate] input, .field[data-validate] select, .field[data-validate] textarea").forEach(function (ctrl) {
      if (ctrl.form && forms.indexOf(ctrl.form) < 0) forms.push(ctrl.form);
    });
    forms.forEach(function (form) {
      if (form.dataset.c22FormReset) return; form.dataset.c22FormReset = "1";
      form.addEventListener("reset", function () {
        setTimeout(function () {
          form.querySelectorAll(".field[data-validate]").forEach(function (f) {
            var e = f.querySelector(".field-error"); if (e) e.textContent = "";
            f.querySelectorAll("input, select, textarea").forEach(function (c) { c.setAttribute("aria-invalid", "false"); });
          });
          form.querySelectorAll("textarea.auto").forEach(autoGrow);
        }, 0);
      });
    });
    // Textarea-Auto-Grow: nativ über field-sizing, sonst JS-Fallback.
    var hasFieldSizing = window.CSS && CSS.supports && CSS.supports("field-sizing: content");
    if (!hasFieldSizing) {
      scope.querySelectorAll("textarea.auto").forEach(function (ta) {
        if (ta.dataset.c22Auto) return; ta.dataset.c22Auto = "1";
        ta.addEventListener("input", function () { autoGrow(ta); });
        autoGrow(ta);
      });
    }
  }
  window.c22InitForms = initForms;

  /* ---------- Accordion (Disclosure) ----------
     Button steuert aria-expanded + Panel-Klasse `.open` (grid-rows-Animation im CSS).
     `.accordion[data-single]` = nur ein Panel gleichzeitig offen. */
  function accSet(btn, open) {
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    var panel = document.getElementById(btn.getAttribute("aria-controls"));
    if (panel) panel.classList.toggle("open", open);
  }
  function initAccordion(root) {
    (root || document).querySelectorAll(".accordion .acc-trigger").forEach(function (btn) {
      if (btn.dataset.c22Acc) return; btn.dataset.c22Acc = "1";
      btn.addEventListener("click", function () {
        var open = btn.getAttribute("aria-expanded") === "true";
        var acc = btn.closest(".accordion");
        if (acc && acc.hasAttribute("data-single") && !open) {
          acc.querySelectorAll('.acc-trigger[aria-expanded="true"]').forEach(function (o) { accSet(o, false); });
        }
        accSet(btn, !open);
      });
    });
  }
  window.c22InitAccordion = initAccordion;

  /* ---------- Tabs / Segmented ----------
     Gleitender Indikator (--x/--w aus offsetLeft/Width), Roving tabindex + Pfeiltasten.
     ResizeObserver hält den Indikator bei Größen-/Font-Achsenwechsel korrekt. */
  function moveIndicator(tabs) {
    var sel = tabs.querySelector('.tab[aria-selected="true"]');
    if (!sel) return;
    tabs.style.setProperty("--x", sel.offsetLeft + "px");
    tabs.style.setProperty("--w", sel.offsetWidth + "px");
  }
  function selectTab(tabs, tab) {
    tabs._tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
    moveIndicator(tabs);
  }
  function initTabs(root) {
    (root || document).querySelectorAll(".tabs").forEach(function (tabs) {
      if (tabs.dataset.c22Tabs) return; tabs.dataset.c22Tabs = "1";
      var all = Array.prototype.slice.call(tabs.querySelectorAll(".tab"));
      if (!all.length) return;
      tabs._tabs = all;
      all.forEach(function (tab) {
        tab.addEventListener("click", function () { selectTab(tabs, tab); });
        tab.addEventListener("keydown", function (e) {
          var i = all.indexOf(tab), n = all.length, ni = null;
          if (e.key === "ArrowRight" || e.key === "ArrowDown") ni = (i + 1) % n;
          else if (e.key === "ArrowLeft" || e.key === "ArrowUp") ni = (i - 1 + n) % n;
          else if (e.key === "Home") ni = 0;
          else if (e.key === "End") ni = n - 1;
          if (ni !== null) { e.preventDefault(); all[ni].focus(); selectTab(tabs, all[ni]); }
        });
      });
      selectTab(tabs, tabs.querySelector('.tab[aria-selected="true"]') || all[0]);
      if (window.ResizeObserver) new ResizeObserver(function () { moveIndicator(tabs); }).observe(tabs);
    });
  }
  window.c22InitTabs = initTabs;

  /* ---------- Navigation: Navbar-hide-on-scroll + Sidebar-Collapse ---------- */
  function initNav(root) {
    var scope = root || document;
    scope.querySelectorAll(".navbar.sticky[data-hide-on-scroll]").forEach(function (nav) {
      if (nav.dataset.c22Nav) return; nav.dataset.c22Nav = "1";
      var last = window.scrollY || 0;
      window.addEventListener("scroll", function () {
        var y = window.scrollY || 0;
        if (y > last && y > 80) nav.classList.add("nav-hidden");   // runter → Leiste weg
        else nav.classList.remove("nav-hidden");                   // hoch → zurück
        last = y;
      }, { passive: true });
    });
    scope.querySelectorAll("[data-sidenav-toggle]").forEach(function (btn) {
      if (btn.dataset.c22Nav) return; btn.dataset.c22Nav = "1";
      btn.addEventListener("click", function () {
        var sel = btn.getAttribute("data-sidenav-toggle");
        var nav = (sel && document.querySelector(sel)) || btn.closest(".sidenav");
        if (nav) { var c = nav.classList.toggle("collapsed"); btn.setAttribute("aria-expanded", c ? "false" : "true"); }
      });
    });
  }
  window.c22InitNav = initNav;

  /* ---------- Slider: WebKit-Track-Füllung (--_fill) + optionale Wert-Ausgabe ---------- */
  function initRange(root) {
    (root || document).querySelectorAll(".c22-range").forEach(function (el) {
      if (el.dataset.c22Range) return; el.dataset.c22Range = "1";
      var out = el.closest(".range-field") && el.closest(".range-field").querySelector("output");
      var upd = function () {
        var min = +el.min || 0, max = el.max === "" ? 100 : +el.max, v = +el.value;
        el.style.setProperty("--_fill", (max > min ? (v - min) / (max - min) * 100 : 0) + "%");
        if (out) out.textContent = el.dataset.suffix ? el.value + el.dataset.suffix : el.value;
      };
      el.addEventListener("input", upd); upd();
    });
  }
  window.c22InitRange = initRange;

  /* ---------- Dual-Thumb-Slider: Füll-Segment (--lo/--hi) + Überkreuz-Sperre + z-index-Vorrang ---------- */
  function initRangeDual(root) {
    (root || document).querySelectorAll(".c22-range-dual").forEach(function (w) {
      if (w.dataset.c22Range) return; w.dataset.c22Range = "1";
      var lo = w.querySelector(".rd-lo"), hi = w.querySelector(".rd-hi");
      var out = w.querySelector(".rd-out") || (w.parentElement && w.parentElement.querySelector(".rd-out"));
      if (!lo || !hi) return;
      var min = +lo.min || 0, max = lo.max === "" ? 100 : +lo.max, sfx = lo.dataset.suffix || "";
      var pct = function (v) { return max > min ? (v - min) / (max - min) * 100 : 0; };
      var upd = function () {
        var a = Math.min(+lo.value, +hi.value), b = Math.max(+lo.value, +hi.value);
        w.style.setProperty("--lo", pct(a) + "%"); w.style.setProperty("--hi", pct(b) + "%");
        if (out) out.textContent = a + sfx + " – " + b + sfx;
      };
      // Zeiger-Wert an Position clientX schätzen.
      var valAt = function (clientX) {
        var r = w.getBoundingClientRect(); if (!r.width) return null;
        return min + Math.min(1, Math.max(0, (clientX - r.left) / r.width)) * (max - min);
      };
      // Hover legt den NÄHEREN Griff nach oben → beim Überlappen/Extrem greift man den richtigen (kein Deadlock).
      var raise = function (clientX) {
        var val = valAt(clientX); if (val == null) return;
        var loTop = Math.abs(val - +lo.value) <= Math.abs(val - +hi.value);
        lo.style.zIndex = loTop ? "5" : "4"; hi.style.zIndex = loTop ? "4" : "5";
      };
      w.addEventListener("pointermove", function (e) { if (!e.buttons) raise(e.clientX); });   // nicht während des Ziehens
      lo.style.zIndex = "4"; hi.style.zIndex = "5";   // Startzustand: einer sicher greifbar
      // Klick auf die SPUR (nicht auf einen Griff) bewegt den NÄHEREN Griff dorthin — UND lässt sich
      // ohne Loslassen weiterziehen. Die Inputs sind pointer-events:none (nur die Griffe fangen), daher
      // fängt das Widget den Spur-Klick und führt einen eigenen Drag bis pointerup.
      var step = +lo.step || 1;
      var setFrom = function (clientX, target) {
        var raw = valAt(clientX); if (raw == null) return;
        target.value = Math.round(raw / step) * step;
        if (+lo.value > +hi.value) { if (target === lo) lo.value = hi.value; else hi.value = lo.value; }
        upd();
      };
      w.addEventListener("pointerdown", function (e) {
        if (e.target === lo || e.target === hi) return;   // direkt am Griff → native Drag
        var raw = valAt(e.clientX); if (raw == null) return;
        var val = Math.round(raw / step) * step;
        var target = (Math.abs(val - +lo.value) <= Math.abs(val - +hi.value)) ? lo : hi;   // näherer Griff
        setFrom(e.clientX, target); target.focus();
        var move = function (ev) { setFrom(ev.clientX, target); };   // weiterziehen
        var end = function () { w.removeEventListener("pointermove", move); w.removeEventListener("pointerup", end); w.removeEventListener("pointercancel", end); };
        try { w.setPointerCapture(e.pointerId); } catch (x) {}
        w.addEventListener("pointermove", move);
        w.addEventListener("pointerup", end);
        w.addEventListener("pointercancel", end);
        e.preventDefault();
      });
      lo.addEventListener("input", function () { if (+lo.value > +hi.value) lo.value = hi.value; upd(); });
      hi.addEventListener("input", function () { if (+hi.value < +lo.value) hi.value = lo.value; upd(); });
      upd();
    });
  }
  window.c22InitRangeDual = initRangeDual;

  /* ---------- Overlay-Engine: gemeinsamer Positionierer + Tooltip + Popover ----------
     placeFloating rechnet Seite/Ausrichtung mit Viewport-Flip und -Klemmung; Tooltip und
     Popover (native Popover-API) teilen ihn. position:fixed → gegen den Viewport gerechnet. */
  function placeFloating(anchor, floating, opts) {
    opts = opts || {};
    var side = opts.side || "top", align = opts.align || "center", gap = opts.gap == null ? 8 : opts.gap;
    floating.style.position = "fixed"; floating.style.left = "0"; floating.style.top = "0";   // sauber messen
    var a = anchor.getBoundingClientRect(), f = floating.getBoundingClientRect();
    var vw = window.innerWidth, vh = window.innerHeight;
    var opp = { top: "bottom", bottom: "top", left: "right", right: "left" };
    function room(s) { return s === "top" ? a.top : s === "bottom" ? vh - a.bottom : s === "left" ? a.left : vw - a.right; }
    var vertical = (side === "top" || side === "bottom");
    var need = (vertical ? f.height : f.width) + gap;
    if (room(side) < need && room(opp[side]) >= need) side = opp[side];   // Flip, wenn drüben mehr Platz
    vertical = (side === "top" || side === "bottom");
    var top, left;
    if (vertical) {
      top = side === "top" ? a.top - f.height - gap : a.bottom + gap;
      left = align === "start" ? a.left : align === "end" ? a.right - f.width : a.left + a.width / 2 - f.width / 2;
    } else {
      left = side === "left" ? a.left - f.width - gap : a.right + gap;
      top = align === "start" ? a.top : align === "end" ? a.bottom - f.height : a.top + a.height / 2 - f.height / 2;
    }
    left = Math.max(6, Math.min(left, vw - f.width - 6));   // in den Viewport klemmen
    top = Math.max(6, Math.min(top, vh - f.height - 6));
    floating.style.left = left + "px"; floating.style.top = top + "px";
    floating.dataset.side = side;
    return side;
  }
  window.c22PlaceFloating = placeFloating;

  function initTooltips(root) {
    var tip = null;
    function ensureTip() {
      if (!tip) { tip = document.createElement("div"); tip.className = "c22-tooltip"; tip.setAttribute("role", "tooltip"); document.body.appendChild(tip); }
      return tip;
    }
    (root || document).querySelectorAll("[data-tooltip]").forEach(function (el) {
      if (el.dataset.c22Tip) return; el.dataset.c22Tip = "1";
      function show() {
        var t = ensureTip();
        t.textContent = el.getAttribute("data-tooltip");
        placeFloating(el, t, { side: el.getAttribute("data-tip-side") || "top", gap: 8 });
        t.classList.add("in");
      }
      function hide() { if (tip) tip.classList.remove("in"); }
      el.addEventListener("mouseenter", show); el.addEventListener("mouseleave", hide);
      el.addEventListener("focus", show); el.addEventListener("blur", hide);
    });
  }

  function initPopovers(root) {
    (root || document).querySelectorAll("[data-popover]").forEach(function (pop) {
      if (pop.dataset.c22Pop || !pop.id) return; pop.dataset.c22Pop = "1";
      pop.addEventListener("toggle", function (e) {
        if (e.newState !== "open") return;
        var trigger = document.querySelector('[popovertarget="' + pop.id + '"]');
        if (trigger) placeFloating(trigger, pop, { side: pop.getAttribute("data-side") || "bottom", align: pop.getAttribute("data-align") || "center", gap: 8 });
      });
    });
  }
  window.c22InitOverlays = function (root) { initTooltips(root); initPopovers(root); };

  /* ---------- ARIA-Menu (Aktions-Menü) — Roving-Tabindex, echter Fokus, Typeahead ---------- */
  function initMenu(root) {
    (root || document).querySelectorAll(".c22-menu").forEach(function (wrap) {
      if (wrap.dataset.c22Menu) return; wrap.dataset.c22Menu = "1";
      var btn = wrap.querySelector('[aria-haspopup="menu"]') || wrap.querySelector("button");
      var list = wrap.querySelector('[role="menu"]');
      if (!btn || !list) return;
      var open = false, buf = "", bufT = 0;
      var items = function () { return Array.prototype.slice.call(list.querySelectorAll('[role="menuitem"]')); };
      var curIndex = function () { return items().indexOf(document.activeElement); };
      function setFocus(i) {
        var it = items(); if (!it.length) return;
        i = (i + it.length) % it.length;
        it.forEach(function (m, mi) { m.tabIndex = mi === i ? 0 : -1; });
        it[i].focus(); it[i].scrollIntoView({ block: "nearest" });
      }
      function onOutside(e) { if (!wrap.contains(e.target) && !list.contains(e.target)) closeMenu(false); }
      function openMenu(last) {
        if (open) return; open = true;
        if (list.parentNode !== document.body) document.body.appendChild(list);   // Portal → position:fixed entkommt transformierten Vorfahren
        list.hidden = false; btn.setAttribute("aria-expanded", "true");
        placeFloating(btn, list, { side: "bottom", align: "start", gap: 6 });
        requestAnimationFrame(function () { list.classList.add("open"); });
        setFocus(last ? items().length - 1 : 0);
        document.addEventListener("pointerdown", onOutside, true);
      }
      function closeMenu(returnFocus) {
        if (!open) return; open = false;
        list.classList.remove("open"); btn.setAttribute("aria-expanded", "false");
        document.removeEventListener("pointerdown", onOutside, true);
        setTimeout(function () { if (!open) list.hidden = true; }, 160);
        if (returnFocus) btn.focus();
      }
      btn.setAttribute("aria-expanded", "false");
      if (list.hidden === false) list.hidden = true;
      btn.addEventListener("click", function () { open ? closeMenu(false) : openMenu(false); });
      btn.addEventListener("keydown", function (e) {
        if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") { e.preventDefault(); openMenu(false); }
        else if (e.key === "ArrowUp") { e.preventDefault(); openMenu(true); }
      });
      list.addEventListener("keydown", function (e) {
        var it = items(), i = curIndex();
        if (e.key === "ArrowDown") { e.preventDefault(); setFocus(i + 1); }
        else if (e.key === "ArrowUp") { e.preventDefault(); setFocus(i - 1); }
        else if (e.key === "Home" || e.key === "PageUp") { e.preventDefault(); setFocus(0); }
        else if (e.key === "End" || e.key === "PageDown") { e.preventDefault(); setFocus(it.length - 1); }
        else if (e.key === "Escape") {   // liegt ein Popup über dem Menü, schließt das zuerst (dismissible-stack)
          e.preventDefault(); e.stopPropagation();
          var pw = document.getElementById("c22-popups");
          var tops = pw ? livePopups(pw).filter(function (p) { return !p.dataset.locked; }) : [];
          if (tops.length) removePopup(tops[tops.length - 1]); else closeMenu(true);
        }
        else if (e.key === "Tab") { closeMenu(false); }   // NICHT preventDefault → Fokus wandert regulär weiter
        else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); var m = it[i]; if (m && m.getAttribute("aria-disabled") !== "true") m.click(); }
        else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {   // Typeahead
          var now = Date.now(); if (now - bufT > 500) buf = ""; bufT = now; buf += e.key.toLowerCase();
          var q = /^(.)\1*$/.test(buf) ? buf.charAt(0) : buf;   // gleicher Buchstabe wiederholt → rotieren
          for (var k = 1; k <= it.length; k++) {
            var idx = (i + k) % it.length;
            if ((it[idx].textContent || "").trim().toLowerCase().indexOf(q) === 0) { setFocus(idx); break; }
          }
        }
      });
      items().forEach(function (m) {
        m.addEventListener("click", function () { if (m.getAttribute("aria-disabled") === "true") return; closeMenu(true); });
      });
    });
  }
  window.c22InitMenu = initMenu;

  /* ---------- Combobox / Autocomplete (list autocomplete, manual selection) ----------
     Realer Fokus bleibt IMMER im <input>; die Hervorhebung wandert per aria-activedescendant durch
     die Optionen (Virtual Focus). Optionen aus <li role=option>-Kindern ODER data-options (JSON). */
  var cbSeq = 0;
  function initCombobox(root) {
    (root || document).querySelectorAll(".c22-combobox").forEach(function (wrap) {
      if (wrap.dataset.c22Cb) return; wrap.dataset.c22Cb = "1";
      var input = wrap.querySelector('input[role="combobox"]') || wrap.querySelector("input");
      var listbox = wrap.querySelector('[role="listbox"]');
      if (!input || !listbox) return;
      var pre = Array.prototype.slice.call(listbox.querySelectorAll('[role="option"]'));
      var master = pre.length ? pre.map(function (o) { return (o.textContent || "").trim(); }) : [];
      if (!master.length) { try { master = (JSON.parse(wrap.getAttribute("data-options") || "[]") || []).map(String); } catch (e) { master = []; } }
      listbox.innerHTML = ""; listbox.hidden = true;   // Startzustand selbst erzwingen (nicht auf [hidden] im Markup verlassen)
      var id = "c22cb" + (++cbSeq);
      if (!listbox.id) listbox.id = id + "-list";
      input.setAttribute("role", "combobox");
      input.setAttribute("aria-autocomplete", "list");
      input.setAttribute("aria-expanded", "false");
      input.setAttribute("aria-controls", listbox.id);
      input.setAttribute("autocomplete", "off");
      if (!listbox.getAttribute("aria-label") && !listbox.getAttribute("aria-labelledby")) listbox.setAttribute("aria-label", input.getAttribute("aria-label") || "Vorschläge");

      var open = false, active = -1, opts = [], lastValue = input.value || "";

      function render(filter) {
        var f = (filter || "").trim().toLowerCase();
        var matches = master.filter(function (m) { return !f || m.toLowerCase().indexOf(f) >= 0; });
        listbox.innerHTML = "";
        opts = matches.map(function (m, i) {
          var li = document.createElement("li");
          li.setAttribute("role", "option"); li.id = listbox.id + "-o" + i; li.textContent = m;
          li.addEventListener("mousedown", function (e) { e.preventDefault(); });   // Fokus im Input halten (sonst Blur → Popup zu vor dem click)
          li.addEventListener("click", function () { choose(i); });
          listbox.appendChild(li); return li;
        });
        if (!matches.length) {
          var none = document.createElement("li");
          none.className = "cb-empty"; none.textContent = "Keine Treffer";   // KEIN role=option → nicht navigierbar
          listbox.appendChild(none);
        }
        return matches.length;
      }
      function setActive(i) {
        if (opts[active]) { opts[active].classList.remove("active"); opts[active].removeAttribute("aria-selected"); }
        active = (i != null && i >= 0 && i < opts.length) ? i : -1;
        if (active >= 0) {
          opts[active].classList.add("active"); opts[active].setAttribute("aria-selected", "true");
          input.setAttribute("aria-activedescendant", opts[active].id);
          opts[active].scrollIntoView({ block: "nearest" });
        } else input.removeAttribute("aria-activedescendant");
      }
      function onOutside(e) { if (!wrap.contains(e.target) && !listbox.contains(e.target)) closeList(); }
      function openList(highlight) {
        if (!master.length) return;
        render(input.value);
        if (listbox.parentNode !== document.body) document.body.appendChild(listbox);   // Portal → position:fixed entkommt transformierten Vorfahren
        if (!open) { open = true; listbox.hidden = false; document.addEventListener("pointerdown", onOutside, true); }
        input.setAttribute("aria-expanded", "true");
        listbox.style.minWidth = input.offsetWidth + "px";
        placeFloating(input, listbox, { side: "bottom", align: "start", gap: 6 });
        requestAnimationFrame(function () { listbox.classList.add("open"); });
        setActive(highlight === "first" ? 0 : highlight === "last" ? opts.length - 1 : -1);
      }
      function closeList() {
        if (!open) return; open = false;
        listbox.classList.remove("open"); input.setAttribute("aria-expanded", "false");
        setActive(-1); document.removeEventListener("pointerdown", onOutside, true);
        setTimeout(function () { if (!open) listbox.hidden = true; }, 150);
      }
      function choose(i) {
        if (i < 0 || !opts[i]) return;
        input.value = opts[i].textContent; lastValue = input.value;
        closeList(); input.focus();
        input.dispatchEvent(new Event("change", { bubbles: true }));
      }

      input.addEventListener("input", function () { openList("none"); });   // filtern, KEIN Auto-Highlight (manual selection)
      input.addEventListener("click", function () { if (!open) openList("none"); });
      input.addEventListener("keydown", function (e) {
        if (e.altKey && e.key === "ArrowDown") { e.preventDefault(); openList("none"); return; }
        if (e.altKey && e.key === "ArrowUp") { e.preventDefault(); if (open) closeList(); return; }
        if (e.key === "ArrowDown") { e.preventDefault(); if (!open) openList("first"); else setActive(active + 1 >= opts.length ? 0 : active + 1); }
        else if (e.key === "ArrowUp") { e.preventDefault(); if (!open) openList("last"); else setActive(active - 1 < 0 ? opts.length - 1 : active - 1); }
        else if (e.key === "Home" && open) { e.preventDefault(); setActive(0); }
        else if (e.key === "End" && open) { e.preventDefault(); setActive(opts.length - 1); }
        else if (e.key === "Enter") { if (open) { e.preventDefault(); if (active >= 0) choose(active); else closeList(); } }
        else if (e.key === "Tab") { if (open && active >= 0) choose(active); else if (open) closeList(); }   // Tab NICHT preventDefault → Fokus wandert
        else if (e.key === "Escape") { if (open) { e.preventDefault(); e.stopPropagation(); closeList(); } else if (input.value !== lastValue) { e.preventDefault(); input.value = lastValue; } }
      });
      input.addEventListener("blur", function () { setTimeout(function () { if (!wrap.contains(document.activeElement)) closeList(); }, 0); });
    });
  }
  window.c22InitCombobox = initCombobox;

  /* ---------- Start ---------- */
  function init() { renderIcons(); initSwitches(); initMenus(); initCenter(); initDialogs(); initPopups(); initForms(); initAccordion(); initTabs(); initNav(); initRange(); initRangeDual(); initTooltips(); initPopovers(); initMenu(); initCombobox(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
