# -*- coding: utf-8 -*-
"""Génère stories/about.html : la présentation animée de la page About (EN et FR).
Même lecteur et mêmes styles que les récits d'expérience (stories-reel.js / stories-reel.css)."""
import pathlib, html

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = (ROOT / "stories" / "experiences.html").read_text(encoding="utf-8")
head_end = SRC.index("<body>")
HEAD = SRC[:head_end]
HEAD = HEAD.replace("<title>Experience stories · Djamal TOE</title>", "<title>About Djamal TOE in one minute</title>")
HEAD = HEAD.replace(
    'content="How each professional experience unfolded: context, question, obstacles, choices, work, checks, outcome and limits."',
    'content="Djamal TOE in one minute: experience, what I am looking for, education, academic and personal projects."')
TAIL = SRC[SRC.index('<script src="stories.js" defer></script>'):]

def a(i, base=0.1, step=0.25):
    return f'style="--d:{base + i * step:.2f}s"'

def chips(items, d=0.6):
    return '<div class="chips">' + "".join(f'<span class="a" {a(i, d, 0.12)}>{html.escape(t)}</span>' for i, t in enumerate(items)) + "</div>"

def stats(items, d=0.5):
    out = []
    for i, (num, pre, suf, label, note) in enumerate(items):
        b = f'<b data-count="{num}" data-pre="{pre}" data-suf="{suf}">{pre}{num}{suf}</b>' if num else f"<b>{pre}</b>"
        out.append(f'<div class="stat a" {a(i, d, 0.3)}>{b}<span>{html.escape(label)}</span>' + (f"<em>{html.escape(note)}</em>" if note else "") + "</div>")
    return '<div class="stats">' + "".join(out) + "</div>"

def flow(steps, d=0.5):
    parts = []
    for i, (t, s) in enumerate(steps):
        if i:
            parts.append(f'<i class="a" {a(i, d - 0.1, 0.35)}>→</i>')
        parts.append(f'<div class="a" {a(i, d, 0.35)}><b>{html.escape(t)}</b><span>{html.escape(s)}</span></div>')
    return '<div class="flow3">' + "".join(parts) + "</div>"

def scene(kicker, title, body, dur=None, note=None):
    d = f' data-dur="{dur}"' if dur else ""
    n = f'<p class="a" style="--d:2.2s">{note}</p>' if note else ""
    return (f'<div class="rs"{d} role="group" aria-roledescription="scene"><span class="k a">{html.escape(kicker)}</span>'
            f'<h3 class="a" style="--d:.1s">{title}</h3>{body}{n}</div>')

