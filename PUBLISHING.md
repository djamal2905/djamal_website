# Publishing workflow

This site is a static Quarto website (`project.output-dir: docs`) deployed by
GitHub Pages from `main` / `/docs`. This document describes how to add new
content and how it gets built and deployed automatically.

## TL;DR — adding a new article or blog post

1. Copy `_templates/new-post-template.qmd` into the right folder (see table below).
2. Rename it to a short slug, e.g. `my-new-analysis.qmd`.
3. Fill in the front matter (`title`, `date`, `author`; add `categories`, `image`,
   `description` — strongly recommended, they drive the listing card).
4. Write the content in Markdown below the front matter.
5. Commit and push to `main`.

That's it. No edit to `_quarto.yml`, the navbar, or any hand-maintained listing
file is required — GitHub Actions renders the site and publishes it for you.

| Where you want it to show up                        | Drop the `.qmd` file into      |
|-------------------------------------------------------|-------------------------------|
| Blog                                                   | `blog/`                       |
| Publications → Statistics & Machine Learning           | `publications/stat_ml/`       |
| Publications → Programming & Interactive Projects      | `publications/programming/`   |
| Publications → Theory & Training material              | `publications/theorie/`       |
| Publications → Exploratory Analysis & Visualization    | `publications/visualisation/` |

Each of these folders has an `index.qmd` with a Quarto `listing:` directive
that scans the folder for `.qmd` files and turns their front matter into a
card automatically (title, image, description, categories, date). The
listing page always excludes itself, so `index.qmd` never shows up as a card.

## Front-matter convention

```yaml
---
title: "Your title here"        # required
date: 2026-01-01                # required — controls sort order
author: "Djamal TOE"            # required
categories: [Python, Machine Learning]   # recommended — tags, used for filtering
image: images/thumbnail.png     # recommended — path relative to the post file
description: >                  # recommended — shown on the listing card
  One or two sentences summarizing the post.
---
```

Only `title`, `date`, and `author` are required for the page to render and be
discovered. `categories`, `image`, and `description` are optional but every
existing listing page displays them, so a post without them will simply show
a plain title with no thumbnail/tags on its card.

If a post needs its own images, keep them next to it (e.g. a small
`images/` sub-folder inside the same directory) and reference them with a
relative path — Quarto copies referenced assets to `docs/` automatically.

## What's a listing page vs. a manual page

- **`blog/index.qmd`** and **`publications/<category>/index.qmd`** are
  *listing pages*: their `listing.contents` includes `"*.qmd"`, so any
  sibling `.qmd` file is picked up automatically. This is the pattern to use
  for all new content going forward.
- **`publications/<category>/<name>.yml`** (`stat_ml.yml`, `prog.yml`,
  `theorie.yml`, `viz.yml`) are legacy manifests kept only so the *existing*
  articles (which physically live under `INFO_MINI_PROJETS/`, `FORMATIONS/`,
  `ANALYSES_FACTORIELLES/`, `projet-traitement-donnees/` rather than under
  `publications/`) keep showing up. You do not need to touch these files for
  new content — just drop the new `.qmd` directly into the matching
  `publications/<category>/` folder instead.
- **`publications.qmd`** (repo root) and **`Projects/index.qmd`** are the
  "hub" pages that list the four categories above. They read from
  `Projects/projects.yml`, a short, hand-maintained list of the categories
  themselves (5 entries) — not individual articles. This file changes only
  if you add/remove/rename a whole *category*, which is rare; it is
  intentionally left as a manual manifest rather than converted to directory
  discovery, since a "category" isn't a discoverable per-file property.
  (Note: at the time of this change neither page is linked from the site's
  main navigation, which currently exposes "Personal Projects" /
  "Academic Projects" instead — that's a content/navigation decision for
  whoever owns the site design, not something this change alters.)
- **`Projects/projects.yml`** was intentionally *not* converted to directory
  discovery — the projects it lists live scattered across several
  directories, not inside `Projects/`, and moving already-published articles
  around to make that possible was judged too risky for this change.

