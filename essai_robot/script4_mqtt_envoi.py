#!/usr/bin/env python3
"""Script 4 : publier un message MQTT chaque seconde depuis le robot.

Sur le robot : ~/cellule/lancer.sh script4_mqtt_envoi.py
Sur un poste : mosquitto_sub -h 192.168.10.10 -u g1e1 -P mot-de-passe-equipe -t 'cellule/g1e1/#' -v
"""
import json
import time
from datetime import datetime

import paho.mqtt.client as mqtt
import rospy
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import BROKER, PORT_MQTT, MQTT_UTILISATEUR, MQTT_MOT_DE_PASSE, EQUIPE, TOPIC_ESSAI

rospy.init_node("essai_script4")
n = NiryoRosWrapper()

# --- Connexion au broker ------------------------------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_script4")
client.username_pw_set(MQTT_UTILISATEUR, MQTT_MOT_DE_PASSE)
client.connect(BROKER, PORT_MQTT, keepalive=60)
client.loop_start()                    # le réseau MQTT est géré en arrière-plan

n.led_ring.flashing([0, 255, 0, 0], period=0.5, iterations=3, wait=False)   # prêt

# --- Un message par seconde ---------------------------------------------
numero = 0
try:
    while not rospy.is_shutdown():
        numero += 1
        message = {
            "evenement": "essai",
            "numero": numero,
            "di5": "HIGH" if n.digital_read("DI5") else "LOW",
            "horodatage": datetime.now().isoformat(timespec="seconds"),
        }
        client.publish(TOPIC_ESSAI, json.dumps(message), qos=1)
        print("Publié :", message)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