EN = [
    scene("Djamal TOE · ENSAI 2027", "Data Scientist, <mark>biostatistics</mark> and machine learning engineer.",
          chips(["Bayesian modelling", "Clinical development", "Health data", "Machine learning", "Tested software"]), 7000,
          "Engineering student in statistical engineering at ENSAI, Rennes."),
    scene("Experience 1 · Servier · 2026", "Estimating the <mark>probability of success</mark> of a Phase III trial.",
          flow([("Phase II data", "and past trials"), ("Hierarchical Bayesian model", "Stan, MAP and mixture priors"), ("R Shiny app", "unit-tested, in production")]), 10000,
          "Presented to the Onco Late Phase team, Global Biometrics and the SFdS Journées de la Biostatistique."),
    scene("Experience 2 · Centre Muraz · 2023 to 2024", "Did village health workers <mark>reduce malaria</mark>?",
          stats([("42", "≈ ", "%", "lower malaria incidence in targeted villages", "adjusted negative-binomial mixed model, stepped-wedge trial")]), 9000),
    scene("Experience 3 · Les Vieilles Charrues · 2025", "Who gets accepted as a <mark>festival volunteer</mark>?",
          flow([("Cleaning", "automated preprocessing"), ("MCA", "profiles of applicants"), ("Logistic regression", "Hosmer-Lemeshow, ROC")]), 9000,
          "A descriptive model: discrimination stayed modest (AUC 0.68)."),
    scene("Next · Pierre Fabre · April 2027", "Six months in <mark>pharmacometrics</mark>.",
          chips(["Population PK", "PD models", "Tumour growth inhibition", "NLME", "Bayesian inference in Stan"]), 8000),
    scene("What I am looking for", "A <mark>PhD (CIFRE)</mark> from late 2027, or a permanent position.",
          chips(["Biostatistics", "Pharmacometrics", "Real-world evidence", "Machine learning for health"]), 8000,
          "Where statistical rigour and software that people actually use both matter."),
    scene("Education", "From Bobo-Dioulasso to <mark>Rennes</mark>.",
          flow([("Université Nazi Boni", "BSc Statistics and Computer Science, 2020 to 2023"), ("ENSAI", "Engineering degree, data science and ML, 2024 to 2027")]), 8000),
    scene("Academic projects", "Statistics and ML on <mark>real, messy data</mark>.",
          stats([("", "217,000+", "", "posts analysed to detect coordinated image sharing", "CLIP, HDBSCAN, permutation tests with FDR control"),
                 ("99.78", "", "%", "test accuracy on brain MRI (906 images)", "exploratory project on public data")]), 10000,
          "Also: clustering of biomedical texts with SciBERT, NBA career length with ridge regression."),
    scene("Personal projects", "Building tools, <mark>quickly</mark>.",
          flow([("AELYN", "a personal assistant running a local LLM"), ("FieldReport Kit", "field reports for NGOs"), ("Science videos", "statistics and AI explained")]), 9000),
    scene("Let's talk", "The full details are on this site, the <mark>short version</mark> is in my CVs.",
          chips(["Experience page", "CV Biostatistics", "CV Machine Learning", "LinkedIn"]), 7000),
]

FR = [
    scene("Djamal TOE · ENSAI 2027", "Data Scientist, <mark>biostatistique</mark> et ingénierie machine learning.",
          chips(["Modélisation bayésienne", "Développement clinique", "Données de santé", "Machine learning", "Logiciel testé"]), 7000,
          "Élève-ingénieur en génie statistique à l'ENSAI, à Rennes."),
    scene("Expérience 1 · Servier · 2026", "Estimer la <mark>probabilité de succès</mark> d'un essai de phase III.",
          flow([("Données de phase II", "et essais passés"), ("Modèle bayésien hiérarchique", "Stan, priors MAP et de mélange"), ("Application R Shiny", "testée, en production")]), 10000,
          "Présenté à l'équipe Onco Late Phase, à Global Biometrics et aux Journées de la Biostatistique (SFdS)."),
    scene("Expérience 2 · Centre Muraz · 2023 à 2024", "Les agents de santé de village ont-ils <mark>réduit le paludisme</mark> ?",
          stats([("42", "≈ ", " %", "de baisse de l'incidence du paludisme dans les villages ciblés", "modèle mixte binomiale négative ajusté, essai en escalier")]), 9000),
    scene("Expérience 3 · Les Vieilles Charrues · 2025", "Qui est retenu comme <mark>bénévole du festival</mark> ?",
          flow([("Nettoyage", "prétraitement automatisé"), ("ACM", "profils des candidats"), ("Régression logistique", "Hosmer-Lemeshow, ROC")]), 9000,
          "Un modèle descriptif : la discrimination reste modeste (AUC 0,68)."),
    scene("Ensuite · Pierre Fabre · avril 2027", "Six mois en <mark>pharmacométrie</mark>.",
          chips(["PK de population", "Modèles PD", "Croissance tumorale (TGI)", "NLME", "Inférence bayésienne sous Stan"]), 8000),
    scene("Ce que je recherche", "Une <mark>thèse (CIFRE)</mark> à partir de fin 2027, ou un CDI.",
          chips(["Biostatistique", "Pharmacométrie", "Données de vie réelle", "Machine learning en santé"]), 8000,
          "Là où la rigueur statistique et des outils réellement utilisés comptent autant l'une que l'autre."),
    scene("Parcours", "De Bobo-Dioulasso à <mark>Rennes</mark>.",
          flow([("Université Nazi Boni", "Licence Statistique et Informatique, 2020 à 2023"), ("ENSAI", "Diplôme d'ingénieur, science des données et ML, 2024 à 2027")]), 8000),
    scene("Projets académiques", "Statistique et ML sur des <mark>données réelles</mark>.",
          stats([("", "217 000+", "", "publications analysées pour détecter un partage d'images coordonné", "CLIP, HDBSCAN, tests de permutation avec contrôle du FDR"),
                 ("99.78", "", " %", "d'exactitude sur des IRM cérébrales (906 images de test)", "projet exploratoire sur données publiques")]), 10000,
          "Aussi : textes biomédicaux avec SciBERT, durée de carrière en NBA par régression ridge."),
    scene("Projets personnels", "Construire des outils, <mark>vite</mark>.",
          flow([("AELYN", "assistant personnel avec un LLM local"), ("FieldReport Kit", "rapports de terrain pour les ONG"), ("Vidéos de vulgarisation", "statistique et IA expliquées")]), 9000),
    scene("On en parle ?", "Le détail est sur ce site, la <mark>version courte</mark> dans mes CV.",
          chips(["Page Expérience", "CV Biostatistique", "CV Machine Learning", "LinkedIn"]), 7000),
]

