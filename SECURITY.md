# Security Review — djamal_website

Static Quarto site, rendered to `docs/`, deployed on GitHub Pages. No backend,
no database, no authentication, no forms. Reviewed the full repository (not
just `docs/`). Findings are ranked by severity. Items marked **[FIXED]** were
corrected directly in this worktree; everything else needs a decision or
action from the repo owner.

Two remotes exist: `origin` (`github.com/djamal2905/djamal_website`) and
`new-origin` (`github.com/Djamal029/djamal_website`) — the compromised key
below must be treated as leaked to anyone who could ever read either repo.

---

## 1. CRITICAL — Leaked SSH private key in git history (ACTION REQUIRED NOW)

**This is the most important item in this report. Read this section even if
you read nothing else.**

A file named `ssh_files` was committed to this repository containing a real
OpenSSH private key (`-----BEGIN OPENSSH PRIVATE KEY-----`, bcrypt-KDF
protected — protected by a passphrase, not "encrypted" in a way that makes it
safe to leave public), together with its public half `ssh_files.pub`. This
was pushed to a public/shared GitHub remote, so **the private key must be
considered fully compromised**, independent of whether the passphrase is
strong.

Verified state:

- Working tree (this worktree, HEAD): `git ls-files | grep -i ssh` →
  no results. The real key content is not present in any file you'd see by
  browsing the repo today.
- History: `git log --all --diff-filter=A --oneline -- ssh_files ssh_files.pub`
  → shows the commit that introduced it (`d73b219 update gen` on the shared
  history; on `main` the key blob itself lives further back and was only
  content-scrubbed / untracked in later commits). **The key material is
  still retrievable from git history on the remote(s)** by anyone who clones
  the repo and runs `git log -p` or checks out the old commit — removing a
  file in a new commit does not delete it from history.
- **This specific worktree branch** (`worktree-agent-aa8cbb7b95b821816`) had
  *not* actually completed the fix that was believed to already be in place:
  `ssh_files`/`ssh_files.pub` were still git-tracked here, just with their
  content overwritten by placeholder text ("PLOKO PLAKA BEURRE - MODIA") in
  an earlier commit (`247208c`) on this branch's own history line — the
  `.gitignore` secret patterns from `main` were also missing here. **[FIXED
  in this worktree]**: ran `git rm --cached ssh_files ssh_files.pub` and
  added `ssh_files`, `ssh_files.pub`, `*.pem`, `*.key`, `id_rsa*`,
  `id_ed25519*`, `.env`, `.env.*` to `.gitignore` (see §8 for why this
  matters: this branch and `main` have diverged and are not simple
  fast-forwards of each other — whoever merges/reconciles them needs to keep
  both fixes).
- Per the explicit instruction from the repo owner, **no `git filter-repo` /
  BFG history rewrite was performed** and none should be attempted without
  the owner personally supervising it (it rewrites commit hashes on every
  branch and requires a force-push + everyone re-cloning).

### What you must do, in this order, right now:

1. **Identify every place this key is authorized** — check `~/.ssh/`,
   `authorized_keys` on any server it grants access to, GitHub account SSH
   keys, GitHub deploy keys on this or any other repo, and any hosting
   provider (VPS, cloud, CI) that trusts it.
2. **Revoke/remove it everywhere** you find it authorized.
3. **Generate a brand-new key pair** (`ssh-keygen -t ed25519`) and
   re-authorize the new public key in place of the old one.
4. Only after that: decide, with the repo owner, whether to still rewrite git
   history (BFG/`git filter-repo` + force-push + all collaborators re-clone)
   to scrub the blob from history for hygiene. This is optional once the key
   is revoked (a revoked key in history is no longer a live credential, just
   clutter), but it is the only way to actually remove the bytes from the
   repo.

**Until step 1–3 are done, assume anyone who has ever cloned or could clone
this repository has this key.**

---

## 2. HIGH — Repository hygiene / accidental content exposure

