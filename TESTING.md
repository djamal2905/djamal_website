# Testing / QA

This is a static [Quarto](https://quarto.org/) site (`.qmd` sources render to
static HTML in `docs/`, served by GitHub Pages). There is no backend, no
API, no database - "testing" here means making sure the build succeeds and
the generated HTML is structurally sound (no broken internal links/images,
basic accessibility hygiene). That verification runs automatically on every
push/PR via GitHub Actions (see below), so nobody has to remember to check
by hand after a publish.

## What gets checked

1. **Build**: `quarto render` must complete without failing. A failed
   render fails the CI job.
2. **Internal links & images** (`scripts/check_site.py`): every internal
   `<a href>`, `<link href>`, `<script src>`, `<img src>`/`srcset`, and
   every `url(...)` reference in CSS/inline styles, must point at a file
   that actually exists in the rendered `docs/` output. In-page and
   cross-page `#fragment` anchors are checked against real `id`
   attributes. **External links (http/https/mailto/etc.) are intentionally
   not checked** here - they need network access and would make CI flaky
   (a third-party site being briefly down would fail an unrelated build).
   Check those occasionally by hand or with a dedicated tool such as
   [lychee](https://github.com/lycheeverse/lychee) if desired.
3. **Basic accessibility / HTML sanity** (same script): each page has
   exactly one non-empty `<title>`, the `<html>` tag has a `lang`
   attribute, and the document isn't obviously truncated (missing closing
   `</html>`, usually a sign the render crashed partway through). Images
   missing `alt` text are reported as warnings (does not fail CI by
   default - see "Known gaps" below).

## Running the checks locally

From the repo root, with Quarto 1.9.36+ on PATH:

```sh
# 1. Build the site
quarto render

# 2. Check the rendered output for broken internal links/images and
#    basic accessibility issues
python scripts/check_site.py --root docs
```

`check_site.py` is pure Python standard library - no `pip install` needed.
Exit code is `0` if there are no errors. Warnings (e.g. missing `alt` text)
are printed but do not fail the run unless you pass `--strict`:

```sh
python scripts/check_site.py --root docs --strict
```

## Continuous monitoring (CI)

`.github/workflows/qa-checks.yml` runs on every `push` and `pull_request`
to `main` (and can be run manually via "Run workflow" in the Actions tab).
It performs, in order:

1. Checks out the repo, installs Quarto 1.9.36, R, and Python with a
   curated set of packages actually used by the `.qmd` files.
2. Runs `quarto render`. This step is allowed to "continue" even on
   failure so the rest of the checks still run and give you full
   diagnostics in one CI run - but the job as a whole is still marked
   failed at the end if the render did not succeed (see the final "Fail
   workflow if render failed" step).
3. Runs `scripts/check_site.py` against `docs/`, printing every broken
   link/image/anchor and every accessibility warning it finds.

Everything runs on free GitHub-hosted runners with no third-party/paid
services.

### Reading a failed CI run

Open the failed run under the repo's **Actions** tab and expand the step
that's red:

- **"Render site (quarto render)" failed** -> scroll the log for the
  first `ERROR:` line; it names the exact `.qmd` file and the R/Python
  error that stopped the render (usually a missing package or a code bug
  in that file's chunk). Fix the file, or install the missing package in
  the workflow's dependency-install steps if it's legitimately needed by
  every render.
- **"Check internal links, images and basic accessibility" prints
  errors** -> each line under `ERRORS (...)` names the file, line number,
  and the exact broken reference (e.g.
  `personal-projects.html:42: [broken image] img -> 'images/foo.png' ...
  does not exist`). Fix the source `.qmd`/asset and re-render.
- **Warnings** (missing `alt` text, multiple `<title>` tags) are printed
  but do not fail the build - treat them as a backlog, not a blocker.

## Known gaps / things this does NOT cover

- **External links** are not checked automatically (see above) - do an
  occasional manual pass, or wire up `lychee`/`lycheeverse/lychee-action`
  in a separate, non-blocking, scheduled workflow if broken external
  links become a recurring problem.
- **A handful of `.qmd` pages use packages that can't run headless in
  CI**: `INFO_MINI_PROJETS/assistant_virtuel.qmd` uses
  `speech_recognition`/`pyttsx3` (needs a microphone/audio device and a
  system TTS engine), `pywhatkit` (drives a real browser/WhatsApp Web),
  and `wolframalpha` (needs a paid API key) - these are not installed in
  `qa-checks.yml` on purpose, so this page's render step may legitimately
  fail in CI even though it renders fine on a developer machine with those
  services configured. Similarly, `INFO_MINI_PROJETS/brain-tumor-classification-effcientnet.qmd`
  references `tensorflow`, which is not installed in CI to keep the
  workflow fast.
- **The real, sustainable fix for all of the above** is Quarto's
  [freeze](https://quarto.org/docs/projects/code-execution.html#freeze)
  feature: set `execute: freeze: auto` in `_quarto.yml`, commit the
  resulting `_freeze/` directory (instead of the current
  `/.quarto/` gitignore rule, which throws the cache away), and CI never
  needs to re-execute any R/Python chunk at all - it just reuses the
  committed computational output and reports a real error only when the
  document/template itself is broken. This is naturally part of the
  publishing-workflow rework already in progress elsewhere in this repo
  (auto-discovering listings + a render/deploy GitHub Actions pipeline),
  so it isn't changed here to avoid stepping on that work - but whoever
  finishes that pipeline should turn freeze on, at which point
  `qa-checks.yml` will automatically get fast and fully green.
- This is a lightweight, dependency-free checker, not a full axe-core
  accessibility audit. It catches structural basics (title, lang, alt,
  truncation) but not color contrast, ARIA correctness, keyboard
  navigation, etc.
