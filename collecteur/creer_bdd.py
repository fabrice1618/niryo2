#!/usr/bin/env python3
"""Crée la base cellule.db, remplie par le collecteur et lue par le site web.

Lancement, une fois, avant le collecteur : python3 creer_bdd.py
Sans risque si la base existe déjà : les tables et leurs données sont conservées.
Pour repartir d'une base vide : supprimer cellule.db, puis relancer ce script.
"""
import sqlite3

# --- Paramètres à adapter -------------------------------------------------
EQUIPE = "g1e1"                        # identifiant de l'équipe
ADRESSE_ROBOT = "192.168.10.21"        # adresse du robot de l'équipe
BASE = "cellule.db"

conn = sqlite3.connect(BASE)

# Les tables : celles des cours de SQL et de Flask
conn.executescript("""
CREATE TABLE IF NOT EXISTS messages (
    id        INTEGER PRIMARY KEY,
    recu_le   TEXT    NOT NULL,          -- heure de réception, en UTC
    sujet     TEXT    NOT NULL,          -- ex. cellule/g1e1/cycle
    charge    TEXT    NOT NULL,          -- contenu du message, tel quel
    qos       INTEGER NOT NULL,
    retain    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS robots (
    id         INTEGER PRIMARY KEY,
    nom        TEXT NOT NULL UNIQUE,
    equipe     TEXT NOT NULL,
    adresse_ip TEXT
);

CREATE TABLE IF NOT EXISTS cycles (
    id        INTEGER PRIMARY KEY,
    robot_id  INTEGER NOT NULL REFERENCES robots(id),
    debut     TEXT NOT NULL,             -- horodatage posé par le robot (heure locale)
    duree     REAL NOT NULL,             -- secondes
    zone      TEXT,
    statut    TEXT NOT NULL DEFAULT 'ok'
);
""")

# Le robot de l'équipe : sans lui, le collecteur ne peut pas enregistrer de cycle
conn.execute("INSERT OR IGNORE INTO robots (nom, equipe, adresse_ip) VALUES (?, ?, ?)",
             (f"ned2-{EQUIPE}", EQUIPE, ADRESSE_ROBOT))
conn.commit()

print(f"Base {BASE} prête :")
for table in ["messages", "robots", "cycles"]:
    nombre = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(f"  table {table} : {nombre} ligne(s)")
conn.close()