### 2a. `Djamal T.rar` (~9.9 MB, repo root) — not a secret leak, but review before keeping public

Listed its contents without extracting (`7z l`): a course project archive
("Presentation-restaurant") — a `.qmd`/`.rmarkdown` report, two PNGs, and 7
`.mp4` demo/recording videos. Not encrypted, no filenames suggesting
credentials or personal documents. This looks like an ordinary project
backup, not a secret leak — **but it does not belong in a git repository**:
it bloats every future clone by ~10 MB forever (git never shrinks
automatically), and its actual necessity/sensitivity for a *public* repo is
something only the owner can judge (are the videos/report meant to be
public? do the videos show anyone's face/voice from the group project who
didn't consent to being on a public GitHub page?).
**Not deleted — left for the owner to decide.** If it's not meant to be
public, it should be removed and (optionally, later) purged from history
the same way as the SSH key.

### 2b. Orphaned build artifacts tracked in git, not part of the deployed site

Found and left for the owner (not deleted, since they're not the SSH-key
class of unambiguous fix):

- Root-level `site_libs/` — a full duplicate copy of the Quarto library
  bundle (bootstrap, popper, video.js, etc.) sitting at the repo root. The
  site's actual `output-dir` is `docs/`, so this copy is not the deployed
  one. It is a leftover from rendering some page outside the project
  context.
- `pub.html`, `pub.qmd`, `pub.yml`, `pub-listing.json` (repo root) — a
  rendered listing page and its inputs, **not referenced anywhere** in
  `_quarto.yml`'s render list or in any navbar/link (confirmed via
  `git grep` across all `.qmd`/`.yml`). Appears to be an abandoned/earlier
  version of the "Publications" listing (compare with the current, linked
  `publications.qmd`).
- These are harmless from a pure-secrecy standpoint but are dead weight and
  can confuse future maintenance (e.g. someone editing `pub.yml` thinking it
  affects the live site, when it doesn't).

**[FIXED]** `quarto-render.log` (a local build log, 33 KB, containing local
Windows file paths like `C:\Users\Djamal TOE\...`) was tracked in git. It's
a pure build byproduct with no reason to ever be committed — untracked it
(`git rm --cached`) and added `quarto-render.log` to `.gitignore`.

---

## 3. MEDIUM — Outdated bundled third-party JS/CSS

Checked what's actually bundled in `docs/site_libs/` right now (this repo's
current render, produced by the installed **Quarto CLI 1.9.36**):

| Library | Version found | Notes |
|---|---|---|
| Bootstrap | **5.3.1** | Current-generation Bootstrap 5; no known critical CVEs at this version. Good. |
| @popperjs/core | 2.11.7 | Current, no known critical CVEs. |
| tippy.js | bundled UMD, paired with popper 2.11.7 | Fine. |
| Fuse.js (search) | 6.6.2 | Fine. |
| Algolia autocomplete-js | 1.19.1 | Fine. |
| clipboard.js | 2.0.11 | Fine. |
| video.js (quarto-contrib, used by several project pages with embedded `<video>`) | **7.20.2** | This is an older video.js 7.x release; video.js is currently on an 8.x major line. Recommend checking `https://github.com/videojs/video.js/security/advisories` for anything affecting 7.20.x before relying on it further, and upgrading via a newer Quarto CLI release (Quarto vendors this itself — see below) rather than hand-patching the vendored file. |

**Important correction to the assumed scope**: the task brief mentioned
`jquery-3.5.1`, `plotly ~2.11.1/4.10.4`, and `crosstalk-1.2.1` as currently
bundled. A full search of the working tree (`git grep` / filename and
content search across all of `docs/` and the source tree) found **no
jquery, plotly, or crosstalk files anywhere in this repo as it stands now**
— only the libraries in the table above. Either an earlier render/version of
the site had them and a since-updated Quarto/renderer dropped them, or a
different snapshot was being described. Documenting what's actually present
rather than assuming stale information.

