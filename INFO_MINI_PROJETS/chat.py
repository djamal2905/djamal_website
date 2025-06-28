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

