#!/usr/bin/env python3
"""
check_site.py - Lightweight, dependency-free QA checker for the rendered
Quarto static site (docs/ by default).

What it checks (all purely local/offline - no network calls, no third-party
services, safe to run in GitHub Actions on every push):

  1. Internal links: every <a href="...">, <link href="...">, and
     <script src="..."> that points at another file inside the rendered
     site must resolve to a file that actually exists (directory-style
     links are resolved against index.html). Fragment identifiers
     (#some-id) are checked against the actual ids present in the target
     page.
  2. Internal images: every <img src="...">, every URL in an <img
     srcset="...">, and every url(...) reference inside <style> blocks,
     style="" attributes, and *.css files (background-image and friends)
     must point at a file that exists.
  3. Basic accessibility / HTML sanity:
       - exactly one non-empty <title> per page (0 = error, >1 = warning)
       - <html lang="..."> is present (missing = error)
       - every <img> has a non-empty alt attribute (missing = warning)
       - the document is not obviously truncated (missing closing
         </html>, which usually means the render crashed midway)

External links (http://, https://, mailto:, tel:, etc.) are intentionally
NOT checked here - they require network access and are a separate concern
better handled by a dedicated tool (e.g. lychee) run occasionally, not on
every push, to avoid flaky CI caused by third-party sites rate-limiting or
going down temporarily.

Usage:
    python scripts/check_site.py [--root docs] [--strict]

Exit code is non-zero if any ERROR-level issue is found. Warnings are
always printed but do not affect the exit code unless --strict is given.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.parse
from dataclasses import dataclass, field
from html.parser import HTMLParser

# Attributes that may contain a single URL to a local resource.
URL_ATTRS = {
    ("a", "href"),
    ("link", "href"),
    ("script", "src"),
    ("img", "src"),
    ("source", "src"),
    ("iframe", "src"),
}

VOID_ISH_SKIP_SCHEMES = (
    "http://", "https://", "//", "mailto:", "tel:", "javascript:",
    "data:", "irc:", "skype:", "sms:", "about:",
)


@dataclass
class PageInfo:
    path: str  # absolute filesystem path
    rel: str  # path relative to site root, forward slashes
    ids: set = field(default_factory=set)
    titles: list = field(default_factory=list)
    html_lang: str | None = None
    has_html_tag: bool = False
    has_doctype: bool = False
    img_missing_alt: int = 0
    truncated: bool = False
    links: list = field(default_factory=list)  # (kind, url, line)

    @property
    def is_full_document(self) -> bool:
        """True if this looks like a standalone HTML page (has <html> or a
        doctype). Some pages on this site are built from raw HTML *include
        fragments* (e.g. a shared sidebar snippet spliced into a page via a
        Quarto include) that are never meant to be complete documents on
        their own - those should not be flagged for a missing <title>/lang
        or treated as "truncated"."""
        return self.has_html_tag or self.has_doctype


class SiteHTMLParser(HTMLParser):
    """Single-pass parser that collects ids, title/lang info, image alt
    coverage, and every URL-bearing attribute worth checking."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.titles: list[str] = []
        self.html_lang: str | None = None
        self.has_html_tag = False
        self.img_missing_alt = 0
        self.links: list[tuple[str, str, int]] = []
        self._in_title = False
        self._title_buf = ""
        self._style_bufs: list[str] = []
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        self._handle_tag(tag, attrs, self_closing=False)

    def handle_startendtag(self, tag, attrs):
        self._handle_tag(tag, attrs, self_closing=True)

    def _handle_tag(self, tag, attrs, self_closing):
        attrd = dict(attrs)
        line = self.getpos()[0]

        if tag == "html":
            self.has_html_tag = True
            if "lang" in attrd and attrd["lang"]:
                self.html_lang = attrd["lang"]

        if "id" in attrd and attrd["id"]:
            self.ids.add(attrd["id"])
        if tag == "a" and attrd.get("name"):
            self.ids.add(attrd["name"])

        if tag == "title":
            self._in_title = True
            self._title_buf = ""

        if tag == "style":
            self._in_style = True

        if tag == "img":
            src = attrd.get("src")
            if src:
                self.links.append(("img", src, line))
            srcset = attrd.get("srcset")
            if srcset:
                for candidate in srcset.split(","):
                    url = candidate.strip().split(" ")[0].strip()
                    if url:
                        self.links.append(("img-srcset", url, line))
            alt = attrd.get("alt")
            if alt is None or alt.strip() == "":
                self.img_missing_alt += 1

        key = (tag, "href")
        if key in URL_ATTRS and "href" in attrd and attrd["href"]:
            kind = "css" if tag == "link" and attrd.get("rel") == "stylesheet" else "link"
            self.links.append((kind, attrd["href"], line))

        key = (tag, "src")
        if key in URL_ATTRS and "src" in attrd and attrd["src"] and tag != "img":
            self.links.append(("resource", attrd["src"], line))

        style = attrd.get("style")
        if style and "url(" in style:
            for url in extract_css_urls(style):
                self.links.append(("css-url", url, line))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
            if self._title_buf.strip():
                self.titles.append(self._title_buf.strip())
        if tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_title:
            self._title_buf += data
        if self._in_style:
            for url in extract_css_urls(data):
                self.links.append(("css-url", url, self.getpos()[0]))