**Recommendation (can't be hand-patched safely):** these bundled files are
generated by Quarto/pandoc's internal resource bundling, not manually
vendored — hand-editing them would just get overwritten on the next
`quarto render` and risks subtly breaking the site (e.g. mismatched
JS/CSS versions). The correct fix path is:
- Keep Quarto CLI itself up to date (`quarto --version`; check
  `https://github.com/quarto-dev/quarto-cli/releases` — currently on 1.9.36
  here) — each Quarto release bumps its vendored JS libraries.
- If/when any `.qmd` starts using DT tables, plotly widgets, or leaflet
  (none currently do, based on this scan), re-render with the latest Quarto
  and check `docs/site_libs/` again — those libraries are pulled in by the R
  htmlwidgets/DT/plotly packages, so upgrading `install.packages("DT")` /
  `install.packages("plotly")` etc. in R before rendering is what actually
  bumps their versions, not editing generated output.

---

## 4. MEDIUM → LOW after fix — Static site security headers (via `<meta>`)

GitHub Pages does not let you set custom HTTP response headers without a
proxy (e.g. Cloudflare), which is explicitly out of scope here (no
third-party services). The only lever available on pure GitHub Pages is
`<meta>` tags in the HTML `<head>`, which have real limits:

- `Content-Security-Policy` **does** work via
  `<meta http-equiv="Content-Security-Policy">`.
- `Referrer-Policy` **does** work via `<meta name="referrer">`.
- `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`,
  and CSP's own `frame-ancestors`/`report-to` directives **do NOT work via
  `<meta>`** — browsers only honor these from real HTTP headers, so no
  clickjacking (`X-Frame-Options`/`frame-ancestors`) protection is
  achievable on plain GitHub Pages without a proxy. Documenting this rather
  than shipping a `frame-ancestors` directive that would silently do
  nothing.

**[FIXED]** Added to `meta/logo-schema.html` (the file every page already
includes via `_quarto.yml`'s `format.html.include-in-header`):

```html
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://www.google-analytics.com https://www.googletagmanager.com; connect-src 'self' https://www.google-analytics.com https://www.googletagmanager.com https://*.google-analytics.com https://*.analytics.google.com; font-src 'self' data:; object-src 'none'; base-uri 'self'; form-action 'self';">
```

Why this exact policy:
- `default-src 'self'` — nothing loads from anywhere else unless explicitly
  allowed below.
- `script-src`/`connect-src`/`img-src` allow `googletagmanager.com` and
  `google-analytics.com` — the only third-party network calls this site
  makes (Google Analytics `gtag.js`, configured in `_quarto.yml` with
  `anonymize-ip: true`). The GA4 tracking ID `G-KPNBXZFEP3` in `_quarto.yml`
  is a public client-side identifier by design, not a secret — correctly not
  flagged as one.
- `'unsafe-inline'` is required for both `script-src` and `style-src`
  because every page template uses inline `<script>` blocks (mobile-menu
  toggle logic) and inline `style="..."` attributes extensively (verified via
  `git grep 'style="' -- '*.qmd'`, hits in ~15 files). A nonce/hash-based CSP
  isn't practical for a static site with no build-time CSP tooling — a
  static nonce embedded in the HTML gives no protection since the "secret"
  nonce is sitting right there in the page source. `'unsafe-inline'` is the
  honest, working trade-off here.
- `object-src 'none'` — no `<embed>`/`<object>` tags exist anywhere in the
  site (checked); the one PDF (`RapportGroupe21.pdf`) is a plain download
  link, not embedded.
- No `<iframe>` usage anywhere in the site (checked), so there was nothing to
  add a `frame-src` allowance for.
- **Caveat**: on the actual home/content pages, Quarto injects the Google
  Analytics `<script src="https://www.googletagmanager.com/...">` tag
  *earlier* in `<head>` than the `include-in-header` content (verified:
  line 74 vs line 83+ in a rendered page). A `<meta>`-based CSP only takes
  effect from the point it's parsed onward, so it does not retroactively
  gate that specific, intentional GA script tag — this is a structural
  limitation of Quarto's header-injection order for this site, not a gap you
  can close without moving GA loading yourself (e.g. loading gtag from
  inside `meta/logo-schema.html` instead of via `_quarto.yml`'s
  `google-analytics` option) or dropping to a real HTTP header via a proxy.
  Everything else on the page (any later resource, any injected node) is
  still governed by the policy.

Applied to **25 of 34** rendered pages in `docs/` — every page that shares
the common site template (i.e. every page using
`format.html.include-in-header`). The other 9:
- 8 are `project-shell.html`/`project-shell-end.html` files — these are HTML
  *fragments* (no `<html>`/`<head>` at all), not standalone documents; a
  `<meta>` tag has nowhere valid to go in them.
- `docs/projet-traitement-donnees/report_writing/Presentation/presentation-ptd.html`
  is a `revealjs`-format presentation (its own head, not the shared `html`
  format's `include-in-header`) — patched directly in the rendered output
  with an equivalent (slightly stricter, no GA) policy, but **the source**
  (`.../Presentation/presentation-ptd.qmd`) was intentionally left
  unmodified: adding `include-in-header` to its `format.revealjs` block
  would need a full re-render to verify (this presentation pulls in
  `bibliography:` + R chunks), and re-rendering group-project computational
  notebooks was judged too risky to do blind in this pass (see §9,
  "Rendering approach and a near-miss"). **Recommendation for the owner**:
  add
  `include-in-header: ../../../../meta/logo-schema.html` (verify the
  relative path — this file is 4 directories deep from repo root) under that
  page's `format: revealjs:` block, then re-render just that one file with
  `quarto render "projet-traitement-donnees/report_writing/Presentation/presentation-ptd.qmd"`
  and check the slides still work.

**Verification**: ran `quarto render` (Quarto CLI 1.9.36) on every
lightweight page individually (`index.qmd`, `contact.qmd`, `about.qmd`,
`skills.qmd`, `education.qmd`, `experience.qmd`, `blog.qmd`,
`academic-projects.qmd`, `personal-projects.qmd`, `publications.qmd`) and
confirmed each produced a clean, minimal diff (exactly the two new meta
lines, nothing else changed) before applying the same two lines to the
remaining already-rendered heavy/computational pages directly (see §9 for
why those weren't re-executed).

---

## 5. LOW — External links and resources

- **No `http://` (non-HTTPS) script/link/img sources** anywhere in `.qmd`
  sources or rendered `docs/*.html` — checked with a repo-wide `git grep`.
- **`target="_blank"` links**: all 4 occurrences across the site
  (`about.qmd` ×2, `academic-projects.qmd` ×2) already carry `rel="noopener"`
  or `rel="noopener noreferrer"`. No fix needed.
- **No third-party CDN `<script src>` tags** anywhere in the site other than
  Google's own `googletagmanager.com/gtag/js` (which Google does not serve
  with a stable hash suitable for Subresource Integrity — SRI is not
  practically applicable to GA's loader script, and this is standard/expected
  for GA across the web). No self-hosted CDN scripts lack SRI because there
  are none — everything else is same-origin (`site_libs/`).
- **No `<iframe>` embeds** anywhere in the site.

---

## 6. LOW — `robots.txt` / `sitemap.xml`

Both reviewed — no issues:

```
User-agent: *
Disallow:

Sitemap: https://djamal2905.github.io/djamal_website/sitemap.xml
```

`robots.txt` allows all crawling (fine for a portfolio site meant to be
found) and does not `Disallow:` any path that would hint at hidden
admin/config areas (there are none — this is a fully static site with no
admin surface). `sitemap.xml` lists only genuine public content pages
(project write-ups, presentations, formations) — nothing sensitive.

---

## 7. LOW / informational — Custom JavaScript and scripts

- Every inline `<script>` block across the `.qmd` files (`about.qmd`,
  `academic-projects.qmd`, `blog.qmd`, `contact.qmd`, `education.qmd`,
  `experience.qmd`, `index.qmd`, `personal-projects.qmd`, `skills.qmd`) is
  the same small, identical mobile-nav-drawer toggle: pure DOM API calls
  (`classList.toggle`, `getElementById`, `addEventListener`), no
  `innerHTML`/`document.write`/`eval` with any dynamic or user-controlled
  string. No injection risk — there is no user input anywhere on this site
  to inject in the first place (no forms, no comments, no query-string
  reflection).
- `test.py` (repo root) is a leftover scratch file containing
  `git filter-repo` blob-callback snippets (for pruning large blobs from
  history) — not part of the site, not executed by anything, not a security
  issue. Purely dev scratch; flagged here only as clutter.
- `commandes.R` (repo root) is a 4-line note of `git` shell commands (how
  the repo was first pushed) written as plain text in an `.R` file — not
  actually R code that runs, and not a security issue.

---

## 8. Branch/history note relevant to this review

This worktree's branch (`worktree-agent-aa8cbb7b95b821816`) diverged from
`main` well before `main`'s own SSH-key remediation commits
(`34783be`, `9c61c17`). It has 9 commits of its own that `main` doesn't have,
including an independent (and, until this review, incomplete) attempt at the
same SSH-key fix. **Whoever reconciles these branches needs to merge, not
silently overwrite, both fixes** — check for `ssh_files`/`ssh_files.pub`
still being untracked and `.gitignore` still containing the secret patterns
after any merge/rebase between this branch and `main`.

---

## 9. Rendering approach and a near-miss (documented for transparency)

A first attempt to verify the header change with a full-project
`quarto render` was killed after ~10 minutes (many pages here execute real
R/Python ML notebooks — CNN training, gradient descent demos, etc. — which
is slow and, more importantly, not safely re-runnable blind: package
versions, random seeds, and local environments can change output). A second,
mistaken attempt to render several `.qmd` files in one `quarto render`
invocation caused `pandoc` to merge unrelated pages' content together
(`docs/contact.html` briefly ended up containing `docs/publications.html`'s
title/content). **This was caught and fully reverted** (`git checkout --`)
before anything was committed — it never reached git history. The final
approach taken: render each lightweight page **individually** (one
`quarto render <file>.qmd` call per page) to prove the header change
produces a clean diff, then apply the identical, verified 2-line change
directly to the remaining already-committed, heavy/computational
`docs/*.html` files via text patch (no code re-execution, so no risk of
silently changing model outputs/figures). Net result: the working tree now
contains only the intended, minimal diffs (see `git diff --stat`), and
nothing from the failed attempts was ever committed.

---

## 10. GitHub repo hygiene — action items for the owner (cannot be done from here)

No `gh` CLI/API access was available in this environment to check or change
repository settings. Recommended checklist:

- [ ] **Enable secret scanning + push protection** (Settings → Code security
      → Secret scanning). This would have caught the `ssh_files` commit
      before it was ever pushed.
- [ ] **Enable Dependabot alerts** (Settings → Code security → Dependabot) —
      low-value for a Quarto-generated static site with no `package.json`,
      but harmless to turn on, and useful if any tooling config
      (e.g. GitHub Actions) is added later.
- [ ] **Branch protection on `main`** (require PR review before merge, or at
      minimum prevent force-pushes) — especially relevant given this repo
      already has multiple diverged branches/worktrees in play.
- [ ] **Revisit deploy keys / SSH keys authorized on the GitHub account(s)**
      as part of the §1 key rotation — while there, check for any other
      forgotten keys.
- [ ] Decide on **`Djamal T.rar`** and the orphaned `pub.*`/root
      `site_libs/` artifacts (§2) — keep, remove, or (for the `.rar`) move
      to private storage.
- [ ] Decide whether a full **history rewrite** (BFG/`git filter-repo`) is
      wanted later, after the key is rotated (§1, step 4) — optional, and
      requires the owner's direct involvement since it force-pushes and
      requires every clone to be redone.

---

## Executive summary

**Top 3 issues, by severity:**

1. **CRITICAL — Leaked SSH private key, still in git history on the
   remote(s).** The key is gone from the current working tree but fully
   recoverable from history by anyone who has ever had repo access. This is
   a live credential-compromise incident, not a hypothetical: **revoke and
   regenerate the key everywhere it's authorized immediately** — this is
   outside what any code fix can address.
2. **HIGH — Incomplete remediation on this specific branch** discovered
   during verification: this worktree's branch still had `ssh_files`/
   `ssh_files.pub` tracked (with joke placeholder content) and lacked the
   `.gitignore` secret patterns present on `main`. Fixed here
   (`git rm --cached` + `.gitignore`), but flags that this repo currently
   has multiple diverged branches that each need to carry the fix — merging
   them naively could reintroduce the tracked files.
3. **HIGH (repo hygiene) — `Djamal T.rar`** (~10 MB backup archive, contents
   inspected and look benign but undetermined intent for public visibility)
   and several **orphaned build artifacts** (root `site_libs/`, unlinked
   `pub.html`/`pub.qmd`/`pub.yml`/`pub-listing.json`) tracked in git for no
   functional reason — left for the owner to decide on removal, since intent
   couldn't be verified from here.

Everything else found (outdated-but-not-critical bundled JS, missing
`<meta>` security headers, `target="_blank"` audit, `robots.txt`/
`sitemap.xml`, custom JS injection risk) was either already fine or fixed
directly in this pass.

**Files touched in this worktree:**

- `SECURITY.md` (new — this report)
- `.gitignore` (added SSH/secret patterns + `quarto-render.log`)
- `meta/logo-schema.html` (added `Referrer-Policy`/CSP `<meta>` tags — the
  source of truth for the shared site header)
- `docs/*.html` — 25 pages patched with the same two `<meta>` lines
  (`about.html`, `academic-projects.html`, `blog.html`, `contact.html`,
  `education.html`, `experience.html`, `index.html`, `personal-projects.html`,
  `publications.html`, `skills.html`, `ANALYSES_FACTORIELLES/acp-kmeans.html`,
  `FORMATIONS/SIG.html`, `FORMATIONS/logistic_regression_diabetes.html`,
  `FORMATIONS/machine-learning/gradient-descent-linear-reg.html`,
  `FORMATIONS/presentations.html`,
  `INFO_MINI_PROJETS/JavaApp/desktop-app-java-mysql.html`,
  `INFO_MINI_PROJETS/anomaly-detection-in-transactions-GMM.html`,
  `INFO_MINI_PROJETS/assistant_virtuel.html`,
  `INFO_MINI_PROJETS/brain-tumor-classification-effcientnet.html`,
  `INFO_MINI_PROJETS/classi_bin_acp_kmeans_knn_logit/Breast-Tumor-Article.html`,
  `INFO_MINI_PROJETS/classi_bin_acp_kmeans_knn_logit/work.html`,
  `INFO_MINI_PROJETS/classification_binaire_svm.html`,
  `INFO_MINI_PROJETS/shifumi-cnn-yolov8.html`,
  `publications/stat_ml/index.html`, `publications/visualisation/index.html`)
  plus `projet-traitement-donnees/report_writing/Presentation/presentation-ptd.html`
  (equivalent CSP without the GA allowance, since that page doesn't load GA)
- `ssh_files`, `ssh_files.pub` (untracked via `git rm --cached`; files remain
  on local disk but are now git-ignored)
- `quarto-render.log` (untracked via `git rm --cached`, now git-ignored)

**Not touched, left for the owner:** `Djamal T.rar`, root `site_libs/`,
`pub.html`/`pub.qmd`/`pub.yml`/`pub-listing.json`, `test.py`, `commandes.R`.

**This worktree's branch:** `worktree-agent-aa8cbb7b95b821816`

No push, no merge into `main`, and no git history rewrite were performed, per
the constraints given.
