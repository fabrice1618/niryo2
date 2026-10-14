# API du robot Ned2

Infrastructure client / serveur dans un contexte industriel

Cette API de départ s'exécute **sur le robot**. Elle reprend les scripts d'essai 7 à 9 (`essai_robot/`) : un endpoint par tâche, qui contient les appels au robot, et un message MQTT au début et à la fin de chaque tâche. Le site web de l'équipe l'appelle pour commander le robot. Le simulateur `simulateurs/simulateur_api.py` a les mêmes endpoints, sans robot.

| Méthode | Endpoint | Fonction | Action |
|---|---|---|---|
| `GET` | `/robot/etat` | `etat()` | Lit l'état du robot : axes, pose, capteur DI5, calibration, températures |
| `POST` | `/robot/home` | `home()` | Retour à la position home |
| `POST` | `/robot/autocalibrate` | `autocalibrate()` | Calibration automatique des moteurs |
| `POST` | `/robot/ledring/<couleur>` | `ledring(couleur)` | Clignotement de l'anneau de LED pendant 2 s (`rouge`, `vert`, `bleu`, `jaune`, `blanc`) |

## Une tâche à la fois, et l'état pour le tableau de bord

Le robot ne fait qu'une tâche à la fois :

| Situation | Réponse |
|---|---|
| Tâche terminée | `200` : `{"tache": "home", "statut": "terminee"}`, à la fin de la tâche |
| Demande pendant une autre tâche | `409` tout de suite : `{"erreur": "robot occupé : tâche autocalibrate en cours", "tache_en_cours": "autocalibrate"}`. La demande n'est **pas** exécutée plus tard : les clics répétés ne s'accumulent pas |
| Erreur du robot (par exemple un mouvement avant la calibration) | `500` : `{"tache": "home", "statut": "erreur", "erreur": "..."}` ; le robot est libéré |
| Couleur inconnue | `400` |

`GET /robot/etat` répond **tout de suite, même pendant une tâche**, avec un champ `tache_en_cours` : le nom de la tâche en cours, ou `null` quand le robot est libre. Le tableau de bord peut l'interroger régulièrement (par exemple toutes les secondes) pour afficher « calibration en cours » et griser les boutons.

Dans le code, chaque endpoint suit le même modèle :

```python
@app.post("/robot/home")
def home():
    if tache_en_cours is not None:     # une tâche à la fois
        return occupe()                # réponse 409
    commencer("home")                  # note la tâche en cours, publie debut_tache
    try:
        n.move_joints(*JOINTS_HOME)    # les appels au robot
    except Exception as e:
        return echec("home", e)        # libère le robot, publie fin_tache en erreur, réponse 500
    return terminer("home")            # libère le robot, publie fin_tache, réponse 200
```

## Messages MQTT

Sur `cellule/<equipe>/tache`, au début puis à la fin de chaque tâche :

```json
{"evenement": "debut_tache", "tache": "ledring", "couleur": "vert", "horodatage": "2026-11-17T08:30:00"}
{"evenement": "fin_tache", "tache": "ledring", "statut": "terminee", "couleur": "vert", "horodatage": "2026-11-17T08:30:02"}
{"evenement": "fin_tache", "tache": "home", "statut": "erreur", "erreur": "...", "horodatage": "2026-11-17T08:31:10"}
```

Le collecteur les enregistre avec les autres messages de l'équipe. Un `fin_tache` est publié pour chaque tâche commencée, même en cas d'erreur.

## Mode d'emploi

Flask et paho-mqtt doivent être installés sur le robot (dossier `install_robot/`).

1. Adapter les **paramètres en haut de `api_robot.py`** : identifiant de l'équipe, adresse du broker.
2. Copier le dossier sur le robot (remplacer `.21` par l'adresse de votre robot) et lancer l'API :

   ```bash
   scp -r api_robot niryo@192.168.10.21:~/cellule/
   ssh niryo@192.168.10.21
   cd ~/cellule/api_robot
   ~/cellule/lancer.sh api_robot.py
   ```

3. Depuis un poste :

   ```bash
   curl http://192.168.10.21:3000/robot/etat
   curl -X POST http://192.168.10.21:3000/robot/autocalibrate
   curl -X POST http://192.168.10.21:3000/robot/ledring/vert
   ```

Chaque appel s'affiche dans la console de l'API, avec les messages MQTT envoyés. En cas d'erreur du robot (par exemple un mouvement demandé avant la calibration), la réponse est `500`, avec le message d'erreur.

`home` et `autocalibrate` font bouger le bras : appliquer les consignes de sécurité de la prise en main. Aucun autre programme ne doit commander le robot en même temps (Niryo Studio, script d'essai).

## Ajouter une tâche

Copier le modèle en fin de fichier, enlever les `#` et remplacer `cycle` par le nom de la tâche (dans l'URL, le nom de la fonction et les appels à `commencer`, `echec` et `terminer`). Dans le `try`, mettre les appels au robot, repris de l'export Python de Niryo Studio. L'endpoint garde ainsi la même forme que les autres : la nouvelle tâche profite du refus `409`, de `tache_en_cours` et des messages MQTT. Ajouter la même tâche au simulateur, avec une attente à la place des appels au robot, permet de développer le site web sans robot.

`commencer`, `terminer` et `echec` acceptent un paramètre, `couleur`, ajouté aux messages MQTT et à la réponse. Une tâche qui a besoin d'un autre paramètre (une zone, un nombre de pièces) le reçoit dans l'URL, comme `ledring`, et l'ajoute de la même façon à ces trois fonctions.

## Documentation

- [Référence du Python ROS Wrapper](https://niryorobotics.github.io/ned_ros/packages/python_ros_wrapper/ros_wrapper_api.html) : toutes les fonctions de `n`, pour écrire de nouvelles tâches ;
- [anneau de LED](https://niryorobotics.github.io/ned_ros/packages/high_level/niryo_robot_led_ring.html) (`ledring`), [état du matériel](https://niryorobotics.github.io/ned_ros/packages/low_level/niryo_robot_hardware_interface.html) (`etat`), [exemples de mouvements](https://niryorobotics.github.io/ned_ros/packages/python_ros_wrapper/examples_motions.html) (`home`) ;
- index principal de la documentation : <https://niryorobotics.github.io/ned_ros/> (repris dans la partie 9 de `cours/01_prise_en_main_robot.md`).

## Essais réalisés et points à vérifier

L'API a été essayée sous Python 3.8, avec les versions de Flask et de paho-mqtt de `install_robot/`, un broker Mosquitto et un **faux** Python ROS Wrapper : les quatre endpoints, la couleur inconnue (`400`), refus `409` pendant une tâche (une seule demande acceptée sur cinq envoyées en même temps), `tache_en_cours` lu pendant une calibration avec une réponse immédiate, erreur du robot (`500`, `fin_tache` en erreur, robot libéré). Restent à vérifier sur un vrai robot : la position home (`JOINTS_HOME`, celle de Niryo Studio), le comportement de `calibrate_auto()` sur un robot déjà calibré, et les champs de l'état matériel, et la lecture de l'état (`GET /robot/etat`) pendant un mouvement du bras.
