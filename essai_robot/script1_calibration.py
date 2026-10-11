#!/usr/bin/env python3
"""Script 1 : calibrer le robot, avec un signal lumineux et sonore au début et à la fin.

Sur le robot : ~/cellule/lancer.sh script1_calibration.py
"""
import rospy
from niryo_robot_python_ros_wrapper.ros_wrapper import *

rospy.init_node("essai_script1")       # nom propre au script, pas celui de Niryo Studio
n = NiryoRosWrapper()                  # n représente le robot


def signal_debut():
    n.led_ring.flashing([102, 255, 255, 0], period=0.5, iterations=3, wait=False)
    n.sound.play("ready.wav", wait_end=True)


def signal_fin():
    n.led_ring.flashing([51, 255, 51, 0], period=0.5, iterations=3, wait=False)
    n.sound.play("stop.wav", wait_end=True)


signal_debut()
n.request_new_calibration()            # oublie la calibration en cours...
n.calibrate_auto()                     # ... et en refait une complète (le bras bouge)
signal_fin()
print("Calibration terminée")
