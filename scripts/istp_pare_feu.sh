#!/bin/bash
# NUC d'ISTP : active le pare-feu (facultatif) en ouvrant SSH, MQTT, le serveur DHCP de la salle,
# les API simulées (5001 à 5008) et les sites des équipes (8001 à 8008).
# Attention : à lancer avec un écran et un clavier à portée de main.
#
# Usage : sudo ./istp_pare_feu.sh
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }

ufw allow 22/tcp
ufw allow 1883/tcp
ufw allow 67/udp           # serveur DHCP (salle D3.10)
ufw allow 5001:5008/tcp
ufw allow 8001:8008/tcp
ufw --force enable
ufw status
