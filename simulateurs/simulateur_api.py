#!/usr/bin/env python3
"""Simulateur de l'API du robot : les mêmes endpoints que l'API du robot (api_robot/api_robot.py), sans robot.

Chaque appel est affiché (endpoint et paramètres), puis la tâche est simulée par une attente :
le temps que mettrait le robot. Un message MQTT est envoyé au début et à la fin de chaque tâche.
Comme sur le robot, une demande qui arrive pendant une tâche est refusée (code 409), et
GET /robot/etat répond tout de suite, avec la tâche en cours.

Lancement : python3 simulateur_api.py
Essai :     curl -X POST http://127.0.0.1:5001/robot/ledring/vert
"""
import json
import random
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from flask import Flask, request

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1e1"                        # identifiant de l'équipe, aussi compte MQTT
MOT_DE_PASSE = "mot-de-passe-equipe"   # mot de passe MQTT de l'équipe ; "" pour un broker sans mot de passe
BROKER = "localhost"                   # "192.168.10.10" depuis un poste du fab lab, ou un broker public
PORT_API = 5001                        # 5000 + numéro de l'équipe (5001 à 5008)
COULEURS = ["rouge", "vert", "bleu", "jaune", "blanc"]

app = Flask(__name__)
app.json.ensure_ascii = False          # accents lisibles dans les réponses JSON


# --- MQTT : un message au début et à la fin de chaque tâche -----------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_simulateur_api")
if MOT_DE_PASSE:                       # pas de compte sur un broker sans mot de passe
    client.username_pw_set(EQUIPE, MOT_DE_PASSE)
client.connect_async(BROKER, 1883)     # l'API démarre même si le broker est absent
client.loop_start()


def publier(evenement, tache, **parametres):
    message = {"evenement": evenement, "tache": tache, **parametres,
               "horodatage": datetime.now().isoformat(timespec="seconds")}
    client.publish(f"cellule/{EQUIPE}/tache", json.dumps(message), qos=1)
    print("  MQTT :", message)


# --- Une tâche à la fois -------------------------------------------------------
tache_en_cours = None                  # nom de la tâche en cours, None quand le robot est libre
verrou = threading.Lock()              # deux demandes simultanées ne peuvent pas réserver le robot


def commencer(tache, **parametres):
    """Réserve le robot pour la tâche et publie son début. Renvoie False si le robot est occupé."""
    global tache_en_cours
    with verrou:
        if tache_en_cours is not None:
            return False
        tache_en_cours = tache
    publier("debut_tache", tache, **parametres)
    return True


def terminer(tache, erreur=None, **parametres):
    """Libère le robot, publie la fin de la tâche (réussie ou en erreur) et renvoie la réponse."""
    global tache_en_cours
    tache_en_cours = None
    if erreur is not None:
        publier("fin_tache", tache, statut="erreur", erreur=str(erreur), **parametres)
        return {"tache": tache, **parametres, "statut": "erreur", "erreur": str(erreur)}, 500
    publier("fin_tache", tache, statut="terminee", **parametres)
    return {"tache": tache, **parametres, "statut": "terminee"}


def occupe():
    """Réponse quand une tâche est déjà en cours."""
    return {"erreur": f"robot occupé : tâche {tache_en_cours} en cours", "tache_en_cours": tache_en_cours}, 409


@app.before_request
def afficher_appel():
    """Affiche chaque appel reçu : endpoint et paramètres."""
    print(f"{request.method} {request.path}  paramètres : {request.view_args}")


# --- Les tâches simulées : une fonction par tâche, du même nom que l'endpoint ---
def etat():
    return {
        "axes": [0.0, 0.3, -1.3, 0.0, 0.0, 0.0],
        "pose": [0.14, 0.0, 0.203, 0.0, 0.759, 0.0],
        "di5": random.choice(["HIGH", "LOW"]),
        "calibration_necessaire": False,
        "temperature_raspberry": random.randint(45, 60),
        "temperatures_moteurs": [random.randint(30, 45) for i in range(6)],
        "simulation": True,
    }


def home():
    time.sleep(4)                      # le robot met environ 4 s pour revenir en position home


def autocalibrate():
    time.sleep(20)                     # une calibration dure environ 20 s


def ledring(couleur):
    time.sleep(2)                      # l'anneau clignote pendant 2 s


# --- Les endpoints : chacun appelle la fonction du même nom ----------------------
@app.get("/robot/etat")
def route_etat():
    return {**etat(), "tache_en_cours": tache_en_cours}


@app.post("/robot/home")
def route_home():
    if not commencer("home"):
        return occupe()
    try:
        home()
    except Exception as e:
        return terminer("home", erreur=e)
    return terminer("home")


@app.post("/robot/autocalibrate")
def route_autocalibrate():
    if not commencer("autocalibrate"):
        return occupe()
    try:
        autocalibrate()
    except Exception as e:
        return terminer("autocalibrate", erreur=e)
    return terminer("autocalibrate")


@app.post("/robot/ledring/<couleur>")
def route_ledring(couleur):
    if couleur not in COULEURS:
        return {"erreur": f"couleur inconnue : {couleur}", "couleurs": COULEURS}, 400
    if not commencer("ledring", couleur=couleur):
        return occupe()
    try:
        ledring(couleur)
    except Exception as e:
        return terminer("ledring", erreur=e, couleur=couleur)
    return terminer("ledring", couleur=couleur)


# --- Ajouter une tâche : copier ce modèle et remplacer « cycle » ----------------
#
# def cycle():
#     time.sleep(18)                   # durée de la tâche sur le vrai robot
#
# @app.post("/robot/cycle")
# def route_cycle():
#     if not commencer("cycle"):
#         return occupe()
#     try:
#         cycle()
#     except Exception as e:
#         return terminer("cycle", erreur=e)
#     return terminer("cycle")


# threaded=True : les requêtes sont traitées en parallèle, pour que GET /robot/etat
# réponde pendant une tâche ; commencer() refuse une seconde tâche
app.run(host="0.0.0.0", port=PORT_API, threaded=True)
