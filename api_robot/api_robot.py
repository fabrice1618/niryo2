#!/usr/bin/env python3
"""API du robot Ned2 : un endpoint par tâche, un message MQTT au début et à la fin de chaque tâche.

    GET  /robot/etat                 état du robot, avec la tâche en cours
    POST /robot/home                 retour à la position home
    POST /robot/autocalibrate        calibration automatique
    POST /robot/ledring/<couleur>    clignotement de l'anneau de LED

Une seule tâche à la fois : une demande qui arrive pendant une tâche est refusée (code 409).
GET /robot/etat répond tout de suite, même pendant une tâche.

Lancement, sur le robot : ~/cellule/lancer.sh api_robot.py
Essai, depuis un poste :  curl -X POST http://192.168.1.21:3000/robot/ledring/vert
"""
import json
from datetime import datetime

import paho.mqtt.client as mqtt
import rospy
from flask import Flask, request
from niryo_robot_python_ros_wrapper.ros_wrapper import *

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1"                        # identifiant de l'équipe, dans les topics MQTT
BROKER = "192.168.1.10"               # serveur du module (le Raspberry Pi d'ISTP est en .11)
PORT_API = 3000                        # le port 5000 du robot est pris par le logiciel de Niryo
JOINTS_HOME = [0.0, 0.3, -1.3, 0.0, 0.0, 0.0]       # position home : angles des 6 axes (radians)
COULEURS = {                           # [rouge, vert, bleu, 0], comme dans l'export de Niryo Studio
    "rouge": [255, 0, 0, 0],
    "vert": [0, 255, 0, 0],
    "bleu": [0, 0, 255, 0],
    "jaune": [255, 255, 0, 0],
    "blanc": [255, 255, 255, 0],
}

rospy.init_node(f"cellule_api_{EQUIPE}")   # nom propre à l'API, différent de celui de Niryo Studio
n = NiryoRosWrapper()
app = Flask(__name__)
app.json.ensure_ascii = False          # accents lisibles dans les réponses JSON

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_api_robot")
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
    """Tâche réussie : libère le robot, publie la fin de la tâche et renvoie la réponse."""
    global tache_en_cours
    tache_en_cours = None
    message = {"evenement": "fin_tache", "tache": tache, "statut": "terminee"}
    reponse = {"tache": tache, "statut": "terminee"}
    if couleur:
        message["couleur"] = couleur
        reponse["couleur"] = couleur
    publier(message)
    return reponse


def echec(tache, erreur, couleur=None):
    """Erreur du robot : libère le robot, publie la fin de la tâche en erreur et renvoie la réponse (500)."""
    global tache_en_cours
    tache_en_cours = None
    message = {"evenement": "fin_tache", "tache": tache, "statut": "erreur", "erreur": str(erreur)}
    reponse = {"tache": tache, "statut": "erreur", "erreur": str(erreur)}
    if couleur:
        message["couleur"] = couleur
        reponse["couleur"] = couleur
    publier(message)
    return reponse, 500


def occupe():
    """Réponse quand une tâche est déjà en cours."""
    return {"erreur": f"robot occupé : tâche {tache_en_cours} en cours", "tache_en_cours": tache_en_cours}, 409


@app.before_request
def afficher_appel():
    """Affiche chaque appel reçu, avant de le traiter."""
    print(request.method, request.path)


# --- Les endpoints : une tâche chacun -------------------------------------------------
@app.get("/robot/etat")
def etat():
    """Lit l'état du robot, sans rien faire bouger (script 8)."""
    materiel = n.get_hardware_status()
    return {
        "axes": list(n.get_joints()),                        # radians
        "pose": list(n.get_pose_as_list()),                  # x, y, z (m), roll, pitch, yaw (rad)
        "di5": "HIGH" if n.digital_read("DI5") else "LOW",   # HIGH : pas de pièce (à vérifier)
        "calibration_necessaire": materiel.calibration_needed,
        "temperature_raspberry": materiel.rpi_temperature,
        "temperatures_moteurs": list(materiel.temperatures),
        "tache_en_cours": tache_en_cours,
    }


@app.post("/robot/home")
def home():
    if tache_en_cours is not None:     # une tâche à la fois
        return occupe()
    commencer("home")
    try:
        n.move_joints(*JOINTS_HOME)
    except Exception as e:             # par exemple un mouvement demandé avant la calibration
        return echec("home", e)
    return terminer("home")


@app.post("/robot/autocalibrate")
def autocalibrate():
    if tache_en_cours is not None:
        return occupe()
    commencer("autocalibrate")
    try:
        n.calibrate_auto()
    except Exception as e:
        return echec("autocalibrate", e)
    return terminer("autocalibrate")


@app.post("/robot/ledring/<couleur>")
def ledring(couleur):
    if couleur not in COULEURS:
        return {"erreur": f"couleur inconnue : {couleur}", "couleurs": list(COULEURS)}, 400
    if tache_en_cours is not None:
        return occupe()
    commencer("ledring", couleur)
    try:
        # wait=True : attend la fin du clignotement (10 fois 0,2 s)
        n.led_ring.flashing(COULEURS[couleur], period=0.2, iterations=10, wait=True)
    except Exception as e:
        return echec("ledring", e, couleur)
    return terminer("ledring", couleur)


# --- Ajouter une tâche : copier ce modèle et remplacer « cycle » ----------------
#
# @app.post("/robot/cycle")
# def cycle():
#     if tache_en_cours is not None:
#         return occupe()
#     commencer("cycle")
#     try:
#         n.move_pose(...)             # les appels au robot, repris de l'export de Niryo Studio
#     except Exception as e:
#         return echec("cycle", e)
#     return terminer("cycle")


# Flask traite les requêtes en parallèle : GET /robot/etat répond même pendant une tâche
app.run(host="0.0.0.0", port=PORT_API)
