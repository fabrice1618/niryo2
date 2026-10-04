# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dossier

Ce n'est pas un dépôt de code mais le dossier d'un **cours** : « Infrastructure client / serveur dans un contexte industriel » (intervenant : Fabrice Guichard, année 2026-2027). Tout le contenu est rédigé en **français**, en Markdown avec des schémas Mermaid. Il n'y a ni build, ni tests, ni lint.

Le cours est **modulaire** : un même socle de supports est décliné en **trois progressions pédagogiques**, une par classe. Chaque classe pioche dans les supports selon son volume horaire, son niveau et son calendrier.

## Organisation

- `progression_pedagogique/` : une progression par classe, nommée d'après le code de la promotion. Les trois classes : `BACHINGE24` (BACH INGE 2024-0, 3e année, alternants, groupes G1 et G2), `B3RNSPP26` et `BACHTECH24`. Seule `BACHINGE24.md` existe pour l'instant ; les deux autres fichiers sont à créer sur le même modèle. Une progression contient : intention générale, compétences visées (C1 à C6), architecture cible, tableau des séances (S1 à S6), détail de chaque séance (objectifs, déroulé minuté, livrables, supports de cours, ressources reprises), configuration du serveur, points à arbitrer.
- `cours/` : les supports de cours, **communs aux trois classes et donc génériques** : aucune mention de promotion, d'année d'étude, de date de séance ni de numéro de séance (S1, S2…), car le découpage en séances diffère d'une classe à l'autre. Pour situer un moment du projet, parler de l'étape (« lors de la prise en main du robot », « tant que le robot n'est pas intégré », « lors de l'intégration ») et renvoyer aux autres supports par leur titre. La correspondance supports / séances se trouve uniquement dans les progressions. Chaque support commence par un titre, la ligne d'en-tête `Fabrice Guichard · Infrastructure client / serveur dans un contexte industriel`, puis un paragraphe qui situe le support dans le projet fil rouge. Les identifiants d'équipe (`g1e1`) et les dates des données d'exemple sont de simples exemples et peuvent rester.
- `*.drawio` / `*.drawio.png` : schémas d'architecture (draw.io) à la racine.
- Les supports de l'année précédente (pile MySQL, Docker, Node-RED, Grafana) sont dans `/home/fab/cours/niryo` ; les progressions y font référence dans les rubriques « Ressources reprises de l'an dernier ».

## Le projet fil rouge (fil conducteur de tous les supports)

Chaque équipe réalise une **cellule robotisée supervisée** :

robot Niryo Ned2 + convoyeur (capteur DI5) → publication MQTT → broker Mosquitto → collecteur Python → base SQLite → site web Flask (tableau de bord) → API Flask de commande CQRS → robot.

Les supports de `cours/` sont tous rattachés à ce fil rouge et partagent des conventions qui doivent rester **cohérentes entre fichiers** (en modifier une suppose de vérifier les autres supports et les progressions) :

- Topics MQTT : `cellule/<equipe>/cycle`, `cellule/<equipe>/etat` (retenu), `cellule/<equipe>/defaut`, avec `<equipe>` de la forme `g1e1`.
- Message JSON : `{"evenement": "fin_cycle", "piece": 12, "duree": 18.2, "zone": "A", "horodatage": "..."}`.
- Tables SQLite : `messages(id, recu_le, sujet, charge, qos, retain)`, `robots(id, nom, equipe, adresse_ip)`, `cycles(id, robot_id, debut, duree, zone, statut)` ; fichier `cellule.db`.
- API CQRS : `GET /requetes/etat`, `POST /commandes/demarrer`, `/commandes/arreter`, `/commandes/calibrer` (réponse `202 Accepted` + id de commande), classe `RobotSimule` pour le mode simulé.
- Ports : API simulée 5001 à 5008, site web 8001 à 8008 (une valeur par équipe), API sur le robot port 5000, MQTT 1883.
- Réseau du fab lab : `192.168.10.0/24`, serveur en `.10`, robots en `.21` à `.24`.
- Pile volontairement allégée : SQLite (pas MySQL), pas de Docker, pas de Grafana ni de Node-RED ; le tableau de bord est le site Flask.

## Conventions de rédaction

- Français, phrases simples, registre de cours. Pas de tiret cadratin (« — ») : utiliser « : », « , » ou des parenthèses.
- Schémas en blocs ```` ```mermaid ```` (flowchart, sequenceDiagram, gantt), libellés entre guillemets avec `<br/>` pour les retours à la ligne.
- Tableaux Markdown pour les déroulés de séance (`Durée | Activité`) et les correspondances supports / séances.
- Quand un support est ajouté ou renommé dans `cours/`, mettre à jour le tableau « Supports de cours » (fin de la section 4) et les rubriques « Supports de cours » des séances concernées dans chaque progression.
