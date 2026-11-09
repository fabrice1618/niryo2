#!/bin/bash
# Serveur du module (NUC d'ISTP ou de l'IRUP) : broker Mosquitto ouvert sur le port 1883,
# sans compte ni mot de passe (réseau local du module), lancé à chaque démarrage.
# Le paquet mosquitto doit être installé.
#
# Usage : sudo ./nuc_mosquitto.sh
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }

cat > /etc/mosquitto/conf.d/cellule.conf <<'CONF'
listener 1883 0.0.0.0
allow_anonymous true
CONF

systemctl enable mosquitto
systemctl restart mosquitto
ss -tlnp | grep ':1883 '
