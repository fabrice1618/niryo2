#!/bin/bash
# Serveur du module (NUC d'ISTP ou de l'IRUP) : environnement Python commun /opt/cellule/venv
# (Flask, paho-mqtt, requests), placé en tête du PATH de tous les comptes, avec une copie
# des paquets dans /opt/cellule/paquets pour une réinstallation sans Internet.
# Internet est nécessaire pendant l'exécution.
#
# Usage : sudo ./nuc_python.sh
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }

python3 -m venv /opt/cellule/venv
/opt/cellule/venv/bin/pip install flask paho-mqtt requests
echo 'export PATH=/opt/cellule/venv/bin:$PATH' > /etc/profile.d/cellule.sh
/opt/cellule/venv/bin/pip download -d /opt/cellule/paquets flask paho-mqtt requests
