#!/usr/bin/env python3
"""Vérifie l'installation des bibliothèques du projet sur le robot Ned2.

À lancer sur le robot, avec le lanceur (qui charge les bibliothèques et ROS) :
    ~/cellule/lancer.sh ~/cellule/test.py
    ~/cellule/lancer.sh ~/cellule/test.py --broker 192.168.1.10
    ~/cellule/lancer.sh ~/cellule/test.py --robot

Rien ne bouge : l'option --robot lit seulement les axes et le capteur DI5.
"""
import argparse
import os
import platform
import shutil
import socket
import sys
import threading

DOSSIER_LIBS = os.path.expanduser("~/cellule/libs")
PORT_API = 3000

# (module à importer, nom du paquet, version minimale)
BIBLIOTHEQUES = [
    ("flask", "Flask", (2, 0)),
    ("werkzeug", "Werkzeug", (2, 0)),
    ("jinja2", "Jinja2", (3, 0)),
    ("markupsafe", "MarkupSafe", (2, 0)),
    ("itsdangerous", "itsdangerous", (2, 0)),
    ("click", "click", (8, 0)),
    ("blinker", "blinker", (1, 6)),
    ("paho.mqtt", "paho-mqtt", (2, 0)),
]

bilan = {"OK": 0, "ÉCHEC": 0, "ATTENTION": 0}


def afficher(statut, message):
    if statut in bilan:
        bilan[statut] += 1
    print("[{:<9}] {}".format(statut, message))


def titre(texte):
    print("\n== " + texte)


def version_tuple(texte):
    nombres = []
    for morceau in texte.split(".")[:2]:
        chiffres = "".join(c for c in morceau if c.isdigit())
        nombres.append(int(chiffres or 0))
    return tuple(nombres)


def verifier_python():
    titre("Python")
    version = platform.python_version()
    statut = "OK" if sys.version_info >= (3, 8) else "ÉCHEC"
    afficher(statut, "Python {} ({}), architecture {}".format(version, sys.executable, platform.machine()))


def verifier_bibliotheques():
    titre("Bibliothèques")
    from importlib import import_module
    from importlib.metadata import version as version_paquet

    for module, paquet, minimum in BIBLIOTHEQUES:
        try:
            mod = import_module(module)
            version = version_paquet(paquet)
        except Exception as e:
            afficher("ÉCHEC", "{} : {}".format(paquet, e))
            continue
        if version_tuple(version) < minimum:
            afficher("ÉCHEC", "{} {} : version {}.{} au moins attendue".format(paquet, version, *minimum))
            continue
        emplacement = os.path.dirname(getattr(mod, "__file__", None) or list(mod.__path__)[0])
        if emplacement.startswith(DOSSIER_LIBS):
            afficher("OK", "{} {}".format(paquet, version))
        else:
            afficher("ATTENTION", "{} {} chargé depuis {} (lancer avec ~/cellule/lancer.sh)".format(
                paquet, version, emplacement))


def verifier_flask():
    titre("Essai de Flask (sans réseau)")
    try:
        from flask import Flask, jsonify, render_template_string

        app = Flask("test_installation")

        @app.get("/requetes/etat")
        def etat():
            return jsonify(statut="au_repos")

        reponse = app.test_client().get("/requetes/etat")
        assert reponse.status_code == 200 and reponse.get_json() == {"statut": "au_repos"}
        with app.app_context():
            assert render_template_string("{{ x }}", x="<b>") == "&lt;b&gt;"
        afficher("OK", "route GET, réponse JSON et gabarit Jinja2")
    except Exception as e:
        afficher("ÉCHEC", "Flask : {!r}".format(e))


def verifier_paho():
    titre("Essai de paho-mqtt (sans réseau)")
    try:
        from paho.mqtt.client import CallbackAPIVersion, Client

        Client(CallbackAPIVersion.VERSION2, client_id="test_installation")
        afficher("OK", "création d'un client MQTT (API de rappel version 2)")
    except Exception as e:
        afficher("ÉCHEC", "paho-mqtt : {!r}".format(e))