def extract_css_urls(css_text: str) -> list[str]:
    urls = []
    idx = 0
    while True:
        i = css_text.find("url(", idx)
        if i == -1:
            break
        j = css_text.find(")", i)
        if j == -1:
            break
        raw = css_text[i + 4:j].strip().strip("'\"")
        if raw and not raw.startswith("data:"):
            urls.append(raw)
        idx = j + 1
    return urls


def is_external(url: str) -> bool:
    return url.startswith(VOID_ISH_SKIP_SCHEMES)


def strip_query_and_fragment(url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlsplit(url)
    fragment = parsed.fragment
    cleaned = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
    return cleaned, fragment


def resolve_targets(root: str, referencing_file: str, url: str) -> list[str]:
    """Resolve a (non-external) URL referenced from referencing_file into
    one or more candidate absolute filesystem paths within root. Returns
    an empty list if the URL can't be represented as a local file at all
    (e.g. it's an empty string after stripping, i.e. a pure "#fragment").

    Root-relative URLs (starting with "/") get two candidates: the literal
    path under `root`, and - because this site deploys to a GitHub Pages
    *project* page (https://user.github.io/repo-name/, not the domain
    root) - the same path with a leading "/repo-name" segment stripped,
    since authors sometimes write root-relative links assuming the repo
    name isn't part of the path, or vice versa.
    """
    cleaned, _fragment = strip_query_and_fragment(url)
    cleaned = urllib.parse.unquote(cleaned)
    if cleaned == "":
        return []  # pure "#fragment" link, handled separately
    if cleaned.startswith("/"):
        cleaned = cleaned.lstrip("/")
        candidates = [os.path.normpath(os.path.join(root, cleaned))]
        parts = cleaned.split("/", 1)
        if len(parts) == 2:
            candidates.append(os.path.normpath(os.path.join(root, parts[1])))
        return candidates
    base_dir = os.path.dirname(referencing_file)
    return [os.path.normpath(os.path.join(base_dir, cleaned))]


def find_existing(target: str) -> tuple[bool, str]:
    """Return (exists, resolved_path). Handles directory-style targets by
    looking for index.html inside."""
    if os.path.isfile(target):
        return True, target
    if os.path.isdir(target):
        idx = os.path.join(target, "index.html")
        if os.path.isfile(idx):
            return True, idx
        return False, target
    return False, target


def collect_html_files(root: str) -> list[str]:
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".html"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def collect_css_files(root: str) -> list[str]:
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".css"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default="docs", help="Rendered site directory to check (default: docs)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors (non-zero exit)")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"ERROR: root directory '{root}' does not exist. Did you run `quarto render`?")
        return 2

    html_files = collect_html_files(root)
    css_files = collect_css_files(root)
    if not html_files:
        print(f"ERROR: no .html files found under '{root}'.")
        return 2

    pages: dict[str, PageInfo] = {}

    for path in html_files:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            print(f"ERROR: could not read {rel}: {e}")
            continue

        p = SiteHTMLParser()
        p.feed(text)
        lower_text = text.lower()
        info = PageInfo(
            path=path,
            rel=rel,
            ids=p.ids,
            titles=p.titles,
            html_lang=p.html_lang,
            has_html_tag=p.has_html_tag,
            has_doctype="<!doctype" in lower_text,
            img_missing_alt=p.img_missing_alt,
            truncated="</html>" not in lower_text,
            links=p.links,
        )
        pages[path] = info

    # --- also scan bare .css files for url() references ---
    css_link_issues: list[str] = []
    css_urls: dict[str, list[tuple[str, int]]] = {}
    for css_path in css_files:
        try:
            with open(css_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            css_link_issues.append(f"could not read {css_path}: {e}")
            continue
        urls = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            for url in extract_css_urls(line):
                urls.append((url, lineno))
        css_urls[css_path] = urls

    errors: list[str] = []
    warnings: list[str] = []

    # --- accessibility / sanity checks ---
    # Skip title/lang/truncation checks for files that are clearly raw HTML
    # *include fragments* (no <html>/doctype at all) rather than standalone
    # pages - e.g. shared sidebar snippets spliced into other pages. Link
    # and image checks still apply to every file regardless.
    for info in pages.values():
        if not info.is_full_document:
            if info.img_missing_alt:
                warnings.append(f"{info.rel}: {info.img_missing_alt} <img> tag(s) missing alt text")
            continue

        if not info.has_html_tag:
            errors.append(f"{info.rel}: no <html> tag found (malformed document)")
        elif not info.html_lang:
            errors.append(f"{info.rel}: <html> tag is missing a lang attribute")

        if len(info.titles) == 0:
            errors.append(f"{info.rel}: missing <title>")
        elif len(info.titles) > 1:
            warnings.append(f"{info.rel}: {len(info.titles)} <title> tags found (expected exactly 1)")

        if info.img_missing_alt:
            warnings.append(f"{info.rel}: {info.img_missing_alt} <img> tag(s) missing alt text")

        if info.truncated:
            errors.append(f"{info.rel}: document has no closing </html> - looks truncated/corrupted")

    # --- link / image / resource checks ---
    broken_links: list[str] = []
    broken_images: list[str] = []
    broken_resources: list[str] = []
    broken_anchors: list[str] = []

    kind_bucket = {
        "link": broken_links,
        "img": broken_images,
        "img-srcset": broken_images,
        "css": broken_resources,
        "css-url": broken_images,
        "resource": broken_resources,
    }

    for info in pages.values():
        for kind, url, line in info.links:
            if is_external(url):
                continue
            if url.startswith("#"):
                frag = url[1:]
                # reveal.js (Quarto's `revealjs` presentation format) uses
                # client-side routes like "#/introduction" or "#/2" to
                # address slides - these are not DOM ids and will never
                # match an id= attribute, so they'd be a permanent false
                # positive here.
                if frag and not frag.startswith("/") and frag not in info.ids:
                    broken_anchors.append(f"{info.rel}:{line}: anchor '#{frag}' has no matching id on this page")
                continue

            candidates = resolve_targets(root, info.path, url)
            if not candidates:
                continue

            exists = False
            resolved = candidates[0]
            for candidate in candidates:
                exists, resolved = find_existing(candidate)
                if exists:
                    break

            bucket = kind_bucket.get(kind, broken_links)
            if not exists:
                rel_resolved = os.path.relpath(resolved, root).replace(os.sep, "/")
                bucket.append(f"{info.rel}:{line}: {kind} -> '{url}' (resolved to docs/{rel_resolved}) does not exist")
                continue

            # fragment check against the *target* page's ids, when we can parse it
            _cleaned, fragment = strip_query_and_fragment(url)
            if fragment and not fragment.startswith("/") and resolved in pages:
                target_ids = pages[resolved].ids
                if fragment not in target_ids:
                    broken_anchors.append(
                        f"{info.rel}:{line}: {kind} -> '{url}' target exists but has no id='{fragment}'"
                    )

    for css_path, urls in css_urls.items():
        rel_css = os.path.relpath(css_path, root).replace(os.sep, "/")
        for url, line in urls:
            if is_external(url):
                continue
            candidates = resolve_targets(root, css_path, url)
            if not candidates:
                continue
            exists = False
            resolved = candidates[0]
            for candidate in candidates:
                exists, resolved = find_existing(candidate)
                if exists:
                    break
            if not exists:
                rel_resolved = os.path.relpath(resolved, root).replace(os.sep, "/")
                broken_images.append(f"{rel_css}:{line}: css url() -> '{url}' (resolved to docs/{rel_resolved}) does not exist")

    errors.extend(f"[broken link] {m}" for m in broken_links)
    errors.extend(f"[broken image] {m}" for m in broken_images)
    errors.extend(f"[broken resource] {m}" for m in broken_resources)
    errors.extend(f"[broken anchor] {m}" for m in broken_anchors)
    errors.extend(f"[css] {m}" for m in css_link_issues)

    # --- report ---
    print(f"Checked {len(html_files)} HTML file(s) and {len(css_files)} CSS file(s) under '{root}'.\n")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in sorted(errors):
            print(f"  - {e}")
        print()
    else:
        print("No errors found.\n")

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in sorted(warnings):
            print(f"  - {w}")
        print()

    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s).")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
