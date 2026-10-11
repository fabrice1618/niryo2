#!/usr/bin/env python3
"""API du robot Ned2 : un endpoint par tâche, un message MQTT au début et à la fin de chaque tâche.

    GET  /robot/etat                 état du robot
    POST /robot/home                 retour à la position home
    POST /robot/autocalibrate        calibration automatique
    POST /robot/ledring/<couleur>    clignotement de l'anneau de LED

Lancement, sur le robot : ~/cellule/lancer.sh api_robot.py
Essai, depuis un poste :  curl -X POST http://192.168.10.21:3000/robot/ledring/vert
"""
import json
from datetime import datetime

import paho.mqtt.client as mqtt
import rospy
from flask import Flask, request
from niryo_robot_python_ros_wrapper.ros_wrapper import *

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1e1"                        # identifiant de l'équipe, aussi compte MQTT
MOT_DE_PASSE = "mot-de-passe-equipe"   # mot de passe MQTT de l'équipe
BROKER = "192.168.10.10"               # serveur du module (le Raspberry Pi d'ISTP est en .11)
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


# --- MQTT : un message au début et à la fin de chaque tâche -----------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_api_robot")
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


# --- Les tâches : une fonction par tâche, du même nom que l'endpoint -----------
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
    }


def home():
    n.move_joints(*JOINTS_HOME)


def autocalibrate():
    n.calibrate_auto()


def ledring(couleur):
    # wait=True : la fonction attend la fin du clignotement (10 fois 0,2 s)
    n.led_ring.flashing(COULEURS[couleur], period=0.2, iterations=10, wait=True)


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
        return {"erreur": f"couleur inconnue : {couleur}", "couleurs": list(COULEURS)}, 400
    publier("debut_tache", "ledring", couleur=couleur)
    ledring(couleur)
    publier("fin_tache", "ledring", couleur=couleur)
    return {"tache": "ledring", "couleur": couleur, "statut": "terminee"}


# --- Ajouter une tâche : copier ce modèle et remplacer « cycle » ----------------
#
# def cycle():
#     n.move_pose(...)                 # les appels au robot, repris de l'export de Niryo Studio
#
# @app.post("/robot/cycle")
# def route_cycle():
#     publier("debut_tache", "cycle")
#     cycle()
#     publier("fin_tache", "cycle")
#     return {"tache": "cycle", "statut": "terminee"}


# threaded=False : une seule requête à la fois, le robot ne fait qu'une chose à la fois
app.run(host="0.0.0.0", port=PORT_API, threaded=False)
