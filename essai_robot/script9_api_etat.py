#!/usr/bin/env python3
"""Script 9 (corrigé de l'énoncé 9, première partie) : l'endpoint GET /robot/etat.

Il réutilise la fonction lire_etat du script 8 : l'état est lu directement sur le robot
à chaque requête, sans rien faire bouger.

Sur le robot : ~/cellule/lancer.sh script9_api_etat.py
Sur un poste : curl http://192.168.1.21:3000/robot/etat
"""
import rospy
from flask import Flask, jsonify
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import PORT_API
from script8_etat_robot import lire_etat

rospy.init_node("essai_script9")
n = NiryoRosWrapper()

app = Flask(__name__)
app.json.ensure_ascii = False          # accents lisibles dans la réponse JSON


@app.get("/robot/etat")
def robot_etat():
    return jsonify(lire_etat(n))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT_API)
