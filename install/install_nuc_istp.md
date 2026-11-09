# Installation du serveur NUC Celeron (SQLite)

Infrastructure client / serveur dans un contexte industriel

Ce document décrit, pas à pas, la préparation du serveur d'ISTP, un NUC à processeur Celeron : il héberge le broker MQTT, un serveur DHCP pour le réseau de la salle et, pour chacune des 8 équipes (`g1` à `g8`), le collecteur, la base SQLite `cellule.db`, le site web et l'API simulée. Le NUC sert d'abord en salle D3.10 sur un réseau séparé, puis au fab lab, toujours en `192.168.1.2` (le NUC de l'IRUP occupe `.10`). Le matériel et le calendrier sont dans `progression_pedagogique/materiel_ISTP.md`.

| Composant | Rôle | Port |
|---|---|---|
| Ubuntu Desktop 24.04 LTS (64 bits) | Système, installé sur le NUC depuis une clé USB, nom de machine `istp` | |
| OpenSSH | Connexion des équipes (terminal, VS Code Remote SSH, `scp`) | 22 |
| Mosquitto | Broker MQTT, ouvert (sans compte) | 1883 |
| dnsmasq | Serveur DHCP de la salle D3.10 (arrêté au fab lab) | 67/udp |
| Python 3.12 + `/opt/cellule/venv` | Collecteurs, sites web et API des équipes | 5001 à 5008, 8001 à 8008 |
| SQLite | Une base `cellule.db` par équipe, dans son dossier | |
| DBeaver, MQTT Explorer | Consultation de la base et des messages, directement sur le NUC (session graphique) | |

Durée indicative : 1 heure 30 (le système est déjà installé et à jour), Internet nécessaire pendant la préparation (pas pendant les séances).


## 1. Système installé (rappel)

L'installation est classique et déjà faite : clé USB d'installation **Ubuntu Desktop 24.04 LTS (amd64)**, démarrage dessus par le menu de démarrage du NUC (touche `F10` au démarrage, `F2` pour le BIOS), puis `apt update` et `apt full-upgrade`. Ubuntu Desktop gère le réseau avec NetworkManager (commande `nmcli`). Choix à vérifier :

- utilisateur `prof`, avec un mot de passe solide ;
- nom de la machine : `istp` ;
- fuseau horaire `Europe/Paris`, clavier `fr` ;
- dans le BIOS, redémarrage automatique après une coupure de courant (réglage « After Power Failure » sur « Power On »), pour que le serveur reparte seul après une coupure en salle.

```bash
lsb_release -d                 # Ubuntu 24.04 LTS
hostnamectl                    # Static hostname : istp
hostname -I                    # adresse actuelle du NUC
```

Ubuntu Desktop n'installe pas le serveur SSH et met la machine en veille quand elle reste inactive : pour un serveur, on installe SSH et on interdit la veille.

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
systemctl is-active ssh        # active
```

Première connexion depuis un poste du même réseau : `ssh prof@istp.local` (ou `ssh prof@<adresse du NUC>`).


## 2. Système, heure et outils

Le système est déjà à jour : il reste à installer les paquets du module. À l'installation, `dnsmasq` peut signaler qu'il n'a pas pu démarrer (le port 53 est déjà pris par le système) : sans importance, la section 3 le configure pour ne faire que du DHCP.

```bash
sudo apt install -y mosquitto mosquitto-clients dnsmasq python3-venv python3-pip sqlite3 git curl tmux htop lm-sensors
sudo timedatectl set-timezone Europe/Paris
```

**Horloge.** Sans Internet, le NUC reprend au démarrage l'heure de son horloge matérielle, alimentée par une pile. Après un redémarrage, `timedatectl` doit afficher la bonne heure et `RTC time`. Hors réseau, régler l'heure à la main si besoin : `sudo timedatectl set-ntp false`, puis `sudo timedatectl set-time "2026-11-09 08:00:00"` (la pile la conserve ensuite).

### DBeaver et MQTT Explorer

Deux outils graphiques pour consulter les données : **DBeaver** (la base SQLite `cellule.db` : tables, requêtes SQL) et **MQTT Explorer** (l'arbre des topics en direct, publication d'un message d'essai). Ils s'installent sur le NUC, qui a une session graphique (Ubuntu Desktop), et se lancent depuis le menu des applications avec l'écran du NUC. Internet est nécessaire pendant l'installation.

```bash
sudo snap install dbeaver-ce
sudo snap install mqtt-explorer
```

Sur les postes Windows des étudiants, les installateurs sont sur <https://dbeaver.io/download/> et <https://mqtt-explorer.com/> (voir `INSTALLATION_POSTE.md`).

- **MQTT Explorer** : nouvelle connexion, hôte `localhost` (depuis un autre poste : `192.168.1.2`), port `1883`, sans nom d'utilisateur ni mot de passe. L'arbre `cellule/` apparaît dès qu'un robot ou un simulateur publie.
- **DBeaver** : nouvelle connexion, type **SQLite**, chemin du fichier `cellule.db`. Au premier essai, DBeaver télécharge le pilote SQLite : le faire pendant la préparation, avec Internet. Les dossiers des équipes sont privés : pour ouvrir la base de l'équipe `g1`, en copier d'abord un exemplaire dans le dossier de `prof` (`sudo cp /home/g1/supervision/cellule.db ~/g1.db`, de préférence collecteur arrêté), puis ouvrir cette copie.


## 3. Réseau : trois profils (fab lab, salle D3.10 et DHCP)

Le serveur a toujours la même adresse fixe, `192.168.1.2`, au fab lab comme en salle D3.10. Ubuntu Desktop gère le réseau avec NetworkManager : on crée un profil de connexion par situation, puis une commande qui active le bon.

```bash
# Nom de l'interface Ethernet du NUC (par exemple enp3s0) : à vérifier avant de continuer
IFACE=$(ip -br link | awk '$1 ~ /^e/ {print $1; exit}')
echo "$IFACE"

