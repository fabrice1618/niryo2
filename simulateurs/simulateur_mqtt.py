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
EQUIPE = "g1"                        # identifiant de l'équipe, dans les topics MQTT
BROKER = "localhost"                   # "192.168.1.10" depuis un poste du fab lab, ou un broker public

MENU = f"""
Simulateur MQTT, équipe {EQUIPE}, broker {BROKER}
  1. Cycle complet (début puis fin)
  2. Début de cycle
  3. Fin de cycle
  4. Changer l'état du robot
  5. Défaut
  6. Tâche de l'API (début puis fin)
  7. Messages mal formés
  8. Production : plusieurs cycles à la suite
  9. Rafale de 1000 messages
 10. Message libre
  0. Quitter"""

piece = 0                              # numéro de la dernière pièce


def publier(sujet, message):
    """Envoie un message sur cellule/<equipe>/<sujet>.

    Un dictionnaire est envoyé en JSON, avec l'heure ajoutée ; un texte est envoyé tel quel.
    """
    if isinstance(message, dict):
        message["horodatage"] = datetime.now().isoformat(timespec="seconds")   # ex. 2026-11-17T08:30:18
        message = json.dumps(message, ensure_ascii=False)
    info = client.publish(f"cellule/{EQUIPE}/{sujet}", message, qos=1, retain=(sujet == "etat"))
    info.wait_for_publish()            # attendre que le broker ait reçu le message
    print(f"  envoyé sur cellule/{EQUIPE}/{sujet} : {message}")


# --- Les messages du robot -------------------------------------------------------
def debut_cycle():
    global piece
    piece = piece + 1
    publier("cycle", {"evenement": "debut_cycle", "piece": piece})


def fin_cycle():
    duree = round(random.uniform(15, 21), 1)
    zone = random.choice(["A", "B"])
    publier("cycle", {"evenement": "fin_cycle", "piece": piece, "duree": duree, "zone": zone})


def etat(valeur):
    publier("etat", {"etat": valeur})


def defaut():
    publier("defaut", {"defaut": "piece_non_detectee", "message": "DI5 inactif après 30 s"})


def tache():
    publier("tache", {"evenement": "debut_tache", "tache": "home"})
    publier("tache", {"evenement": "fin_tache", "tache": "home", "statut": "terminee"})


def messages_mal_formes():
    """Des messages incorrects : le collecteur doit les garder sans s'arrêter."""
    publier("cycle", "ceci n'est pas du JSON")
    publier("cycle", '{"evenement": "fin_cycle", "piece": 7')            # JSON coupé
    publier("cycle", '{"evenement": "fin_cycle", "piece": 7}')           # durée manquante
    publier("cycle", '{"evenement": "fin_cycle", "duree": "rapide"}')    # durée qui n'est pas un nombre
    publier("cycle", '["fin_cycle", 7, 18.2]')                           # liste au lieu d'un objet
    publier("cycle", "")                                                 # message vide


def production(nombre):
    """Plusieurs cycles à la suite, un toutes les 2 secondes ; un sur dix finit en défaut."""
    etat("en_cycle")
    for i in range(nombre):
        debut_cycle()
        time.sleep(2)
        if random.random() < 0.1:
            defaut()
        else:
            fin_cycle()
    etat("arrete")


def rafale():
    """1000 fins de cycle à la suite : le collecteur doit toutes les enregistrer."""
    global piece
    for i in range(1000):
        piece = piece + 1
        fin_cycle()


# --- Connexion au broker -----------------------------------------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_simulateur")
try:
    client.connect(BROKER, 1883)
except OSError as e:
    print(f"Broker {BROKER} injoignable : {e}")
    raise SystemExit(1)
client.loop_start()
time.sleep(1)                          # le temps que le broker accepte la connexion
if not client.is_connected():
    print("Connexion refusée par le broker : vérifier BROKER")
    raise SystemExit(1)

# --- Le menu ---------------------------------------------------------------------------
while True:
    print(MENU)
    choix = input("Votre choix : ").strip()
    if choix == "1":
        debut_cycle()
        fin_cycle()
    elif choix == "2":
        debut_cycle()
    elif choix == "3":
        fin_cycle()
    elif choix == "4":
        etat(input("  État (en_cycle, attente, arrete) : ").strip() or "en_cycle")
    elif choix == "5":
        defaut()
    elif choix == "6":
        tache()
    elif choix == "7":
        messages_mal_formes()
    elif choix == "8":
        production(int(input("  Nombre de cycles : ") or "10"))
    elif choix == "9":
        rafale()
    elif choix == "10":
        sujet = input(f"  Sujet (après cellule/{EQUIPE}/) : ").strip() or "essai"
        publier(sujet, input("  Message : "))
    elif choix == "0":
        break
    else:
        print("  choix inconnu")

client.loop_stop()
client.disconnect()
