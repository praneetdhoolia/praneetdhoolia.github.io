# praneetdhoolia.github.io - project conventions

Repo-level guidance for any Claude Code session working in this repository.

## What this is

The source for **https://praneetdhoolia.github.io** - Praneet Dhoolia's personal site and
writing, published by **GitHub Pages** from the `main` branch of
`praneetdhoolia/praneetdhoolia.github.io`.

**There is no build system and no Jekyll.** Every page is hand-authored HTML served exactly as
committed (`.nojekyll` turns Jekyll off). The site is:

- a root `index.html` - the landing page, a reverse-chronological list of everything written,
  each entry carrying a short **insight/summary** of the piece;
- a standalone post is a single `<slug>.html` at the repo root;
- a folder is a **series**: its own `index.html` (the series landing page) plus parts named
  `part-<n>-<slug>.html`;
- `assets/site.css` - the one stylesheet every page links;
- `media/` - images referenced by posts; `docs/` - served documents (e.g. `docs/Profile.pdf`).

Posts were originally dated Jekyll markdown in `_posts/`. They were converted to HTML artifacts;
the markdown originals are gone from the working tree but remain in git history.

## Working style (apply to every change)

1. **Inventory first.** Read the relevant files; state your understanding; flag
   contradictions, gaps and decisions.
2. **Plan, then get sign-off.** Propose the change and **wait for approval** before writing
   files.
3. **Implement.** Only after approval. Prefer clear TODOs over speculative implementation.

## Hard constraints (do not violate)

- **This is a live, public site.** `main` is what the world sees - GitHub Pages publishes it
  on push. Work on a branch; don't push straight to `main` without saying so.
- **Don't rewrite published posts' meaning.** Post content is the author's voice and record.
  Reformatting, restructuring, or re-styling is fair game; changing what a post *claims* is
  not, unless asked.
- **URLs.** Keep current pages resolving at their published paths - a rename means adding a
  redirect stub (`<link rel="canonical">` + `<meta http-equiv="refresh">` + `noindex, follow`)
  at the path being vacated, and repointing any stub that already targeted it. The original
  dated Jekyll post paths under `2024/` and `2025/` had such stubs; the author retired them
  deliberately, so those seven URLs now 404. Recover them from git history if that turns out to
  be a mistake. Don't drop a stub on your own initiative - that call is the author's.
- **Self-contained pages.** Pages reference only assets committed to this repo - no CDN scripts,
  no remote fonts, no external trackers, no analytics. Two deliberate carve-outs: the shared
  `assets/site.css` (committed here, linked by every page), and **author-placed media embeds**
  that are part of the content - e.g. the YouTube `<iframe>` demo in
  `universal-assistant-langgraph-mcp.html`, which predates this rule and is the author's own
  material. Do not add new third-party embeds without asking.
- **Every page is responsive and theme-aware** (light + dark via `prefers-color-scheme`), with no
  horizontal body scroll. Wide content - code blocks, tables - scrolls inside its own box.

## Rule: keep the landing page in sync

*(This structure and rule follow `pdhoolia/research-notes`, which this site is modelled on.)*

Whenever a post, collection, or series is added (or renamed/removed), update the root
`index.html` **in the same commit**:

1. Add a new `<li class="note">` at the **top** of the `ol.notes` list (newest first).
2. Use the post's `<h1>` as the entry title, and its standfirst as the **summary** - write the
   standfirst once, reuse it verbatim here. Where a post has none (the seven converted posts do
   not), write a real summary: the insight, not a restatement of the title. This is the point of
   the index; an entry without one is incomplete.
3. For a series, link the entry title to `<folder>/`, tag it `Series · N parts`, and list the
   parts in a `ul.parts` block. Adding a part updates that entry's part list and count; the entry
   only moves to the top if the series is the newest work.
4. Tag each entry with a short category (e.g. Agent Design, MCP, Series).
5. Use the publication date as the entry date - for new writing, the commit date.
6. A post that supersedes an older one replaces it in the list - never list the same content
   twice. A series part that supersedes a standalone post replaces it; don't list both.

## Series landing pages

A series folder's `index.html` carries four things, in order (see
`retrieval-agent/index.html`):

1. **Masthead** - kicker reading `Series · N parts · <date range>`, the series `<h1>`, and a
   standfirst saying what the series set out to do.
2. **The arc, in one breath** - a single `.arc` paragraph naming every part and how each one
   hands to the next. A reader who stops here should still know the shape of the whole thing.
3. **Part cards** - one `<a class="part">` per part, the whole card a link, carrying a kicker
   (`Part N · <thematic label> · <date>`), the part's title, a summary, and a `Read Part N →`
   affordance.
4. The standard site footer.

## Conventions

- **Cross-references carry a hover description.** A link in prose (or in a colophon) to another
  post on this site is never a bare link - the reader should learn what is behind it without
  clicking. Mark it up for the shared tooltip:
  `<a class="t" data-ref="Part 1 &middot; The model" data-tip="One sentence on what they will
  find there." href="/...">link text</a>`. The page needs `<div id="tip" role="tooltip"></div>`
  and `<script src="/assets/tip.js" defer></script>` before `</body>`. This does **not** apply to
  the prev/next pager cards or the index and series-landing cards - those already show the target's
  title and summary on screen.
- **Tooltips are one shared script.** `assets/tip.js` drives all three tooltip forms - `data-k`
  (glossary, defined per page as `window.GLOSS = {...}` in an inline `<script>` before the file
  loads), `data-src` (outbound citation, labelled SOURCE), and `data-ref` + `data-tip`
  (cross-reference). Styling lives in `assets/site.css` (`.t`, `#tip`). Never paste the engine
  inline into a page.