# Fab lab : adresse fixe, routeur du fab lab
sudo nmcli connection add type ethernet ifname "$IFACE" con-name cellule-fablab autoconnect no \
    ipv4.method manual ipv4.addresses 192.168.1.2/24 ipv4.gateway 192.168.1.1 ipv4.dns 192.168.1.1

# Salle D3.10 : même adresse, sans routeur (le NUC y est le serveur DHCP, voir plus bas)
sudo nmcli connection add type ethernet ifname "$IFACE" con-name cellule-salle autoconnect no \
    ipv4.method manual ipv4.addresses 192.168.1.2/24

# Préparation à la maison ou en cas de doute : adresse donnée par la box (DHCP)
sudo nmcli connection add type ethernet ifname "$IFACE" con-name cellule-dhcp autoconnect no \
    ipv4.method auto
```

Dans la salle, l'adresse reste à confirmer avec ISTP. Si ISTP fournit un routeur vers Internet, l'ajouter au profil : `sudo nmcli connection modify cellule-salle ipv4.gateway <routeur> ipv4.dns <routeur>`. Pour voir les profils : `nmcli connection show`.

Une petite commande change de profil :

```bash
sudo tee /usr/local/sbin/profil-reseau >/dev/null <<'EOF'
#!/bin/bash
# Usage : sudo profil-reseau fablab|salle|dhcp
set -e
profil="cellule-$1"
nmcli -g NAME connection show | grep -qx "$profil" || { echo "Profils : fablab salle dhcp"; exit 1; }
# Au prochain démarrage du NUC, seul le profil choisi démarre
nmcli -g NAME,TYPE connection show | awk -F: '$2=="802-3-ethernet" {print $1}' | while read -r c; do
    nmcli connection modify "$c" connection.autoconnect no
done
nmcli connection modify "$profil" connection.autoconnect yes
nmcli connection up "$profil"
# Serveur DHCP (voir plus bas) : démarré seulement dans le profil salle
if [ "$1" = salle ]; then
    systemctl enable dnsmasq
    systemctl restart dnsmasq
else
    systemctl disable --now dnsmasq
fi
ip -4 -br addr show scope global
echo "dnsmasq : $(systemctl is-active dnsmasq)"
EOF
sudo chmod 755 /usr/local/sbin/profil-reseau
```

`sudo profil-reseau fablab` au fab lab, `sudo profil-reseau salle` en salle D3.10 (c'est le seul profil qui démarre le serveur DHCP). Attention : en SSH, la connexion est coupée si l'adresse change ; garder un écran et un clavier à portée de main.


### Serveur DHCP (salle D3.10)

Sur le réseau séparé de la salle, le NUC distribue lui-même les adresses aux laptops et aux postes Linux, avec **dnsmasq** (DHCP seul, sans DNS). Les postes reçoivent une adresse de la plage `192.168.1.100` à `192.168.1.199` (la même que les postes étudiants au fab lab), le NUC garde `192.168.1.2`, hors de cette plage.

**Règle : un seul serveur DHCP par réseau.** Si le réseau de la salle a déjà son DHCP (routeur d'ISTP), ne pas démarrer celui du NUC. Au fab lab, le routeur de l'IRUP distribue déjà les adresses : le serveur du NUC doit y être arrêté, sinon les postes reçoivent des adresses de deux serveurs.

```bash
IFACE=$(ip -br link | awk '$1 ~ /^e/ {print $1; exit}')     # même interface qu'au-dessus

