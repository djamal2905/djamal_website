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

| Where you want it to show up                        | Drop the `.qmd` file into                        |
|-------------------------------------------------------|--------------------------------------------------|
| Blog                                                   | `blog/` (auto-discovered, see below)             |
| A machine-learning project                             | `content/machine-learning/<project-slug>/`       |
| A programming project                                   | `content/programming/<project-slug>/`            |
| A data-visualization / presentation project             | `content/data-visualization/<project-slug>/`     |

`blog/` is the one truly auto-discovering folder: `blog/index.qmd` has a
Quarto `listing:` directive that scans the folder for `.qmd` files and turns
their front matter into a card automatically (title, image, description,
categories, date) — drop a file in and it appears, no other edit needed.

The `content/<domain>/` folders are where individual **project** pages live
(one sub-folder per project, holding its `.qmd`, data files, and images
together). These are *not* an auto-discovery listing — `personal-projects.qmd`
and `academic-projects.qmd` are hand-crafted pages with a bespoke card per
project (custom description, tags, links), so after adding a new project
folder here you still add one card block to the relevant page pointing at
`content/<domain>/<project-slug>/<file>.html`. This is intentional: these are
curated feature pages, not a generic feed.

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

- **`blog/index.qmd`** is the one true *listing page*: its `listing.contents`
  includes `"*.qmd"`, so any sibling `.qmd` file is picked up automatically.
  This is the pattern to use for short articles/notes going forward.
- **`content/<domain>/<project-slug>/`** folders hold full project write-ups
  (one folder per project, its `.qmd` plus data/images/etc. together). They
  are *not* auto-discovered — `personal-projects.qmd` and
  `academic-projects.qmd` are hand-crafted pages with one bespoke card per
  project, so a new project folder here still needs one card added to the
  relevant page.
- **The old `publications/` category-listing system (Statistics & ML,
  Programming, Theory, Visualization) has been retired and moved to
  `content/archive/publications-legacy/`.** It was never linked from the
  site's live navigation (which exposes "Personal Projects" / "Academic
  Projects" instead) and duplicated project listings that already live on
  those two pages. It is excluded from `_quarto.yml`'s render list, so it no
  longer builds — the files are kept only for history. `publications.qmd`
  and `Projects/index.qmd` (the old "hub" pages for that system) were
  archived alongside it for the same reason.

## The Blog

`blog.qmd` (repo root) is the main, hand-styled "Blog" page linked from the
site navigation — it highlights a curated set of articles with the same
portfolio-shell design as the rest of the site. `blog/index.qmd` is a
separate, plain Quarto listing that auto-discovers any `.qmd` dropped into
`blog/`; it's linked from a "Tous les articles →" button on `blog.qmd` as the
full, ever-growing archive. `blog/bienvenue-sur-le-blog.qmd` is a real
starter post kept in place as a working example of the front-matter
convention — feel free to delete it once there are real posts.

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
