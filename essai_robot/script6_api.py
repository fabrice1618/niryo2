#!/usr/bin/env python3
"""Script 6 : une API web sur le robot. POST /led fait clignoter l'anneau de LED.

Sur le robot : ~/cellule/lancer.sh script6_api.py
Sur un poste : curl -X POST http://192.168.1.21:3000/led -H "Content-Type: application/json" -d '{"couleur": "bleu"}'
"""
import rospy
from flask import Flask, jsonify, request
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import PORT_API, COULEURS

rospy.init_node("essai_script6")       # avant Flask, dans le programme principal
n = NiryoRosWrapper()

app = Flask(__name__)


@app.post("/led")
def commande_led():
    donnees = request.get_json(silent=True) or {}
    couleur = str(donnees.get("couleur", "")).lower()
    if couleur not in COULEURS:
        return jsonify(erreur="envoyer {\"couleur\": \"rouge\"}, \"vert\" ou \"bleu\""), 400
    n.led_ring.flashing(COULEURS[couleur], period=0.2, iterations=10, wait=False)
    return jsonify(statut="ok", couleur=couleur)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_API)     # toutes les interfaces : joignable depuis le réseau