def verifier_ros():
    titre("Python ROS Wrapper")
    try:
        import rospy  # noqa: F401
        from niryo_robot_python_ros_wrapper.ros_wrapper import NiryoRosWrapper  # noqa: F401

        afficher("OK", "rospy et NiryoRosWrapper importés")
        return True
    except Exception as e:
        afficher("ÉCHEC", "{!r} : environnement ROS non chargé (lancer avec ~/cellule/lancer.sh)".format(e))
        return False


def verifier_robot():
    titre("Connexion au robot (ROS)")
    try:
        import rospy
        from niryo_robot_python_ros_wrapper.ros_wrapper import NiryoRosWrapper

        rospy.init_node("test_installation", anonymous=True)
        n = NiryoRosWrapper()
        axes = ", ".join("{:.2f}".format(a) for a in n.get_joints())
        afficher("OK", "axes (rad) : " + axes)
        di5 = n.digital_read("DI5")
        afficher("OK", "DI5 = {} ({} avec un capteur câblé HIGH sans pièce)".format(
            "HIGH" if di5 else "LOW", "pas de pièce" if di5 else "pièce détectée"))
    except Exception as e:
        afficher("ÉCHEC", "robot : {!r}".format(e))


def verifier_port(port):
    titre("Port de l'API")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", port))
        afficher("OK", "port {} libre pour l'API".format(port))
    except OSError:
        afficher("ÉCHEC", "port {} déjà utilisé (une API est-elle déjà lancée ? voir ss -tlnp)".format(port))
    finally:
        s.close()


def verifier_broker(hote, port):
    titre("Broker MQTT {}:{}".format(hote, port))
    from paho.mqtt.client import CallbackAPIVersion, Client

    connecte = threading.Event()
    resultat = {}

    def on_connect(client, userdata, flags, reason_code, properties):
        resultat["code"] = reason_code
        connecte.set()

    client = Client(CallbackAPIVersion.VERSION2, client_id="test_installation")
    client.on_connect = on_connect
    try:
        client.connect(hote, port, keepalive=10)
    except Exception as e:
        afficher("ÉCHEC", "connexion impossible : {!r}".format(e))
        return
    client.loop_start()
    try:
        if not connecte.wait(5):
            afficher("ÉCHEC", "pas de réponse du broker en 5 s")
        elif resultat["code"].is_failure:
            afficher("ÉCHEC", "connexion refusée : {}".format(resultat["code"]))
        else:
            afficher("OK", "connexion acceptée")
    finally:
        client.disconnect()
        client.loop_stop()


def verifier_outils():
    titre("Outils pour lancer un programme en arrière-plan")
    for outil in ("tmux", "screen", "nohup"):
        chemin = shutil.which(outil)
        print("[{:<9}] {} : {}".format("INFO", outil, chemin or "absent"))


def main():
    parser = argparse.ArgumentParser(description="Vérifie l'installation du projet sur le robot Ned2.")
    parser.add_argument("--broker", metavar="HOTE", help="tester aussi la connexion au broker MQTT")
    parser.add_argument("--port-mqtt", type=int, default=1883, help="port du broker (1883)")
    parser.add_argument("--port-api", type=int, default=PORT_API, help="port de l'API ({})".format(PORT_API))
    parser.add_argument("--robot", action="store_true", help="se connecter au robot (lit les axes et DI5)")
    parser.add_argument("--sans-ros", action="store_true", help="ne pas tester ROS (essai sur un PC)")
    args = parser.parse_args()

    verifier_python()
    verifier_bibliotheques()
    verifier_flask()
    verifier_paho()
    if not args.sans_ros and verifier_ros() and args.robot:
        verifier_robot()
    verifier_port(args.port_api)
    if args.broker:
        verifier_broker(args.broker, args.port_mqtt)
    verifier_outils()

    titre("Bilan")
    print("{} OK, {} attention, {} échec".format(bilan["OK"], bilan["ATTENTION"], bilan["ÉCHEC"]))
    sys.exit(1 if bilan["ÉCHEC"] else 0)


if __name__ == "__main__":
    main()
