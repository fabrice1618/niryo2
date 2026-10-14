#!/usr/bin/env python3
"""Simulateur de l'API du robot : les mêmes endpoints que l'API du robot (api_robot/api_robot.py), sans robot.

Chaque appel est affiché, puis la tâche est simulée par une attente : le temps que mettrait le robot.
Un message MQTT est envoyé au début et à la fin de chaque tâche.
Comme sur le robot, une demande qui arrive pendant une tâche est refusée (code 409), et
GET /robot/etat répond tout de suite, avec la tâche en cours.

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
EQUIPE = "g1"                        # identifiant de l'équipe, dans les topics MQTT
BROKER = "localhost"                   # "192.168.1.10" depuis un poste du fab lab, ou un broker public
PORT_API = 5001                        # 5000 + numéro de l'équipe (5001 à 5008)
COULEURS = ["rouge", "vert", "bleu", "jaune", "blanc"]

app = Flask(__name__)
app.json.ensure_ascii = False          # accents lisibles dans les réponses JSON

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_simulateur_api")
client.connect_async(BROKER, 1883)     # l'API démarre même si le broker est absent
client.loop_start()

tache_en_cours = None                  # nom de la tâche en cours, None quand le robot est libre


# --- Début et fin des tâches ------------------------------------------------------
def publier(message):
    """Envoie le message sur cellule/<equipe>/tache, avec l'heure."""
    message["horodatage"] = datetime.now().isoformat(timespec="seconds")
    client.publish(f"cellule/{EQUIPE}/tache", json.dumps(message), qos=1)
    print("  MQTT :", message)


def commencer(tache, couleur=None):
    """Note la tâche en cours et publie son début."""
    global tache_en_cours
    tache_en_cours = tache
    message = {"evenement": "debut_tache", "tache": tache}
    if couleur:
        message["couleur"] = couleur
    publier(message)


def terminer(tache, couleur=None):
    """Libère le robot, publie la fin de la tâche et renvoie la réponse."""
    global tache_en_cours
    tache_en_cours = None
    message = {"evenement": "fin_tache", "tache": tache, "statut": "terminee"}
    reponse = {"tache": tache, "statut": "terminee"}
    if couleur:
        message["couleur"] = couleur
        reponse["couleur"] = couleur
    publier(message)
    return reponse


def occupe():
    """Réponse quand une tâche est déjà en cours."""
    return {"erreur": f"robot occupé : tâche {tache_en_cours} en cours", "tache_en_cours": tache_en_cours}, 409


@app.before_request
def afficher_appel():
    """Affiche chaque appel reçu, avant de le traiter."""
    print(request.method, request.path)


# --- Les endpoints : une tâche simulée par une attente ------------------------------
@app.get("/robot/etat")
def etat():
    return {
        "axes": [0.0, 0.3, -1.3, 0.0, 0.0, 0.0],
        "pose": [0.14, 0.0, 0.203, 0.0, 0.759, 0.0],
        "di5": random.choice(["HIGH", "LOW"]),
        "calibration_necessaire": False,
        "temperature_raspberry": random.randint(45, 60),
        "temperatures_moteurs": [random.randint(30, 45) for i in range(6)],
        "simulation": True,
        "tache_en_cours": tache_en_cours,
    }


@app.post("/robot/home")
def home():
    if tache_en_cours is not None:     # une tâche à la fois
        return occupe()
    commencer("home")
    time.sleep(4)                      # le robot met environ 4 s pour revenir en position home
    return terminer("home")


@app.post("/robot/autocalibrate")
def autocalibrate():
    if tache_en_cours is not None:
        return occupe()
    commencer("autocalibrate")
    time.sleep(20)                     # une calibration dure environ 20 s
    return terminer("autocalibrate")


@app.post("/robot/ledring/<couleur>")
def ledring(couleur):
    if couleur not in COULEURS:
        return {"erreur": f"couleur inconnue : {couleur}", "couleurs": COULEURS}, 400
    if tache_en_cours is not None:
        return occupe()
    commencer("ledring", couleur)
    time.sleep(2)                      # l'anneau clignote pendant 2 s
    return terminer("ledring", couleur)


# --- Ajouter une tâche : copier ce modèle et remplacer « cycle » ----------------
#
# @app.post("/robot/cycle")
# def cycle():
#     if tache_en_cours is not None:
#         return occupe()
#     commencer("cycle")
#     time.sleep(18)                   # durée de la tâche sur le vrai robot
#     return terminer("cycle")


# Flask traite les requêtes en parallèle : GET /robot/etat répond même pendant une tâche
app.run(host="0.0.0.0", port=PORT_API)
