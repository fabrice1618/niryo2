# Installation du serveur Raspberry Pi (SQLite)

Infrastructure client / serveur dans un contexte industriel

Ce document décrit, pas à pas, la préparation du serveur Raspberry Pi d'ISTP : il héberge le broker MQTT et, pour chacune des 8 équipes (`g1e1` à `g2e4`), le collecteur, la base SQLite `cellule.db`, le site web et l'API simulée. Le Pi sert d'abord en salle D3.10 sur un réseau séparé, puis au fab lab, en `192.168.10.11` (le NUC de l'IRUP occupe `.10`). Le matériel et le calendrier sont dans `progression_pedagogique/materiel_ISTP.md`.

| Composant | Rôle | Port |
|---|---|---|
| Ubuntu Server 24.04 LTS (64 bits) | Système, sur SSD USB | |
| OpenSSH | Connexion des équipes (terminal, VS Code Remote SSH, `scp`) | 22 |
| Mosquitto | Broker MQTT, un compte par équipe | 1883 |
| Python 3.12 + `/opt/cellule/venv` | Collecteurs, sites web et API des équipes | 5001 à 5008, 8001 à 8008 |
| SQLite | Une base `cellule.db` par équipe, dans son dossier | |

Durée indicative : 2 heures, Internet nécessaire pendant la préparation (pas pendant les séances).


## 1. Préparer le SSD

Sur un poste avec Internet et **Raspberry Pi Imager** :

