#!/usr/bin/env python3
"""Script 5 : recevoir un ordre par MQTT et faire clignoter l'anneau de LED dans la couleur reçue.

Sur le robot : ~/cellule/lancer.sh script5_mqtt_reception.py
Sur un poste : mosquitto_pub -h 192.168.10.10 -t cellule/g1e1/led -m rouge
"""
import time

import paho.mqtt.client as mqtt
import rospy
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import BROKER, PORT_MQTT, EQUIPE, TOPIC_LED, COULEURS

rospy.init_node("essai_script5")
n = NiryoRosWrapper()


def clignoter(couleur):
    """Fait clignoter l'anneau 2 secondes ; renvoie False si la couleur est inconnue."""
    if couleur not in COULEURS:
        print("Couleur inconnue :", couleur)
        return False
    n.led_ring.flashing(COULEURS[couleur], period=0.2, iterations=10, wait=False)   # 10 x 0,2 s
    return True


# --- Fonctions appelées par paho-mqtt -----------------------------------
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connecté au broker :", reason_code)
    client.subscribe(TOPIC_LED)        # (ré)abonnement à chaque connexion


def on_message(client, userdata, msg):
    couleur = msg.payload.decode().strip().lower()
    print("Reçu sur", msg.topic, ":", couleur)
    clignoter(couleur)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_script5")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT_MQTT, keepalive=60)
client.loop_start()

# --- Le programme principal attend : tout se passe dans on_message ------
try:
    while not rospy.is_shutdown():
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