sudo tee /etc/dnsmasq.d/cellule.conf >/dev/null <<EOF
# DHCP seul : port=0 désactive la partie DNS (le port 53 est pris par systemd-resolved)
port=0
interface=$IFACE
bind-dynamic
dhcp-authoritative
dhcp-range=192.168.1.100,192.168.1.199,255.255.255.0,12h
# Ni passerelle ni DNS envoyés aux postes : la salle n'a pas forcément d'accès à Internet.
# S'il y a un routeur, remplacer ces deux lignes par :
#   dhcp-option=option:router,192.168.1.1
#   dhcp-option=option:dns-server,192.168.1.1
dhcp-option=3
dhcp-option=6
EOF

sudo dnsmasq --test             # "syntax check OK"
```

Le NUC doit avoir son adresse fixe `192.168.1.2` (profil `salle`) : sans une adresse dans le réseau `192.168.1.0/24`, dnsmasq n'a aucune plage à distribuer sur l'interface.

Commandes de gestion du serveur DHCP :

| Action | Commande |
|---|---|
| Démarrer | `sudo systemctl start dnsmasq` |
| Arrêter | `sudo systemctl stop dnsmasq` |
| Redémarrer (après une modification de la configuration) | `sudo systemctl restart dnsmasq` |
| Savoir s'il tourne | `systemctl is-active dnsmasq` (`active` ou `inactive`), détail : `systemctl status dnsmasq` |
| Le lancer à chaque démarrage du NUC | `sudo systemctl enable dnsmasq` |
| Ne plus le lancer au démarrage | `sudo systemctl disable dnsmasq` |
| Le démarrer et le lancer au démarrage | `sudo systemctl enable --now dnsmasq` |
| L'arrêter et ne plus le lancer au démarrage | `sudo systemctl disable --now dnsmasq` |
| Adresses distribuées (échéance, MAC, adresse, nom) | `cat /var/lib/misc/dnsmasq.leases` |
| Journal en direct (demandes et réponses DHCP) | `journalctl -u dnsmasq -f` |

`stop` n'arrête le serveur que jusqu'au prochain redémarrage du NUC, alors que `disable` l'empêche de repartir. La commande `profil-reseau` fait tout cela : `salle` active et redémarre dnsmasq, `fablab` et `dhcp` l'arrêtent et le désactivent. En SSH, ne changer de profil qu'en sachant que la connexion peut être coupée.


## 4. Comptes des équipes

Copier le dépôt du cours sur le NUC (ou seulement le dossier `scripts/`), puis créer les 8 comptes :

```bash
cd ~/niryo2/scripts
sudo ./creer_comptes_equipes.sh inge        # crée comptes_inge.txt (mode 600)
```

Le script crée les comptes `g1` à `g8` avec des mots de passe aléatoires et des dossiers personnels privés (une équipe ne lit pas les fichiers des autres). Garder `comptes_inge.txt` : il sert pour les postes de la salle D3.10 (`sudo ./creer_comptes_equipes.sh --fichier comptes_inge.txt inge`).


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

Le robot d'une équipe, ses simulateurs et son collecteur utilisent le même identifiant d'équipe dans les topics.


## 6. Python : un environnement commun

Ubuntu 24.04 interdit `pip install` dans le Python du système. On crée un environnement commun, en tête du `PATH` de tous les comptes : `python3` et `pip` désignent alors cet environnement, sans `source` ni `activate`.

```bash
sudo python3 -m venv /opt/cellule/venv
sudo /opt/cellule/venv/bin/pip install flask paho-mqtt requests
echo 'export PATH=/opt/cellule/venv/bin:$PATH' | sudo tee /etc/profile.d/cellule.sh

