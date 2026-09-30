"""Every inline-SVG text in every post must sit inside its labelled box and inside the SVG's viewBox.

Needs Playwright with a Chromium-family browser (pip install playwright; playwright install chromium).
Serves the repository root itself and measures each post's diagrams as the browser lays them out:

    python .github/scripts/check_svg_text.py            # every post
    python .github/scripts/check_svg_text.py URL ...    # given pages

Exit status 1 lists every text that overflows, with the figure it sits in. A text is judged against
the smallest <rect> it starts inside (a labelled box) and against the viewBox; free-standing labels
that start outside every box are judged against the viewBox only.
"""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]

JS = r"""
() => {
  const out = [];
  document.querySelectorAll('article svg').forEach((svg) => {
    const fig = svg.closest('figure');
    const cap = fig ? (fig.querySelector('figcaption b') || {}).textContent : '';
    const vb = svg.viewBox.baseVal;
    const rects = [...svg.querySelectorAll('rect')].map(r => r.getBBox())
      .filter(b => b.width > 30 && b.height > 14 && b.width < vb.width - 2);
    svg.querySelectorAll('text').forEach(t => {
      const b = t.getBBox();
      if (!b.width) return;
      if ((t.getAttribute('transform') || '').includes('rotate')) return;   // a rotated label reads its own axis
      const txt = t.textContent.trim();
      let host = null;
      for (const r of rects) {
        if (b.x >= r.x - 1 && b.y + b.height / 2 >= r.y && b.y + b.height / 2 <= r.y + r.height && b.x <= r.x + r.width) {
          if (!host || r.width * r.height < host.width * host.height) host = r;
        }
      }
      const right = b.x + b.width, bottom = b.y + b.height;
      if (host && (right > host.x + host.width + 1 || bottom > host.y + host.height + 1))
        out.push({fig: cap, text: txt, over: Math.round(right - (host.x + host.width)), box: Math.round(host.width)});
      if (right > vb.width + 0.5 || bottom > vb.height + 0.5 || b.x < -0.5)
        out.push({fig: cap, text: txt, over: Math.round(right - vb.width), box: 'viewBox'});
    });
  });
  return out;
}
"""


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a, **k: None
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def posts():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if p.name == "index.html" or rel.parts[0].startswith(".") or "docs" in rel.parts or "the-city-twice" in rel.parts:
            continue
        yield rel.as_posix()


def main() -> int:
    urls = sys.argv[1:]
    srv = None
    if not urls:
        srv = serve()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        urls = [f"{base}/{rel}" for rel in posts()]
    problems = 0
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(channel="msedge", headless=True)
        except Exception:
            b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        for url in urls:
            pg.goto(url, wait_until="load")
            res = pg.evaluate(JS)
            problems += len(res)
            if res:
                print("==", url.rsplit("/", 1)[-1], len(res), "overflow(s)")
            for r in res:
                print("  ", json.dumps(r, ensure_ascii=False))
        b.close()
    if srv:
        srv.shutdown()
    if problems:
        print(f"{problems} overflowing SVG text(s) across {len(urls)} post(s).")
        return 1
    print(f"OK: no SVG text overflows in {len(urls)} posts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
