#!/usr/bin/env python3
"""Lance un programme du projet, depuis la racine du dossier.

    python lancer.py collecteur    enregistre les messages MQTT dans cellule.db
    python lancer.py site          le site web (tableau de bord)
    python lancer.py api           le simulateur d'API du robot
    python lancer.py mqtt          le simulateur de messages MQTT (menu)

Un programme par terminal. Ctrl+C arrête le programme.
Au premier lancement, l'environnement Python (dossier venv) et la base cellule.db sont créés tout seuls.
Les paramètres (équipe, broker, ports) se règlent en tête de chaque programme.
"""
import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.abspath(__file__))
os.chdir(RACINE)                       # la base cellule.db est cherchée dans le dossier courant : toujours la racine

PROGRAMMES = {
    "collecteur": "collecteur/collecteur.py",
    "site": "site_web/supervision.py",
    "api": "simulateurs/simulateur_api.py",
    "mqtt": "simulateurs/simulateur_mqtt.py",
}

if os.name == "nt":                    # Windows
    PYTHON = os.path.join(RACINE, "venv", "Scripts", "python.exe")
else:
    PYTHON = os.path.join(RACINE, "venv", "bin", "python")


def installer_environnement():
    """Crée le dossier venv et y installe les bibliothèques de requirements.txt."""
    print("Première utilisation : installation de l'environnement Python (une à deux minutes, Internet nécessaire)...")
    subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    subprocess.check_call([PYTHON, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Environnement installé.\n")


def executer(script):
    """Lance un script avec l'environnement du projet et attend sa fin."""
    programme = subprocess.Popen([PYTHON, script])
    try:
        programme.wait()
    except KeyboardInterrupt:          # Ctrl+C : le programme le reçoit aussi et s'arrête proprement
        programme.wait()


if len(sys.argv) != 2 or sys.argv[1] not in PROGRAMMES:
    print(__doc__)
    raise SystemExit(1)

if not os.path.exists(PYTHON):
    installer_environnement()

if sys.argv[1] in ("collecteur", "site") and not os.path.exists("cellule.db"):
    executer("collecteur/creer_bdd.py")

executer(PROGRAMMES[sys.argv[1]])
