#!/usr/bin/env python3
"""Script 2 : faire tourner le convoyeur jusqu'à ce que le capteur DI5 détecte une pièce.

Sur le robot : ~/cellule/lancer.sh script2_convoyeur.py
"""
import rospy
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import VITESSE_CONVOYEUR

rospy.init_node("essai_script2")
n = NiryoRosWrapper()

n.set_conveyor()                       # active le convoyeur branché sur le robot
n.wait(2)

n.control_conveyor(ConveyorID.ID_1, True, VITESSE_CONVOYEUR, ConveyorDirection.BACKWARD)
try:
    while n.digital_read("DI5"):       # HIGH : pas de pièce devant le capteur
        n.wait(0.1)
    print("Pièce détectée")
finally:
    # arrêt du convoyeur dans tous les cas, même après Ctrl+C
    n.control_conveyor(ConveyorID.ID_1, False, 0, ConveyorDirection.BACKWARD)
