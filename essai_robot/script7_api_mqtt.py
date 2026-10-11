#!/usr/bin/env python3
"""Script 7 : API web et MQTT. POST /led fait clignoter l'anneau, puis publie un événement MQTT.

Sur le robot : ~/cellule/lancer.sh script7_api_mqtt.py
Sur un poste :
    mosquitto_sub -h 192.168.10.10 -u g1e1 -P mot-de-passe-equipe -t 'cellule/g1e1/#' -v
    curl -X POST http://192.168.10.21:3000/led -H "Content-Type: application/json" -d '{"couleur": "vert"}'
"""
import json
from datetime import datetime

import paho.mqtt.client as mqtt
import rospy
from flask import Flask, jsonify, request
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import (BROKER, PORT_MQTT, MQTT_UTILISATEUR, MQTT_MOT_DE_PASSE, EQUIPE,
                    TOPIC_ESSAI, PORT_API, COULEURS)

rospy.init_node("essai_script7")
n = NiryoRosWrapper()

# --- MQTT ---------------------------------------------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_script7")
client.username_pw_set(MQTT_UTILISATEUR, MQTT_MOT_DE_PASSE)
client.connect(BROKER, PORT_MQTT, keepalive=60)
client.loop_start()


def publier(evenement, **donnees):
    message = {"evenement": evenement, **donnees,
               "horodatage": datetime.now().isoformat(timespec="seconds")}
    client.publish(TOPIC_ESSAI, json.dumps(message), qos=1)
    print("Publié :", message)


# --- API ----------------------------------------------------------------
app = Flask(__name__)


@app.post("/led")
def commande_led():
    donnees = request.get_json(silent=True) or {}
    couleur = str(donnees.get("couleur", "")).lower()
    if couleur not in COULEURS:
        publier("led_erreur", couleur=couleur)
        return jsonify(erreur="couleur inconnue"), 400
    # wait=True : la fonction ne rend la main qu'à la fin du clignotement (2 s)
    n.led_ring.flashing(COULEURS[couleur], period=0.2, iterations=10, wait=True)
    publier("led_terminee", couleur=couleur)   # publié une fois l'action terminée
    return jsonify(statut="ok", couleur=couleur)


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=PORT_API)
    finally:
        client.loop_stop()
        client.disconnect()
