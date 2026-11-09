#!/bin/bash
# NUC de l'IRUP : installe Grafana (dépôt officiel de Grafana Labs) et l'adaptateur SQLite
# (frser-sqlite-datasource). Internet est nécessaire pendant l'exécution.
# Versions essayées : Grafana 13.2 et adaptateur 4.0.
#
# Usage : sudo ./irup_grafana_installer.sh
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }

apt install -y apt-transport-https wget gnupg
mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor --yes -o /etc/apt/keyrings/grafana.gpg
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
    > /etc/apt/sources.list.d/grafana.list
apt update
apt install -y grafana
grafana cli plugins install frser-sqlite-datasource
