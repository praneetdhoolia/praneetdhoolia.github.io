"""Check that every post on the site follows the one post anatomy in .claude/CLAUDE.md.

Standard library only; no build step. Run from the repository root:

    python .github/scripts/check_posts.py

A post is any .html page that is not an index page, the about page or a served
document under docs/. Exit status 1 lists every page that drifted and why.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://praneetdhoolia.github.io"
SUFFIX = " - Praneet Dhoolia"
EM_DASH = "—"
EM_DASH_ENTITY = "&" + "mdash;"  # built, so this file does not trip its own check


def text(fragment: str) -> str:
    """Visible text of an HTML fragment, entities decoded, whitespace collapsed."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def strip_scripts(doc: str) -> str:
    """The page without its inline scripts (Part 4 carries a whole embedded page in one)."""
    return re.sub(r"<script\b[^>]*>.*?</script>", "", doc, flags=re.S)


def site_path(page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()
    return "/" + (rel[: -len("index.html")] if rel.endswith("index.html") else rel)


def posts() -> list[Path]:
    out = []
    for page in sorted(ROOT.rglob("*.html")):
        rel = page.relative_to(ROOT).as_posix()
        if rel.split("/")[0].startswith(".") or rel.startswith("docs/"):
            continue
        if page.name == "index.html":
            continue
        out.append(page)
    return out


def check_post(page: Path) -> list[str]:
    doc = page.read_text(encoding="utf-8")
    body = strip_scripts(doc)
    bad = []

    def need(cond: bool, why: str) -> None:
        if not cond:
            bad.append(why)

    need('<link rel="stylesheet" href="/assets/site.css">' in doc, "does not link /assets/site.css")
    need(f'<link rel="canonical" href="{SITE}{site_path(page)}">' in doc,
         f"canonical is not {SITE}{site_path(page)}")

    h1 = re.search(r"<h1>(.*?)</h1>", body, flags=re.S)
    title = re.search(r"<title>(.*?)</title>", doc, flags=re.S)
    need(h1 is not None, "has no <h1>")
    if h1 and title:
        need(text(title.group(1)) == text(h1.group(1)) + SUFFIX,
             f"<title> is not the <h1> plus '{SUFFIX}'")

    header = re.search(r'<div class="post-header">(.*?)</div>', body, flags=re.S)
    need(header is not None, "has no post-header")
    if header:
        h = header.group(1)
        need('class="eyebrow ruled"' in h, "eyebrow is not 'eyebrow ruled'")
        need('class="standfirst"' in h, "has no standfirst")
        date = re.search(r'<p class="date">(.*?)</p>', h, flags=re.S)
        need(date is not None and "<time datetime=" in date.group(1), "date line has no <time datetime>")
        need(date is not None and "min read" in date.group(1), "date line has no read time")

    article = re.search(r'<article class="post-body">(.*)</article>', body, flags=re.S)
    need(article is not None, "has no article.post-body")
    if article:
        a = article.group(1)
        need(re.search(r"<section>\s*<h2>", a) is not None, "has no <section> opening with an <h2>")
        need("&sect;" not in a and "§" not in a,
             "uses a section sign; headings are plain words and prose names a section by what it holds")
        need('<div class="sources">' in a, "has no sources block")

        figs = re.findall(r"<figcaption><b>FIG (\d+)</b>", a)
        need(figs == [str(i) for i in range(1, len(figs) + 1)],
             f"figure numbers run {figs}, not 1..{len(figs)}")
        need(len(re.findall(r"<figcaption>", a)) == len(figs),
             "a figcaption does not open with <b>FIG n</b>")
        for img in re.findall(r"<img\b[^>]*>", a):
            need("width=" in img and "height=" in img, f"image without width/height: {img[:70]}")
        loose = re.sub(r"<figure>.*?</figure>", "", a, flags=re.S)
        need("<img" not in loose, "an image sits outside a <figure>")

    need('<p class="colophon">' in body, "has no colophon")
    need('class="pager"' not in body, "still uses the retired pager")

    uses_tip = re.search(r'class="t"|data-k=|data-ref=|data-src=', body) is not None
    if uses_tip:
        need('<div id="tip" role="tooltip"></div>' in doc, "uses tooltips but has no #tip")
        need('<script src="/assets/tip.js" defer></script>' in doc, "uses tooltips but does not load tip.js")
    keys = set(re.findall(r'data-k="([^"]+)"', body))
    gloss = re.search(r"window\.GLOSS\s*=\s*\{(.*?)\n\};", doc, flags=re.S)
    defined = set(re.findall(r"^\s*([A-Za-z0-9_]+)\s*:\s*\{", gloss.group(1), flags=re.M)) if gloss else set()
    for k in sorted(keys - defined):
        bad.append(f"glossary key '{k}' is used but not defined in window.GLOSS")

    for ref in re.findall(r'<(?:a|img|link)\b[^>]*?\s(?:href|src)="([^"]+)"', body):
        if not ref.startswith(("/", "http://", "https://", "#", "mailto:")):
            bad.append(f"path is not site-absolute: {ref}")
    for src in re.findall(r'<script\b[^>]*\bsrc="([^"]+)"', doc):
        need(src.startswith("/"), f"loads a script from outside the site: {src}")
    return bad


def check_index() -> list[str]:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    bad = []
    for page in posts():
        if f'href="{site_path(page)}"' not in index:
            folder = page.parent
            if folder != ROOT and f'href="/{folder.name}/"' in index:
                continue
            bad.append(f"index.html does not list {site_path(page)}")
    for landing in sorted(ROOT.glob("*/index.html")):
        folder = landing.parent
        parts = sorted(folder.glob("part-*.html"))
        if not parts:
            continue
        doc = landing.read_text(encoding="utf-8")
        for part in parts:
            if f'href="{site_path(part)}"' not in doc:
                bad.append(f"{site_path(landing)} has no card for {part.name}")
        m = re.search(r"Series &middot; (\d+) parts", doc)
        if not m or int(m.group(1)) != len(parts):
            bad.append(f"{site_path(landing)} kicker does not say {len(parts)} parts")
        entry = re.search(rf'href="/{folder.name}/">.*?</li>\s*</ul>', index, flags=re.S)
        if entry:
            listed = re.findall(r'<span class="pn">Part (\d+)</span>', entry.group(0))
            if len(listed) != len(parts):
                bad.append(f"index.html lists {len(listed)} parts of /{folder.name}/, the folder has {len(parts)}")
    return bad


def check_navigation() -> list[str]:
    """Cross-references name their target by its eyebrow; series colophons link the landing, the previous part and
    the next part in that order; index and landing links carry the target's exact title; read times fit the words."""
    bad = []
    info = {}
    for page in posts():
        doc = strip_scripts(page.read_text(encoding="utf-8"))
        h1 = re.search(r"<h1>(.*?)</h1>", doc, flags=re.S)
        eb = re.search(r'<p class="eyebrow ruled"><span>(.*?)</span>', doc, flags=re.S)
        art = re.search(r'<article class="post-body">(.*)</article>', doc, flags=re.S)
        words = len(text(re.sub(r"<svg\b.*?</svg>", " ", art.group(1), flags=re.S)).split()) if art else 0
        info[site_path(page)] = dict(h1=text(h1.group(1)) if h1 else "", eyebrow=text(eb.group(1)) if eb else "",
                                     words=words, figures=len(re.findall(r"<figure\b", doc)), doc=doc)
    for landing in sorted(ROOT.glob("*/index.html")):
        folder = landing.parent
        parts = sorted(folder.glob("part-*.html"), key=lambda p: int(re.search(r"part-(\d+)", p.name).group(1)))
        if parts:
            info[f"/{folder.name}/"] = dict(h1="", eyebrow=f"{info[site_path(parts[0])]['eyebrow'].split(' · ')[0]} · {len(parts)} parts",
                                            words=0, figures=0, doc="", landing=True)
    for src, p in info.items():
        if p.get("landing"):
            continue
        for m in re.finditer(r'<a class="t" data-ref="([^"]*)"\s*data-tip="([^"]*)"\s*href="([^"]*)"', p["doc"], flags=re.S):
            ref, href = html.unescape(m.group(1)), m.group(3)
            tgt = info.get(href)
            if tgt is None:
                if href.startswith("/") and not href.startswith("/docs/"):
                    bad.append(f"{src[1:]}: cross-reference to {href}, which is not a post")
                continue
            eb = tgt["eyebrow"]
            if " · " in eb:  # a series part: its eyebrow, with or without the series name in front
                ok = ref in {eb, " · ".join(eb.split(" · ")[1:])}
            else:  # a standalone: its category, then a descriptor of the post
                ok = ref.startswith(f"{eb} · ") and len(ref) > len(eb) + 3
            if not ok:
                bad.append(f"{src[1:]}: cross-reference label '{ref}' should name the target by its eyebrow '{eb}' ({href})")
    for landing in sorted(ROOT.glob("*/index.html")):
        folder = landing.parent
        parts = sorted(folder.glob("part-*.html"), key=lambda p: int(re.search(r"part-(\d+)", p.name).group(1)))
        for i, part in enumerate(parts):
            col = re.search(r'<p class="colophon">(.*?)</p>', info[site_path(part)]["doc"], flags=re.S)
            hrefs = re.findall(r'href="([^"]*)"', col.group(1)) if col else []
            want = [f"/{folder.name}/"] + ([site_path(parts[i - 1])] if i else []) + ([site_path(parts[i + 1])] if i + 1 < len(parts) else [])
            if hrefs != want:
                bad.append(f"{part.relative_to(ROOT).as_posix()}: colophon links {hrefs}, expected the landing, the previous part and the next part: {want}")
            for m in re.finditer(r'href="(/[^"]+\.html)">(.*?)</a>', col.group(1) if col else "", flags=re.S):
                tgt = info.get(m.group(1))
                if tgt and text(m.group(2)) != tgt["h1"].split(":")[0].strip():
                    bad.append(f"{part.relative_to(ROOT).as_posix()}: colophon names {m.group(1)} '{text(m.group(2))}', its title starts '{tgt['h1'].split(':')[0].strip()}'")
    for src in [ROOT / "index.html", *ROOT.glob("*/index.html")]:
        doc = src.read_text(encoding="utf-8")
        for m in re.finditer(r'<a(?: class="part")? href="(/[^"]+\.html)">\s*(?:<p class="part-kicker">.*?</p>\s*<h2>(.*?)</h2>|(.*?)</a>)', doc, flags=re.S):
            tgt = info.get(m.group(1))
            shown = text(m.group(2) or m.group(3) or "")
            if tgt and shown != tgt["h1"]:
                bad.append(f"{src.relative_to(ROOT).as_posix()}: links {m.group(1)} as '{shown}', its title is '{tgt['h1']}'")
    for src, p in info.items():
        m = re.search(r"~(\d+) min read", p["doc"])
        if m:
            est = p["words"] / 220 + 0.5 * p["figures"]
            if abs(int(m.group(1)) - est) > max(2, 0.3 * est):
                bad.append(f"{src[1:]}: says ~{m.group(1)} min read; {p['words']} words and {p['figures']} figures read in about {est:.0f}")
    return bad


def check_em_dashes() -> list[str]:
    """Every served page, stylesheet and script (the conventions file quotes the rule itself).

    A `vendor/` folder holds third-party code copied in unchanged (a hosted artefact's libraries);
    it is not this site's writing, so it is not held to this site's typography."""
    bad = []
    for f in sorted(ROOT.rglob("*")):
        if not f.is_file() or ".git" in f.parts or "vendor" in f.parts or f.suffix not in {".html", ".css", ".js"}:
            continue
        s = f.read_text(encoding="utf-8", errors="replace")
        if EM_DASH in s or EM_DASH_ENTITY in s:
            bad.append(f"{f.relative_to(ROOT).as_posix()}: contains an em dash")
    return bad


def main() -> int:
    problems = []
    for page in posts():
        for why in check_post(page):
            problems.append(f"{page.relative_to(ROOT).as_posix()}: {why}")
    problems += check_index()
    problems += check_navigation()
    problems += check_em_dashes()
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s) across {len(posts())} post(s).")
        return 1
    print(f"OK: {len(posts())} posts follow the post anatomy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
