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

# Initialisation du moteur de synthèse vocale
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
        self.app_id = "YOUR-ID"
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
