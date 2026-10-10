# Matériel et préparation : IRUP (BACHTECH24 et B3RNSPP26)

- **Établissement :** IRUP
- **Classes :** BACH TECH 2024-0 (BACHTECH24, 2 équipes) et B3 RNSPP 2026-0 (B3RNSPP26, 4 équipes), effectifs inférieurs à 12 étudiants
- **Cours :** Infrastructure client / serveur dans un contexte industriel (progressions : `BACHTECH24.md` et `B3RNSPP26.md`)
- **Version :** v1.1 (brouillon), 08/10/2026
- **Dates :** plannings `seances_BACHTECH24.xlsx` et `seances_B3RNSPP26.xlsx` ; les lieux sont à réserver (section 7)
- **Document associé :** `materiel_ISTP.md` (autre établissement, autre serveur)

**En bref**

- Le serveur est le **NUC présent au fab lab**. Il démarre sur un **disque externe préparé à l'avance**. Il n'est pas accessible depuis la salle de classe.
- Conséquence : toutes les séances qui utilisent le serveur ont lieu **au fab lab**. C'est le cas de 12 séances sur 13 pour BACHTECH24 et de 9 séances sur 12 pour B3RNSPP26.
- 6 équipes au total (2 + 4), une équipe par robot. Les 2 équipes de BACHTECH24 utilisent des robots équipés d'une caméra (séances 10 et 11).
- Grafana tourne sur le NUC : à la séance 11 pour B3RNSPP26 et à la séance 12 pour BACHTECH24.
- À faire en premier : vérifier les robots avant la séance 1 de B3RNSPP26 (jeu. 15/10/2026), identifier les robots avec caméra, puis préparer le disque du NUC avant le ven. 06/11/2026.


## 1. Séances et besoins

**Légende :** Robots = robots et convoyeurs utilisés ; Serveur = NUC utilisé (broker, collecteur, sites, API) ; Grafana = dashboard.

### 1.1 B3RNSPP26 (4 équipes)

| Séance | Date | Lieu | Robots | Serveur | Remarque |
|--------|------|------|--------|---------|----------|
| Séance 1 | jeu. 15/10/2026, 08:30-12:00 | Fab lab | Oui | Non | Prise en main du robot |
| Séance 2 | jeu. 15/10/2026, 13:30-17:00 | Salle de cours | Non | Non | Analyse, dossier ; vidéoprojecteur |
| Séance 3 | mar. 10/11/2026, 08:30-12:00 | Fab lab | Non | Oui | Collecteur MQTT |
| Séance 4 | lun. 15/02/2027, 13:30-17:00 | Salle de cours | Non | Non | Cours HTTP, HTML, Flask ; serveur Flask lancé sur le poste |
| Séance 5 | mar. 16/02/2027, 13:30-17:00 | Salle de cours | Non | Non | Cours Flask et API ; pas de serveur |
| Séance 6 | mer. 17/02/2027, 08:30-12:00 | Fab lab | Non | Oui | Site web |
| Séance 7 | jeu. 18/02/2027, 08:30-12:00 | Fab lab | Non | Oui | API simulée |
| Séance 8 | jeu. 18/02/2027, 13:30-17:00 | Fab lab | Non | Oui | Site et API, dossier v2 |
| Séance 9 | mer. 24/02/2027, 08:30-12:00 | Fab lab | Oui | Oui | Le robot publie en MQTT |
| Séance 10 | mar. 04/05/2027, 08:30-12:00 | Fab lab | Oui | Oui | API sur le robot |
| Séance 11 | mar. 04/05/2027, 13:30-17:00 | Fab lab | Oui | Oui, Grafana | Dashboard Grafana, recette à blanc |
| Séance 12 | mer. 05/05/2027, 08:30-12:00 | Fab lab | Oui | Oui | Évaluation |

### 1.2 BACHTECH24 (2 équipes)

