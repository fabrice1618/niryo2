#!/bin/bash
# NUC de l'IRUP : déclare dans Grafana une source de données SQLite par équipe
# (« provisioning » : recréées à chaque démarrage), puis redémarre Grafana.
# Chemin de la base : /home/<equipe>/supervision/cellule.db, ouverte en lecture seule
# (mode=ro, query_only), avec une attente de 5 s si le collecteur écrit (busy_timeout).
# Tant que le collecteur d'une équipe n'a pas créé sa base, sa source répond
# « unable to open database file » : c'est normal.
#
# Usage : sudo ./irup_grafana_sources.sh [fichier_comptes]     (défaut : comptes_irup.txt, à côté du script)
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }
comptes=${1:-$(dirname "$(readlink -f "$0")")/comptes_irup.txt}
fichier=/etc/grafana/provisioning/datasources/cellule.yaml

{
echo "apiVersion: 1"
echo "datasources:"
grep -v '^#' "$comptes" | while IFS=: read -r equipe mdp; do
cat <<CONF
  - name: SQLite ${equipe}
    uid: sqlite-${equipe}
    type: frser-sqlite-datasource
    jsonData:
      path: /home/${equipe}/supervision/cellule.db
      pathPrefix: "file:"
      pathOptions: "mode=ro&_pragma=query_only(1)&_pragma=busy_timeout(5000)"
CONF
done
} > "$fichier"

systemctl enable grafana-server
systemctl restart grafana-server
echo "Sources déclarées dans $fichier"