# Copie des paquets pour une réinstallation sans Internet
sudo /opt/cellule/venv/bin/pip download -d /opt/cellule/paquets flask paho-mqtt requests
```

Une équipe qui veut une bibliothèque de plus l'installe pour elle seule : `pip install --user nom` (dans `~/.local`). Les paquets de `/opt/cellule/venv` ne sont modifiables que par `prof`.

**SQLite** : rien d'autre à installer. Chaque collecteur crée sa base `cellule.db` dans le dossier de l'équipe (`~/supervision/cellule.db`, structure de projet du cours de Flask, comme sur le NUC) ; l'outil `sqlite3` sert à l'interroger.


## 7. Briques fournies aux équipes

Les briques remises à la séance 2 sont aussi déposées sur le serveur, en lecture pour tous : les simulateurs (`simulateurs/`), le collecteur et le script de création de la base (`collecteur/`), la base du tableau de bord (`site_web/`) et l'API du robot (`api_robot/`), copiés depuis ce dépôt (cloné dans `~/niryo2`), ainsi que les autres fournitures de la séance (squelette de l'API CQRS en mode simulé, gabarits) :

```bash
sudo mkdir -p /opt/cellule/fournitures
sudo cp -r ~/niryo2/{simulateurs,collecteur,site_web,api_robot} /opt/cellule/fournitures/
sudo cp -r ~/fournitures/* /opt/cellule/fournitures/      # autres fournitures, s'il y en a
sudo chmod -R a+rX /opt/cellule/fournitures
```

Chaque équipe copie ce dont elle a besoin dans son dossier, en suivant le `README.md` de chaque brique : collecteur et site dans `~/supervision/` (`cp /opt/cellule/fournitures/collecteur/*.py ~/supervision/`, `cp -r /opt/cellule/fournitures/site_web/* ~/supervision/`), simulateurs dans le dossier personnel, avec ses ports : API simulée `5000 + n`, site `8000 + n`, où `n` est le numéro de l'équipe (1 à 8).


## 8. Pare-feu (facultatif)

Sur le réseau séparé de la salle et au fab lab, le pare-feu peut rester désactivé. Pour l'activer :

```bash
sudo ufw allow 22/tcp
sudo ufw allow 1883/tcp
sudo ufw allow 67/udp           # serveur DHCP (salle D3.10)
sudo ufw allow 5001:5008/tcp
sudo ufw allow 8001:8008/tcp
sudo ufw enable
```


## 9. Vérifications

```bash
systemctl is-active mosquitto ssh               # active, active
ss -tlnp | grep -E ':22 |:1883 '                # 0.0.0.0:1883 et 0.0.0.0:22
python3 -c "import flask, paho.mqtt, requests; print('ok')"   # depuis un compte d'équipe

# MQTT : sans compte, le message publié est reçu par l'abonné
mosquitto_sub -h localhost -t 'cellule/#' -v &
mosquitto_pub -h localhost -t cellule/g1/etat -m '{"etat": "essai"}'      # s'affiche
```

- [ ] Connexion SSH avec un compte d'équipe, depuis un poste Linux de la salle et depuis un laptop
- [ ] Une équipe ne peut pas lire le dossier d'une autre (`ls /home/g2` refusé)
- [ ] Le site Flask d'une équipe de test s'ouvre depuis un laptop (`flask run --host 0.0.0.0 --port 8001`)
- [ ] **Essai de charge** : 8 simulateurs, 8 collecteurs et 16 serveurs Flask lancés ensemble, plusieurs connexions VS Code Remote SSH ; surveiller la mémoire et la température avec `htop` et `sensors`
- [ ] Redémarrage complet : Mosquitto et SSH repartent seuls, l'heure est juste (dnsmasq repart seulement avec le profil salle)
- [ ] Profil salle : après `sudo profil-reseau salle`, `systemctl is-active dnsmasq` répond `active` et un laptop branché au réseau reçoit une adresse de `.100` à `.199` (`cat /var/lib/misc/dnsmasq.leases`)
- [ ] Profil fab lab : après `sudo profil-reseau fablab`, `systemctl is-active dnsmasq` répond `inactive` (un seul serveur DHCP sur le réseau)
- [ ] MQTT Explorer se connecte au broker du NUC et affiche `cellule/#` ; DBeaver ouvre une `cellule.db`
- [ ] Le robot publie sur le broker du NUC (au fab lab) : `~/cellule/lancer.sh ~/cellule/test.py --broker 192.168.1.2` sur le robot


## 10. Sauvegarde et restauration

- **Image complète du disque**, une fois l'installation terminée, le NUC démarré sur la clé USB d'installation (mode « Try Ubuntu ») et un disque externe monté sur `/mnt/sauvegarde` (vérifier le nom du disque du NUC avec `lsblk`, ici `/dev/sdX`, ou `/dev/nvme0n1`) :

  ```bash
  sudo dd if=/dev/sdX of=/mnt/sauvegarde/nuc-istp.img bs=4M status=progress conv=fsync
  sudo dd if=/mnt/sauvegarde/nuc-istp.img of=/dev/sdY bs=4M status=progress conv=fsync   # vers un disque de remplacement
  ```

- **Après chaque séance**, collecteurs arrêtés (une base copiée pendant une écriture peut être incohérente), copie du travail des équipes :

  ```bash
  sudo tar czf ~/sauvegarde_$(date +%F).tgz /home/g[1-8] /etc/mosquitto
  ```

- **Remise à zéro** en fin de module : réécrire l'image du disque, ou supprimer les comptes (`sudo ./creer_comptes_equipes.sh --supprimer inge`).
