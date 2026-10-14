# Installation du serveur NUC (SQLite et Grafana)

Infrastructure client / serveur dans un contexte industriel

Ce document décrit, pas à pas, la préparation du serveur NUC du fab lab de l'IRUP. Il héberge le broker MQTT et, pour chacune des 6 équipes (`tech1`, `tech2` de BACHTECH24, `g1` à `g4` de B3RNSPP26), le collecteur, la base de données, le site web et l'API simulée, ainsi qu'une instance **Grafana** commune. Il démarre sur un SSD externe : le disque interne n'est ni utilisé ni modifié. Le matériel et le calendrier sont dans `progression_pedagogique/materiel_IRUP.md`.

Par rapport au Raspberry Pi d'ISTP ([`install_raspberry.md`](install_raspberry.md)), le NUC ajoute **Grafana**, qui lit directement la base SQLite `cellule.db` de chaque équipe, en lecture seule, grâce à un adaptateur (le plugin communautaire `frser-sqlite-datasource`). Il n'y a qu'une base par équipe : le collecteur et le site web restent ceux des cours.

| Composant | Rôle | Port |
|---|---|---|
| Ubuntu Server 24.04 LTS | Système, sur SSD USB | |
| OpenSSH | Connexion des équipes | 22 |
| Mosquitto | Broker MQTT, ouvert (sans compte) | 1883 |
| Python 3.12 + `/opt/cellule/venv` | Collecteurs, sites web et API des équipes | 5001 à 5006, 8001 à 8006 |
| SQLite | Base `~/supervision/cellule.db` de chaque équipe, écrite par son collecteur, lue par son site web et par Grafana | |
| Grafana + adaptateur SQLite | Dashboards de production, une source de données et un dossier par équipe | 3000 |

```mermaid
flowchart LR
    ROB["Robot Ned2"] -- "MQTT" --> MQ["Mosquitto<br/>:1883"]
    MQ --> COL["Collecteur<br/>de l'équipe"]
    COL -- "INSERT" --> SQ[("~/supervision/cellule.db<br/>SQLite")]
    SQ -- "SELECT" --> WEB["Site web Flask<br/>:8003"]
    SQ -- "SELECT<br/>(lecture seule)" --> GF["Grafana<br/>:3000"]
```

