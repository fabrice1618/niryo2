#!/usr/bin/env python3
"""Simulateur de l'API du robot : les mêmes endpoints que l'API du robot (api_robot/api_robot.py), sans robot.

Chaque appel est affiché (endpoint et paramètres), puis la tâche est simulée par une attente :
le temps que mettrait le robot. Un message MQTT est envoyé au début et à la fin de chaque tâche.

Lancement : python3 simulateur_api.py
Essai :     curl -X POST http://127.0.0.1:5001/robot/ledring/vert
"""
import json
import random
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
    return etat()


@app.post("/robot/home")
def route_home():
    publier("debut_tache", "home")
    home()
    publier("fin_tache", "home")
    return {"tache": "home", "statut": "terminee"}


@app.post("/robot/autocalibrate")
def route_autocalibrate():
    publier("debut_tache", "autocalibrate")
    autocalibrate()
    publier("fin_tache", "autocalibrate")
    return {"tache": "autocalibrate", "statut": "terminee"}


@app.post("/robot/ledring/<couleur>")
def route_ledring(couleur):
    if couleur not in COULEURS:
        return {"erreur": f"couleur inconnue : {couleur}", "couleurs": COULEURS}, 400
    publier("debut_tache", "ledring", couleur=couleur)
    ledring(couleur)
    publier("fin_tache", "ledring", couleur=couleur)
    return {"tache": "ledring", "couleur": couleur, "statut": "terminee"}


# --- Ajouter une tâche : copier ce modèle et remplacer « cycle » ----------------
#
# def cycle():
#     time.sleep(18)                   # durée de la tâche sur le vrai robot
#
# @app.post("/robot/cycle")
# def route_cycle():
#     publier("debut_tache", "cycle")
#     cycle()
#     publier("fin_tache", "cycle")
#     return {"tache": "cycle", "statut": "terminee"}


# threaded=False : une seule requête à la fois, comme le robot qui ne fait qu'une chose à la fois
app.run(host="0.0.0.0", port=PORT_API, threaded=False)