1. Choisir le modèle **Raspberry Pi 5**, le système **Other general-purpose OS > Ubuntu > Ubuntu Server 24.04 LTS (64-bit)**, et le SSD USB comme support.
2. Dans les réglages (« Edit settings ») :
   - nom d'hôte : `pi-cellule` ;
   - utilisateur : `prof`, avec un mot de passe solide ;
   - fuseau horaire `Europe/Paris`, clavier `fr` ;
   - onglet Services : **activer SSH** (mot de passe ou clé publique de l'enseignant).
3. Écrire le SSD, le brancher sur un port USB 3 (bleu) du Pi, **sans carte microSD**, et démarrer avec l'alimentation officielle 27 W.

Le Pi 5 démarre sur USB quand il n'y a pas de carte microSD. S'il ne démarre pas : écrire avec Imager l'image **Misc utility images > Bootloader (Pi 5 family) > USB Boot** sur la carte microSD, démarrer une fois dessus (l'anneau vert clignote quand c'est fini), retirer la carte et redémarrer.

Pour la première connexion, brancher le Pi sur une box ou un réseau avec DHCP (ou écran et clavier) : `ssh prof@pi-cellule.local`.


## 2. Système, heure et outils

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y mosquitto mosquitto-clients python3-venv python3-pip sqlite3 git curl tmux htop
sudo timedatectl set-timezone Europe/Paris
```

**Horloge (pile RTC).** Sans Internet, le Pi reprend l'heure de sa pile au démarrage. La pile officielle est rechargeable : activer sa charge, puis redémarrer.

```bash
echo "dtparam=rtc_bbat_vchg=3000000" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

Après le redémarrage, `timedatectl` doit afficher la bonne heure et `RTC time`. Hors réseau, régler l'heure à la main si besoin : `sudo timedatectl set-time "2026-11-09 08:00:00"` (la pile la conserve ensuite).


## 3. Réseau : deux profils (fab lab et salle D3.10)

Le réseau est configuré par netplan. On empêche cloud-init de réécrire la configuration, puis on prépare un fichier par lieu.

```bash
echo "network: {config: disabled}" | sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
sudo mkdir -p /etc/netplan-profils

sudo tee /etc/netplan-profils/fablab.yaml >/dev/null <<'EOF'
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      addresses: [192.168.10.11/24]
      routes:
        - to: default
          via: 192.168.10.1
      nameservers:
        addresses: [192.168.10.1]
EOF

# Salle D3.10 : adresse à fixer avec ISTP. Par défaut, la même adresse si le réseau séparé l'accepte.
sudo cp /etc/netplan-profils/fablab.yaml /etc/netplan-profils/salle.yaml

# Préparation à la maison ou en cas de doute : DHCP
sudo tee /etc/netplan-profils/dhcp.yaml >/dev/null <<'EOF'
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: true
EOF
```

Une petite commande change de profil :

```bash
sudo tee /usr/local/sbin/profil-reseau >/dev/null <<'EOF'
#!/bin/bash
# Usage : sudo profil-reseau fablab|salle|dhcp
set -e
[ -f "/etc/netplan-profils/$1.yaml" ] || { echo "Profils : $(ls /etc/netplan-profils | sed 's/.yaml//' | tr '\n' ' ')"; exit 1; }
rm -f /etc/netplan/*.yaml
install -m 600 "/etc/netplan-profils/$1.yaml" /etc/netplan/50-cellule.yaml
netplan apply
ip -4 addr show eth0
EOF
sudo chmod 755 /usr/local/sbin/profil-reseau
```

`sudo profil-reseau fablab` au fab lab, `sudo profil-reseau salle` en salle D3.10. Attention : en SSH, la connexion est coupée si l'adresse change ; garder l'écran micro-HDMI à portée de main.


## 4. Comptes des équipes

Copier le dépôt du cours sur le Pi (ou seulement le dossier `scripts/`), puis créer les 8 comptes :

```bash
cd ~/niryo2/scripts
sudo ./creer_comptes_equipes.sh inge        # crée comptes_inge.txt (mode 600)
```

Le script crée les comptes `g1e1` à `g2e4` avec des mots de passe aléatoires et des dossiers personnels privés (une équipe ne lit pas les fichiers des autres). Garder `comptes_inge.txt` : il sert pour Mosquitto (section 5) et pour les postes de la salle D3.10 (`sudo ./creer_comptes_equipes.sh --fichier comptes_inge.txt inge`).


## 5. Broker Mosquitto

Chaque équipe se connecte avec son identifiant et son mot de passe Linux, et n'accède qu'à ses topics. L'enseignant (`prof`) voit tout.

```bash
sudo tee /etc/mosquitto/conf.d/cellule.conf >/dev/null <<'EOF'
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl
EOF

sudo tee /etc/mosquitto/acl >/dev/null <<'EOF'
# Enseignant : tout le projet
user prof
topic readwrite cellule/#

# Chaque équipe : uniquement cellule/<son identifiant>/...
pattern readwrite cellule/%u/#
EOF

sudo install -m 600 /dev/null /etc/mosquitto/passwd     # créé non lisible par les autres
grep -v '^#' ~/niryo2/scripts/comptes_inge.txt | while IFS=: read -r equipe mdp; do
    sudo mosquitto_passwd -b /etc/mosquitto/passwd "$equipe" "$mdp"
done
sudo mosquitto_passwd -b /etc/mosquitto/passwd prof 'MOT_DE_PASSE_PROF'
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd /etc/mosquitto/acl
sudo chmod 600 /etc/mosquitto/passwd /etc/mosquitto/acl
sudo systemctl enable mosquitto
sudo systemctl restart mosquitto
```

Le robot d'une équipe publie avec les identifiants de l'équipe. Les simulateurs et collecteurs aussi.


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
sudo ufw allow 5001:5008/tcp
sudo ufw allow 8001:8008/tcp
sudo ufw enable
```


## 9. Vérifications

```bash
systemctl is-active mosquitto ssh               # active, active
ss -tlnp | grep -E ':22 |:1883 '                # 0.0.0.0:1883 et 0.0.0.0:22
python3 -c "import flask, paho.mqtt, requests; print('ok')"   # depuis un compte d'équipe

# MQTT : g1e1 reçoit ses messages...
mosquitto_sub -h localhost -u g1e1 -P 'mdp-g1e1' -t 'cellule/g1e1/#' -v &
mosquitto_pub -h localhost -u g1e1 -P 'mdp-g1e1' -t cellule/g1e1/etat -m '{"etat": "essai"}'
# ... mais ne voit pas ceux de g1e2 (rien ne s'affiche)
mosquitto_pub -h localhost -u g1e2 -P 'mdp-g1e2' -t cellule/g1e2/etat -m '{"etat": "secret"}'
mosquitto_sub -h localhost -u g1e1 -P 'mdp-g1e1' -t 'cellule/g1e2/#' -v -W 3
# Sans mot de passe : refusé
mosquitto_pub -h localhost -t cellule/g1e1/etat -m x            # Connection Refused: not authorised
```

- [ ] Connexion SSH avec un compte d'équipe, depuis un poste Linux de la salle et depuis un laptop
- [ ] Une équipe ne peut ni lire le dossier d'une autre (`ls /home/g1e2` refusé), ni ses topics
- [ ] Le site Flask d'une équipe de test s'ouvre depuis un laptop (`flask run --host 0.0.0.0 --port 8001`)
- [ ] **Essai de charge** : 8 simulateurs, 8 collecteurs et 16 serveurs Flask lancés ensemble, plusieurs connexions VS Code Remote SSH ; surveiller la mémoire et la température avec `htop` et `vcgencmd measure_temp`
- [ ] Redémarrage complet : Mosquitto et SSH repartent seuls, l'heure est juste
- [ ] Le robot publie sur le broker du Pi (au fab lab) : `~/cellule/lancer.sh ~/cellule/test.py --broker 192.168.10.11` sur le robot


## 10. Sauvegarde et restauration

- **Image complète du SSD**, une fois l'installation terminée, depuis un autre poste Linux (le Pi éteint, le SSD branché sur le poste, ici `/dev/sdX` ; vérifier le nom avec `lsblk`) :

  ```bash
  sudo dd if=/dev/sdX of=pi-cellule.img bs=4M status=progress conv=fsync
  sudo dd if=pi-cellule.img of=/dev/sdY bs=4M status=progress conv=fsync   # vers le SSD de secours
  ```

- **Après chaque séance**, collecteurs arrêtés (une base copiée pendant une écriture peut être incohérente), copie du travail des équipes :

  ```bash
  sudo tar czf ~/sauvegarde_$(date +%F).tgz /home/g?e? /etc/mosquitto
  ```

- **Remise à zéro** en fin de module : réécrire l'image du SSD, ou supprimer les comptes (`sudo ./creer_comptes_equipes.sh --supprimer inge`).