| Séance | Date | Lieu | Robots | Serveur | Remarque |
|--------|------|------|--------|---------|----------|
| Séance 1 | mer. 28/10/2026, 08:30-12:00 | Fab lab | Oui | Non | Prise en main du robot |
| Séance 2 | mar. 03/11/2026, 13:30-17:00 | Salle de cours | Non | Non | Analyse, dossier ; vidéoprojecteur |
| Séance 3 | ven. 06/11/2026, 13:30-17:00 | Fab lab | Non | Oui | MQTT, simulateur de process |
| Séance 4 | mar. 01/12/2026, 13:30-17:00 | Fab lab | Non | Oui | Collecteur MQTT vers SQLite |
| Séance 5 | mar. 08/12/2026, 08:30-12:00 | Fab lab | Non | Oui | API simulée |
| Séance 6 | lun. 25/01/2027, 13:30-17:00 | Fab lab | Non | Oui | Site web |
| Séance 7 | jeu. 28/01/2027, 13:30-17:00 | Fab lab | Non | Oui | Site et API, mise en exploitation |
| Séance 8 | jeu. 25/03/2027, 08:30-12:00 | Fab lab | Oui | Oui | Le robot publie en MQTT |
| Séance 9 | mar. 06/04/2027, 13:30-17:00 | Fab lab | Oui | Oui | API sur le robot, recette à blanc |
| Séance 10 | ven. 09/04/2027, 13:30-17:00 | Fab lab | Oui, avec caméra | Non | Vision (1) : caméra et OpenCV |
| Séance 11 | jeu. 29/04/2027, 08:30-12:00 | Fab lab | Oui, avec caméra | Oui | Vision (2) : la vision dans le cycle |
| Séance 12 | mar. 11/05/2027, 13:30-17:00 | Fab lab | Non | Oui, Grafana | Dashboard Grafana |
| Séance 13 | jeu. 17/06/2027, 13:30-17:00 | Fab lab | Oui | Oui | Évaluation |

Le fab lab est dans la même configuration pour toutes les classes (section 3.2). Seul le serveur change : celui d'ISTP est un Raspberry Pi, décrit dans `materiel_ISTP.md`.


## 2. Équipes

Chaque équipe a un **identifiant technique** (minuscules, sans accent, utilisé dans les comptes, les topics MQTT et les noms de fichiers) et un **nom** affiché sur le site web et dans Grafana. Les deux classes partagent le NUC : les identifiants et les ports sont donc distincts d'une classe à l'autre.

| Identifiant | Nom | Classe | Robot | Port API simulée | Port site web |
|-------------|-----|--------|-------|------------------|---------------|
| `t1e1` | Vega | BACHTECH24 | Robot avec caméra, numéro à renseigner | 5001 | 8001 |
| `t1e2` | Altair | BACHTECH24 | Robot avec caméra, numéro à renseigner | 5002 | 8002 |
| `r1e1` | Loire | B3RNSPP26 | Robot 1 (`192.168.10.21`) | 5003 | 8003 |
| `r1e2` | Rhône | B3RNSPP26 | Robot 2 (`192.168.10.22`) | 5004 | 8004 |
| `r1e3` | Seine | B3RNSPP26 | Robot 3 (`192.168.10.23`) | 5005 | 8005 |
| `r1e4` | Garonne | B3RNSPP26 | Robot 4 (`192.168.10.24`) | 5006 | 8006 |

Un thème par classe : les étoiles pour BACHTECH24 (Sirius, Rigel, Antares et Capella en réserve), les fleuves de France pour B3RNSPP26 (Dordogne, Marne, Saône et Meuse en réserve), les métaux pour BACHINGE24 (voir `materiel_ISTP.md`). Les robots de B3RNSPP26 sont les robots restants une fois les robots avec caméra affectés à BACHTECH24 (les numéros sont à ajuster en conséquence). Chaque équipe garde le même robot pendant toute la durée du projet : les poses et la calibration sont propres à un robot.

