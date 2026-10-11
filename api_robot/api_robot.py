#!/usr/bin/env python3
"""API du robot Ned2 : un endpoint par tâche, un message MQTT au début et à la fin de chaque tâche.

    GET  /robot/etat                 état du robot, avec la tâche en cours
    POST /robot/home                 retour à la position home
    POST /robot/autocalibrate        calibration automatique
    POST /robot/ledring/<couleur>    clignotement de l'anneau de LED

Une seule tâche à la fois : une demande qui arrive pendant une tâche est refusée (code 409).
GET /robot/etat répond tout de suite, même pendant une tâche.

Lancement, sur le robot : ~/cellule/lancer.sh api_robot.py
Essai, depuis un poste :  curl -X POST http://192.168.10.21:3000/robot/ledring/vert
"""
import json
import threading
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
app.json.ensure_ascii = False          # accents lisibles dans les réponses JSON


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
        return {"erreur": f"couleur inconnue : {couleur}", "couleurs": list(COULEURS)}, 400
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
#     n.move_pose(...)                 # les appels au robot, repris de l'export de Niryo Studio
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
