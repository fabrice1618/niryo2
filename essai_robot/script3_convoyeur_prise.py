#!/usr/bin/env python3
"""Script 3 : un cycle complet. Le convoyeur amène la pièce, le robot la prend et la dépose.

Sur le robot : ~/cellule/lancer.sh script3_convoyeur_prise.py
"""
import rospy
from niryo_robot_python_ros_wrapper.ros_wrapper import *

from config import POSE_ATTENTE, POSE_PRISE, POSE_DEPOSE_A, VITESSE_CONVOYEUR

rospy.init_node("essai_script3")
n = NiryoRosWrapper()

n.calibrate_auto()                     # sans effet si le robot est déjà calibré
n.update_tool()                        # détecte la pince


def aller_en_attente():
    n.move_pose(*POSE_ATTENTE)


def attendre_piece():
    """Fait tourner le convoyeur jusqu'à la détection de la pièce."""
    n.control_conveyor(ConveyorID.ID_1, True, VITESSE_CONVOYEUR, ConveyorDirection.BACKWARD)
    try:
        while n.digital_read("DI5"):
            n.wait(0.1)
    finally:
        n.control_conveyor(ConveyorID.ID_1, False, 0, ConveyorDirection.BACKWARD)


def prendre_et_deposer():
    n.pick_from_pose(*POSE_PRISE)      # approche, ouverture, descente, fermeture, retrait
    n.place_from_pose(*POSE_DEPOSE_A)


aller_en_attente()
n.set_conveyor()
n.wait(2)
attendre_piece()
prendre_et_deposer()
aller_en_attente()
print("Cycle terminé")