Sur le NUC, un compte Linux, un utilisateur MQTT et un compte Grafana sont créés par identifiant.


## 3. Matériel

Statuts : **Existant** (présent, à vérifier), **À fournir** (demande à l'IRUP), **Apporté** (par l'intervenant).

### 3.1 Serveur : NUC et disque externe

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 1 | NUC du fab lab, avec son alimentation | Mémoire de 8 Go ou plus recommandée (6 équipes et Grafana), ports USB 3 et Ethernet, démarrage sur USB autorisé | Existant, à vérifier |
| 1 | SSD externe USB 3, 256 Go | Disque de démarrage préparé à l'avance (contenu en section 5.1). Le disque interne du NUC n'est ni utilisé ni modifié | À fournir |
| 1 | SSD externe identique | Copie de secours, remise à jour après chaque séance | À fournir |
| 1 | Câble RJ45 cat. 6, 2 m | NUC vers le switch du fab lab | Existant, à vérifier |
| 1 | Écran, clavier, souris et câble vidéo | Maintenance du NUC (BIOS, première configuration). L'écran du fab lab peut convenir | Existant, à prêter |
| 1 | Multiprise parasurtenseur, onduleur si possible | Une coupure brutale peut corrompre une base SQLite | À fournir |

### 3.2 Fab lab (configuration commune à toutes les classes)

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 4 | Robots Niryo Ned2 avec alimentation | Firmware identique et à jour. Plusieurs robots ont une caméra | Existant, à vérifier |
| 4 | Convoyeurs Niryo avec capteur branché sur l'entrée DI5, alimentation | Capteur testé : il sert de déclencheur du cycle | Existant, à vérifier |
| 24 environ | Pièces à convoyer (cubes ou cylindres) | Quelques pièces par robot, plus des pièces de rechange | Existant, à vérifier |
| 4 | Câbles RJ45 2 à 3 m | Robots vers le switch du fab lab | Existant, à vérifier |
| 1 | Switch Gigabit du fab lab | Robots (4), NUC (1) et postes. Nombre de ports libres à vérifier | Existant, à vérifier |
| 1 | Routeur du fab lab, passerelle `192.168.10.1` avec DHCP | Plan d'adressage à relever sur place (section 4) | Existant, à vérifier |
| 6 | Postes avec Niryo Studio (ou laptops des étudiants) | Version compatible avec le firmware des robots. Un poste par équipe | Existant, à vérifier |
| 6 | Multiprises | Une par poste de travail | Existant, à vérifier |

### 3.3 Vision (BACHTECH24, séances 10 et 11)

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 2 au moins | Robots Ned2 avec caméra en état de marche | À identifier ; affectés aux 2 équipes dès la séance 8 pour qu'elles gardent le même robot | Existant, à vérifier |
| 2 | Espaces de travail calibrables (plateau avec repères) | Espace de travail (workspace) calibré dans Niryo Studio | À vérifier |
| 2 jeux | Pièces de plusieurs couleurs et de plusieurs formes (carré, rond) | Au moins 3 pièces par couleur et par forme | À vérifier, à compléter |
| 2 | Éclairage stable (lampe diffuse) | Une luminosité constante d'une séance à l'autre limite les réglages de seuils | À fournir |
| 2 | Postes avec `pyniryo` et `opencv-python` | Laptops des étudiants ou postes du fab lab | À vérifier |

### 3.4 Postes de travail et salle de cours

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 12 au plus | Laptops des étudiants, ou postes de l'IRUP | Python 3.10 ou plus, VS Code, MQTT Explorer, DB Browser for SQLite, `mosquitto-clients`, `curl`. Niryo Studio pour les séances avec robot | À vérifier |
| 1 | Vidéoprojecteur ou écran, câble HDMI | Séances de cours en salle (séances 2, 4 et 5 de B3RNSPP26 ; séance 2 de BACHTECH24) | À vérifier |
| 1 | Poste ou laptop de l'intervenant | Démonstrations, administration du NUC | Apporté |

