#!/usr/bin/env python3
"""Collecteur MQTT : enregistre dans la base cellule.db les messages de l'équipe.

Chaque message reçu est enregistré tel quel dans la table messages.
Chaque fin de cycle est aussi enregistrée dans la table cycles, lue par le site web.

Avant le premier lancement, créer la base : python3 creer_bdd.py
Lancement : python3 collecteur.py   (Ctrl+C pour l'arrêter)
"""
import json
import os
import queue
import sqlite3
import threading
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1"                        # identifiant de l'équipe, dans les topics MQTT
BROKER = "localhost"                   # "localhost" sur le serveur du module, "192.168.1.10" depuis un poste
BASE = "cellule.db"                    # créée par creer_bdd.py

file_messages = queue.Queue()          # messages reçus, en attente d'écriture dans la base


# --- Réception des messages --------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Connexion refusée par le broker : {reason_code}")
        client.disconnect()
    else:
        client.subscribe(f"cellule/{EQUIPE}/#", qos=1)   # tous les messages de l'équipe
        print(f"Connecté à {BROKER}, abonné à cellule/{EQUIPE}/#")


def on_message(client, userdata, msg):
    """Appelée à chaque message reçu : le dépose dans la file, sans attendre la base."""
    recu_le = datetime.now(timezone.utc).isoformat(timespec="seconds")
    charge = msg.payload.decode("utf-8", errors="replace")
    file_messages.put((recu_le, msg.topic, charge, msg.qos, msg.retain))


# --- Écriture dans la base ----------------------------------------------------
def enregistrer_cycle(conn, charge):
    """Enregistre une fin de cycle dans la table cycles. Les autres messages sont ignorés."""
    try:
        donnees = json.loads(charge)
        if donnees["evenement"] == "fin_cycle":
            conn.execute("INSERT INTO cycles (robot_id, debut, duree, zone) "
                         "SELECT id, ?, ?, ? FROM robots WHERE equipe = ?",
                         (donnees["horodatage"], float(donnees["duree"]), donnees.get("zone"), EQUIPE))
    except (ValueError, KeyError, TypeError):    # pas du JSON, champ manquant, durée qui n'est pas un nombre
        print("  message mal formé, pas de cycle enregistré")


def ecrivain():
    """Tourne à part : prend les messages dans la file, un par un, et les écrit dans la base."""
    conn = sqlite3.connect(BASE, timeout=10)
    while True:
        recu_le, sujet, charge, qos, retain = file_messages.get()   # attend le message suivant
        print(f"{recu_le}  {sujet}  {charge}")
        try:
            conn.execute("INSERT INTO messages (recu_le, sujet, charge, qos, retain) VALUES (?, ?, ?, ?, ?)",
                         (recu_le, sujet, charge, qos, retain))
            if sujet == f"cellule/{EQUIPE}/cycle":
                enregistrer_cycle(conn, charge)
            conn.commit()
        except sqlite3.Error as e:
            print("  erreur d'écriture dans la base :", e)


# --- Programme principal --------------------------------------------------------
if not os.path.exists(BASE):
    print(f"Base {BASE} absente : la créer d'abord avec python3 creer_bdd.py")
    raise SystemExit(1)

threading.Thread(target=ecrivain, daemon=True).start()

# client_id fixe et clean_session=False : le broker garde les messages
# publiés pendant que le collecteur est arrêté, et les envoie au redémarrage
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"{EQUIPE}_collecteur", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, 1883)
except OSError as e:
    print(f"Broker {BROKER} injoignable : {e}")
    raise SystemExit(1)

print(f"Collecteur de l'équipe {EQUIPE}, base {BASE} (Ctrl+C pour arrêter)")
try:
    client.loop_forever()              # reçoit les messages ; se reconnecte seul après une coupure
except KeyboardInterrupt:
    print("Collecteur arrêté")