## The Blog

`blog/` is a plain Quarto listing (`blog/index.qmd`), independent of the
publications hierarchy above. Drop a `.qmd` there and it appears on the blog
automatically. `blog/bienvenue-sur-le-blog.qmd` is a real starter post kept
in place as a working example of the front-matter convention — feel free to
delete it once there are real posts.

The blog replaces the previous `blog.qmd`, which was a single hand-coded
HTML page with hardcoded "coming soon" cards; every page's navbar link that
used to point to `blog.qmd` now points to `blog/index.qmd` (same "Blog" label,
same position in the nav).

## Automatic build & deploy (GitHub Actions)

`.github/workflows/publish.yml` runs on every push to `main` (except pushes
that only touch `docs/**`, see below) and on manual trigger:

1. Checks out the repo.
2. Installs Quarto CLI 1.9.36 (same version used locally), R, and Python,
   plus the R/Python packages the *existing* articles' code chunks import
   (grepped from the `.qmd` files — see the workflow file for the exact list).
3. Runs `quarto render`.
4. Commits the regenerated `docs/` folder back to `main` with
   `chore: publish rendered site [skip ci]` and pushes it.

**No one-time GitHub setting needs to change.** GitHub Pages already serves
this site from `main` / `/docs` (that's how the previous manual
render-and-commit workflow worked); this pipeline simply automates the exact
same commit the owner used to make by hand. If you ever want to switch
Pages to serve from a `gh-pages` branch instead (cleaner, but a different
publish strategy), that would require a manual change under **Settings →
Pages → Source** — this repo does not currently need that change.

### Avoiding infinite loops

The workflow trigger uses `paths-ignore: [docs/**]`, and the bot's own commit
message contains `[skip ci]` — either one alone is enough to stop the bot's
commit from re-triggering the workflow; both are used for safety.

### Freezing computations (important for reliability)

`_quarto.yml` sets:

```yaml
execute:
  freeze: auto
```

Some existing articles run R/Python code chunks that depend on things a
GitHub Actions runner does not have — e.g.
`INFO_MINI_PROJETS/assistant_virtuel.qmd` opens a live microphone
(`sr.Microphone()`) to demonstrate speech recognition. `freeze: auto` tells
Quarto to reuse the last successfully computed output for a document instead
of re-executing its code, as long as the document's source hasn't changed
since that cache (`_freeze/`) was generated.

New content added via this workflow (blog posts, new publication write-ups)
is plain Markdown with no code chunks, so it always renders instantly and
never needs a cache entry.

**One-time step the owner should do once, locally, for the existing
hardware/interaction-dependent articles:** run `quarto render` on a machine
where those chunks actually work (e.g. a normal desktop with a microphone
and all Python packages installed), then commit the resulting `_freeze/`
folder. After that, CI will reuse those cached results and never attempt to
re-run the risky code, until that specific file's content changes again. If
`_freeze/` for such a file is missing when CI runs, `quarto render` will try
to execute it for real and may fail in CI (this is a pre-existing
characteristic of that content, not something this pipeline can paper over) —
either seed the cache as described above, or mark the offending chunk
`eval: false` the same way the author already did for the adjacent
`pywhatkit`/`wolframalpha` chunks in that same file.

## Files touched by this change

- `_quarto.yml` — render list + `execute: freeze: auto`
- `publications/{stat_ml,programming,theorie,visualisation}/index.qmd` —
  listing `contents` now also globs `"*.qmd"` in the same folder
- `publications.qmd` — converted from a hand-written page to a Quarto listing
- `blog/index.qmd`, `blog/bienvenue-sur-le-blog.qmd` — new Blog section
- `blog.qmd` (old hand-coded page) — removed
- navbar `href="blog.qmd"` → `href="blog/index.qmd"` in every page that links to Blog
- `_templates/new-post-template.qmd` — new
- `.github/workflows/publish.yml` — new
- `PUBLISHING.md` — new (this file)