Les séances en salle de cours n'ont pas besoin du serveur : Flask est lancé sur les postes (séances 4 et 5 de B3RNSPP26).

### 3.5 Petit matériel de rechange (à apporter à chaque séance)

| Qté | Désignation | Remarque | Statut |
|-----|-------------|----------|--------|
| 4 | Souris USB | Des souris peuvent manquer | Apporté |
| 2 | Claviers USB | Remplacement en cas de panne | Apporté |
| 8 | Câbles RJ45 2 m | Réserve. Des câbles réseau peuvent manquer | Apporté |
| 2 | Adaptateurs USB vers RJ45 Gigabit | Pour les laptops sans prise Ethernet | Apporté |
| 1 | Clé USB 32 Go | Copies de fichiers, paquets Python hors ligne | Apporté |
| 1 | Rallonge 5 m avec multiprise | Postes éloignés d'une prise | Apporté |
| 1 | Lot d'étiquettes | Identifiants des équipes sur les postes et les robots | Apporté |


## 4. Réseau du fab lab

Plan d'adressage proposé, à comparer avec la configuration réelle du fab lab :

| Élément | Adresse |
|---------|---------|
| Routeur (passerelle) | `192.168.10.1` |
| NUC de l'IRUP (serveur résident) | `192.168.10.10` |
| Raspberry Pi d'ISTP (visiteur, quelques séances) | `192.168.10.11` |
| Robots Ned2 | `192.168.10.21` à `192.168.10.24` |
| Postes des étudiants (DHCP) | `192.168.10.100` à `192.168.10.199` |

Le NUC et le Raspberry Pi d'ISTP ne doivent jamais avoir la même adresse : le NUC reste branché en permanence sur le réseau du fab lab, où le Pi vient les 12/10, 17/11 et 19/11/2026.

| Service | Port | Machine |
|---------|------|---------|
| SSH | 22 | NUC |
| Broker MQTT (Mosquitto) | 1883 | NUC |
| API simulée de chaque équipe | 5001 à 5006 | NUC |
| Site web de chaque équipe | 8001 à 8006 | NUC |
| Grafana | 3000 | NUC |
| API de commande sur le robot | 5000 | Robot |

L'heure du NUC doit être correcte (horodatage des cycles). Elle est réglée par NTP si le NUC a accès à Internet, sinon par le routeur ou à la main au démarrage.


## 5. Préparation et vérifications

### 5.1 Disque externe du NUC (à préparer en avance)

Contenu du disque :