- **No em dashes. Anywhere.** Not in prose, headings, `<title>` tags, meta descriptions, SVG
  labels, tooltip text, alt text, commit messages, or PR bodies. Use a plain spaced hyphen
  (`Tutor - The University of Queensland`), or restructure with a comma, colon or full stop.
  Neither the raw character (U+2014) nor the `&mdash;` entity belongs in this repo. En dashes (`&ndash;`)
  are fine and are still the right thing for ranges (`Feb 2022 &ndash; Jun 2026`).
- **Page naming.** Standalone post: `<kebab-slug>.html` at the repo root. Series: a
  `<kebab-slug>/` folder holding `index.html` and `part-<n>-<kebab-slug>.html`. Keep slugs stable
  - a rename means a new redirect stub.
- **Paths in HTML are site-absolute** (`/assets/site.css`, `/media/foo.png`, `/retrieval-agent/`).
  This is a user site served from the domain root, so there is no baseurl to worry about, and
  absolute paths work identically from a root page, a series folder, and a dated stub.
- **New pages start from an existing one.** Copy the nearest sibling (a post artifact, or
  `retrieval-agent/index.html` for a series) rather than writing markup from scratch, so the
  header, footer, `<link rel="canonical">` and metadata stay consistent.
- **Branch naming.** `<git-handle>/<short-kebab-description>`, with `<git-handle>` derived from
  the active git identity (the `…+<handle>@users.noreply.github.com` email, else the owner
  segment of the `origin` remote - here `praneetdhoolia`). **Never `claude/*`** - if the
  harness assigns one, this rule wins: `git branch -m …` before committing. A SessionStart hook
  surfaces this each session.
- **Attribution.** No Claude co-author trailer or PR attribution (`attribution.commit`/`pr`
  empty, `includeCoAuthoredBy: false` in `.claude/settings.json`); a SessionStart hook pins the
  git identity. **No `claude.ai/code` session link** in commit messages or PR bodies either.
  `attribution.sessionUrl: false` is set, but it is **not** sufficient on its own (the cloud
  platform injects a session-link footer into PR bodies regardless), so this is enforced
  deterministically across four layers:
  1. `.githooks/commit-msg` strips the session link / `Claude-Session:` trailer from every
     commit (activated each session via `core.hooksPath`, set in the SessionStart hook because
     an ephemeral container doesn't track `.git/hooks`);
  2. `.claude/hooks/block-session-ref-in-pr.sh` (`PreToolUse`) denies
     `create`/`update_pull_request` MCP calls whose title/body carry the link;
  3. `.claude/hooks/block-session-ref-in-gh-pr.sh` (`PreToolUse`) denies `gh pr create`/`gh pr
     edit` commands carrying it (the `gh` CLI path). Note it matches the URL anywhere in the
     payload, so a PR body that *discusses* this policy is blocked too - reword, don't fight it;
  4. `.github/workflows/strip-session-ref.yml` scrubs the link from a PR **body** server-side -
     the only layer that catches a body injected by the cloud **platform** (outside the agent's
     tool loop, and not in git history, so layers 1–3 structurally cannot see it). It is a
     scrub-after-creation.
- **Path references in prose.** Never abbreviate a file path with `…`/`...` (e.g.
  `retrieval-agent/.../part.html`). Renderers auto-link it into a literal, broken URL. Write the
  full real path - `retrieval-agent/part-1-expanding-the-template.html`.

## Repo map

| Path | What it holds |
|------|---------------|
| `index.html` | Landing page: reverse-chron list of all writing, one summary per entry. |
| `about/index.html` | The `/about/` page. |
| `retrieval-agent/` | Series: `index.html` landing page + `part-1…5-*.html`. |
| `city-digital-twin/` | Series: `index.html` landing page + `part-<n>-*.html`. |
| `software-engineering-agent-langgraph.html`, `universal-assistant-langgraph-mcp.html` | Standalone posts. |
| `assets/tip.js` | The shared glossary / source / cross-reference tooltip engine. |
| `assets/site.css` | The single shared stylesheet (light + dark, system fonts, responsive). Includes the **essay-artifact layer** - `figure`/`figcaption`, `.fig-scroll`, the `.sv-*` SVG text classes, `.callout` (and `.callout.flag`), `.sources`, `.colophon`, `.eyebrow.ruled`, and the `.t` / `#tip` glossary tooltip - so a post that argues with diagrams needs no bespoke CSS. |
| `media/` | Images, GIFs and diagrams referenced by posts (`/media/...`). |
| `docs/` | Static documents served from the site (e.g. `docs/Profile.pdf`). |
| `.nojekyll` | Turns GitHub Pages' Jekyll processing off; the HTML is served as committed. |
| `.claude/CLAUDE.md` | This file - the project conventions, loaded into every session. |
| `.claude/settings.json` | Harness config: attribution suppression, SessionStart + PreToolUse hooks, sandbox network allowlist. |
| `.claude/hooks/` | PreToolUse session-link guards + the SessionStart branch-naming reminder. |
| `.githooks/commit-msg` | Strips any `claude.ai/code` session link from commit messages. |
| `.github/workflows/strip-session-ref.yml` | Server-side scrub of a session link from a PR body. |
| `.gitattributes` | Pins LF endings for `*.sh` / `.githooks/*` so hooks stay runnable on Linux. |
