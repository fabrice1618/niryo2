#!/bin/bash
# NUC de l'IRUP : remplit la base d'une équipe de test avec 500 cycles fictifs, un par minute,
# pour essayer Grafana avant les vrais cycles. Lancé avec le compte de l'équipe, à qui la base
# appartient. Les tables sont celles du cours de SQL.
# Pour effacer ensuite la base d'essai (le collecteur la recrée) :
#     sudo -u g1 rm /home/g1/supervision/cellule.db
#
# Usage : sudo ./irup_grafana_donnees_essai.sh [equipe]     (défaut : g1)
set -euo pipefail

[ "$(id -u)" -eq 0 ] || { echo "À lancer avec sudo."; exit 1; }
equipe=${1:-g1}
base="/home/$equipe/supervision/cellule.db"

sudo -u "$equipe" mkdir -p "/home/$equipe/supervision"
sudo -u "$equipe" sqlite3 "$base" <<SQL
CREATE TABLE IF NOT EXISTS robots (
    id INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE,
    equipe TEXT NOT NULL, adresse_ip TEXT);
CREATE TABLE IF NOT EXISTS cycles (
    id INTEGER PRIMARY KEY, robot_id INTEGER NOT NULL REFERENCES robots(id),
    debut TEXT NOT NULL, duree REAL NOT NULL, zone TEXT, statut TEXT NOT NULL DEFAULT 'ok');
INSERT INTO robots (nom, equipe, adresse_ip) VALUES ('robot1', '$equipe', '192.168.1.21');
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 500)
INSERT INTO cycles (robot_id, debut, duree, zone, statut)
SELECT 1, strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime', -i || ' minutes'),
       round(15 + abs(random() % 60) / 10.0, 1),
       CASE WHEN i % 2 = 0 THEN 'A' ELSE 'B' END,
       CASE WHEN abs(random() % 100) < 5 THEN 'defaut' ELSE 'ok' END
FROM n;
SQL
sudo -u "$equipe" sqlite3 "$base" "SELECT count(*) || ' cycles' FROM cycles;"
