#!/usr/bin/env python3
"""Script 8 : lire l'état du robot, sans rien faire bouger.

La fonction lire_etat(n) renvoie un dictionnaire prêt à être converti en JSON :
c'est la brique de l'endpoint GET /robot/etat de l'API (énoncé 9).

Sur le robot :
    ~/cellule/lancer.sh script8_etat_robot.py              # une lecture
    ~/cellule/lancer.sh script8_etat_robot.py --boucle 1   # une lecture par seconde (Ctrl+C pour arrêter)
"""
import argparse
import json
import time
from datetime import datetime

import rospy
from niryo_robot_python_ros_wrapper.ros_wrapper import *


def materiel(statut):
    """Met en forme le HardwareStatus du robot (températures, tensions, erreurs des moteurs)."""
    moteurs = [
        {"nom": nom, "temperature": temperature, "tension": round(tension, 2), "erreur": erreur}
        for nom, temperature, tension, erreur in zip(
            statut.motor_names, statut.temperatures, statut.voltages, statut.hardware_errors)
    ]
    return {
        "temperature_raspberry": statut.rpi_temperature,
        "connexion_moteurs": statut.connection_up,
        "calibration_necessaire": statut.calibration_needed,
        "calibration_en_cours": statut.calibration_in_progress,
        "message_erreur": statut.error_message,
        "moteurs": moteurs,
    }


def convoyeurs():
    """Lit l'état des convoyeurs sur le topic ROS de retour d'état (attente de 2 s au plus)."""
    from conveyor_interface.msg import ConveyorFeedbackArray
    retour = rospy.wait_for_message("/niryo_robot/conveyor/feedback", ConveyorFeedbackArray, timeout=2)
    return [
        {"id": c.conveyor_id, "connecte": c.connection_state, "en_marche": c.running,
         "vitesse": c.speed, "sens": c.direction}
        for c in retour.conveyors
    ]


def lire_etat(n):
    """Renvoie l'état du robot sous forme de dictionnaire.

    Chaque valeur est lue à part : si une lecture échoue, la valeur vaut None
    et l'erreur est notée dans "erreurs_lecture", sans bloquer les autres.
    """
    etat = {"horodatage": datetime.now().isoformat(timespec="seconds"), "erreurs_lecture": []}

    def lire(cle, fonction):
        try:
            etat[cle] = fonction()
        except Exception as e:
            etat[cle] = None
            etat["erreurs_lecture"].append(f"{cle} : {e}")

    lire("axes", lambda: [round(a, 3) for a in n.get_joints()])               # radians
    lire("pose", lambda: [round(v, 3) for v in n.get_pose_as_list()])         # x, y, z (m), roll, pitch, yaw (rad)
    lire("mode_apprentissage", n.get_learning_mode)                           # True : bras libre (FreeMotion)
    lire("outil", lambda: int(n.get_current_tool_id()))                       # identifiant de l'outil monté
    lire("di5", lambda: "HIGH" if n.digital_read("DI5") else "LOW")
    etat["piece_detectee"] = None if etat["di5"] is None else etat["di5"] == "LOW"   # polarité à vérifier
    lire("materiel", lambda: materiel(n.get_hardware_status()))
    lire("convoyeurs", convoyeurs)
    return etat


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lit l'état du robot Ned2 (rien ne bouge).")
    parser.add_argument("--boucle", type=float, metavar="SECONDES", help="relire l'état à intervalle régulier")
    args = parser.parse_args()

    rospy.init_node("essai_script8")
    n = NiryoRosWrapper()              # pas de calibrate_auto : le script ne doit rien faire bouger

    try:
        while True:
            print(json.dumps(lire_etat(n), indent=2, ensure_ascii=False))
            if not args.boucle or rospy.is_shutdown():
                break
            time.sleep(args.boucle)
    except KeyboardInterrupt:
        pass
