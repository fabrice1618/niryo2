# Site web de supervision : base du tableau de bord

Infrastructure client / serveur dans un contexte industriel

Le site web est le tableau de bord de l'opérateur, ouvert dans un navigateur. Ce dossier en est la **base** : une seule page, volontairement simple et sans mise en forme recherchée, que chaque équipe complète et embellit (cours *HTML et CSS* et *Le framework Flask*). La page :

- propose les **commandes** du robot sous forme de boutons, avec un paramètre si besoin (la couleur de l'anneau de LED) ;
- affiche l'**état du robot**, mis à jour toutes les 2 secondes ;
- affiche les **20 derniers messages MQTT** enregistrés par le collecteur, mis à jour en même temps.

```mermaid
flowchart LR
    N["Navigateur<br/>de l'opérateur"] -- "HTTP, port 8001" --> S["Site web<br/>supervision.py"]
    S -- "HTTP<br/>GET /robot/etat<br/>POST /robot/…" --> A["API du robot<br/>(ou simulateur d'API)"]
    S -- "SELECT" --> DB[("cellule.db<br/>remplie par le collecteur")]
```

| Fichier | Rôle |
|---|---|
| `supervision.py` | Le site : paramètres en haut du fichier, une route par page et par commande |
| `templates/accueil.html` | La page : titre, boutons de commande, et quelques lignes de JavaScript qui rechargent l'état |
| `templates/etat.html` | La partie « état du robot et derniers messages », rechargée toutes les 2 secondes |
| `static/style.css` | La mise en forme, minimale |

Le site utilise Flask et `requests` (déjà installés sur le serveur ; sur un poste : voir *Lancement en local*).


## Mode d'emploi sur le serveur du module

1. **Copier le site** dans `~/supervision/`, à côté du collecteur et de sa base `cellule.db` :

   ```bash
   cp -r /opt/cellule/fournitures/site_web/* ~/supervision/
   ```

   Le dossier contient alors `creer_bdd.py`, `collecteur.py`, `cellule.db`, `supervision.py`, `templates/` et `static/`.

2. **Adapter les paramètres** en haut de `supervision.py` :

   ```python
   EQUIPE = "g1"                        # identifiant de l'équipe, affiché en titre
   URL_API = "http://127.0.0.1:5001"      # simulateur d'API ; le robot : "http://192.168.1.21:3000"
   BASE = "cellule.db"                    # base remplie par le collecteur
   PORT_SITE = 8001                       # 8000 + numéro de l'équipe (8001 à 8008)
   ```

   Chaque équipe a ses ports : site `8000 + n`, simulateur d'API `5000 + n` (paramètre `PORT_API` du simulateur), où `n` est le numéro de l'équipe.

3. **Lancer** le site, depuis `~/supervision` :

   ```bash
   cd ~/supervision
   python3 supervision.py
   ```

4. **Ouvrir** la page dans un navigateur : `http://192.168.1.10:8001` depuis un poste du fab lab (adresse du serveur, port de l'équipe).

Comme le collecteur, le site peut tourner dans une session `tmux` pour continuer après la fermeture du terminal (voir `collecteur/README.md`).

Avec `debug=True` (dernière ligne de `supervision.py`), le site redémarre tout seul à chaque modification d'un fichier : il suffit de recharger la page dans le navigateur. En cas d'erreur dans le code, le message s'affiche dans le terminal.


## Lancement en local

Sur son propre poste (Windows, macOS ou Linux), sans le serveur du module, tout le projet se lance **depuis la racine du dépôt**, avec un seul outil : `lancer.py`. Il n'y a rien à copier, ni environnement à activer.

**1. Installer Python**, une seule fois (les autres logiciels du poste, VS Code, WinSCP, DB Browser, MQTT Explorer, sont dans `INSTALLATION_POSTE.md`, à la racine) : version 3.10 ou plus récente, sur <https://www.python.org/downloads/>. Sous Windows, **cocher « Add python.exe to PATH »** dans la première fenêtre de l'installateur. Vérifier dans un terminal (PowerShell sous Windows) :

```bash
python --version             # sous Linux et macOS : python3 --version
```

Sous Windows, si `python` ouvre le Microsoft Store ou n'est pas reconnu, essayer `py --version` et utiliser `py` à la place de `python` dans toutes les commandes ci-dessous.

**2. Ouvrir le dossier du projet dans un terminal.** Avec VS Code : *Fichier > Ouvrir le dossier*, puis *Terminal > Nouveau terminal* : le terminal s'ouvre dans le bon dossier. Sinon, `cd` vers le dossier qui contient `lancer.py`.

**3. Régler les paramètres** en tête de chaque programme (ouvrir le fichier, modifier, enregistrer). Les valeurs par défaut conviennent pour un essai avec un broker installé sur le poste ; il suffit de les rendre **identiques partout** :

| Fichier | Paramètres à régler |
|---|---|
| `collecteur/creer_bdd.py` | `EQUIPE`, `ADRESSE_ROBOT` |
| `collecteur/collecteur.py` | `EQUIPE`, `BROKER` |
| `simulateurs/simulateur_api.py` | `EQUIPE`, `BROKER`, `PORT_API` (5001 par défaut) |
| `simulateurs/simulateur_mqtt.py` | `EQUIPE`, `BROKER` |
| `site_web/supervision.py` | `EQUIPE`, `URL_API` (`http://127.0.0.1:` suivi de `PORT_API`), `PORT_SITE` (8001 par défaut) |

**4. Un broker MQTT**, pour le collecteur et les simulateurs. Deux solutions, au choix :

- **Le broker public de test `test.mosquitto.org`**, sans rien installer : mettre `BROKER = "test.mosquitto.org"` dans les trois programmes qui l'utilisent (`collecteur.py`, `simulateur_api.py`, `simulateur_mqtt.py`). Il est ouvert à tous sur le port 1883 : pas de compte et aucun chiffrement. Trois précautions, parce que **tout le monde** y publie et s'y abonne :

  - **Choisir un `EQUIPE` unique**, le même dans les cinq fichiers du tableau (par exemple `g1-dupont`, avec votre nom). Avec `g1`, vous recevriez les messages de toute personne qui fait le même essai, et deux collecteurs qui portent le même nom de client se déconnectent l'un l'autre ;
  - **n'y envoyer rien de confidentiel** : les messages sont lisibles par tous, et un message retenu (`etat`) reste sur le broker après l'arrêt du simulateur ;
  - **ne pas en dépendre** : c'est un service de test, parfois lent ou indisponible. Il convient pour essayer le site, pas pour une séance : sur le serveur du module, le broker est le Mosquitto du serveur.

- **Un Mosquitto installé sur le poste** (`BROKER = "localhost"`, la valeur par défaut). Sous Windows : installateur sur <https://mosquitto.org/download/>. Sous Ubuntu :

  ```bash
  sudo apt install mosquitto             # démarre tout seul ; systemctl status mosquitto pour vérifier
  ```

  Sans fichier de configuration particulier, Mosquitto 2 n'accepte que les connexions de la machine elle-même, sans compte : c'est ce qu'il faut ici. Les messages restent sur le poste.

**5. Lancer**, un programme par terminal (dans VS Code, le bouton **+** du panneau Terminal ouvre un terminal de plus), toujours depuis la racine :

| Terminal | Commande | Rôle |
|---|---|---|
| 1 | `python lancer.py collecteur` | Enregistre les messages MQTT dans `cellule.db` |
| 2 | `python lancer.py api` | Simulateur d'API : remplace l'API du robot, sur le port 5001 |
| 3 | `python lancer.py site` | Le site, sur le port 8001 |
| 4 | `python lancer.py mqtt` | Simulateur de messages (cycle, état, défaut) : un menu où l'on choisit |

Ouvrir ensuite `http://127.0.0.1:8001` dans un navigateur. `Ctrl+C` arrête le programme du terminal ; après avoir modifié un paramètre, l'arrêter et le relancer.

**Au premier lancement**, `lancer.py` prépare tout seul ce qui manque, avec Internet (une à deux minutes) : le dossier `venv` (l'environnement Python du projet, avec les bibliothèques de `requirements.txt` : Flask, paho-mqtt, requests) et la base `cellule.db`, à la racine. Ces deux éléments ne sont pas versionnés (`.gitignore`). Pour repartir d'une base vide : arrêter le collecteur et le site, supprimer `cellule.db`, relancer.

`api_robot/` et `essai_robot/` ne se lancent pas ainsi : ils utilisent le Python ROS Wrapper et s'exécutent **sur le robot** (voir `install_robot/`). En local, le simulateur d'API les remplace. Une fois le projet au point, la copie sur le serveur se fait comme décrit dans la section précédente (les programmes y sont lancés avec `python3`, depuis `~/supervision`, sans `lancer.py`).

En cas de problème :

| Message | Cause |
|---|---|
| `python` : commande introuvable, ou le Microsoft Store s'ouvre | Python n'est pas installé, ou pas dans le `PATH` (le cocher à l'installation) : essayer `py lancer.py ...` |
| `No module named venv` (Ubuntu, Debian) | `sudo apt install python3-venv`, puis relancer |
| `Port 8001 is in use by another program` | Un autre programme du poste utilise ce port : mettre une autre valeur dans `PORT_SITE` (8002...) et ouvrir la page sur ce port |
| `Address already in use` au lancement du simulateur d'API | Même cause, pour `PORT_API` (et changer aussi `URL_API` dans `supervision.py`) |
| `Broker ... injoignable` ou `Connection refused` | Mosquitto n'est pas démarré (`sudo systemctl start mosquitto`) ; avec le broker public : pas de réseau, ou service de test indisponible |
| `API du robot injoignable` dans la page | Le simulateur d'API n'est pas lancé, ou `URL_API` ne correspond pas à son `PORT_API` |
| `Aucun message : le collecteur tourne-t-il ?` | Le collecteur n'est pas lancé, ou n'a pas le même `BROKER` et le même `EQUIPE` que le simulateur MQTT |


## Essayer sans robot

Le site a besoin de deux choses : une API qui répond (pour l'état et les commandes) et une base remplie par le collecteur (pour les messages). Sans robot, on les remplace par les simulateurs (`simulateurs/README.md`). Sur son poste, voir *Lancement en local* ; sur le serveur, les simulateurs sont copiés dans le dossier personnel avec les mêmes paramètres que le site et le collecteur (`EQUIPE`, `BROKER`, et `PORT_API` pour le simulateur d'API) :

```bash
cp /opt/cellule/fournitures/simulateurs/*.py ~/
```

Puis, dans quatre terminaux, depuis `~/supervision` :

| Terminal | Commande | Rôle |
|---|---|---|
| 1 | `python3 collecteur.py` | Enregistre les messages MQTT dans `cellule.db` (après `python3 creer_bdd.py`, une fois) |
| 2 | `python3 ~/simulateur_api.py` | Remplace l'API du robot, sur le port `5000 + n` |
| 3 | `python3 supervision.py` | Le site, sur le port `8000 + n` |
| 4 | `python3 ~/simulateur_mqtt.py` | Envoie des messages de cycle, d'état, de défaut |

Vérifier :

- l'heure « mis à jour à » change toutes les 2 secondes ;
- **Calibration** : le message « commande envoyée, tâche en cours » s'affiche, « Tâche en cours » passe à `autocalibrate`, puis revient à « aucune » après 20 secondes ; les messages `debut_tache` puis `fin_tache` apparaissent dans la liste ;
- **Position home** pendant la calibration : « refusée, robot occupé : tâche autocalibrate en cours » ;
- un message envoyé par le simulateur MQTT apparaît dans la liste au plus 2 secondes plus tard ;
- simulateur d'API arrêté : « API du robot injoignable » dans l'état et après chaque commande ; collecteur arrêté : la liste des messages ne bouge plus.

Pour passer au vrai robot, il suffit de changer `URL_API` (`http://192.168.1.21:3000`, adresse du robot de l'équipe) et de relancer le site : les endpoints, les réponses et les messages de l'API du robot sont ceux du simulateur.


## Comment il fonctionne

| Route | Rôle |
|---|---|
| `GET /` | Affiche la page `accueil.html` : titre, messages de la dernière commande, boutons |
| `GET /etat` | Demande l'état du robot à l'API (`lire_etat`), lit les 20 derniers messages dans la base (`derniers_messages`), et renvoie le morceau de page `etat.html` |
| `POST /commande/home`, `/commande/autocalibrate`, `/commande/ledring` | Un bouton chacun : envoie la commande à l'API (`envoyer`), puis revient à la page d'accueil, qui affiche le résultat |

**La mise à jour toutes les 2 secondes** : à la fin de `accueil.html`, quelques lignes de JavaScript demandent `/etat` au site toutes les 2 secondes et remplacent le contenu du bloc `<div id="etat">` par la réponse. Seule cette partie de la page change : les boutons et la couleur choisie restent en place. Le morceau de page est fabriqué par Flask avec un template, comme une page entière.

**Les commandes** : chaque bouton est un petit formulaire qui envoie un `POST` au site ; le site relaie la commande à l'API du robot avec `requests`, puis revient à la page d'accueil (schéma Post / Redirect / Get du cours de Flask) et affiche le résultat avec un message `flash`. L'API du robot ne répond qu'**à la fin de la tâche** (20 secondes pour une calibration) : le site n'attend qu'une seconde (`timeout=1`). Passé ce délai, il affiche « commande envoyée, tâche en cours » ; la tâche continue sur le robot, et sa fin se voit dans l'état (« Tâche en cours : aucune ») et dans les messages (`fin_tache`, avec `statut` `terminee` ou `erreur`).

| Résultat affiché | Cause |
|---|---|
| `tâche terminée` | La tâche a duré moins d'une seconde |
| `commande envoyée, tâche en cours` | La tâche dure plus d'une seconde : elle continue sur le robot |
| `refusée, robot occupé : tâche ... en cours` | Une autre tâche est en cours (`409`) |
| `refusée, couleur inconnue : ...` | Paramètre refusé par l'API (`400`) |
| `commande inconnue de l'API du robot` | La route n'existe pas dans l'API (`404`) : commande ajoutée au site mais pas à l'API |
| `API du robot injoignable` | API arrêtée, mauvaise adresse dans `URL_API` |

Le site ne fait que **lire** la base : seul le collecteur y écrit.


## Adapter le site

**Ajouter une commande** (une tâche ajoutée à l'API du robot et à son simulateur) :

1. dans `supervision.py`, copier le modèle en fin de fichier, enlever les `#` et remplacer `cycle` par le nom de la tâche ;
2. dans `templates/accueil.html`, copier le modèle de bouton (entre `{#` et `#}`), le sortir du commentaire et remplacer `cycle`.

Pour une commande avec un paramètre, prendre modèle sur l'anneau de LED : un champ dans le formulaire (`<select name="couleur">`, ou `<input name="nombre" type="number">`), lu dans la route avec `request.form["couleur"]` et ajouté au chemin de l'API.

**Afficher autre chose** : ajouter une fonction de lecture dans `supervision.py` (sur le modèle de `derniers_messages`, avec une requête `SELECT`), passer son résultat au template dans la route `etat`, l'afficher dans `etat.html`. Par exemple : le nombre de cycles du jour et la durée moyenne (table `cycles`, cours de SQL), le dernier défaut.

**Pistes pour aller plus loin** :

- présenter l'état du robot de façon lisible : un voyant « libre / occupé », la valeur du capteur DI5 en clair (« pièce présente »), des températures arrondies, plutôt que le tableau brut ;
- griser les boutons pendant une tâche (`tache_en_cours`) ;
- afficher les messages de façon lisible, une couleur par sujet ; filtrer par sujet ;
- ajouter des pages : liste des cycles, détail d'un cycle, incidents (cours *Le framework Flask*) ;
- soigner la mise en forme (cours *HTML et CSS*) : en-tête, cartes, couleurs, affichage sur téléphone.


## Essais réalisés

Avec un broker Mosquitto configuré comme celui du serveur du module, le collecteur, le simulateur d'API et le simulateur MQTT :

- page d'accueil et mise à jour de l'état toutes les 2 secondes, vérifiées dans un navigateur (Chrome) sur un écran d'ordinateur et à la largeur d'un téléphone ;
- les trois commandes : « commande envoyée, tâche en cours » en une seconde, « Tâche en cours » qui passe à `autocalibrate` puis revient à « aucune » après 20 secondes, messages `debut_tache` et `fin_tache` affichés ;
- refus pendant une tâche (`409`), couleur inconnue (`400`), simulateur d'API arrêté (« API du robot injoignable ») ;
- messages du simulateur MQTT, y compris mal formés, affichés dans la liste.
