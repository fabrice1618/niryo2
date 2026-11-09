#!/bin/bash
# NUC de l'IRUP : donne à Grafana (compte système « grafana ») le strict nécessaire pour lire
# la base ~/supervision/cellule.db de chaque équipe : traverser les dossiers (sans pouvoir
# les lister) et lire les fichiers créés ensuite dans supervision/. Les autres équipes n'ont
# toujours aucun accès. À relancer si une équipe supprime et recrée son dossier supervision.
#
# Usage : sudo ./irup_grafana_acl.sh [fichier_comptes]     (défaut : comptes_irup.txt, à côté du script)
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }
comptes=${1:-$(dirname "$(readlink -f "$0")")/comptes_irup.txt}

grep -v '^#' "$comptes" | while IFS=: read -r equipe mdp; do
    sudo -u "$equipe" mkdir -p "/home/$equipe/supervision"
    setfacl -m u:grafana:x "/home/$equipe" "/home/$equipe/supervision"
    setfacl -d -m u:grafana:r "/home/$equipe/supervision"
    # Base déjà existante : l'ACL par défaut ne vaut que pour les fichiers créés après elle
    if [ -f "/home/$equipe/supervision/cellule.db" ]; then
        setfacl -m u:grafana:r "/home/$equipe/supervision/cellule.db"
    fi
    echo "$equipe : ok"
done
