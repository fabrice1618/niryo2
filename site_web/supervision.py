#!/usr/bin/env python3
"""Site web de supervision : le tableau de bord de la cellule.

    /                  la page : commandes, état du robot, derniers messages MQTT
    /etat              la partie « état et messages », rechargée toutes les 2 s par la page
    /commande/...      une route par bouton : envoie la commande à l'API du robot

Lancement, dans le dossier du site : python3 supervision.py
Puis ouvrir http://192.168.10.10:8001 depuis un poste (http://127.0.0.1:8001 sur son poste)
"""
import sqlite3
from datetime import datetime

import requests
from flask import Flask, flash, redirect, render_template, request, url_for

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1e1"                        # identifiant de l'équipe, affiché en titre
URL_API = "http://127.0.0.1:5001"      # simulateur d'API ; le robot : "http://192.168.10.21:3000"
BASE = "cellule.db"                    # base remplie par le collecteur
PORT_SITE = 8001                       # 8000 + numéro de l'équipe (8001 à 8008)
COULEURS = ["rouge", "vert", "bleu", "jaune", "blanc"]   # couleurs de l'anneau de LED, comme dans l'API

app = Flask(__name__)
app.secret_key = "dev-seulement"       # nécessaire pour les messages flash


# --- Lire l'état du robot et les derniers messages ----------------------------
def lire_etat():
    """Demande l'état du robot à l'API. Renvoie None si l'API ne répond pas."""
    try:
        return requests.get(f"{URL_API}/robot/etat", timeout=1).json()
    except requests.RequestException:
        return None


def derniers_messages():
    """Les 20 derniers messages MQTT enregistrés par le collecteur, du plus récent au plus ancien."""
    conn = sqlite3.connect(BASE)
    conn.row_factory = sqlite3.Row     # accès aux colonnes par leur nom : m.sujet
    try:
        return conn.execute("SELECT time(recu_le, 'localtime') AS heure, sujet, charge "
                            "FROM messages ORDER BY id DESC LIMIT 20").fetchall()
    except sqlite3.Error:              # base pas encore créée (creer_bdd.py)
        return []
    finally:
        conn.close()


# --- Envoyer une commande à l'API du robot ---------------------------------------
def envoyer(chemin):
    """Envoie la commande à l'API du robot et prépare le message à afficher sur la page.

    L'API ne répond qu'à la fin de la tâche (20 s pour une calibration) : le site
    n'attend qu'une seconde. La tâche continue ensuite sur le robot ; sa fin se voit
    dans l'état du robot et dans les messages MQTT.
    """
    try:
        reponse = requests.post(f"{URL_API}{chemin}", timeout=1)
        if reponse.status_code == 200:
            flash(f"{chemin} : tâche terminée")
        elif reponse.status_code == 404:
            flash(f"{chemin} : commande inconnue de l'API du robot")
        else:                          # 409 robot occupé, 400 paramètre incorrect, 500 erreur du robot
            flash(f"{chemin} : refusée, {reponse.json()['erreur']}")
    except requests.exceptions.ReadTimeout:
        flash(f"{chemin} : commande envoyée, tâche en cours")
    except requests.RequestException:
        flash(f"{chemin} : API du robot injoignable ({URL_API})")


# --- Les pages -------------------------------------------------------------------
@app.get("/")
def accueil():
    return render_template("accueil.html", equipe=EQUIPE, couleurs=COULEURS)


@app.get("/etat")
def etat():
    return render_template("etat.html", etat=lire_etat(), messages=derniers_messages(),
                           heure=datetime.now().strftime("%H:%M:%S"))


# --- Les commandes : une route par bouton de la page -----------------------------
@app.post("/commande/home")
def home():
    envoyer("/robot/home")
    return redirect(url_for("accueil"))


@app.post("/commande/autocalibrate")
def autocalibrate():
    envoyer("/robot/autocalibrate")
    return redirect(url_for("accueil"))


@app.post("/commande/ledring")
def ledring():
    couleur = request.form["couleur"]  # le paramètre choisi dans la liste du formulaire
    envoyer(f"/robot/ledring/{couleur}")
    return redirect(url_for("accueil"))


# --- Ajouter une commande : copier ce modèle et remplacer « cycle » ------------
# (et ajouter son bouton dans templates/accueil.html)
#
# @app.post("/commande/cycle")
# def cycle():
#     envoyer("/robot/cycle")
#     return redirect(url_for("accueil"))


# debug=True : le site redémarre seul à chaque modification d'un fichier
app.run(host="0.0.0.0", port=PORT_SITE, debug=True)
