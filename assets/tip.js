/* Shared glossary / source / cross-reference tooltip.
 *
 * Linked by any page that needs it; the styling lives in site.css (.t and #tip).
 * A page opts in with a <div id="tip" role="tooltip"></div> and any of:
 *
 *   glossary   <span class="t" data-k="key">term</span>
 *              with window.GLOSS = { key: {t:"Title", d:"Definition"} } declared
 *              in an inline <script> before this file loads.
 *
 *   source     <a class="t" data-src="Author, Publication, year" href="...">text</a>
 *              labelled SOURCE, for outbound citations.
 *
 *   cross-ref  <a class="t" data-ref="Part 1 &middot; The model"
 *                 data-tip="What the reader will find there." href="...">text</a>
 *              for links to other writing on this site, so a bare link never
 *              asks the reader to click blind.
 *
 * Hover or focus shows the tooltip; click follows the link; Escape dismisses.
 * On touch, the first tap on a link reveals the tooltip and the second follows it.
 */
(function () {
  var tip = document.getElementById('tip');
  if (!tip) return;

  var GLOSS = window.GLOSS || {};
  var current = null;
  var hideTimer = null;

  function render(cls, label, body, trailing) {
    tip.className = cls;
    tip.textContent = '';
    var tt = document.createElement('span');
    tt.className = 'tt';
    tt.textContent = label;
    tip.appendChild(tt);
    tip.appendChild(document.createTextNode(body + (trailing || '')));
  }

  function show(el) {
    var k = el.getAttribute('data-k');
    var src = el.getAttribute('data-src');
    var ref = el.getAttribute('data-ref');

    if (k && GLOSS[k]) {
      render('', GLOSS[k].t, GLOSS[k].d);
    } else if (ref) {
      render('ref', ref, el.getAttribute('data-tip') || '', ' →');
    } else if (src) {
      render('src', 'Source', src, ' ↗');
    } else {
      return;
    }

    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
    tip.style.display = 'block';

    var r = el.getBoundingClientRect();
    var tw = tip.offsetWidth;
    var x = window.scrollX + r.left + (r.width / 2) - (tw / 2);
    x = Math.max(10, Math.min(x, window.scrollX + document.documentElement.clientWidth - tw - 10));
    var y = window.scrollY + r.top - tip.offsetHeight - 10;
    if (y < window.scrollY + 4) y = window.scrollY + r.bottom + 10;
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
    current = el;
  }

  function hideSoon() {
    if (hideTimer) clearTimeout(hideTimer);
    hideTimer = setTimeout(function () { tip.style.display = 'none'; current = null; }, 140);
  }

  function hideNow() {
    if (hideTimer) clearTimeout(hideTimer);
    tip.style.display = 'none';
    current = null;
  }

  tip.addEventListener('mouseenter', function () {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  });
  tip.addEventListener('mouseleave', hideSoon);

  var targets = document.querySelectorAll('.t, a[data-src], a[data-ref]');
  targets.forEach(function (el) {
    var isLink = el.tagName === 'A';
    if (!isLink) { el.setAttribute('tabindex', '0'); }
    el.addEventListener('mouseenter', function () { show(el); });
    el.addEventListener('mouseleave', hideSoon);
    el.addEventListener('focus', function () { show(el); });
    el.addEventListener('blur', hideSoon);
    el.addEventListener('click', function (e) {
      if (!isLink) {
        e.preventDefault();
        if (current === el) { hideNow(); } else { show(el); }
      }
    });
    el.addEventListener('touchend', function (e) {
      if (isLink && (el.getAttribute('data-k') || el.getAttribute('data-ref')) && current !== el) {
        e.preventDefault();
        show(el);
      }
    });
  });

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hideNow(); });
  document.addEventListener('touchstart', function (e) {
    if (current && !current.contains(e.target) && !tip.contains(e.target)) hideNow();
  }, { passive: true });
})();
