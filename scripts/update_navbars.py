"""
Update all navbars in .qmd files and project-shell.html files:
- Remove Contact link
- Add Blog link before About
"""
import os, re

BASE = r"E:\ENSAI\djamal_site"

QMD_FILES = [
    "index.qmd",
    "experience.qmd",
    "academic-projects.qmd",
    "personal-projects.qmd",
    "skills.qmd",
    "education.qmd",
    "about.qmd",
    "contact.qmd",
]

SHELL_FILES = [
    r"INFO_MINI_PROJETS\project-shell.html",
    r"INFO_MINI_PROJETS\JavaApp\project-shell.html",
]

def update_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # ── Desktop nav replacements (qmd files use .qmd hrefs) ──────────────
    # Case 1: contact is active
    content = content.replace(
        '<a href="about.qmd">About</a><a class="active" href="contact.qmd">Contact</a>',
        '<a href="blog.qmd">Blog</a><a href="about.qmd">About</a>'
    )
    # Case 2: about is active
    content = content.replace(
        '<a class="active" href="about.qmd">About</a><a href="contact.qmd">Contact</a>',
        '<a href="blog.qmd">Blog</a><a class="active" href="about.qmd">About</a>'
    )
    # Case 3: neither active
    content = content.replace(
        '<a href="about.qmd">About</a><a href="contact.qmd">Contact</a>',
        '<a href="blog.qmd">Blog</a><a href="about.qmd">About</a>'
    )

    # ── Mobile drawer (qmd files) ─────────────────────────────────────────
    content = content.replace(
        '<li><a href="about.qmd">About</a></li><li><a href="contact.qmd">Contact</a></li>',
        '<li><a href="blog.qmd">Blog</a></li><li><a href="about.qmd">About</a></li>'
    )
    # Newline variant
    content = content.replace(
        '<li><a href="about.qmd">About</a></li>\n      <li><a href="contact.qmd">Contact</a></li>',
        '<li><a href="blog.qmd">Blog</a></li>\n      <li><a href="about.qmd">About</a></li>'
    )
    content = content.replace(
        '<li><a href="about.qmd">About</a></li>\n          <li><a href="contact.qmd">Contact</a></li>',
        '<li><a href="blog.qmd">Blog</a></li>\n          <li><a href="about.qmd">About</a></li>'
    )

    # ── Sidebar footer contact link in index.qmd ──────────────────────────
    content = content.replace(
        '<a href="contact.qmd">Contact</a>',
        ''
    )

    # ── page-list card in index.qmd ───────────────────────────────────────
    content = content.replace(
        '<a class="page-link-card" href="about.qmd"><h3>About</h3><p>Narrative and methodology overview.</p></a>\n          <a class="page-link-card" href="contact.qmd"><h3>Contact</h3><p>Professional links and contact route.</p></a>',
        '<a class="page-link-card" href="blog.qmd"><h3>Blog</h3><p>Technical articles and tutorials.</p></a>\n          <a class="page-link-card" href="about.qmd"><h3>About &amp; Contact</h3><p>Who I am and how to reach me.</p></a>'
    )

    # ── Shell html files (use .html hrefs) ───────────────────────────────
    # Case 1: exact pattern with ../
    for prefix in ['../', '../../']:
        content = content.replace(
            f'<a href="{prefix}about.html">About</a>\n        <a href="{prefix}contact.html">Contact</a>',
            f'<a href="{prefix}blog.html">Blog</a>\n        <a href="{prefix}about.html">About</a>'
        )
        content = content.replace(
            f'<a href="{prefix}about.html">About</a><a href="{prefix}contact.html">Contact</a>',
            f'<a href="{prefix}blog.html">Blog</a><a href="{prefix}about.html">About</a>'
        )
        content = content.replace(
            f'<li><a href="{prefix}about.html">About</a></li>\n          <li><a href="{prefix}contact.html">Contact</a></li>',
            f'<li><a href="{prefix}blog.html">Blog</a></li>\n          <li><a href="{prefix}about.html">About</a></li>'
        )
        content = content.replace(
            f'<li><a href="{prefix}about.html">About</a></li><li><a href="{prefix}contact.html">Contact</a></li>',
            f'<li><a href="{prefix}blog.html">Blog</a></li><li><a href="{prefix}about.html">About</a></li>'
        )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  UPDATED: {os.path.basename(path)}")
    else:
        print(f"  no change: {os.path.basename(path)}")

print("=== Updating QMD files ===")
for fname in QMD_FILES:
    update_file(os.path.join(BASE, fname))

print("=== Updating shell HTML files ===")
for fname in SHELL_FILES:
    update_file(os.path.join(BASE, fname))

print("Done.")
