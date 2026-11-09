#!/bin/bash
# Serveur du module (NUC d'ISTP ou de l'IRUP) : dépose dans /opt/cellule/fournitures, en lecture
# pour tous, les briques remises aux équipes (simulateurs/, collecteur/, site_web/, api_robot/),
# copiées depuis ce dépôt. Un dossier d'autres fournitures (squelette de l'API CQRS,
# gabarits...) peut être ajouté en argument.
#
# Usage : sudo ./nuc_fournitures.sh [dossier_autres_fournitures]
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }
depot=$(dirname "$(dirname "$(readlink -f "$0")")")

mkdir -p /opt/cellule/fournitures
cp -r "$depot"/{simulateurs,collecteur,site_web,api_robot} /opt/cellule/fournitures/
if [ -n "${1:-}" ]; then
    cp -r "$1"/* /opt/cellule/fournitures/
fi
chmod -R a+rX /opt/cellule/fournitures
ls /opt/cellule/fournitures
