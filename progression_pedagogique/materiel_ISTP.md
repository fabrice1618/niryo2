# Matériel et préparation : ISTP (BACHINGE24)

- **Établissement :** ISTP
- **Classe :** BACH INGE 2024-0 (BACHINGE24), 3e année, 22 étudiants alternants, groupes G1 et G2
- **Cours :** Infrastructure client / serveur dans un contexte industriel (progression : `BACHINGE24.md`)
- **Version :** v1.3 (brouillon), 11/10/2026
- **Dates :** planning `seances_BACHINGE24.xlsx` mis à jour le 10/10/2026, salles déjà réservées
- **Document associé :** `materiel_IRUP.md` (autres classes, autre établissement, autre serveur)

**En bref**

- 5 séances du 12/10 au 19/11/2026 : séance 2 en salle C1.07, séance 3 en salle D3.10, séances 1, 4 et 5 au fab lab.
- Le serveur est un **NUC Celeron** (Ubuntu Desktop, nom `istp`, adresse fixe `192.168.1.2`). Il est installé en salle D3.10, sur un réseau séparé où il distribue aussi les adresses (DHCP), pour la séance 3, puis transporté au fab lab pour les séances 4 et 5.
- 8 équipes (4 par groupe) pour 4 robots. Jusqu'à 22 étudiants en salle D3.10 à la séance 3, mais chaque équipe ne raccorde au réseau qu'un laptop environ (8 au plus) ; elle peut aussi utiliser un poste Linux de la salle, déjà relié au réseau.
- Échéances proches : robots vérifiés avant la séance 1 (lun. 12/10), puis **salle D3.10 remise en fonctionnement et NUC prêt avant la séance 3** (lun. 09/11, 08:30), soit au plus tard le ven. 06/11 (sections 5.1 et 5.2).


## 1. Séances et besoins

| Séance | Date | Lieu | Qui | Matériel utilisé |
|--------|-------------------|------|-----|------------------|
| Séance 1 | lun. 12/10/2026, 08:30-12:00 (G1) et 13:30-17:00 (G2) | Fab lab | Un groupe à la fois, environ 11 étudiants | 4 robots, 4 convoyeurs, Niryo Studio. Pas de serveur |
| Séance 2 | mer. 14/10/2026, 08:30-12:00 | Salle C1.07 | G1 + G2, 22 étudiants | Laptops des étudiants, vidéoprojecteur, prises électriques. Pas de robot, pas de serveur |
| Séance 3 | lun. 09/11/2026, 08:30-12:00 | Salle D3.10 | G1 + G2, 22 étudiants | NUC (serveur et DHCP), réseau séparé, 2 switches, postes Linux et laptops (un par équipe environ) : 8 collecteurs MQTT, 8 sites Flask et 8 API simulées |
| Séance 4 | mar. 17/11/2026, 08:30-12:00 (G1) et 13:30-17:00 (G2) | Fab lab | Un groupe à la fois, environ 11 étudiants | 4 robots, NUC : une équipe par robot, 3h30 par groupe |
| Séance 5 | jeu. 19/11/2026, 13:30-15:15 (G1) et 15:15-17:00 (G2) | Fab lab | Un groupe à la fois, environ 11 étudiants | 4 robots, NUC : évaluation, environ 25 min par équipe |

Le fab lab est dans la même configuration pour toutes les classes (section 3.4). Seul le serveur change.

La séance 3 a lieu quatre semaines après la séance 2 : le NUC et le réseau de la salle D3.10 peuvent être installés la veille ou une heure avant la séance, après un essai complet fait en amont (section 5.4). Entre les séances 2 et 3, les équipes travaillent sur leur laptop, sans serveur.


## 2. Équipes

4 équipes par groupe, soit 8 équipes (6 équipes de 3 et 2 équipes de 2). Chaque équipe a un **identifiant technique** (minuscules, sans accent, utilisé dans les comptes, les topics MQTT et les noms de fichiers).

