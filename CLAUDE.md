# praneetdhoolia.github.io — project conventions

Repo-level guidance for any Claude Code session working in this repository.

## What this is

The source for **https://praneetdhoolia.github.io** — Praneet Dhoolia's personal site and
writing, published by **GitHub Pages** from the `main` branch of
`praneetdhoolia/praneetdhoolia.github.io`.

Current state: a Jekyll site on the `jekyll/minima` remote theme — `_config.yml`, a
`layout: home` `index.md`, `about.md`, dated Markdown posts in `_posts/`, images in `media/`.

Planned direction: an overhaul to a **modern, HTML-artifact-based** site — a central index
that tracks every post with a short insight/summary per entry, with each post a standalone
HTML artifact rather than a themed Markdown page. Until that lands, treat the Jekyll
structure above as current.

## Working style (apply to every change)

1. **Inventory first.** Read the relevant files; state your understanding; flag
   contradictions, gaps and decisions.
2. **Plan, then get sign-off.** Propose the change and **wait for approval** before writing
   files.
3. **Implement.** Only after approval. Prefer clear TODOs over speculative implementation.

## Hard constraints (do not violate)

- **This is a live, public site.** `main` is what the world sees — GitHub Pages publishes it
  on push. Work on a branch; don't push straight to `main` without saying so.
- **Don't rewrite published posts' meaning.** Post content is the author's voice and record.
  Reformatting, restructuring, or re-styling is fair game; changing what a post *claims* is
  not, unless asked.
- **Don't break existing URLs.** Published post paths and `/about/` are linked from
  elsewhere; if a restructure changes a path, add a redirect rather than silently dropping it.
- **Self-contained pages.** HTML artifacts inline their own CSS/JS and reference only assets
  committed to this repo — no CDN scripts, no remote fonts, no external trackers.
- **Every page is responsive and theme-aware** (light + dark), with no horizontal body scroll.

## Conventions

- **Branch naming.** `<git-handle>/<short-kebab-description>`, with `<git-handle>` derived from
  the active git identity (the `…+<handle>@users.noreply.github.com` email, else the owner
  segment of the `origin` remote — here `praneetdhoolia`). **Never `claude/*`** — if the
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
     edit` commands carrying it (the `gh` CLI path);
  4. `.github/workflows/strip-session-ref.yml` scrubs the link from a PR **body** server-side —
     the only layer that catches a body injected by the cloud **platform** (outside the agent's
     tool loop, and not in git history, so layers 1–3 structurally cannot see it). It is a
     scrub-after-creation.
- **Path references in prose.** Never abbreviate a file path with `…`/`...` (e.g.
  `_posts/.../post.md`). Renderers auto-link it into a literal, broken URL. Write the full real
  path — `_posts/2025-02-08-software-engineering-agent-langgraph.md`.
- **Post filenames** follow Jekyll's dated convention: `_posts/YYYY-MM-DD-kebab-title.md`.
  Keep the date the publication date; don't renumber existing posts.

## Repo map

| Path | What it holds |
|------|---------------|
| `_config.yml` | Jekyll site config: title, author, remote theme, plugins, social links. |
| `index.md` | Site home (currently `layout: home`, i.e. the theme's post list). |
| `about.md` | The `/about/` page. |
| `_posts/` | Dated Markdown posts (`YYYY-MM-DD-slug.md`). |
| `media/` | Images, GIFs and diagrams referenced by posts (`/media/...`). |
| `docs/` | Static documents served from the site (e.g. `docs/Profile.pdf`). |
| `.claude/settings.json` | Harness config: attribution suppression, SessionStart + PreToolUse hooks, sandbox network allowlist. |
| `.claude/hooks/` | PreToolUse session-link guards + the SessionStart branch-naming reminder. |
| `.githooks/commit-msg` | Strips any `claude.ai/code` session link from commit messages. |
| `.github/workflows/strip-session-ref.yml` | Server-side scrub of a session link from a PR body. |
| `.gitattributes` | Pins LF endings for `*.sh` / `.githooks/*` so hooks stay runnable on Linux. |
