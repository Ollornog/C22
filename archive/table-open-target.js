// ARCHIVE: not built, not shipped. See archive/README.md.
// What: the pointing part of the level-table selection in c22.js as it was with data-open-target: zeige() marks what a double
//       click would open (third argument), the mouseover handler passes the merged cell with data-href or td[data-primary].
// Why archived: replaced by link underlines on the code and name (data-follow); zeige() lost its third argument.
// Last live in commit f2c8dcd (c22/static/js/c22.js, table selection section).
  // Pointing: the same rows a click would take, and the merged cells by the same rule.
  function zeige(table, zeilen, ziel) {
    table.querySelectorAll('[data-hover], [data-open-target]').forEach(function (el) { el.removeAttribute('data-hover'); el.removeAttribute('data-open-target'); });
    if (!zeilen.length) return;
    zeilen.forEach(function (tr) { tr.setAttribute('data-hover', 'full'); });
    var drin = new Set(zeilen);
    jeZelle(table, function (tr) { return drin.has(tr); }, function (td, s) { if (s) td.setAttribute('data-hover', s); });
    if (ziel) ziel.setAttribute('data-open-target', '');
  }
  var gezeigt = { table: null, punkt: null };
  document.addEventListener('mouseover', function (e) {
    var tr = e.target.closest && e.target.closest(TABLE + ' tbody tr');
    var table = tr && tr.closest('table');
    var td = tr && e.target.closest('td');
    var punkt = td && td.hasAttribute('data-merged') ? td : tr;
    if (punkt === gezeigt.punkt) return;
    if (gezeigt.table && gezeigt.table !== table) zeige(gezeigt.table, [], null);
    gezeigt = { table: table, punkt: punkt };
    if (!tr) return;
    if (punkt === td) zeige(table, mitGleichen(table, zeilenVon(td)), explorer(table) && td.hasAttribute('data-href') ? td : null);
    else zeige(table, mitGleichen(table, [tr]), explorer(table) ? tr.querySelector('td[data-primary]') : null);