| Identifiant | Groupe | Robot (IP) | Port API simulée | Port site web |
|-------------|--------|------------|------------------|---------------|
| `g1` | G1 | 1 (`192.168.1.21`) | 5001 | 8001 |
| `g2` | G1 | 2 (`192.168.1.22`) | 5002 | 8002 |
| `g3` | G1 | 3 (`192.168.1.23`) | 5003 | 8003 |
| `g4` | G1 | 4 (`192.168.1.24`) | 5004 | 8004 |
| `g5` | G2 | 1 (`192.168.1.21`) | 5005 | 8005 |
| `g6` | G2 | 2 (`192.168.1.22`) | 5006 | 8006 |
| `g7` | G2 | 3 (`192.168.1.23`) | 5007 | 8007 |
| `g8` | G2 | 4 (`192.168.1.24`) | 5008 | 8008 |

Aux séances 4 et 5, chaque groupe passe à son tour : l'équipe `gN` (`g1` à `g4`), puis l'équipe `g(N+4)` (`g5` à `g8`), utilisent le robot N, chacune seule sur son créneau. Un compte Linux est créé par identifiant sur le NUC. Les mêmes comptes Linux, avec les mêmes identifiants, sont créés sur les postes Linux de la salle D3.10 (section 3.3).


## 3. Matériel

