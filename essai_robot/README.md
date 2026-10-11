# Scripts d'essai sur le robot Ned2

Infrastructure client / serveur dans un contexte industriel

Ces scripts reprennent, en les adaptant aux conventions du projet, les essais réalisés sur les robots l'année précédente. Chacun teste **une seule brique** du projet fil rouge directement sur le robot : la calibration, le convoyeur, le cycle, la publication et la réception MQTT, l'API web, la lecture de l'état du robot. Les énoncés correspondants sont dans la partie 7 du support de cours [`cours/01_prise_en_main_robot.md`](../cours/01_prise_en_main_robot.md) ; les scripts en sont les corrigés.

## Contenu

| Fichier | Ce qu'il fait | Bras en mouvement |
|---|---|---|
| `config.py` | Paramètres communs : équipe, broker, port de l'API, poses, couleurs | |
| `script1_calibration.py` | Calibration complète, avec signal lumineux et sonore | Oui |
| `script2_convoyeur.py` | Convoyeur en marche jusqu'à la détection d'une pièce sur DI5 | Non (convoyeur) |
| `script3_convoyeur_prise.py` | Un cycle complet : convoyeur, prise, dépose, retour en attente | Oui |
| `script4_mqtt_envoi.py` | Publie un message JSON chaque seconde sur `cellule/<equipe>/essai` | Non |
| `script5_mqtt_reception.py` | Fait clignoter l'anneau de LED à la réception d'une couleur sur `cellule/<equipe>/led` | Non |
| `script6_api.py` | API web : `POST /led` fait clignoter l'anneau de LED | Non |
| `script7_api_mqtt.py` | Comme le script 6, puis publie un événement MQTT à la fin de l'action | Non |
| `script8_etat_robot.py` | Lit l'état du robot (axes, pose, DI5, outil, températures, convoyeur) : fonction `lire_etat(n)` | Non |
| `script9_api_etat.py` | API web : `GET /robot/etat` renvoie l'état lu par le script 8 | Non |

## Ce qui a changé par rapport à l'année précédente

- Un **nom de nœud ROS propre à chaque script** (`essai_script1`…) au lieu de `niryo_blockly_interpreted_code`, utilisé par Niryo Studio.
- Les **paramètres regroupés** dans `config.py` : on adapte un seul fichier à son équipe et à son robot.
- Les **topics du projet** (`cellule/<equipe>/…`), des messages en **JSON** horodatés, et `paho-mqtt` 2 (`CallbackAPIVersion.VERSION2`).
- L'API sur le **port 3000** (le port 5000 du robot est pris par le logiciel système de Niryo), Flask lancé par le programme principal.
- Le **convoyeur arrêté dans tous les cas** (`try` / `finally`), même après `Ctrl+C`.
- Les scripts qui ne bougent pas le bras ne relancent plus de calibration à chaque démarrage.
- Le **script 8** (état du robot) et le **script 9** (`GET /robot/etat`) sont nouveaux.

## Mode d'emploi

Les bibliothèques Flask et paho-mqtt doivent être installées sur le robot (dossier `install_robot/`, voir son `README.md`).

1. Adapter `config.py` : identifiant de l'équipe, adresse du broker, identifiant et mot de passe MQTT, poses relevées sur votre robot.
2. Copier le dossier sur le robot (remplacer `.21` par l'adresse de votre robot) :

   ```bash
   scp -r essai_robot niryo@192.168.10.21:~/cellule/
   ```

3. Lancer un script sur le robot, depuis le dossier :

   ```bash
   ssh niryo@192.168.10.21
   cd ~/cellule/essai_robot
   ~/cellule/lancer.sh script8_etat_robot.py
   ```

4. Arrêter un script : `Ctrl+C`. Un seul script à la fois commande le robot, et aucun programme ne doit tourner en même temps depuis Niryo Studio.

Les scripts 1 à 3 font bouger le bras ou le convoyeur : appliquer les consignes de sécurité de la prise en main (zone dégagée, arrêt d'urgence à portée de main).

## Documentation

Toutes les fonctions de `n` utilisées par les scripts sont décrites dans la [référence du Python ROS Wrapper](https://niryorobotics.github.io/ned_ros/packages/python_ros_wrapper/ros_wrapper_api.html), avec des exemples (mouvements, pince, convoyeur). Index principal de la documentation : <https://niryorobotics.github.io/ned_ros/> (repris dans la partie 9 de `cours/01_prise_en_main_robot.md`).

## Essais réalisés

Les scripts ont été essayés sous Python 3.8, avec les bibliothèques de `install_robot/`, un broker Mosquitto et un **faux** robot (modules `rospy` et Python ROS Wrapper simulés). Ils restent à valider sur un vrai robot, en particulier :

- les noms des champs de l'état matériel (`get_hardware_status`) et le topic du convoyeur (`/niryo_robot/conveyor/feedback`) lus par le script 8, pris dans la documentation ROS de Niryo ([état du matériel](https://niryorobotics.github.io/ned_ros/packages/low_level/niryo_robot_hardware_interface.html), [convoyeur](https://niryorobotics.github.io/ned_ros/packages/low_level/conveyor_interface.html)) ;
- le sens du convoyeur (`BACKWARD` dans l'export de l'an dernier) et la polarité du capteur DI5.