Durée indicative : 2 heures 30, Internet nécessaire pendant la préparation (installation de Grafana et de l'adaptateur), pas pendant les séances.


## 1. Préparer le SSD externe

Le NUC démarre sur le SSD externe : Ubuntu s'installe sur ce SSD, **pas sur le disque interne**, qui contient peut-être les données de l'an dernier.

1. Sur un poste avec Internet, écrire l'image **Ubuntu Server 24.04 LTS (amd64)** sur une clé USB (Raspberry Pi Imager, Balena Etcher ou `dd`).
2. Brancher la clé et le SSD externe sur le NUC ; dans le BIOS (touche `F2` au démarrage), autoriser le démarrage sur USB et désactiver Secure Boot si l'installateur ne démarre pas.
3. Pendant l'installation :
   - disque : choisir **le SSD externe** (vérifier la taille et le modèle), « utiliser tout le disque », sans LVM chiffré ;
   - nom de la machine : `nuc-cellule` ; utilisateur `prof` ;
   - cocher **Install OpenSSH server**.
4. À la fin, retirer la clé ; dans le BIOS, placer le SSD externe en tête de l'ordre de démarrage et activer le redémarrage automatique après une coupure de courant.
5. Vérifier que le disque interne n'a pas été touché : `lsblk -f` doit montrer ses partitions inchangées, non montées.

L'installateur place le chargeur de démarrage sur le disque choisi. Si le NUC ne démarre plus sans le SSD, le disque interne n'a pas été modifié : c'est seulement l'ordre de démarrage du BIOS.


## 2. Système et heure

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y mosquitto mosquitto-clients python3-venv python3-pip sqlite3 acl git curl tmux htop
sudo timedatectl set-timezone Europe/Paris
timedatectl                                     # heure juste ; NTP actif si le NUC a Internet
```

Le NUC a une horloge sauvegardée : sans Internet au fab lab, il garde l'heure. La vérifier à chaque séance. Le fuseau `Europe/Paris` sert aussi à Grafana pour convertir en UTC l'heure locale posée par les robots (section 7.7). Le paquet `acl` donne à Grafana l'accès aux bases des équipes (section 7.3).


## 3. Réseau : adresse fixe

Repérer le nom de l'interface Ethernet (`ip link`, par exemple `enp86s0`), puis :

```bash
echo "network: {config: disabled}" | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
sudo rm -f /etc/netplan/*.yaml
sudo tee /etc/netplan/50-cellule.yaml >/dev/null <<'EOF'
network:
  version: 2
  ethernets:
    enp86s0:
      dhcp4: false
      addresses: [192.168.10.10/24]
      routes:
        - to: default
          via: 192.168.10.1
      nameservers:
        addresses: [192.168.10.1]
EOF
sudo chmod 600 /etc/netplan/50-cellule.yaml
sudo netplan apply
```

Pendant la préparation hors du fab lab, remplacer le contenu par `dhcp4: true`.


## 4. Comptes des équipes

```bash
cd ~/niryo2/scripts
sudo ./creer_comptes_equipes.sh irup        # crée comptes_irup.txt (mode 600)
```

Les comptes `tech1`, `tech2` et `g1` à `g4` ont des dossiers privés. Le même mot de passe sert pour SSH et Grafana.


## 5. Broker Mosquitto

Le broker est **ouvert** : pas de compte, pas de mot de passe, pas de droits par sujet. Il n'est joignable que sur le réseau local du module. Chaque équipe publie sous `cellule/<son identifiant>/` : c'est une **convention**, que le broker ne vérifie pas.

```bash
sudo tee /etc/mosquitto/conf.d/cellule.conf >/dev/null <<'EOF'
listener 1883 0.0.0.0
allow_anonymous true
EOF

sudo systemctl enable mosquitto
sudo systemctl restart mosquitto
```

Limite connue : une équipe peut lire et écrire les topics d'une autre (identifiant mal recopié, curiosité). Deux clients MQTT de même nom, par exemple deux collecteurs lancés avec le même `EQUIPE`, se déconnectent l'un l'autre : en cas de messages qui manquent, vérifier d'abord que chaque équipe a son propre identifiant.


## 6. Python : un environnement commun

```bash
sudo python3 -m venv /opt/cellule/venv
sudo /opt/cellule/venv/bin/pip install flask paho-mqtt requests
echo 'export PATH=/opt/cellule/venv/bin:$PATH' | sudo tee /etc/profile.d/cellule.sh
sudo /opt/cellule/venv/bin/pip download -d /opt/cellule/paquets flask paho-mqtt requests
```

Les briques fournies aux équipes se déposent dans `/opt/cellule/fournitures`, comme sur le Raspberry Pi (section 7 de `install_raspberry.md`).


## 7. Grafana et l'adaptateur SQLite

### 7.1 Installation (avec Internet)

Grafana vient du dépôt officiel de Grafana Labs. L'adaptateur SQLite, un plugin communautaire, s'installe ensuite avec la commande `grafana cli` :

```bash
sudo apt install -y apt-transport-https wget gnupg
sudo mkdir -p /etc/apt/keyrings
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg >/dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
    | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update && sudo apt install -y grafana
sudo grafana cli plugins install frser-sqlite-datasource
```

Versions essayées : Grafana 13.2 et adaptateur 4.0. L'adaptateur n'est pas maintenu par Grafana Labs : avant une mise à jour de Grafana, vérifier sur sa page (grafana.com, « SQLite » dans les plugins) qu'il reste compatible.

### 7.2 Configuration

Dans `/etc/grafana/grafana.ini`, modifier les lignes suivantes (enlever le `;` de début de ligne) :

```ini
[server]
http_port = 3000

[security]
admin_user = admin
admin_password = MOT_DE_PASSE_ADMIN_GRAFANA

[users]
allow_sign_up = false
default_language = fr-FR

[analytics]
reporting_enabled = false
check_for_updates = false
check_for_plugin_updates = false
```

Les deux dernières options évitent que Grafana cherche Internet pendant les séances. Les réglages de sécurité de l'adaptateur restent ceux par défaut : pas d'`ATTACH` (lecture d'une autre base depuis une requête), fichiers sensibles bloqués (dont la base interne `grafana.db`).

### 7.3 Accès de Grafana aux bases des équipes

Chaque équipe range sa base à un emplacement fixe, celui de la structure de projet du cours de Flask : `~/supervision/cellule.db`, où son collecteur écrit et où son site web lit. Grafana tourne sous le compte système `grafana`, alors que les dossiers des équipes sont privés (mode 700). Des ACL lui donnent le strict nécessaire : traverser les dossiers jusqu'à la base et la lire.

```bash
grep -v '^#' ~/niryo2/scripts/comptes_irup.txt | while IFS=: read -r equipe mdp; do
    sudo -u "$equipe" mkdir -p "/home/$equipe/supervision"
    # traverser le dossier personnel et supervision/, sans pouvoir en lister le contenu
    sudo setfacl -m u:grafana:x "/home/$equipe" "/home/$equipe/supervision"
    # lire les fichiers créés ensuite dans supervision/, dont cellule.db
    sudo setfacl -d -m u:grafana:r "/home/$equipe/supervision"
done
```

- Les autres équipes n'ont toujours aucun accès au dossier : `ls /home/g1` reste refusé.
- L'ACL par défaut ne vaut que pour les fichiers créés **après** elle. Pour une base qui existait déjà : `sudo setfacl -m u:grafana:r /home/g1/supervision/cellule.db`. Si une équipe supprime et recrée son dossier `supervision`, relancer la boucle.
- Aucun réglage n'est demandé aux équipes, pas même le mode WAL : Grafana ouvre la base en lecture seule et, si le collecteur est en train d'écrire un lot, attend qu'il ait fini (section 7.4). Les écritures du collecteur, par lots courts, ne sont pas gênées.

### 7.4 Une source de données par équipe

Les sources de données sont déclarées dans un fichier (« provisioning ») : elles sont recréées à chaque démarrage, à l'identique.

```bash
{
echo "apiVersion: 1"
echo "datasources:"
grep -v '^#' ~/niryo2/scripts/comptes_irup.txt | while IFS=: read -r equipe mdp; do
cat <<EOF
  - name: SQLite ${equipe}
    uid: sqlite-${equipe}
    type: frser-sqlite-datasource
    jsonData:
      path: /home/${equipe}/supervision/cellule.db
      pathPrefix: "file:"
      pathOptions: "mode=ro&_pragma=query_only(1)&_pragma=busy_timeout(5000)"
EOF
done
} | sudo tee /etc/grafana/provisioning/datasources/cellule.yaml >/dev/null

sudo systemctl enable grafana-server
sudo systemctl restart grafana-server
```

Les options du chemin protègent la base de l'équipe :

- `mode=ro` : ouverture en lecture seule ;
- `_pragma=query_only(1)` : toute requête d'écriture (`INSERT`, `DELETE`…) est refusée, un dashboard mal écrit ne peut rien modifier ;
- `_pragma=busy_timeout(5000)` : si le collecteur écrit, Grafana attend jusqu'à 5 secondes au lieu de renvoyer « database is locked ».

Tant que le collecteur d'une équipe n'a pas créé sa base, sa source de données renvoie « unable to open database file » : c'est normal.

### 7.5 Un utilisateur et un dossier par équipe

Chaque équipe a un compte Grafana (mêmes identifiant et mot de passe) et un dossier de dashboards où elle seule peut écrire. Le compte est créé avec le rôle « Viewer » : l'équipe ne modifie que son dossier.

```bash
GF="http://admin:MOT_DE_PASSE_ADMIN_GRAFANA@localhost:3000"
JSON="Content-Type: application/json"
grep -v '^#' ~/niryo2/scripts/comptes_irup.txt | while IFS=: read -r equipe mdp; do
    curl -s -X POST -H "$JSON" "$GF/api/admin/users" \
         -d "{\"name\":\"${equipe}\",\"login\":\"${equipe}\",\"password\":\"${mdp}\"}"; echo
    curl -s -X POST -H "$JSON" "$GF/api/folders" \
         -d "{\"uid\":\"${equipe}\",\"title\":\"Équipe ${equipe}\"}"; echo
    id=$(curl -s "$GF/api/users/lookup?loginOrEmail=${equipe}" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')
    # remplace les droits par défaut : l'équipe modifie, l'administrateur gère, les autres ne voient pas
    curl -s -X POST -H "$JSON" "$GF/api/folders/${equipe}/permissions" \
         -d "{\"items\":[{\"userId\":${id},\"permission\":2},{\"role\":\"Admin\",\"permission\":4}]}"; echo
done
```

Limite de la version gratuite de Grafana : toutes les sources de données sont visibles de toutes les équipes (les droits par source de données sont réservés à la version Enterprise). Chaque équipe doit choisir **sa** source `SQLite <equipe>` dans ses panneaux.

### 7.6 Données d'essai

Pour tester Grafana avant les vrais cycles, remplir la base d'une équipe de test avec 500 cycles fictifs, un par minute. La commande est lancée avec le compte de l'équipe, à qui la base appartient ; les tables sont celles du cours de SQL.

```bash
sudo -u g1 sqlite3 /home/g1/supervision/cellule.db <<'SQL'
CREATE TABLE IF NOT EXISTS robots (
    id INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE,
    equipe TEXT NOT NULL, adresse_ip TEXT);
CREATE TABLE IF NOT EXISTS cycles (
    id INTEGER PRIMARY KEY, robot_id INTEGER NOT NULL REFERENCES robots(id),
    debut TEXT NOT NULL, duree REAL NOT NULL, zone TEXT, statut TEXT NOT NULL DEFAULT 'ok');
INSERT INTO robots (nom, equipe, adresse_ip) VALUES ('robot1', 'g1', '192.168.10.21');
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 500)
INSERT INTO cycles (robot_id, debut, duree, zone, statut)
SELECT 1, strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime', -i || ' minutes'),
       round(15 + abs(random() % 60) / 10.0, 1),
       CASE WHEN i % 2 = 0 THEN 'A' ELSE 'B' END,
       CASE WHEN abs(random() % 100) < 5 THEN 'defaut' ELSE 'ok' END
FROM n;
SQL
```

Comme dans le collecteur, `debut` est l'heure locale posée par le robot, sans fuseau (`2026-11-17T08:30:18`). Effacer la base d'essai ensuite (le collecteur la recrée) : `sudo -u g1 rm /home/g1/supervision/cellule.db`.

### 7.7 Panneau d'essai

Se connecter à `http://192.168.10.10:3000` avec le compte `g1`, créer un dashboard dans le dossier « Équipe g1 », un panneau « Time series » sur la source `SQLite g1`, avec la requête :

```sql
SELECT unixepoch(debut, 'utc') AS time, duree AS "durée (s)"
FROM cycles
WHERE unixepoch(debut, 'utc') BETWEEN $__from / 1000 AND $__to / 1000
ORDER BY time
```

- SQLite n'a pas de type date. `unixepoch(debut, 'utc')` convertit l'heure locale du robot en secondes UTC, avec le fuseau du NUC (section 2) ; Grafana affiche ensuite l'heure locale du navigateur.
- Une colonne nommée `time` est reconnue comme l'heure du point (réglage « Time formatted columns » de l'éditeur de requête, qui contient `time` et `ts` par défaut).
- `$__from` et `$__to` sont les bornes de la période choisie en haut du dashboard, en millisecondes. La macro `$__timeFilter` des sources MySQL ou PostgreSQL n'existe pas avec cet adaptateur.

Pour compter les cycles par heure : `SELECT unixepoch(debut, 'utc') / 3600 * 3600 AS time, count(*) AS cycles FROM cycles WHERE … GROUP BY time ORDER BY time`.


## 8. Vérifications

```bash
systemctl is-active mosquitto ssh grafana-server            # 3 fois active
ss -tlnp | grep -E ':22 |:1883 |:3000 '
python3 -c "import flask, paho.mqtt, requests; print('ok')"  # depuis un compte d'équipe
sudo -u grafana sqlite3 "file:/home/g1/supervision/cellule.db?mode=ro" "SELECT count(*) FROM cycles;"   # Grafana lit la base
sudo -u g2 ls /home/g1                                   # refusé : dossier d'une autre équipe
```

- [ ] MQTT : chaque équipe publie et reçoit sur ses topics, rien sur ceux des autres (mêmes commandes que dans `install_raspberry.md`, section 9)
- [ ] Une équipe ne lit ni le dossier, ni les topics, ni la base d'une autre
- [ ] Grafana : connexion avec un compte d'équipe, panneau d'essai sur les données fictives, création d'un dashboard dans son dossier ; le dossier d'une autre équipe n'apparaît pas
- [ ] Collecteur d'une équipe de test en marche : ses nouveaux cycles apparaissent dans Grafana (rafraîchissement toutes les 5 s), sans erreur « database is locked » ni côté collecteur ni côté Grafana
- [ ] Redémarrage complet : les trois services repartent seuls
- [ ] Mémoire disponible avec Grafana et 6 équipes actives (`htop`)
- [ ] Le robot publie sur le broker du NUC : `~/cellule/lancer.sh ~/cellule/test.py --broker 192.168.10.10` sur le robot


## 9. Sauvegarde et restauration

- **Image complète du SSD** après l'installation, depuis un autre poste Linux, et copie sur le SSD de secours (mêmes commandes `dd` que pour le Raspberry Pi).
- **Après chaque séance**, collecteurs arrêtés (une base copiée pendant une écriture peut être incohérente) : dossiers des équipes avec leurs bases, configuration et dashboards Grafana. L'option `--acls` conserve les droits donnés à Grafana.

  ```bash
  sudo tar czf ~/sauvegarde_$(date +%F).tgz --acls /home/tech[12] /home/g[1-4] /etc/mosquitto /etc/grafana /var/lib/grafana
  ```

- **Restauration d'une base** : `sudo tar xzf sauvegarde_2027-03-25.tgz --acls -C / home/g1/supervision/cellule.db`.