Statuts : **Existant** (présent, à vérifier), **À fournir** (demande à ISTP), **Apporté** (par l'intervenant).

### 3.1 Serveur : NUC Celeron

Le serveur est un NUC à processeur Celeron sous Ubuntu Desktop 24.04 (installation classique depuis une clé USB, déjà faite), nom de machine `istp`, adresse fixe `192.168.1.2` en salle D3.10 comme au fab lab. La mémoire est dimensionnée par l'usage de VS Code à distance par les étudiants (8 Go au minimum) : à vérifier.

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 1 | NUC Celeron, Ubuntu Desktop 24.04 | Serveur du module : broker, serveur DHCP de la salle, 8 collecteurs, 8 sites, 8 API | Existant, à vérifier |
| 1 | Alimentation d'origine du NUC | Charge continue pendant 3h30 : vérifier aussi la température | Existant, à vérifier |
| 1 | Écran, clavier et souris, ou câble HDMI vers l'écran de la salle | Le NUC a une session graphique (DBeaver, MQTT Explorer) et sert de console locale en cas de panne réseau | À fournir |
| 2 | Câbles RJ45 cat. 6, 2 m | Un par lieu (salle D3.10 et fab lab), le NUC voyage avec son câble | À fournir |
| 1 | Valise ou boîte de transport avec calage | Le NUC voyage entre la salle D3.10 et le fab lab | À fournir |
| 1 | Disque externe USB 3, 256 Go au minimum | Image du disque du NUC (copie de secours), remise à jour après chaque séance | À fournir |
| 1 | Clé USB d'installation Ubuntu Desktop 24.04 | Réinstallation ou restauration de l'image (mode « Try Ubuntu ») | Apporté |
| 1 | Second NUC ou autre machine de secours | Facultatif : on y restaure l'image du disque pour reprendre rapidement | Option |

### 3.2 Réseau de la salle D3.10

La salle D3.10 dispose d'un réseau séparé qui permet d'utiliser le serveur. Les deux switches relient les laptops des étudiants et le NUC à ce réseau (voir la section 4.1).

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 2 | Switch 5 ports, avec câbles | Raccordés au réseau séparé : laptops, NUC. Les câbles RJ45 sont fournis avec chaque switch | À fournir |
| 12 | Câbles RJ45 cat. 5e ou 6, 2 m | 8 laptops (un par équipe), le NUC, la liaison au réseau et 2 de réserve, en complément des câbles fournis avec les switches. Des câbles peuvent manquer : compter sur place | À fournir |
| 4 | Adaptateurs USB vers RJ45 Gigabit | Pour les laptops sans prise Ethernet | Option |
| 1 | Routeur Wi-Fi avec DHCP | Secours, fourni par ISTP. Le NUC distribue lui-même les adresses du réseau `192.168.1.0/24` (serveur DHCP dnsmasq) ; ce routeur ne sert que si le NUC ne peut pas le faire ou si le réseau séparé n'a pas assez de prises | Option (ISTP) |
| 5 | Multiprises 6 prises | Chargeurs des laptops, switches, NUC | À fournir |

### 3.3 Postes de travail de la salle D3.10

Des postes Linux (Ubuntu 24.04 desktop) sont disponibles pour le développement. Ils sont à remettre en fonctionnement (section 5.1).

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 8 au moins | Postes Linux Ubuntu 24.04 desktop | Un par équipe au minimum. Nombre réel à compter | Existant, à remettre en état |
| 8 au moins | Écrans, claviers, souris | Des souris peuvent manquer | Existant, à compléter |
| 1 | Vidéoprojecteur ou grand écran, câble HDMI, en salle D3.10 | TP et démonstrations de la séance 3 | Existant, à vérifier |
| 1 | Vidéoprojecteur ou grand écran, câble HDMI, en salle C1.07 | Cours et présentations flash de la séance 2 (8 équipes de 5 min) | Existant, à vérifier |
| 22 | Places avec prise électrique, en salle C1.07 | Les étudiants travaillent sur leur laptop (séance 2) | À vérifier |
| 1 | Poste ou laptop de l'intervenant, avec accès au NUC | Démonstrations, administration | Apporté |

Logiciels attendus sur chaque poste Linux : Python 3.12 avec `python3-venv` et `pip`, `git`, VS Code (extensions Python et Remote-SSH), `mosquitto-clients`, MQTT Explorer, DB Browser for SQLite (`sqlitebrowser`), `curl`, un navigateur web. Paquets Python du projet (`paho-mqtt`, `flask`, `requests`) disponibles en local si le réseau séparé n'a pas d'accès à Internet.

**Comptes du projet.** Les 8 comptes des équipes (`g1` à `g8`) existent sur chaque poste Linux, avec les mêmes identifiants que sur le NUC. Ils sont créés par le script `scripts/creer_comptes_equipes.sh`, qui génère un mot de passe aléatoire par compte (procédure en section 5.1). Les dossiers personnels des postes sont locaux : le travail de référence d'une équipe reste dans son dossier sur le NUC, quel que soit le poste utilisé.

### 3.4 Fab lab (configuration commune à toutes les classes)

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 4 | Robots Niryo Ned2 avec alimentation | Firmware identique et à jour. Plusieurs robots ont une caméra (non utilisée par cette classe) | Existant, à vérifier |
| 4 | Convoyeurs Niryo avec capteur branché sur l'entrée DI5, alimentation | Capteur testé : il sert de déclencheur du cycle | Existant, à vérifier |
| 24 environ | Pièces à convoyer (cubes ou cylindres) | Quelques pièces par robot, plus des pièces de rechange | Existant, à vérifier |
| 4 | Câbles RJ45 2 à 3 m | Robots vers le switch du fab lab | Existant, à vérifier |
| 1 | Switch Gigabit du fab lab | Robots (4), serveur (1) et postes. Nombre de ports libres à vérifier | Existant, à vérifier |
| 1 | Routeur Wi-Fi avec DHCP du fab lab, passerelle `192.168.1.1` | Fourni par l'IRUP. Plan d'adressage `192.168.1.0/24` (section 4.2) | À fournir (IRUP) |
| 4 | Postes avec Niryo Studio (ou laptops des étudiants) | Une version de Niryo Studio compatible avec le firmware des robots | Existant, à vérifier |
| 4 | Multiprises | Une par poste de travail | Existant, à vérifier |

Aux séances 1, 4 et 5, un seul groupe (environ 11 étudiants) est au fab lab à la fois : vérifier la capacité du réseau (Wi-Fi ou câble) pour les laptops.


## 4. Réseau

### 4.1 Salle D3.10

- Le réseau séparé de la salle relie les postes Linux (déjà raccordés) et le NUC. Les deux switches (section 3.2) y raccordent les laptops des équipes, un par équipe environ.
- Autorisations nécessaires entre les postes et le NUC : SSH (22), MQTT (1883), HTTP sur les ports des équipes (5001 à 5008 et 8001 à 8008). Pas de blocage entre un poste et le NUC (pas d'isolation des clients).
- Adresses : le NUC est le serveur DHCP du réseau séparé (plage `192.168.1.100` à `192.168.1.199`, assez large pour les 8 laptops, les postes Linux et l'intervenant) et garde l'adresse fixe `192.168.1.2`. Il faut donc qu'aucun autre serveur DHCP ne réponde sur ce réseau (à vérifier avec ISTP) ; sinon, le NUC garde son adresse fixe et ne distribue rien.
- Internet n'est pas indispensable pendant les séances. Sans Internet, VS Code Remote SSH ne peut pas installer son composant serveur sur le NUC : le développement se fait alors sur les postes Linux, avec déploiement vers le NUC par `scp` ou `git`.

### 4.2 Fab lab

Plan d'adressage du fab lab (réseau `192.168.1.0/24`), à configurer sur le routeur Wi-Fi fourni par l'IRUP :

| Élément | Adresse |
|---------|---------|
| Routeur (passerelle) | `192.168.1.1` |
| Serveur du module (NUC d'ISTP, ou NUC de l'IRUP les autres jours) | `192.168.1.2` |
| Robots Ned2 | `192.168.1.21` à `192.168.1.24` |
| Postes des étudiants (DHCP) | `192.168.1.100` à `192.168.1.199` |

Le NUC d'ISTP garde la même adresse (`192.168.1.2`) en salle D3.10 et au fab lab. Trois profils réseau sont préparés sur le NUC (`salle`, `fablab`, `dhcp`) et on change de profil à l'installation avec `sudo profil-reseau`. Le serveur DHCP du NUC ne tourne qu'en salle D3.10 : au fab lab, le routeur de l'IRUP distribue déjà les adresses, un seul serveur DHCP par réseau. Le NUC de l'IRUP a la même adresse (`192.168.1.2`) : les deux NUC ne doivent jamais être branchés en même temps sur le réseau du fab lab. Les 17/11 et 19/11/2026, jours où celui d'ISTP vient, le NUC de l'IRUP est débranché.

### 4.3 Ports

| Service | Port | Machine |
|---------|------|---------|
| SSH | 22 | Serveur |
| Broker MQTT (Mosquitto) | 1883 | Serveur |
| API simulée de chaque équipe | 5001 à 5008 | Serveur |
| Site web de chaque équipe | 8001 à 8008 | Serveur |
| API de commande sur le robot (le port 5000 est pris par le logiciel système de Niryo) | 3000 | Robot |


## 5. Préparation et vérifications

### 5.1 Remise en fonctionnement des ordinateurs de la salle D3.10

Étape dédiée, sur place, avant la seule séance en salle D3.10 : la séance 3, lun. 09/11/2026 à 08:30. Prévoir une demi-journée à une journée, au plus tard le **ven. 06/11/2026**.

- [ ] Obtenir l'accès à la salle (clé, badge) et le droit d'intervenir sur les postes (compte administrateur)
- [ ] Compter les postes Linux, les repérer et les numéroter (étiquettes)
- [ ] Allumer chaque poste : alimentation, démarrage, connexion à une session
- [ ] Pour chaque poste, vérifier l'écran, le clavier et la souris, et noter ce qui manque
- [ ] Vérifier l'espace disque libre et la date et l'heure
- [ ] Mettre à jour Ubuntu 24.04 (sécurité) et vérifier que le système démarre encore
- [ ] Installer ou compléter les logiciels de la section 3.3, puis tester chacun (VS Code, MQTT Explorer, DB Browser for SQLite, `mosquitto_pub`)
- [ ] Créer les 8 comptes des équipes sur chaque poste avec `scripts/creer_comptes_equipes.sh` (procédure ci-dessous) et vérifier une ouverture de session graphique avec l'un d'eux
- [ ] Vérifier la liaison réseau de chaque poste vers le réseau séparé : prise murale, câble, adresse obtenue
- [ ] Compter les prises réseau et les prises électriques de la salle, comparer au nombre de laptops à raccorder (8, un par équipe)
- [ ] Vérifier le vidéoprojecteur ou l'écran et son câble
- [ ] Salle C1.07 (séance 2) : vidéoprojecteur, prises électriques pour 22 laptops, accès à la salle à 08:30
- [ ] Noter dans un tableau : numéro du poste, état, ce qui a été remplacé, ce qui reste à faire

**Création des comptes des équipes.** Le script crée un compte par équipe (`g1` à `g8`) avec un mot de passe aléatoire de 12 caractères, sans caractères ambigus. Il enregistre les mots de passe dans un fichier `identifiant:motdepasse` en lecture seule pour son propriétaire. Réutiliser ce fichier donne les mêmes mots de passe sur toutes les machines, NUC compris. Les dossiers personnels sont en accès privé (une équipe ne lit pas les fichiers d'une autre) et les comptes n'ont pas de droits d'administration.

```bash
# 1. Une seule fois, sur le NUC (ou sur le laptop de l'intervenant) : crée les comptes
#    et le fichier comptes_inge.txt (essai possible avec --simulation, sans rien modifier)
sudo ./creer_comptes_equipes.sh inge

# 2. Sur chaque poste Linux de la salle D3.10 : mêmes comptes, mêmes mots de passe.
#    Copier le fichier dans le dossier de l'administrateur (une clé USB FAT ne garde pas les droits)
sudo cp /media/cle/comptes_inge.txt /root/ && sudo chmod 600 /root/comptes_inge.txt
sudo ./creer_comptes_equipes.sh --fichier /root/comptes_inge.txt inge
sudo shred -u /root/comptes_inge.txt

# 3. Après le dernier cours : supprimer les comptes et leurs dossiers (demande une confirmation)
sudo ./creer_comptes_equipes.sh --supprimer inge
```

- Imprimer une fiche par équipe (identifiant, nom, mot de passe) à distribuer à la séance 3 une fois les démonstrations des équipes faites, et conserver le fichier des mots de passe chez l'intervenant uniquement.
- Un mot de passe oublié ou compromis se change avec `--reinitialiser` sur la machine concernée ; penser à le changer aussi sur les autres machines (relancer avec le fichier mis à jour).
- Le script a été essayé dans un conteneur Ubuntu 24.04 (création, relance, réinitialisation, suppression). Une dernière vérification sur un poste de la salle D3.10 reste à faire.

### 5.2 Serveur NUC

- [ ] Contrôle du matériel de la section 3.1 (NUC, mémoire, alimentation, câbles, disque externe)
- [ ] Préparation du NUC : Ubuntu Desktop (nom `istp`), SSH, Mosquitto ouvert (sans compte), Python et paquets, SQLite, DBeaver et MQTT Explorer, 8 comptes Linux créés par `scripts/creer_comptes_equipes.sh inge` (le fichier des mots de passe sert ensuite aux postes de la salle D3.10), ports attribués : procédure complète dans `install/install_nuc_istp.md`
- [ ] Veille désactivée, redémarrage automatique après une coupure de courant (BIOS), services Mosquitto et SSH repartis seuls au redémarrage
- [ ] Heure vérifiée après un arrêt complet
- [ ] Adresse fixe `192.168.1.2` et profils réseau (`salle`, `fablab`, `dhcp`) ; serveur DHCP (dnsmasq) actif en profil `salle`, arrêté en profil `fablab`
- [ ] Un laptop branché au réseau de la salle reçoit bien une adresse de `.100` à `.199`
- [ ] Température et stabilité après 1 heure de charge
- [ ] **Essai de charge** : 8 simulateurs, 8 collecteurs et 16 serveurs Flask lancés en même temps, avec plusieurs connexions VS Code Remote SSH
- [ ] Sauvegarde : image du disque sur le disque externe, procédure de restauration testée
- [ ] Image propre conservée pour remettre le serveur à zéro
- [ ] **Serveur de secours** si le NUC n'est pas disponible pour la séance 3 (lun. 09/11) : laptop de l'intervenant sous Ubuntu, avec Mosquitto, Python, SQLite et les 8 comptes (même script), branché au switch avec l'adresse prévue pour le NUC (`192.168.1.2`)

### 5.3 Fab lab et robots

À faire avant la séance 1 (lun. 12/10/2026). La vérification est la même pour toutes les classes.

- [ ] Chaque robot démarre, se calibre et exécute un mouvement ; noter le numéro et l'adresse IP de chacun
- [ ] Firmware identique sur les 4 robots ; version de Niryo Studio compatible installée sur les postes
- [ ] Chaque convoyeur tourne, son capteur répond sur DI5 (test avec une pièce)
- [ ] Logiciel des robots en version 5.3 ou plus (Python 3.8), accès SSH avec le compte `niryo` ; bibliothèques du projet installées sur chaque robot avec le dossier `install_robot/` du dépôt (`./install.sh`, puis `~/cellule/lancer.sh ~/cellule/test.py --robot`). Les robots sont communs aux trois classes : une seule installation suffit
- [ ] Pièces en nombre suffisant et en bon état
- [ ] Les 4 robots sont connectés au réseau du fab lab (câble) avec les adresses `192.168.1.21` à `.24`
- [ ] Routeur Wi-Fi du fab lab (fourni par l'IRUP) configuré selon la section 4.2 : réseau `192.168.1.0/24`, plage DHCP, adresses fixes des deux NUC et des robots
- [ ] Capacité du réseau pour une douzaine de laptops (un groupe à la fois, séances 1, 4 et 5)
- [ ] Prises électriques, multiprises, zones de sécurité et arrêt d'urgence repérés

### 5.4 Répétition et installation le jour de la séance

- [ ] **Avant la séance 3 (au plus tard le ven. 06/11)** : installation complète en salle D3.10 (2 switches, câbles, NUC, 2 postes Linux et 2 laptops), connexion SSH, publication et réception MQTT, ouverture d'un site Flask depuis un laptop
- [ ] **Jour de la séance 3 (lun. 09/11)** : arriver 1 heure avant, installer les switches et le NUC (`sudo profil-reseau salle`), tester une connexion depuis un poste Linux et depuis un laptop
- [ ] **Avant la séance 4 (mar. 17/11, avant 08:30)** : transporter le NUC au fab lab, le brancher, passer en profil fab lab (`sudo profil-reseau fablab`, ce qui arrête le serveur DHCP), vérifier l'accès du robot au broker (`~/cellule/lancer.sh ~/cellule/test.py --broker 192.168.1.2` sur chaque robot) et l'accès du serveur à l'API du robot (port 3000)
- [ ] **Après chaque séance** : sauvegarde du disque du NUC, relevé du matériel manquant, remise en état de la salle


## 6. Calendrier de préparation

Les dates sont celles du planning `seances_BACHINGE24.xlsx` : les échéances sont à décaler si elles changent. Le calendrier est serré en fin de module : les séances 3, 4 et 5 ont lieu les 09/11, 17/11 et 19/11.

| Échéance | Action | Séance concernée |
|----------|--------|------------------|
| Avant le lun. 12/10/2026 | Vérification du fab lab et des robots (section 5.3) | Séance 1 |
| Mer. 14/10/2026 | Séance 2 en salle C1.07 (vidéoprojecteur, prises pour 22 laptops, accès à 08:30) : pas de matériel serveur | Séance 2 |
| Avant le ven. 06/11/2026 | Matériel de la section 3.1 contrôlé, NUC préparé et testé (section 5.2) ; remise en fonctionnement de la salle D3.10 (section 5.1) ; réponses d'ISTP sur le réseau et les salles (section 7). Sans NUC, préparer le serveur de secours | Séance 3 |
| Ven. 06/11/2026 | Installation complète en salle D3.10 : switches, câbles, NUC, essai depuis un poste Linux et depuis un laptop (section 5.4) | Séance 3 |
| Lun. 09/11/2026, 1 heure avant | Installation du NUC en salle D3.10 (profil `salle`, serveur DHCP actif) ; avant : mises à jour, état du disque, nouvel essai de charge | Séance 3 |
| Lun. 09/11/2026, après la séance | Sauvegarde du disque ; le NUC repart chez l'intervenant | Séance 4 |
| Mar. 17/11/2026, avant 08:30 | Installation du NUC d'ISTP au fab lab (profil `fablab`, serveur DHCP arrêté, NUC de l'IRUP débranché : même adresse `192.168.1.2`), vérifications réseau : robots vers le broker, serveur vers l'API des robots | Séance 4 |
| Mar. 17/11/2026, entre les deux groupes | Contrôle du NUC, sauvegarde du disque | Séance 4 |
| Jeu. 19/11/2026, avant 13:30 | NUC allumé et vérifié, robots prêts | Séance 5 |
| Après le jeu. 19/11/2026 | Suppression des comptes sur les postes de la salle D3.10 (`--supprimer`), remise en état de la salle | Fin du module |


## 7. Points à régler avec ISTP

Les salles sont déjà réservées (planning `seances_BACHINGE24.xlsx`) : séance 2 en salle C1.07, séance 3 en salle D3.10, séances 1, 4 et 5 au fab lab. Le calendrier est une contrainte non modifiable. Restent à obtenir d'ISTP les points suivants, tous à régler avant la séance 3 (lun. 09/11).

1. **Salles.** Réservées : rien à confirmer, sauf l'accès à la salle D3.10 avant la séance 3 (point 4).
2. **Réseau séparé de la salle D3.10.** Distribution d'adresses (DHCP : le NUC peut le faire lui-même, à condition qu'aucun autre serveur DHCP ne réponde sur ce réseau), nombre de prises murales, ports autorisés (22, 1883, 5001 à 5008, 8001 à 8008), isolation des clients, accès à Internet.
3. **Postes Linux.** Combien de postes ? Qui administre ? L'intervenant peut-il avoir les droits (`sudo`) pour installer des logiciels et créer des comptes ? (Les postes sont déjà reliés au réseau séparé.)
4. **Accès à la salle D3.10.** Possibilité d'y entrer avant la séance 3 (au plus tard le ven. 06/11) pour l'installation, et une heure avant la séance du lun. 09/11.
5. **Équipement des salles.** À vérifier sur place : vidéoprojecteur ou écran dans les salles C1.07 et D3.10, et prises électriques pour 22 laptops en salle C1.07.
6. **Mise à disposition du NUC et de ses accessoires** (section 3.1), disponibilité (le NUC doit être prêt le 06/11), qui conserve le matériel entre les séances.
7. **Laptops des étudiants.** Tous les laptops ont-ils une prise Ethernet ? Sinon, quels adaptateurs prévoir ?
8. **Équipes.** La section 2 suppose 4 équipes par groupe (8 au total), comme dans la progression `BACHINGE24.md`. À corriger si le découpage des équipes est différent.
9. **Serveur de secours.** Si le NUC n'est pas disponible avant le 06/11, ISTP peut-il prêter une machine Linux pour la séance 3, ou l'intervenant utilise-t-il son laptop ?
