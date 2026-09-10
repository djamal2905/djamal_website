---
title: "Djamaldbz - Crée ton assistant virtuel en python !!!"
author: "Djamal TOE"
date: "2022"

---





# Introduction

|       Ce document explique en détail le fonctionnement du code Python du Voxa Assistant, un assistant vocal interactif développé en 2022 et utilisant plusieurs bibliothèques pour la reconnaissance vocale, la synthèse vocale et les requêtes en ligne. J'utilise en particulier **Wolfram Alpha**.


## Wolfram Alpha : C'est quoi et à quoi ça sert ?

**Wolfram Alpha** est un moteur de calcul et de réponse basé sur l'intelligence artificielle et les algorithmes symboliques. Contrairement à un moteur de recherche classique comme Google, qui fournit des liens vers des sites web, **Wolfram Alpha génère directement des réponses précises basées sur des bases de connaissances et des algorithmes mathématiques avancés**. Il est souvent utilisé pour des calculs, des questions scientifiques et des recherches basées sur des données structurées.

#### Utilité :

- Résolution d'équations mathématiques et scientifiques
- Recherche et analyse de données (statistiques, physique, chimie, finance, etc.)
- Interprétation de requêtes en langage naturel
- Génération de graphiques et de simulations

🔗 **Créer un compte Wolfram Alpha** :
Si vous souhaitez utiliser l'API de Wolfram Alpha dans votre projet, vous devez créer un compte via ce lien :
👉 [Créer un compte Wolfram Alpha](https://www.wolframalpha.com/)
Je posterai une demo sur comment creer son compte et recupérer un id pour une application. Car en effet, il existe plusieurs type d'ID qui servent à différentes type d'applications. Il fonctionne en Anglais donc nous allons écrire une fonction pour la traduction du Francais en Anglais afin de poser des questions et une pour la traduction de l'Anglais en Français pour la reponse trouvée. Vous avez bien entendu besoin de connexion pour effectuer les recherches.

> ⚠️ **MISE À JOUR IMPORTANTE DE L'API WOLFRAMALPHA – 24 JUIN 2024**
>
> Depuis le **24 juin 2024**, **l'API WolframAlpha a changé**.
> **L'ancienne méthode avec `Client.query()` et `next(response.results)` n'est plus fiable** et peut générer des erreurs (`StopIteration`, `TypeError`, etc.).
>
> ---
>
> ### ✅ Nouvelle méthode recommandée :
> Utilisez l'API REST `v2/query` directement via `requests` :
>
> ```python
> import requests
> import xml.etree.ElementTree as ET
>
> def wolfram_query(query):
>     url = "https://api.wolframalpha.com/v2/query"
>     params = {
>         "appid": APP_ID,
>         "input": query,
>         "format": "plaintext"
>     }
>     response = requests.get(url, params=params)
>     root = ET.fromstring(response.content)
>     pods = root.findall('.//pod')
>
>     for pod in pods:
>         title = pod.attrib.get('title', '').lower()
>         if any(kw in title for kw in ['result', 'definition', 'primary']):
>             txt = pod.find('.//plaintext')
>             if txt is not None and txt.text:
>                 return txt.text
>     return "Aucune réponse trouvée."
> ```
>
> ---
>
> 🎙️ **Et pour les commandes vocales ?**
> Traduisez votre question en anglais avant l'envoi (`translate_fr_en`) et traduisez la réponse inversement pour l'afficher ou la vocaliser (`translate_en_fr`).
>
> 💡 **Exemple vocal** :
> Dites **“Intégrale de ln(x)”** → traduit en **"integrate ln(x)"** → réponse traitée par l’API.


**Exemple d'utilisation**


::: {.cell}

:::




::: {.cell}

```{.python .cell-code}
import wolframalpha
# id_ = "YOUR_WOLFRAMALPHA_ID"
##-- J'utliserai le mien que j'ai masqué
# id_ = r.id_
client = wolframalpha.Client(id_)
queries = [
  "who is the president of France",
  "compute 2 times 2 times ln(2)",
  "derivate xln(x)",
  "integrate exponential of 2x between 2 and 4"
]
# print(id_)
```
:::




::: {.cell}

```{.python .cell-code}
import requests
import xml.etree.ElementTree as ET

def wolfram_query(query):
    """
    Interroge l'API WolframAlpha avec une requête textuelle et extrait la réponse principale.

    Paramètres :
    -----------
    query : str
        La question ou l'expression mathématique à envoyer à WolframAlpha.

    Retour :
    --------
    str ou None
        Le texte de la réponse principale si trouvée, sinon None.

    Fonctionnement :
    ----------------
    - Envoie la requête à l'API WolframAlpha (format XML).
    - Vérifie que la réponse est bien en XML.
    - Parse le XML pour extraire les 'pods' (blocs de réponses).
    - Recherche prioritairement un pod dont le titre contient 'result', 'definition' ou 'primary'.
    - Sinon retourne le premier pod contenant du texte.
    - Si aucune réponse trouvée, retourne None.
    """

    # URL de l'API WolframAlpha pour requêtes de type 'query'
    url = "https://api.wolframalpha.com/v2/query"

    # Paramètres envoyés : clé API, la question, format de réponse demandé (texte brut)
    params = {
        "appid": id_,
        "input": query,
        "format": "plaintext"
    }

    # Envoi de la requête HTTP GET
    response = requests.get(url, params=params)

    # Vérification que la réponse est bien du XML
    content_type = response.headers.get('Content-Type', '')
    if 'xml' not in content_type:
        raise ValueError(f"Format inattendu : {content_type}")

    # Parsing du contenu XML de la réponse
    root = ET.fromstring(response.content)

    # Recherche de tous les pods (sections de réponse)
    pods = root.findall('.//pod')

    # Première passe : chercher un pod contenant la réponse principale
    for pod in pods:
        title = pod.attrib.get('title', '').lower()
        if 'result' in title or 'definition' in title or 'primary' in title:
            plaintext = pod.find('.//plaintext')
            if plaintext is not None and plaintext.text:
                print(f"Réponse pour '{query}' : {plaintext.text}")
                return plaintext.text

    # Seconde passe : si pas de pod "résultat", afficher le premier pod avec du texte
    for pod in pods:
        plaintext = pod.find('.//plaintext')
        if plaintext is not None and plaintext.text:
            print(f"Réponse pour '{query}' : {plaintext.text}")
            return plaintext.text

    # Si aucun pod avec texte, afficher message d'erreur
    print(f"Aucune réponse trouvée pour '{query}'")
    return None
```
:::





::: {.cell}

```{.python .cell-code}
wolfram_query(queries[0])
```

::: {.cell-output .cell-output-stdout}

```
Réponse pour 'who is the president of France' : Emmanuel Macron (from 14/05/2017 to present)
'Emmanuel Macron (from 14/05/2017 to present)'
```


:::
:::



::: {.cell}

```{.python .cell-code}
wolfram_query(queries[1])
```

::: {.cell-output .cell-output-stdout}

```
Réponse pour 'compute 2 times 2 times ln(2)' : 4 log(2)
'4 log(2)'
```


:::
:::



::: {.cell}

```{.python .cell-code}
wolfram_query(queries[2])
```

::: {.cell-output .cell-output-stdout}

```
Réponse pour 'derivate xln(x)' : d/dx(x log(x)) = log(x) + 1
'd/dx(x log(x)) = log(x) + 1'
```


:::
:::



::: {.cell}

```{.python .cell-code}
wolfram_query(queries[3])
```

::: {.cell-output .cell-output-stdout}

```
Réponse pour 'integrate exponential of 2x between 2 and 4' : integral_2^4 exp(2 x) dx = 1/2 e^4 (e^4 - 1)≈1463.2
'integral_2^4 exp(2 x) dx = 1/2 e^4 (e^4 - 1)≈1463.2'
```


:::
:::


### Explication des parties techniques de votre code

Le script commence par l'importation des bibliothèques nécessaires :


::: {.cell}

```{.python .cell-code}
import datetime
import webbrowser
import sys
import pywhatkit
import speech_recognition as sr
import pyttsx3 as ttx
import wikipedia
from googletrans import Translator
import wolframalpha
```
:::


- `datetime` : gestion des dates et heures.
- `webbrowser` : ouverture des pages web.
- `sys` : gestion des fonctionnalités système.
- `pywhatkit` : exécution de commandes interactives comme la recherche YouTube.
- `speech_recognition` : reconnaissance vocale.
- `pyttsx3` : synthèse vocale.
- `wikipedia` : récupération d'informations depuis Wikipédia.
- `googletrans` : traduction de texte.
- `wolframalpha` : moteur de réponse à des questions scientifiques et mathématiques.

Intaller les avec la commande :


::: {.cell}

```{.python .cell-code}
modules = [
    "pywhatkit", "speechrecognition", "pyttsx3",
    "wikipedia", "googletrans==4.0.0-rc1", "wolframalpha", "pyaudio"
]

import subprocess
import sys
def install_modules():
    for module in modules:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
        except:
            print("Quelque chose s'est mal passée")

install_modules()
```
:::



## 2. Configuration du moteur de synthèse vocale

Le code initialise `pyttsx3` et affiche les voix disponibles :


::: {.cell}

```{.python .cell-code}
moteur = ttx.init()
voix_disponibles = moteur.getProperty("voices")

for index, voix in enumerate(voix_disponibles):
    print(f"Index {index} - ID: {voix.id} - Langue: {voix.languages} - Nom: {voix.name}")
```

::: {.cell-output .cell-output-stdout}

```
Index 0 - ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0 - Langue: [] - Nom: Microsoft David Desktop - English (United States)
Index 1 - ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0 - Langue: [] - Nom: Microsoft Zira Desktop - English (United States)
Index 2 - ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_FR-FR_HORTENSE_11.0 - Langue: [] - Nom: Microsoft Hortense Desktop - French
```


:::
:::


Ensuite, une voix spécifique est sélectionnée et testée :


::: {.cell}

```{.python .cell-code}
moteur.setProperty("voice", voix_disponibles[2].id)
moteur.say("Bonjour, ceci est un test avec une autre voix.")
moteur.runAndWait()
```
:::


## 3. Définition de la classe `voxaAssistant`
La classe `voxaAssistant` gère toutes les fonctionnalités de l'assistant vocal.

### 3.1 Initialisation


::: {.cell}

```{.python .cell-code}
class voxaAssistant:
    def __init__(self):
        self.ecouteur = sr.Recognizer()
        self.moteur = ttx.init()
        self.voix_disponibles = self.moteur.getProperty("voices")
        self.moteur.setProperty("voice", self.voix_disponibles[2].id)
        self.moteur.setProperty("rate", 170)
        self.app_id = id_
        self.client = wolframalpha.Client(self.app_id)
```
:::


Cette méthode :
- Initialise le moteur de reconnaissance vocale (`speech_recognition`)

- Configure la synthèse vocale avec `pyttsx3`

- Définit la clé API pour Wolfram Alpha.

### 3.2 Fonction `parler`

Cette fonction génère une sortie vocale à partir d'un texte donné.


::: {.cell}

```{.python .cell-code}
def parler(self, texte):
    self.moteur.say(texte)
    self.moteur.runAndWait()
```
:::


### 3.3 Fonction `saluer`

Cette fonction ajuste le message de salutation en fonction de l'heure.


::: {.cell}

```{.python .cell-code}
def saluer(self):
    heure_actuel = int(datetime.datetime.now().hour)
    if 0 <= heure_actuel <= 12:
        self.parler("Bonjour à vous Djamal")
    else:
        self.parler("Bonsoir à vous Djamal")
```
:::


## 4. Reconnaissance et Traitement des Requêtes Vocales

### Fonction `voxa_requete`

Cette fonction écoute l'utilisateur et transcrit la parole en texte.


::: {.cell}

```{.python .cell-code}
def voxa_requete(self):
    with sr.Microphone() as parole:
        print("Entrain d'écouter ...")
        self.ecouteur.adjust_for_ambient_noise(parole, duration=1)
        self.ecouteur.pause_threshold = 1.5
        try:
            voix = self.ecouteur.listen(parole, timeout=5, phrase_time_limit=5)
            command = self.ecouteur.recognize_google(voix, language="fr").lower()
            print("Vous avez dit .... : ", command)
            return command
        except sr.UnknownValueError:
            print("Je n'ai pas compris, veuillez répéter.")
            return ""
        except sr.RequestError:
            print("Erreur avec le service de reconnaissance vocale.")
            return ""
```
:::


### Recherche Google et YouTube

Si l'utilisateur mentionne `Google` ou `YouTube`, la recherche est effectuée automatiquement.


::: {.cell}

```{.python .cell-code}
elif "google" in voix:
    url = voix.split().index("google")
    elt_rechercher = voix.split()[url + 1:]
    self.parler("D'accord, je lance la recherche")
    webbrowser.open("https://www.google.com/search?q=" + "+".join(elt_rechercher), new=2)
```
:::



::: {.cell}

```{.python .cell-code}
elif "recherche sur youtube" in voix or "recherche sur youtube.com" in voix:
                url = voix.split().index("youtube")
                elt_rechercher = voix.split()[url + 1:]
                self.parler("d'accord  je  lance  la  recherche")
                webbrowser.open(
                    "http://www.youtube.com/results?search_query="
                    + "+".join(elt_rechercher),
                    new=2,
                )
```
:::



#### **1️⃣ `split()` : Pourquoi l'utiliser ici ?**


::: {.cell}

```{.python .cell-code}
url = voix.split().index("google")
elt_rechercher = voix.split()[url + 1:]
```
:::


- **`split()`** découpe une chaîne de caractères en une liste de mots.
- Ici, on cherche l'index du mot **"google"** pour récupérer les mots suivants, qui correspondent à la requête de l'utilisateur.
- **Exemple :**
  - **Entrée** : `"cherche sur google c'est quoi la capitale de la France"`
  - **Après split()** : `["cherche","sur", "google", "c", "'", "est", "quoi", "la", "capitale", "de", "la", "France"]`
  - **Index du mot "google"** : `3`
  - **Ce qui est recherché** : `["c", "'", "est", "quoi", "la", "capitale", "de", "la", "France"]` → Ici, on devrait prendre les mots après **"google"**.

#### 2️⃣ Pourquoi y a-t-il des `+` dans l'URL de Google et YouTube ?



::: {.cell}

```{.python .cell-code}
webbrowser.open("https://www.google.com/search?q=" + "+".join(elt_rechercher), new=2)
```
:::




::: {.cell}

```{.python .cell-code}
elif "youtube" in voix:
    s = voix.replace("youtube", "")
    self.parler("D'accord sans soucis")
    pywhatkit.playonyt(s)
```
:::


- **Explication du `+`.**
  - Dans une URL, un **espace** est souvent remplacé par **`+` ou `%20`**.
  - **Exemple** : Si l'utilisateur dit *"recherche machine learning sur google"*, on doit transformer `"machine learning"` en `"machine+learning"` pour que Google comprenne.
  - **Autre solution** : `"%20".join(elt_rechercher)` aurait aussi pu être utilisé.

### Recherches Avancées avec Wolfram Alpha et Wikipédia

#### Utilisation de Wolfram Alpha pour répondre aux questions générales


::: {.cell}

```{.python .cell-code}
    def question_generale(self, voix):
        voix = self.translate_eng_fr(voix)
        try:
            reponse = self.client.query(voix)
            res = next(reponse.results).text
            res = self.translate_fr_eng(res)
            print("Un instant ...")
            print(res)
            self.parler(res)
        except:
            self.parler("Je n'ai pas trouvé de réponse.")
```
:::


|       Ici, l'assistant vocal envoie la requête à Wolfram Alpha, récupère la réponse et la traduit en français avant de la prononcer.
Si aucune réponse n'est trouvée, une recherche est effectuée sur Wikipédia.

#### Utilisation de wikipedia pour répondre aux questions générales


::: {.cell}

```{.python .cell-code}
try:
    wikipedia.set_lang("fr")
    info = wikipedia.summary(voix, 1)
    self.parler(str(info))
except:
    self.parler("Je n'ai pas bien compris")
```
:::



#### 3️⃣ `query` : À quoi ça sert dans Wolfram Alpha*


::: {.cell}

```{.python .cell-code}
reponse = self.client.query(voix)
res = next(reponse.results).text
```
:::


- **`.query(voix)`** : envoie la question de l'utilisateur à Wolfram Alpha.
- **`next(reponse.results).text`** : récupère la première réponse retournée et extrait le texte.
- **Si Wolfram Alpha trouve une réponse pertinente, elle est lue à haute voix.**


### **Résumé des concepts clés :**
| Élément | Explication |
|---------|------------|
| **Wolfram Alpha** | Moteur de calcul intelligent répondant à des requêtes scientifiques et analytiques |
| **split()** | Découpe une phrase en liste de mots |
| **query()** | Envoie une requête à Wolfram Alpha |
| **join("+")** | Transforme une liste de mots en requête lisible par un moteur de recherche |

# Code complet pour l'assistant virtuel

```{.python, eval = FALSE}
import requests
import xml.etree.ElementTree as ET
import datetime
import webbrowser
import sys
import pywhatkit
import speech_recognition as sr
import pyttsx3 as ttx
import wikipedia
from googletrans import Translator
import wolframalpha

import pyttsx3

id_ = "YOUR-ID-WOLFRAMALPHA"


def wolfram_query(query):
    """
    Interroge l'API WolframAlpha avec une requête textuelle et extrait la réponse principale.

    Paramètres :
    -----------
    query : str
        La question ou l'expression mathématique à envoyer à WolframAlpha.

    Retour :
    --------
    str ou None
        Le texte de la réponse principale si trouvée, sinon None.

    Fonctionnement :
    ----------------
    - Envoie la requête à l'API WolframAlpha (format XML).
    - Vérifie que la réponse est bien en XML.
    - Parse le XML pour extraire les 'pods' (blocs de réponses).
    - Recherche prioritairement un pod dont le titre contient 'result', 'definition' ou 'primary'.
    - Sinon retourne le premier pod contenant du texte.
    - Si aucune réponse trouvée, retourne None.
    """

    # URL de l'API WolframAlpha pour requêtes de type 'query'
    url = "https://api.wolframalpha.com/v2/query"

    # Paramètres envoyés : clé API, la question, format de réponse demandé (texte brut)
    params = {
        "appid": APP_ID,
        "input": query,
        "format": "plaintext"
    }

    # Envoi de la requête HTTP GET
    response = requests.get(url, params=params)

    # Vérification que la réponse est bien du XML
    content_type = response.headers.get('Content-Type', '')
    if 'xml' not in content_type:
        raise ValueError(f"Format inattendu : {content_type}")

    # Parsing du contenu XML de la réponse
    root = ET.fromstring(response.content)

    # Recherche de tous les pods (sections de réponse)
    pods = root.findall('.//pod')

    # Première passe : chercher un pod contenant la réponse principale
    for pod in pods:
        title = pod.attrib.get('title', '').lower()
        if 'result' in title or 'definition' in title or 'primary' in title:
            plaintext = pod.find('.//plaintext')
            if plaintext is not None and plaintext.text:
                print(f"Réponse pour '{query}' : {plaintext.text}")
                return plaintext.text

    # Seconde passe : si pas de pod "résultat", afficher le premier pod avec du texte
    for pod in pods:
        plaintext = pod.find('.//plaintext')
        if plaintext is not None and plaintext.text:
            print(f"Réponse pour '{query}' : {plaintext.text}")
            return plaintext.text

    # Si aucun pod avec texte, afficher message d'erreur
    print(f"Aucune réponse trouvée pour '{query}'")
    return None


moteur = pyttsx3.init()

# Récupération des voix disponibles
voix_disponibles = moteur.getProperty("voices")

# Affichage des identifiants des voix disponibles
for index, voix in enumerate(voix_disponibles):
    print(
        f"Index {index} - ID: {voix.id} - Langue: {voix.languages} - Nom: {voix.name}"
    )

# Sélection d'une voix spécifique (par exemple, la deuxième voix)
moteur.setProperty(
    "voice", voix_disponibles[2].id
)  # Modifier l'index selon la voix souhaitée

# Test de la nouvelle voix
moteur.say("Bonjour, ceci est un test avec une autre voix.")
moteur.runAndWait()


class voxaAssistant:
    def __init__(self):
        self.ecouteur = sr.Recognizer()
        self.moteur = ttx.init()
        self.voix_disponibles = self.moteur.getProperty("voices")
        self.moteur.setProperty("voice", self.voix_disponibles[2].id)
        self.moteur.setProperty("rate", 170)
        self.app_id = id_
        self.client = wolframalpha.Client(self.app_id)

    def parler(self, texte):
        self.moteur.say(texte)
        self.moteur.runAndWait()

    def saluer(self):
        heure_actuel = int(datetime.datetime.now().hour)
        if 0 <= heure_actuel <= 12:
            self.parler("Bonjour à vous Djamal")
        else:
            self.parler("Bonsoir à vous Djamal")

    def voxa_requete(self):
        with sr.Microphone() as parole:
            print("Entrain d'écouter ...")
            self.ecouteur.adjust_for_ambient_noise(parole, duration=1)
            self.ecouteur.pause_threshold = 1.5
            try:
                voix = self.ecouteur.listen(parole, timeout=5, phrase_time_limit=5)
                command = self.ecouteur.recognize_google(voix, language="fr").lower()
                print("Vous avez dit .... : ", command)
                return command
            except sr.UnknownValueError:
                print("Je n'ai pas compris, veuillez répéter.")
                return ""
            except sr.RequestError:
                print("Erreur avec le service de reconnaissance vocale.")
                return ""

    def translate_eng_fr(self, texte):
        translator = Translator()
        t = translator.translate(texte, src="fr", dest="en")
        return t.text

    def translate_fr_eng(self, texte):
        translator = Translator()
        t = translator.translate(texte, src="en", dest="fr")
        return t.text

    def question_generale(self, voix):
      voix_en = self.translate_eng_fr(voix)
      reponse = wolfram_query(voix_en)
      if reponse:
          res_fr = self.translate_fr_eng(reponse)
          print("Un instant ...")
          print(res_fr)
          self.parler(res_fr)
      else:
          self.parler("Je n'ai pas trouvé de réponse.")

    def voxa(self):
        voix = self.voxa_requete()
        if voix:
            if "arretes-toi" in voix or "arrête-toi" in voix:
                self.parler("Merci, ca a été un réel plaisir de vous avoir aidé")
                sys.exit()
            elif "recherche sur youtube" in voix or "recherche sur youtube.com" in voix:
                url = voix.split().index("youtube")
                elt_rechercher = voix.split()[url + 1:]
                self.parler("d'accord  je  lance  la  recherche")
                webbrowser.open(
                    "http://www.youtube.com/results?search_query="
                    + "+".join(elt_rechercher),
                    new=2,
                )
            elif (
                "google" in voix
                or "recherche sur google" in voix
                or "sur google" in voix
            ):
                url = voix.split().index("google")
                elt_rechercher = voix.split()[url + 1:]
                self.parler("d'accord  je  lance  la  recherche")
                webbrowser.open(
                    "https://www.google.com/search?q=" + "+".join(elt_rechercher), new=2
                )
                self.parler("voici  ce  que  jai  trouvé  sur  google ")
            elif "youtube" in voix:
                s = voix.replace("youtube", "")
                self.parler("D'accord sans soucis")
                pywhatkit.playonyt(s)
            elif "répète" in voix:
                self.parler("Bienvenue sur la chaine Djamal Dev")
            else:
                try:
                    self.question_generale(voix)
                except:
                    try:
                        wikipedia.set_lang("fr")
                        info = wikipedia.summary(voix, 1)
                        self.parler(str(info))
                    except:
                        self.parler("Je n'ai pas bien compris")


if __name__ == "__main__":
    assistant = voxaAssistant()
    while True:
        assistant.voxa()


```

## Test du code

{{< video https://djamal2905.github.io/djamal_website/INFO_MINI_PROJETS/assistant.mp4 >}}

## Conclusion

Ce code met en place un assistant vocal capable de reconnaître et d'exécuter des commandes vocales en français, d'effectuer des recherches sur le web, et de répondre aux questions grâce à Wolfram Alpha et Wikipédia. Il constitue une base quelque peu solide pour un assistant personnel plus ou moins intelligent.


[**Télécharger le fichier .python**](https://djamal2905.github.io/djamal_website/INFO_MINI_PROJETS/chat.py)

[**Télécharger la vidéo**](https://djamal2905.github.io/djamal_website/INFO_MINI_PROJETS/assistant.mp4)

Si vous avez des questions, vous pouvez me contacter !!!

[Retour à la page d'accueuil](https://djamal2905.github.io/djamal_website)
