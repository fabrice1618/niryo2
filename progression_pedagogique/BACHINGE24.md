# Progression pédagogique : Infrastructure client / serveur dans un contexte industriel

- **Promotion :** BACH INGE 2024-0 (3e année), 22 étudiants alternants, groupes G1 et G2
- **Année :** 2026-2027
- **Version :** v1.5 (brouillon), 08/10/2026
- **Prérequis :** Python (cours de 1re année)
- **Sources :** `seances_BACHINGE24.xlsx` (planning : dates, horaires, salles et matériel, à confirmer) et supports 2025-2026 (dossier de l'année précédente)
- **Présentation du projet :** `README.md` à la racine (contexte, besoins, objectifs, fonctions, synoptique, données échangées), commun aux trois classes
- **Supports de cours :** dossier `cours/` (voir la fin de la section 4)

**En bref**

- 6 séances, du 12 octobre au 19 novembre 2026, soit 19h15 par étudiant.
- 22 étudiants en 8 équipes de 2 ou 3, sur 4 robots.
- Le serveur est un Raspberry Pi, installé en salle D3.10 puis au fab lab (voir `materiel_ISTP.md`).
- Un projet fil rouge : une cellule robotisée supervisée, construite séance après séance.
- Évaluation : chaque équipe déroule son propre cahier de recette devant l'enseignant.


## 1. Intention générale

Le module est organisé en **projet fil rouge** : chaque équipe conçoit, réalise et fait recetter une **cellule robotisée supervisée**.

➡️ process robot (Niryo Ned2 + convoyeur) → remontée des données par MQTT → stockage SQL → site web et API de pilotage

Par rapport à l'an dernier :

- on part d'un **process défini par les étudiants** et non plus d'exercices techniques isolés ;
- une **phase d'analyse** (dossier, présentation, tests de recette) est ajoutée avant la partie technique ;
- la pile technique est **allégée** : SQLite au lieu de MySQL, pas de Docker, pas de Grafana ni de Node-RED, le tableau de bord est le site web Flask ;
- l'évaluation repose sur l'**exécution du cahier de recette** rédigé par l'équipe elle-même.


## 2. Compétences visées

| Code | Compétence | Séances |
|------|------------|---------|
| C1 | Programmer une séquence robotisée (Blockly puis Python) | 1 et 5 |
| C2 | Analyser un process industriel et le spécifier (dossier, recette) | 1 et 2 |
| C3 | Mettre en œuvre une communication client / serveur (MQTT, HTTP) | 3, 4 et 5 |
| C4 | Collecter et stocker des données de production (SQL / SQLite) | 3 et 5 |
| C5 | Développer une interface web et une API en Python (Flask) | 4 et 5 |
| C6 | Intégrer, tester et valider un système (recette) | 5 et 6 |


## 3. Architecture cible du fil rouge

L'architecture, les fonctions F1 à F7, le cycle instrumenté et le scénario complet des échanges sont présentés dans le `README.md` (sections 4 et 5). Dans cette classe, le serveur du module est un Raspberry Pi (voir section 6) et les robots sont au fab lab.

![Architecture de la cellule](../robot_niryo-architecture.drawio.png)

**Séance où chaque fonction est réalisée**

| Fonction | Brique | Réalisée en | Passage sur le robot réel |
|----------|--------|-------------|---------------------------|
| F1 Exécuter le cycle | Programme process | Séance 1 (Blockly, export Python) | Séance 5 |
| F2 Recevoir les commandes | API CQRS | Séance 4, en mode simulé sur le serveur | Séance 5 |
| F3 Exposer l'état | API CQRS | Séance 4, en mode simulé sur le serveur | Séance 5 |
| F4 Publier les événements | Client MQTT du robot | Séance 3 avec le simulateur de process fourni, puis entre les séances 3 et 4 dans le programme robot | Séance 5 |
| F5 Transmettre les messages | Broker Mosquitto | Préparé par l'enseignant sur le serveur (section 6) | (sur le serveur) |
| F6 Collecter et stocker | Collecteur Python + base SQLite | Séance 3 | (sur le serveur) |
| F7 Présenter | Site web Flask | Séance 4 | (sur le serveur) |

**Exemple de process :** une pièce est posée sur le convoyeur, le convoyeur tourne jusqu'au capteur (DI5), le robot prend la pièce, la dépose dans une zone, le cycle est compté et horodaté (diagramme dans le `README.md`, section 5, « Le cycle instrumenté »).

**Données remontées** (à définir par chaque équipe à la séance 2) : début / fin de cycle, durée de cycle, nombre de pièces, état du robot, défauts.


## 4. Vue d'ensemble des séances

| Séance | Thème | Groupe | Date | Lieu | Durée | Livrable en fin de séance |
|--------|-------|--------|------|------|-------|---------------------------|
| Séance 1 | Prise en main du robot, export Python, définition du process | G1 | lun. 12/10/2026, 08:30-12:00 | Fab lab | 3h30 | Programme Blockly et export `.py`, fiche process v0 |
| Séance 1 | (idem) | G2 | lun. 12/10/2026, 13:30-17:00 | Fab lab | 3h30 | (idem) |
| Séance 2 | Analyse, dossier, présentation, tests de recette | G1 + G2 | mer. 14/10/2026, 08:30-12:00 | Salle C1.07 | 3h30 | Dossier d'analyse v1, cahier de recette v1 |
| Séance 3 | MQTT, rappel SQL, collecte des données dans SQLite | G1 + G2 | mer. 14/10/2026, 13:30-17:00 | Salle D3.10, serveur | 3h30 | Collecteur MQTT → SQLite sur le serveur, alimenté par des données simulées |
| Séance 4 | Python, site web et API | G1 + G2 | lun. 09/11/2026, 08:30-12:00 | Salle D3.10, serveur | 3h30 | Site web et API (mode simulé) sur le serveur |
| Séance 5 | Intégration sur les robots, recette à blanc | G1 | mar. 17/11/2026, 08:30-12:00 | Fab lab | 3h30 | Système intégré, recette à blanc |
| Séance 5 | (idem) | G2 | mar. 17/11/2026, 13:30-17:00 | Fab lab | 3h30 | (idem) |
| Séance 6 | Évaluation : recette | G1 | jeu. 19/11/2026, 13:30-15:15 | Fab lab | 1h45 | Recette signée, code déposé |
| Séance 6 | (idem) | G2 | jeu. 19/11/2026, 15:15-17:00 | Fab lab | 1h45 | (idem) |

Dates, horaires, salles et matériel : planning `seances_BACHINGE24.xlsx`. Les dates et les salles sont à confirmer (voir la section 7).

```mermaid
gantt
    title Calendrier 2026-2027
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    tickInterval 1week
    todayMarker off
    section G1 + G2
        Séances 2 et 3 · Analyse, MQTT, collecte  : 2026-10-14, 1d
        Séance 4 · Python, site web, API          : 2026-11-09, 1d
        Rendu dossier v2 (proposé)                : milestone, 2026-11-16, 0d
        Séance 6 · Évaluation (1h45 par groupe)  : milestone, 2026-11-19, 0d
    section G1
        Séance 1 · Prise en main du robot         : 2026-10-12, 1d
        Séance 5 · Intégration (3h30)             : crit, 2026-11-17, 1d
    section G2
        Séance 1 · Prise en main du robot         : 2026-10-12, 1d
        Séance 5 · Intégration (3h30)             : crit, 2026-11-17, 1d
```

**Volumes horaires** (planning)

- **Par étudiant :** 5 séances de 3h30 + 1 séance de 1h45, soit **19h15**.
- **Pour l'enseignant :** séances 1 et 5 assurées deux fois (4 × 3h30) + séances 2, 3 et 4 (3 × 3h30) + séance 6 assurée deux fois (2 × 1h45), soit **28h**.

**Organisation des équipes**

- 4 robots, une équipe par robot dans chaque groupe : 4 équipes par groupe, 8 équipes au total.
- 22 étudiants : 6 équipes de 3 et 2 équipes de 2.
- Les équipes sont constituées à la séance 1 et restent les mêmes jusqu'à l'évaluation.
- Identifiants `g1e1` à `g2e4` et noms (thème des métaux) : voir `materiel_ISTP.md`.

**Supports de cours** (dossier `cours/`, et `README.md` à la racine)

| Fichier | Titre | Séances |
|---------|-------|---------|
| `README.md` | Présentation du projet : contexte, besoins, objectifs, fonctions, synoptique | 1 (présentation) et 2 |
| `reseau_TCP_IP.md` | Révisions réseau : TCP/IP, adressage, routage, sous-réseaux, configuration statique et DHCP | 3 (révision) et 5 |
| `collecteur_MQTT.md` | Collecteur de messages MQTT en Python vers une base de données | 3 |
| `SQL.md` | Rappels de SQL | 3 |
| `site_web_HTML_CSS.md` | Cours HTML et CSS : réaliser les pages d'un site web | 4 |
| `intro_flask.md` | Le framework Flask : premiers pas | 4 |
| `API_CQRS_REST_Flask.md` | Une API CQRS pour le robot Niryo, comparée à REST, avec Flask | 4 et 5 |


## 5. Détail des séances

### Séance 1 : prise en main du robot, export Python, définition du process

| Lieu | Groupes | Durée | Matériel |
|------|---------|-------|----------|
| Fab lab | G1 le matin, G2 l'après-midi | 3h30 | Robots Ned2 et convoyeurs |

**Objectifs**

- Utiliser le robot Ned2 en sécurité
- Programmer un pick & place avec convoyeur en Blockly (Niryo Studio)
- Exporter le programme en Python et en comprendre la structure
- Définir le process que l'équipe va industrialiser

**Déroulé**

| Durée | Activité |
|-------|----------|
| 20 min | **Lancement** : présentation du module et du fil rouge (`README.md`, sections 1 à 3), constitution des équipes, consignes de sécurité (zone de travail, arrêt d'urgence, vitesses) |
| 60 min | **Prise en main** : connexion Niryo Studio, calibration, mode apprentissage, mouvements articulaires et cartésiens, pince |
| 70 min | **Scénario guidé** : convoyeur jusqu'au capteur DI5, prise de la pièce, dépose, retour en position d'attente |
| 30 min | **Export Python** : lecture du code généré (`calibrate_auto`, `move_pose`, `pick_from_pose`, `control_conveyor`, `digital_read`), repérage des poses et des fonctions |
| 30 min | **Process de l'équipe** : étapes, entrées / sorties, cas d'erreur, premières données à remonter |

**Livrables**

- Programme Blockly et export `.py` déposés (avec les poses relevées, à conserver pour l'intégration du 17/11)
- Fiche process v0 (une page)

**Ressources reprises de l'an dernier**

- `essai_robot/script1_autocalibrate.py`, `script2_convoyeur.py`, `script3_convoyeur_pick.py`
- `documentation/sdk.md`


### Séance 2 : analyse, dossier, présentation, tests de recette

| Lieu | Groupes | Durée | Matériel |
|------|---------|-------|----------|
| Salle C1.07 | G1 + G2 ensemble (22 étudiants) | 3h30 | Pas de robot, pas de serveur. Vidéoprojecteur |

**Objectifs**

- Situer le projet dans une architecture client / serveur industrielle
- Rédiger un dossier d'analyse
- Écrire des tests de recette vérifiables
- Présenter son projet à l'oral

**Déroulé**

| Durée | Activité |
|-------|----------|
| 45 min | **Cours** : architecture client / serveur en contexte industriel (niveaux terrain, supervision, gestion) ; du besoin (piloter, informer, observer) aux fonctions F1 à F7 et au rôle de chaque brique du fil rouge ; cahier des charges et recette |
| 2h | **Atelier par équipe** : rédaction du dossier d'analyse à partir d'un gabarit fourni |
| 45 min | **Présentations flash** : 5 min par équipe (8 équipes), puis retours |

**Contenu attendu du dossier d'analyse**

Le dossier peut suivre le plan du `README.md` (contexte, besoins, objectifs, fonctions, synoptique), appliqué au process de l'équipe :

- Description du process (séquence ou grafcet simplifié)
- Schéma d'architecture : composants et flux
- Dictionnaire des données : quelle donnée, à quel moment, quel format
- Fonctions attendues du site web (maquette papier acceptée)
- Cahier de recette : au moins 8 tests (identifiant, exigence, préconditions, procédure, résultat attendu)

La partie technique (topics MQTT, table SQL, routes de l'API) reste au niveau fonctionnel. Elle sera précisée dans la v2 du dossier, après les séances 3 et 4 (rendu proposé : lun. 16/11/2026, avant la séance 5).

**Livrables**

- Dossier d'analyse v1 et cahier de recette v1

**Supports de cours**

- `README.md` (présentation du projet, à utiliser comme modèle de plan pour le dossier)


### Séance 3 : MQTT, rappel SQL, collecte des données dans SQLite

| Lieu | Groupes | Durée | Matériel |
|------|---------|-------|----------|
| Salle D3.10 | G1 + G2 ensemble (22 étudiants) | 3h30 | Serveur Raspberry Pi (section 6) sur le réseau séparé de la salle, postes Linux et laptops des étudiants. Pas de robot : le process est simulé |

La séance a lieu l'après-midi même de la séance 2 : les données définies le matin dans le dossier v1 servent de point de départ au simulateur.

**Objectifs**

- Expliquer le modèle publication / abonnement
- Se connecter au serveur et y travailler à distance
- Publier et recevoir des messages JSON via le broker du serveur
- Créer une table et l'alimenter depuis Python
- Collecter les données du process de l'équipe sur le serveur

**Déroulé**

| Durée | Activité |
|-------|----------|
| 40 min | **Cours MQTT** : broker, clients, topics, payload JSON, QoS, authentification. Démonstration avec `mosquitto_pub` / `mosquitto_sub` sur le broker du serveur |
| 50 min | **TP connexion et MQTT** : connexion au serveur (SSH, avec VS Code Remote SSH si la salle a accès à Internet) avec le compte de l'équipe (mêmes identifiant et mot de passe sur le serveur et sur les postes Linux de la salle), puis publier et s'abonner sur le broker du serveur (MQTT Explorer puis `paho-mqtt`) |
| 30 min | **Rappel SQL** : table, types, clé primaire, `CREATE`, `INSERT`, `SELECT`, `WHERE`, `GROUP BY`. SQLite (module `sqlite3`, DB Browser for SQLite) |
| 1h30 | **TP collecte** : un simulateur publie les événements du process de l'équipe ; le collecteur tourne sur le serveur, reçoit les messages, les valide et les insère dans SQLite. Requêtes de contrôle (nombre de cycles, durée moyenne) |

**Flux de collecte**

```mermaid
sequenceDiagram
    participant SIM as Simulateur de process (robot en séance 5)
    participant B as Broker Mosquitto
    participant C as Collecteur Python
    participant DB as Base SQLite
    C->>B: Abonnement à cellule/<equipe>/#35;
    SIM->>B: Publication sur cellule/<equipe>/cycle (JSON)
    B->>C: Transmission du message
    C->>DB: INSERT INTO messages (message brut)
    C->>C: Validation du JSON
    C->>DB: INSERT INTO cycles (fin de cycle valide)
```

**Proposition de modèle de données (point de départ)**

Conventions reprises des supports `cours/collecteur_MQTT.md` et `cours/SQL.md` (détail et exemples de messages dans le `README.md`, section 6) :

- Topics : `cellule/<equipe>/cycle`, `cellule/<equipe>/etat` (message retenu), `cellule/<equipe>/defaut`, avec `<equipe>` de la forme `g1e1`
- Message : `{"evenement": "fin_cycle", "piece": 12, "duree": 18.2, "zone": "A", "horodatage": "2026-11-17T08:30:18"}`
- Tables : `messages(id, recu_le, sujet, charge, qos, retain)` (journal brut), `robots(id, nom, equipe, adresse_ip)` et `cycles(id, robot_id, debut, duree, zone, statut)` (lue par le site web)

**Livrables**

- `collecteur.py` déployé sur le serveur et fonctionnel sur données simulées, script de création de la base

**Supports de cours**

- `cours/collecteur_MQTT.md`
- `cours/SQL.md`
- `cours/reseau_TCP_IP.md` (révision : adressage, ports, connexion au serveur)

**Ressources reprises de l'an dernier**

- `code/mqtt_message/` : `sender.py` (à transformer en simulateur de process) et `subscriber.py` (à passer de MySQL à SQLite)
- `essai_robot/script4_mqtt_send.py`, `script5_mqtt_receive.py`
- `tp/fiche_configuration.md` (à adapter : comptes, topics, ports par équipe)

**Travail entre les séances 3 et 4 (4 semaines)**

- Dossier v2 : topics, format des messages, schéma de la base, routes de l'API
- Finaliser le collecteur
- Préparer dans le programme robot les appels de publication MQTT


### Séance 4 : Python, site web et API

| Lieu | Groupes | Durée | Matériel |
|------|---------|-------|----------|
| Salle D3.10 | G1 + G2 ensemble (22 étudiants) | 3h30 | Serveur Raspberry Pi (section 6) : exécution de l'API et du site web, base SQLite de la séance 3. Pas de robot : l'API fonctionne en mode simulé |

**Objectifs**

- Réinvestir les acquis Python de 1re année dans un projet
- Expliquer une requête HTTP et une API REST
- Développer une API de commande et un site web avec Flask, et les exécuter sur le serveur

**Déroulé**

| Durée | Activité |
|-------|----------|
| 15 min | **Python pour le projet** (le langage a été vu en 1re année) : environnement virtuel et `pip`, bibliothèques `flask` et `requests` |
| 30 min | **Cours HTTP / REST** : client / serveur, `GET` / `POST`, codes de retour, JSON. Tests avec `curl` |
| 1h15 | **TP API** : écrire l'API de commande du robot selon le principe CQRS (`GET /requetes/etat`, `POST /commandes/demarrer`, `/commandes/arreter`, `/commandes/calibrer`) en mode simulé (`RobotSimule`), sans appel au robot. Exécution sur le serveur, sur le port attribué à l'équipe (5001 à 5008) |
| 1h30 | **TP site web** : tableau de bord exécuté sur le serveur (port 8001 à 8008), lisant la base SQLite de la séance 3 (dernier état, liste des cycles, compteurs), avec des boutons de commande appelant l'API |

**Flux de consultation et de commande**

```mermaid
sequenceDiagram
    actor O as Opérateur
    participant W as Site web Flask
    participant DB as Base SQLite
    participant A as API de commande (simulée, puis robot en séance 5)
    O->>W: GET / (tableau de bord)
    W->>DB: SELECT des derniers cycles
    DB-->>W: Résultats
    W-->>O: Page HTML
    O->>W: Clic sur « Démarrer »
    W->>A: POST /commandes/demarrer
    A-->>W: 202 Accepted + id de commande
    W-->>O: Confirmation affichée
```

Le scénario complet, de la commande jusqu'à l'affichage des cycles, est dans le `README.md` (section 5, « Les échanges : un scénario complet »).

**Livrables**

- Site web et API (mode simulé) déployés sur le serveur, alimentés par les données simulées de la séance 3

**Supports de cours**

- `cours/site_web_HTML_CSS.md` (HTML, CSS, principe des routes)
- `cours/intro_flask.md` (routes, templates Jinja2, formulaires, lecture de la base SQLite, appel de l'API)
- `cours/API_CQRS_REST_Flask.md` (API de commande du robot, mode simulé)

**Ressources reprises de l'an dernier**

- `code/api_robot_test/` (API simulée du robot de l'an dernier, port 3000 : remplacée par l'API CQRS du cours, ports 5001 à 5008)
- `code/website_commande/specification.md`
- `essai_robot/script6_api.py`, `script7_API_mqtt.py`

**Travail entre les séances 4 et 5 (8 jours)**

- Terminer le dossier v2 (rendu proposé : lun. 16/11/2026)
- Tester le programme process et l'API en mode simulé : seul le passage au robot réel doit rester à faire à la séance 5


### Séance 5 : intégration sur les robots

| Lieu | Groupes | Durée | Matériel |
|------|---------|-------|----------|
| Fab lab | Par groupe : G1 le matin, G2 l'après-midi | 3h30 | Robots, convoyeurs et serveur (Raspberry Pi apporté de la salle D3.10) |

Le collecteur, la base et le site web tournent déjà sur le serveur depuis les séances 3 et 4 : la séance porte sur le robot et sa liaison avec le serveur.

Chaque groupe a le fab lab pendant 3h30, avec une équipe par robot (4 équipes, 4 robots). Le robot n'a pas été utilisé depuis la séance 1, cinq semaines plus tôt : la séance commence par une reprise en main. L'intégration n'est possible dans ce temps que si le programme process et l'API ont été testés en mode simulé avant la séance (voir la section 7).

**Objectifs**

- Déployer le programme process et l'API sur le robot
- Remplacer le simulateur de process et l'API simulée par le robot réel
- Faire fonctionner la chaîne de bout en bout
- Dérouler la recette à blanc et corriger

**Déroulé**

| Durée | Activité |
|-------|----------|
| 15 min | **Vérifications réseau** (préparées par l'enseignant avant la séance) : IP du robot et du serveur, accès du robot au broker, accès du serveur à l'API du robot |
| 30 min | **Reprise en main** : consignes de sécurité, calibration, relecture de l'export Python de la séance 1 et des poses relevées |
| 1h30 | **Déploiement** sur le robot : programme process, publication MQTT et API (passage du mode simulé aux appels réels), reprise des poses si besoin |
| 45 min | **Essai de bout en bout** (robot → serveur → site web → robot) et **recette à blanc** sur une sélection de tests du cahier |
| 30 min | **Bilan** : corrections à faire avant l'évaluation, deux jours plus tard, mise à jour du cahier de recette |

**Livrables**

- Système intégré, cahier de recette pré-rempli

**Supports de cours**

- `cours/reseau_TCP_IP.md`, section « Application : le réseau de la cellule robotisée » (connexion au Ned2, flux, diagnostic)
- `cours/API_CQRS_REST_Flask.md`, section « Dans le projet fil rouge » (passage de l'API simulée au robot)

**Ressources reprises de l'an dernier**

- `flask_arm/` : paquets Python pour l'installation hors ligne sur le robot


### Séance 6 : évaluation par la recette

| Lieu | Groupes | Durée | Matériel |
|------|---------|-------|----------|
| Fab lab | Par groupe : G1 de 13:30 à 15:15, G2 de 15:15 à 17:00 | 1h45 | Cellule intégrée de chaque équipe (robot et serveur) |

**Déroulé** (4 équipes par groupe, environ 25 min par équipe)

Pendant qu'une équipe passe, l'équipe suivante prépare sa cellule sur un autre robot.

| Durée | Activité |
|-------|----------|
| 18 min | **Recette** : l'équipe déroule les tests de son cahier choisis par l'enseignant ; chaque test est noté conforme ou non conforme |
| 7 min | **Questions individuelles** sur l'architecture et le code |

**Proposition de grille** (à valider)

| Élément | Poids |
|---------|-------|
| Dossier d'analyse et cahier de recette (version finale) | 30 % |
| Recette : tests conformes, fonctionnement de bout en bout | 50 % |
| Questions individuelles | 20 % |


## 6. Serveur : Raspberry Pi

ISTP met à disposition un Raspberry Pi qui fait office de serveur. Il démarre sur un SSD USB contenant un Linux préparé à l'avance par l'enseignant. Le matériel demandé, le réseau, les comptes et les vérifications sont détaillés dans `materiel_ISTP.md`.

Le serveur sert aux séances 3 et 4 (salle D3.10, sur un réseau séparé), puis aux séances 5 et 6 (fab lab). Le travail des équipes reste sur le SSD d'une séance à l'autre.

**Intérêts**

- Aucune installation sur le parc ISTP, hors les comptes du projet sur les postes Linux de la salle D3.10
- Environnement identique pour toutes les équipes, maîtrisé par l'enseignant
- Le Pi se transporte facilement de la salle D3.10 au fab lab ; en cas de panne, le SSD de secours démarre sur un autre Raspberry Pi
- Remise à zéro rapide à partir d'une image du SSD

**Contenu préparé sur le SSD**

- Distribution Linux 64 bits pour Raspberry Pi (par exemple Ubuntu Server 24.04 LTS) avec serveur SSH
- Un compte par équipe (8 comptes : `g1e1` à `g2e4`), avec son dossier personnel, créés avec `scripts/creer_comptes_equipes.sh` (mêmes comptes sur les postes Linux de la salle D3.10)
- Broker Mosquitto avec authentification : un utilisateur MQTT par équipe, limité aux topics de l'équipe
- Python 3 et les paquets du projet (`paho-mqtt`, `flask`, `requests`), installés à l'avance
- SQLite (bibliothèque et outil en ligne de commande)
- Ports attribués par équipe : 5001 à 5008 pour l'API simulée, 8001 à 8008 pour le site web
- Outils fournis aux équipes : simulateur de process (publie sur `cellule/<equipe>/…`), squelette de l'API CQRS en mode simulé

**Réseau**

- **En salle D3.10 (séances 3 et 4)** : un réseau séparé permet d'utiliser le serveur. Les postes Linux de la salle y sont raccordés ; un switch apporté par l'enseignant connecte les laptops des étudiants et le Pi. SSH (22), MQTT (1883) et les ports HTTP (5001 à 5008 et 8001 à 8008) doivent être autorisés entre les postes et le Pi.
- **Au fab lab (séances 5 et 6)** : le serveur rejoint le réseau des robots avec une adresse IP fixe (plan d'adressage proposé dans `cours/reseau_TCP_IP.md` : réseau `192.168.10.0/24`, robots en `.21` à `.24`). Le NUC de l'IRUP occupe l'adresse `.10` : le Pi prend `.11` (voir `materiel_ISTP.md`). L'API tourne alors sur chaque robot, port 5000.

```mermaid
flowchart TB
    subgraph SALLE["Séances 3 et 4 : salle D3.10"]
        direction LR
        PE1["Postes Linux et laptops étudiants"] --- SW1["Switch<br/>réseau séparé de la salle"]
        SW1 --- SV1["Raspberry Pi<br/>serveur"]
    end
    subgraph FAB["Séances 5 et 6 : fab lab"]
        direction LR
        PE2["Laptops étudiants"] --- R2["Réseau des robots"]
        R2 --- SV2["Raspberry Pi<br/>même SSD, IP fixe"]
        R2 --- ROB["4 robots Ned2"]
    end
    SALLE -. "même SSD : travail des équipes conservé" .-> FAB
```

**À vérifier avec ISTP**

- Disponibilité de la salle C1.07 (séance 2), de la salle D3.10 (séances 3 et 4) et du fab lab (séances 1, 5 et 6), ainsi que de la salle D3.10 la veille de la séance 3 pour l'installation
- Réseau séparé de la salle D3.10 : distribution d'adresses, nombre de prises, ports autorisés, accès à Internet
- Postes Linux de la salle D3.10 : nombre, état, droits pour créer les comptes
- Fourniture du Raspberry Pi et de ses accessoires (demande du 06/10/2026), délai de livraison

**Calendrier de préparation**

- Robots et fab lab vérifiés avant la séance 1 (lun. 12/10)
- Salle D3.10 remise en état et Raspberry Pi prêt et testé avant la séance 3, soit au plus tard le mar. 13/10, la veille. Si le Pi n'est pas livré à temps, un serveur de secours (laptop de l'intervenant avec la même configuration) assure la séance 3
- Sauvegarde du SSD après chaque séance (image complète ou copie des dossiers des équipes)

**Ressources reprises de l'an dernier**

- `documentation/config_nuc.md` (IP fixe avec netplan), `documentation/config_routeur.md`
- `package_nuc/` : paquets Python pour l'installation hors ligne


## 7. Points à arbitrer

1. **Début de module très rapproché.** Les séances 2 et 3 ont lieu le même jour (mer. 14/10) : analyse le matin en salle C1.07, serveur l'après-midi en salle D3.10. La salle D3.10 et le Raspberry Pi doivent être prêts au plus tard le mar. 13/10 (liste dans `materiel_ISTP.md`).
   - Le dossier d'analyse v1 est produit le matin même : le simulateur de la séance 3 part des données qu'il définit, ou des messages proposés dans cette progression si le dossier est en retard.
   - Si le Pi n'est pas livré à temps, prévoir un serveur de secours (laptop de l'intervenant).
2. **Fin de module en trois jours.** Les séances 4, 5 et 6 sont séparées de 8 jours, puis de 2 jours (09/11, 17/11, 19/11). Le programme process et l'API doivent être testés en mode simulé avant le 17/11, et les corrections se font entre la séance 5 et l'évaluation.
   - Rendu du dossier v2 proposé le lun. 16/11, avant la séance 5 ; dossier final à l'évaluation.
   - La recette de l'évaluation (environ 25 min par équipe, dont 18 min de recette) porte sur une sélection de tests ; les questions individuelles sont courtes.
3. **Salles à confirmer.** Le planning donne les salles : C1.07 (séance 2), D3.10 (séances 3 et 4), fab lab (séances 1, 5 et 6). À vérifier : l'équipement de la salle C1.07 (vidéoprojecteur, prises pour 22 laptops) et le réseau séparé de la salle D3.10. Les dates restent à confirmer.
4. **Peu de temps sur les robots.** Les étudiants n'ont le robot qu'à la séance 1 (3h30), à la séance 5 (3h30) et à l'évaluation (25 min par équipe). Le process doit rester simple. Aux séances 3 et 4, le travail se fait sur le serveur réel, mais avec un process simulé et une API en mode simulé.
5. **Typage des séances.** Toutes les lignes du planning sont en « CM » sauf l'évaluation du 19/11 (« TEST »), alors que les séances 1 et 5 sont des TP et la séance 2 un atelier.
6. **Intervalle de 4 semaines entre les séances 3 et 4** (14/10 → 09/11). Les équipes finalisent le collecteur et préparent dans le programme robot les appels de publication MQTT. Un point d'étape en début de séance 4 suffit à maintenir le rythme.