- Ubuntu Server 24.04 LTS avec SSH, adresse IP fixe `192.168.10.10` (reprendre `documentation/config_nuc.md` de l'an dernier : netplan)
- Mosquitto avec authentification : un utilisateur MQTT par équipe (6), limité aux topics de l'équipe
- Python 3, paquets du projet (`paho-mqtt`, `flask`, `requests`) installés à l'avance, ainsi qu'un dépôt local de paquets pour une installation hors ligne (`package_nuc/` de l'an dernier)
- SQLite (bibliothèque et outil en ligne de commande), bases en mode WAL pour que Grafana lise pendant que le collecteur écrit
- Grafana (port 3000) avec le plugin SQLite, un utilisateur et un dossier de dashboards par équipe
- Un compte Linux par équipe (6), avec son dossier personnel, créés par `scripts/creer_comptes_equipes.sh irup` (mots de passe aléatoires, enregistrés dans un fichier que seul l'intervenant conserve)
- Outils fournis : simulateur de process, squelette de l'API CQRS en mode simulé, script d'historique simulé pour Grafana
- Services système (`systemd`) pour que le broker et Grafana redémarrent après une coupure

Préparation et tests :

- [ ] Disque préparé sur une machine avec accès à Internet (installation de Grafana et de son plugin), puis cloné sur le SSD de secours
- [ ] Démarrage du NUC sur le disque externe, sans toucher au disque interne
- [ ] Adresse fixe, connexion SSH depuis un laptop du fab lab
- [ ] Publication et réception MQTT avec chaque utilisateur d'équipe ; refus d'accès sur les topics des autres équipes
- [ ] Collecteur, API et site d'une équipe de test, ouverts depuis un laptop
- [ ] Grafana : connexion, lecture d'une base SQLite, panneau de test, alerte de test
- [ ] Redémarrage complet : les services repartent sans intervention
- [ ] Sauvegarde du disque après chaque séance (image complète ou copie des dossiers des équipes)

### 5.2 NUC et fab lab

- [ ] Le NUC s'allume, ne chauffe pas anormalement et son ventilateur tourne
- [ ] BIOS ou UEFI : démarrage sur USB autorisé, ordre de démarrage, Secure Boot, mot de passe éventuel connu ; redémarrage automatique après coupure de courant
- [ ] Mémoire, port USB 3 libre pour le SSD, port Ethernet
- [ ] Le disque interne contient peut-être des données de l'an dernier (MySQL, Docker, Grafana) : ne pas y toucher
- [ ] Le NUC est relié au switch du fab lab par un câble, sur une prise stable
- [ ] Adressage réel du fab lab relevé (routeur, plage DHCP, adresses déjà prises) et comparé à la section 4
- [ ] Internet : le NUC a-t-il accès à Internet ? Sans accès, VS Code Remote SSH ne peut pas installer son composant serveur : le développement se fait alors sur les laptops, avec déploiement par `scp` ou `git`
- [ ] Capacité du réseau pour 12 laptops au plus (Wi-Fi ou câble)
- [ ] Réservation du fab lab confirmée pour toutes les dates de la section 1

### 5.3 Robots, convoyeurs et caméras

À faire avant la séance 1 de B3RNSPP26 (jeu. 15/10/2026), puis avant la séance 1 de BACHTECH24 (mer. 28/10/2026).

- [ ] Chaque robot démarre, se calibre et exécute un mouvement ; noter le numéro et l'adresse IP de chacun
- [ ] Firmware identique sur les 4 robots ; version de Niryo Studio compatible installée sur les postes
- [ ] Chaque convoyeur tourne, son capteur répond sur DI5 (test avec une pièce)
- [ ] Pièces en nombre suffisant et en bon état
- [ ] Les 4 robots sont connectés au réseau du fab lab (câble) avec les adresses `192.168.10.21` à `.24`
- [ ] **Caméras** : repérer les robots équipés, afficher l'image dans Niryo Studio, vérifier la netteté et le champ de vue, lire une image depuis Python avec `pyniryo`
- [ ] Espace de travail calibré dans Niryo Studio pour les 2 robots affectés à BACHTECH24 ; éclairage installé
- [ ] Prises électriques, multiprises, zones de sécurité et arrêt d'urgence repérés

### 5.4 Salle de cours et postes

- [ ] Salle réservée pour la séance 2 de chaque classe et pour les séances 4 et 5 de B3RNSPP26
- [ ] Vidéoprojecteur ou écran testé
- [ ] Postes ou laptops : Python, `flask` et `pip` fonctionnent (séances 4 et 5 de B3RNSPP26 sans serveur) ; logiciels de la section 3.4 installés
- [ ] Souris et câbles réseau de rechange apportés

### 5.5 Répétition

- [ ] **Avant la séance 3 de BACHTECH24 (ven. 06/11/2026)** : répétition complète au fab lab avec un laptop : connexion SSH, publication MQTT, collecteur, site web
- [ ] **Avant la séance 9 de B3RNSPP26 et la séance 8 de BACHTECH24** : essai du robot réel publiant sur le broker du NUC
- [ ] **Avant la séance 11 de B3RNSPP26 et la séance 12 de BACHTECH24** : essai de Grafana avec l'historique simulé
- [ ] **Après chaque séance** : sauvegarde du disque, relevé du matériel manquant


## 6. Calendrier de préparation

| Échéance | Action | Séance concernée |
|----------|--------|------------------|
| Avant le jeu. 15/10/2026 | Vérification du fab lab et des robots (section 5.3) ; confirmation des réservations d'octobre et novembre | B3RNSPP26, séance 1 |
| Avant le mer. 28/10/2026 | Caméras repérées et testées, robots avec caméra affectés aux équipes `t1e1` et `t1e2` | BACHTECH24, séance 1 |
| Avant le ven. 06/11/2026 | Vérification du NUC (section 5.2) ; disque préparé, cloné et testé (section 5.1) ; répétition (section 5.5) | BACHTECH24, séance 3 |
| Avant le mar. 10/11/2026 | Comptes de B3RNSPP26 vérifiés ; sauvegarde du disque | B3RNSPP26, séance 3 |
| Avant le mar. 01/12/2026 | Sauvegarde ; mises à jour de sécurité | BACHTECH24, séances 4 et 5 |
| Avant le lun. 25/01/2027 | Contrôle du disque, des services et de la sauvegarde | BACHTECH24, séances 6 et 7 |
| Avant le mer. 17/02/2027 | Contrôle du disque, des services et de la sauvegarde | B3RNSPP26, séances 6 à 8 |
| Avant le mer. 24/02/2027 et le jeu. 25/03/2027 | Essai du robot publiant sur le broker du NUC ; poses des robots | B3RNSPP26 séance 9, BACHTECH24 séance 8 |
| Avant le ven. 09/04/2027 | Caméras, espaces de travail, éclairage, pièces de couleurs | BACHTECH24, séances 10 et 11 |
| Avant le mar. 04/05/2027 | Robots, API sur les robots, Grafana et historique simulé | B3RNSPP26, séances 10 à 12 |
| Avant le mar. 11/05/2027 | Grafana, plugin, comptes et dossiers par équipe | BACHTECH24, séance 12 |
| Avant le jeu. 17/06/2027 | Contrôle complet de chaque cellule, sauvegarde | BACHTECH24, séance 13 |


## 7. Points à confirmer avec l'IRUP

1. **Réservations du fab lab.** Presque toutes les séances ont lieu au fab lab, car le NUC n'est pas accessible depuis la salle de classe : 12 séances de BACHTECH24 et 9 séances de B3RNSPP26 (dates en section 1). Le fab lab est-il disponible sur tous ces créneaux ? Il accueille aussi ISTP les 12/10, 17/11 et 19/11/2026 : aucun chevauchement avec les créneaux de l'IRUP.
2. **NUC.** Modèle, mémoire, état, accès au BIOS ou à l'UEFI, démarrage sur USB, qui peut intervenir dessus. Peut-il rester allumé en permanence ?
3. **Réseau du fab lab.** Plan d'adressage réel, plage DHCP, nombre de ports libres sur le switch, Wi-Fi pour les laptops, accès à Internet.
4. **Robots avec caméra.** Lesquels ? Combien ? Peut-on les réserver aux 2 équipes de BACHTECH24 ? Les robots sans caméra sont-ils tous en état de marche ?
5. **Postes de travail.** Les étudiants viennent-ils avec leur laptop, ou y a-t-il des postes de l'IRUP ? Quel système ? Une prise Ethernet est-elle disponible ?
6. **Salle de cours.** Quelle salle pour les séances 2 (les deux classes) et 4 et 5 de B3RNSPP26 ? Vidéoprojecteur disponible ?
7. **Équipes.** La section 2 propose 2 équipes pour BACHTECH24 et 4 équipes pour B3RNSPP26. À corriger si l'effectif ou le découpage est différent.
8. **Grafana.** Installation d'un service sur le NUC (port 3000) acceptée par l'IRUP ? Les étudiants peuvent-ils ouvrir le port 3000 depuis leur poste ?
9. **Fourniture des SSD.** Qui fournit le SSD de démarrage et sa copie de secours ? Qui conserve la copie entre les séances ?
