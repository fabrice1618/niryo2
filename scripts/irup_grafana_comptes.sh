#!/bin/bash
# NUC de l'IRUP : crée dans Grafana, pour chaque équipe, un compte (mêmes identifiant et mot
# de passe que le compte Linux, rôle « Viewer ») et un dossier de dashboards où elle seule
# peut écrire. Grafana doit tourner (irup_grafana_sources.sh lancé avant).
# Le mot de passe de l'administrateur Grafana (admin_password de grafana.ini) est demandé.
#
# Usage : ./irup_grafana_comptes.sh [fichier_comptes]     (défaut : comptes_irup.txt, à côté du script)
set -euo pipefail

comptes=${1:-$(dirname "$(readlink -f "$0")")/comptes_irup.txt}
read -rsp "Mot de passe de l'administrateur Grafana : " mdp_admin; echo
GF="http://localhost:3000"
JSON="Content-Type: application/json"

grep -v '^#' "$comptes" | while IFS=: read -r equipe mdp; do
    curl -s -u "admin:$mdp_admin" -X POST -H "$JSON" "$GF/api/admin/users" \
         -d "{\"name\":\"${equipe}\",\"login\":\"${equipe}\",\"password\":\"${mdp}\"}"; echo
    curl -s -u "admin:$mdp_admin" -X POST -H "$JSON" "$GF/api/folders" \
         -d "{\"uid\":\"${equipe}\",\"title\":\"Équipe ${equipe}\"}"; echo
    id=$(curl -s -u "admin:$mdp_admin" "$GF/api/users/lookup?loginOrEmail=${equipe}" \
         | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
    # Remplace les droits par défaut : l'équipe modifie, l'administrateur gère, les autres ne voient pas
    curl -s -u "admin:$mdp_admin" -X POST -H "$JSON" "$GF/api/folders/${equipe}/permissions" \
         -d "{\"items\":[{\"userId\":${id},\"permission\":2},{\"role\":\"Admin\",\"permission\":4}]}"; echo
done
