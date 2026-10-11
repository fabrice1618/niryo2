#!/usr/bin/env python3
"""Simulateur MQTT : envoie au broker, au choix dans un menu, les messages du robot.

Il sert à tester le collecteur avant que le robot soit intégré.
Lancement : python3 simulateur_mqtt.py
"""
import json
import random
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1e1"                        # identifiant de l'équipe, aussi compte MQTT
MOT_DE_PASSE = "mot-de-passe-equipe"   # mot de passe MQTT de l'équipe ; "" pour un broker sans mot de passe
BROKER = "localhost"                   # "192.168.10.10" depuis un poste du fab lab, ou un broker public


# --- Connexion au broker -----------------------------------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_simulateur")
if MOT_DE_PASSE:                       # pas de compte sur un broker sans mot de passe
    client.username_pw_set(EQUIPE, MOT_DE_PASSE)
piece = 0                              # numéro de la dernière pièce


def maintenant():
    """Heure locale, au format utilisé par le robot : 2026-11-17T08:30:18."""
    return datetime.now().isoformat(timespec="seconds")


def publier(sujet, message):
    """Envoie un message sur cellule/<equipe>/<sujet>. Un dictionnaire est envoyé en JSON."""
    if isinstance(message, dict):
        message = json.dumps(message, ensure_ascii=False)
    info = client.publish(f"cellule/{EQUIPE}/{sujet}", message, qos=1, retain=(sujet == "etat"))
    info.wait_for_publish()            # attendre que le broker ait reçu le message
    print(f"  envoyé sur cellule/{EQUIPE}/{sujet} : {message}")


# --- Les messages du menu ------------------------------------------------------
def debut_cycle():
    global piece
    piece = piece + 1
    publier("cycle", {"evenement": "debut_cycle", "piece": piece, "horodatage": maintenant()})


def fin_cycle():
    duree = round(random.uniform(15, 21), 1)
    zone = random.choice(["A", "B"])
    publier("cycle", {"evenement": "fin_cycle", "piece": piece, "duree": duree, "zone": zone,
                      "horodatage": maintenant()})


def cycle_complet():
    debut_cycle()
    fin_cycle()


def changer_etat():
    etat = input("  État (en_cycle, attente, arrete) : ").strip() or "en_cycle"
    publier("etat", {"etat": etat, "horodatage": maintenant()})


def defaut():
    publier("defaut", {"defaut": "piece_non_detectee", "message": "DI5 inactif après 30 s",
                       "horodatage": maintenant()})


def tache():
    publier("tache", {"evenement": "debut_tache", "tache": "home", "horodatage": maintenant()})
    publier("tache", {"evenement": "fin_tache", "tache": "home", "statut": "terminee",
                      "horodatage": maintenant()})


def messages_invalides():
    """Des messages mal formés : le collecteur doit les garder sans s'arrêter."""
    publier("cycle", "ceci n'est pas du JSON")
    publier("cycle", '{"evenement": "fin_cycle", "piece": 7')            # JSON coupé
    publier("cycle", '{"evenement": "fin_cycle", "piece": 7}')           # durée manquante
    publier("cycle", '{"evenement": "fin_cycle", "duree": "rapide"}')    # durée qui n'est pas un nombre
    publier("cycle", '["fin_cycle", 7, 18.2]')                           # liste au lieu d'un objet
    publier("cycle", "")                                                 # message vide


def production():
    """Plusieurs cycles à la suite, un toutes les 2 secondes ; Ctrl+C pour revenir au menu."""
    nombre = int(input("  Nombre de cycles : ") or "10")
    publier("etat", {"etat": "en_cycle", "horodatage": maintenant()})
    try:
        for i in range(nombre):
            debut_cycle()
            time.sleep(2)
            if random.random() < 0.1:          # un cycle sur dix finit en défaut
                defaut()
            else:
                fin_cycle()
    except KeyboardInterrupt:
        print("  interrompu")
    publier("etat", {"etat": "arrete", "horodatage": maintenant()})


def rafale():
    """1000 fins de cycle envoyées d'un coup : le collecteur doit toutes les enregistrer."""
    global piece
    for i in range(1000):
        piece = piece + 1
        message = {"evenement": "fin_cycle", "piece": piece, "duree": 18.0, "zone": "A",
                   "horodatage": maintenant()}
        info = client.publish(f"cellule/{EQUIPE}/cycle", json.dumps(message), qos=1)
    info.wait_for_publish()
    print(f"  1000 fins de cycle envoyées sur cellule/{EQUIPE}/cycle (pièces {piece - 999} à {piece})")


def message_libre():
    sujet = input(f"  Sujet (après cellule/{EQUIPE}/) : ").strip() or "essai"
    texte = input("  Message : ")
    publier(sujet, texte)


MENU = {
    "1": ("Cycle complet (début puis fin)", cycle_complet),
    "2": ("Début de cycle", debut_cycle),
    "3": ("Fin de cycle", fin_cycle),
    "4": ("Changer l'état du robot", changer_etat),
    "5": ("Défaut", defaut),
    "6": ("Tâche de l'API (début puis fin)", tache),
    "7": ("Messages mal formés", messages_invalides),
    "8": ("Production : plusieurs cycles à la suite", production),
    "9": ("Rafale de 1000 messages", rafale),
    "10": ("Message libre", message_libre),
}


# --- Programme principal --------------------------------------------------------
try:
    client.connect(BROKER, 1883)
except OSError as e:
    print(f"Broker {BROKER} injoignable : {e}")
    raise SystemExit(1)
client.loop_start()
time.sleep(1)                          # le temps que le broker accepte la connexion
if not client.is_connected():
    print("Connexion refusée par le broker : vérifier EQUIPE et MOT_DE_PASSE")
    raise SystemExit(1)

while True:
    print(f"\nSimulateur MQTT, équipe {EQUIPE}, broker {BROKER}")
    for numero, (libelle, fonction) in MENU.items():
        print(f"{numero:>3}. {libelle}")
    print("  0. Quitter")
    choix = input("Votre choix : ").strip()
    if choix == "0":
        break
    if choix in MENU:
        libelle, fonction = MENU[choix]
        fonction()
    else:
        print("  choix inconnu")

client.loop_stop()
client.disconnect()
