"""Paramètres communs aux scripts d'essai : à adapter à votre équipe et à votre robot."""

EQUIPE = "g1e1"                        # identifiant de l'équipe (topics MQTT, client MQTT)

# Broker MQTT du serveur du module
BROKER = "192.168.10.10"               # adresse du serveur (le Raspberry Pi d'ISTP est en .11)
PORT_MQTT = 1883

# Topics des essais (les topics du projet sont cycle, etat et defaut)
TOPIC_ESSAI = f"cellule/{EQUIPE}/essai"     # publié par le robot (scripts 4 et 7)
TOPIC_LED = f"cellule/{EQUIPE}/led"         # écouté par le robot (script 5)

# API sur le robot : le port 5000 est pris par le logiciel système de Niryo
PORT_API = 3000

# Poses relevées en FreeMotion [x, y, z, roll, pitch, yaw] : à remplacer par celles de votre robot
POSE_ATTENTE = [0.14, 0.0, 0.203, -0.017, 0.761, -0.001]
POSE_PRISE = [-0.168, 0.182, 0.149, -1.832, 1.483, -0.371]
POSE_DEPOSE_A = [0.20, 0.20, 0.10, 0.0, 1.57, 0.0]

# Convoyeur : vitesse en %, délai maximal d'attente d'une pièce en secondes
VITESSE_CONVOYEUR = 50
DELAI_MAX_PIECE = 30

# Couleurs de l'anneau de LED [rouge, vert, bleu, 0], comme dans l'export de Niryo Studio
COULEURS = {
    "rouge": [255, 0, 0, 0],
    "vert": [0, 255, 0, 0],
    "bleu": [0, 0, 255, 0],
}