def reel(scenes, lang):
    n = len(scenes)
    sc = "".join(s.replace('aria-roledescription="scene">', f'aria-roledescription="scene" aria-label="{"Scène" if lang == "fr" else "Scene"} {i + 1} {"sur" if lang == "fr" else "of"} {n}">', 1) for i, s in enumerate(scenes))
    fr = lang == "fr"
    ctrl = (f'<button type="button" class="reel-tap l" aria-label="{"Scène précédente" if fr else "Previous scene"}" tabindex="-1"></button>'
            f'<button type="button" class="reel-tap r" aria-label="{"Scène suivante" if fr else "Next scene"}" tabindex="-1"></button>'
            f'<div class="reel-ctrl"><button type="button" data-r="prev" aria-label="{"Scène précédente" if fr else "Previous scene"}">←</button>'
            f'<button type="button" data-r="play" aria-pressed="false">{"Lecture" if fr else "Play"}</button>'
            f'<button type="button" data-r="next" aria-label="{"Scène suivante" if fr else "Next scene"}">→</button>'
            f'<button type="button" class="langbtn" data-lang="{"en" if fr else "fr"}" aria-label="{"View in English" if fr else "Voir en français"}">{"EN" if fr else "FR"}</button>'
            f'<button type="button" data-r="music" aria-pressed="false">{"♪ Musique" if fr else "♪ Music"}</button><span class="cnt"></span></div>')
    cap = ("Appuie sur Lecture, touche les côtés ou utilise les flèches." if fr else "Press Play, tap the sides or use the arrow keys.")
    return (f'<div class="lg" lang="{lang}"><figure class="reel" data-dur="8000" aria-label="{"Djamal TOE en une minute" if fr else "Djamal TOE in one minute"}">'
            f'<div class="reel-stage" tabindex="0"><div class="reel-bars" aria-hidden="true"></div>'
            f'<span class="reel-tag">{"En une minute" if fr else "In one minute"}</span>{sc}{ctrl}</div>'
            f'<figcaption class="reel-cap">{cap}</figcaption></figure></div>')

BODY = ('<body class="about-embed"><style>body.about-embed{margin:0;background:transparent}'
        'body.about-embed .reel{margin:0}</style><main>' + reel(EN, "en") + reel(FR, "fr") + "</main>\n")
(ROOT / "stories" / "about.html").write_text(HEAD + BODY + TAIL, encoding="utf-8")
print("stories/about.html written")
