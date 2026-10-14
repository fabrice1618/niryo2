# Cahier de recette de la cellule robotisée supervisée

Infrastructure client / serveur dans un contexte industriel

Le cahier de recette est la liste des **tests** qui prouvent que la cellule fait ce que le dossier d'analyse (`dossier_analyse.md`) a promis. Il est **présenté le jour de l'évaluation** : l'équipe déroule devant l'enseignant les tests que celui-ci choisit dans le cahier, sur la cellule réelle (robot, serveur, site web). **Chaque test est noté conforme ou non conforme.**

Ce fichier contient deux tests déjà rédigés (T01 et T02), qui montrent le niveau de précision attendu, et des modèles à compléter pour les autres.

## Comment le remplir

- **Au moins 8 tests**, chacun relié à **une exigence** de la rubrique 9 du dossier d'analyse, et **chaque exigence couverte par au moins un test**.
- Le cahier se complète **au fur et à mesure** du projet, et se rend **une seule fois, à la fin**. Vérifier chaque test en le déroulant vraiment, avant l'évaluation : un test jamais essayé est presque toujours faux.
- Les deux tests fournis (T01 et T02) sont à **adapter à votre cellule** : remplacer les cases `À COMPLÉTER` (adresses, ports, valeurs) et corriger ce qui ne correspond pas à votre site ou à votre API. Les garder comme tests de l'équipe, ou les remplacer par des tests mieux adaptés à votre process.
- Les tests suivants (T03 et suivants) se rédigent avec le **modèle** de la rubrique 4.
- **Ne jamais écrire de mot de passe** dans ce document.

### Ce qui fait un bon test

| Un bon test... | Exemple à éviter | Exemple correct |
|---|---|---|
| **Se déroule en 2 à 3 minutes**, devant quelqu'un d'autre | « Faire fonctionner la cellule pendant une heure » | « Lancer un cycle et vérifier la ligne enregistrée » |
| **Vérifie une seule chose**, reliée à une exigence | « Tout marche de bout en bout » | « Une fin de cycle apparaît dans la table `cycles` » |
| Donne une **procédure que n'importe qui peut suivre** : actions précises, commandes écrites en entier | « Lancer le site » | « Dans un terminal du serveur : `cd ~/supervision`, puis `python3 supervision.py` » |
| Donne un **résultat observable et vérifiable** : une valeur, un message, une ligne en base, un mouvement | « Ça marche », « le robot réagit » | « Le compteur passe de 12 à 13 ; `duree` est comprise entre 10 et 30 » |
| Décrit les **préconditions** (état de départ) | rien | « Robot calibré, collecteur lancé, base notée avant le test » |
| Est **reproductible** : le même test donne le même résultat | dépend d'un réglage non écrit | tous les réglages sont dans les préconditions |

Un test peut aussi vérifier qu'un cas **d'erreur** est bien traité (robot occupé, message mal formé, API arrêtée) : c'est souvent ce qui montre que la cellule est fiable.


## 1. Les exigences à couvrir

Recopier ici les exigences de la rubrique 9 du dossier d'analyse (même identifiant, même intitulé) et indiquer les tests qui les vérifient. Les deux premières lignes sont celles des deux tests fournis : les reprendre dans votre dossier, ou les remplacer.

| Exigence | Intitulé | Tests qui la vérifient |
|---|---|---|
| E1 | L'opérateur peut commander le robot depuis le site web | T01 |
| E2 | La collecte continue de fonctionner quand elle reçoit un message mal formé | T02 |
| E3 | À COMPLÉTER | À COMPLÉTER |
| E4 | À COMPLÉTER | À COMPLÉTER |
| E5 | À COMPLÉTER | À COMPLÉTER |
| E6 | À COMPLÉTER | À COMPLÉTER |
| E7 | À COMPLÉTER | À COMPLÉTER |
| E8 | À COMPLÉTER | À COMPLÉTER |

Une exigence sans test n'est pas vérifiée ; un test relié à aucune exigence n'a pas de raison d'être.


## 2. Conditions de la recette

À préparer **avant** de commencer les tests, et à écrire ici pour que chaque test puisse dire « conditions de la rubrique 2 ».

### 2.1 Matériel et adresses

| Élément | Valeur |
|---|---|
| Équipe (`EQUIPE`) | À COMPLÉTER |
| Robot (numéro, adresse IP) | À COMPLÉTER |
| Serveur (adresse) | À COMPLÉTER |
| Adresse du site web | `http://<adresse du serveur>:<PORT_SITE>` : À COMPLÉTER |
| Adresse de l'API du robot | `http://<adresse du robot>:3000` : À COMPLÉTER |
| Poste utilisé pour la recette | À COMPLÉTER |

### 2.2 Programmes à lancer avant le premier test

| Programme | Où | Commande | Vérification que c'est lancé |
|---|---|---|---|
| Collecteur MQTT | Serveur, dossier `~/supervision` | `python3 collecteur.py` | Affiche `Connecté à ..., abonné à cellule/<équipe>/#` |
| Site web | Serveur, dossier `~/supervision` | `python3 supervision.py` | La page s'ouvre dans le navigateur ; « mis à jour à » change toutes les 2 secondes |
| API du robot | Robot | `~/cellule/lancer.sh api_robot.py` | `curl http://<adresse du robot>:3000/robot/etat` répond |
| Programme process | Robot | À COMPLÉTER | À COMPLÉTER |
| Simulateur MQTT (seulement pour les tests de robustesse) | Serveur | `python3 simulateur_mqtt.py` | Affiche son menu |
| À COMPLÉTER | À COMPLÉTER | À COMPLÉTER | À COMPLÉTER |

### 2.3 État de départ

| Élément | État attendu |
|---|---|
| Robot | Calibré, en pose d'attente, aucune tâche en cours |
| Convoyeur et pièces | À COMPLÉTER (pièces disponibles, convoyeur libre) |
| Base `cellule.db` | À COMPLÉTER (vide, ou notée avant chaque test qui la lit) |
| Fenêtres ouvertes | Navigateur sur le site ; un terminal sur le serveur pour interroger la base (`sqlite3 ~/supervision/cellule.db`) ; le terminal du collecteur visible |


## 3. Les tests

Chaque test a la même forme : une fiche (exigence, préconditions), une procédure en étapes avec le résultat attendu à chaque étape, un critère de conformité, et les cases que l'on remplit **le jour de la recette**.

### T01 : commander l'anneau de LED depuis le site web  *(exemple fourni)*

| Champ | Contenu |
|---|---|
| Exigence | E1 : l'opérateur peut commander le robot depuis le site web |
| Objectif | Vérifier toute la chaîne de commande : site web, API du robot, robot, puis les messages MQTT de début et de fin de tâche dans la base |
| Préconditions | Conditions de la rubrique 2 remplies. Le site utilise l'API **du robot** (`URL_API = "http://<adresse du robot>:3000"`). Le collecteur est lancé. La page affiche « Tâche en cours : aucune ». Personne ne se tient dans la zone du robot |
| Durée estimée | 2 minutes |

| N° | Action | Résultat attendu |
|---|---|---|
| 1 | Ouvrir le site : À COMPLÉTER (adresse et port de l'équipe) | La page s'affiche, avec le titre de l'équipe et les boutons ; l'heure « mis à jour à » change toutes les 2 secondes |
| 2 | Dans la liste de l'anneau de LED, choisir `vert`, puis cliquer sur le bouton de l'anneau de LED | Le message `/robot/ledring/vert : commande envoyée, tâche en cours` s'affiche en haut de la page |
| 3 | Regarder l'anneau de LED du robot pendant 3 secondes | L'anneau **clignote en vert** pendant environ 2 secondes, puis s'arrête |
| 4 | Regarder la partie « état du robot » de la page, quelques secondes après le clic | « Tâche en cours » revient à `aucune` (elle peut avoir affiché `ledring` pendant le clignotement) |
| 5 | Dans la liste des derniers messages de la page, repérer les deux messages les plus récents sur le sujet `cellule/<équipe>/tache` | Deux messages : `debut_tache` puis `fin_tache`, avec `"tache": "ledring"` et `"couleur": "vert"` ; `fin_tache` porte `"statut": "terminee"` |

**Critère de conformité** : l'anneau a clignoté en vert **et** la page affiche la fin de la tâche (`aucune`) **et** les messages `debut_tache` et `fin_tache` (statut `terminee`) sont visibles. Si l'un des trois manque, le test est non conforme.

**Le jour de la recette**

| Résultat obtenu | Conforme | Observation |
|---|---|---|
| À COMPLÉTER | Oui / Non | À COMPLÉTER |

### T02 : un message mal formé n'arrête pas la collecte  *(exemple fourni)*

| Champ | Contenu |
|---|---|
| Exigence | E2 : la collecte continue de fonctionner quand elle reçoit un message mal formé |
| Objectif | Vérifier que le collecteur garde un message invalide dans `messages`, ne crée pas de cycle avec lui, **ne s'arrête pas**, et enregistre le message correct qui suit |
| Préconditions | Conditions de la rubrique 2 remplies. Collecteur lancé (son terminal est visible). Simulateur MQTT lancé avec les mêmes `EQUIPE` et `BROKER` que le collecteur. Un terminal sur le serveur est ouvert dans `~/supervision` |
| Durée estimée | 3 minutes |

| N° | Action | Résultat attendu |
|---|---|---|
| 1 | Dans le terminal du serveur, noter les deux compteurs : `sqlite3 cellule.db "SELECT (SELECT count(*) FROM messages), (SELECT count(*) FROM cycles);"` | Deux nombres s'affichent (par exemple `42\|7`) : les noter, ce sont **M** (messages) et **C** (cycles) |
| 2 | Dans le simulateur MQTT, taper `7` (« Messages mal formés ») | Le simulateur affiche 6 messages envoyés ; le terminal du collecteur affiche 6 fois `message mal formé, pas de cycle enregistré` |
| 3 | Vérifier que le collecteur **tourne toujours** | Le terminal du collecteur n'affiche aucune erreur d'arrêt et n'est pas revenu à l'invite de commande |
| 4 | Relancer la requête de l'étape 1 | Le premier nombre vaut **M + 6** (les 6 messages sont gardés) ; le second vaut toujours **C** (aucun cycle créé) |
| 5 | Dans le simulateur MQTT, taper `1` (« Cycle complet ») | Le collecteur affiche le début et la fin de cycle |
| 6 | Relancer la requête de l'étape 1 | Le second nombre vaut **C + 1** : le cycle correct est enregistré malgré les erreurs précédentes |

**Critère de conformité** : après les 6 messages mal formés, les messages sont dans `messages` (+ 6), aucun cycle n'est ajouté, le collecteur n'est pas arrêté, **et** un cycle correct envoyé ensuite est bien enregistré (+ 1).

**Le jour de la recette**

| Résultat obtenu | Conforme | Observation |
|---|---|---|
| À COMPLÉTER | Oui / Non | À COMPLÉTER |

### T03 à T08 (et suivants) : à rédiger par l'équipe

Voir le modèle de la rubrique 4. Pour trouver des tests, partir des **exigences** de votre dossier. Idées à partir des programmes fournis :

| Idée de test | Ce qu'on vérifie | Où l'on regarde |
|---|---|---|
| Un cycle complet du process | La fin de cycle est publiée, puis enregistrée dans `cycles` avec sa durée et sa zone | Table `cycles`, page du site |
| L'état du robot est affiché | L'état lu par `GET /robot/etat` apparaît sur le site et se met à jour | Page du site |
| Un défaut est signalé | Un défaut du process (par exemple pièce non détectée) est publié et visible | Sujet `defaut`, table `messages`, site |
| Un ordre est refusé quand le robot est occupé | Une commande envoyée pendant une tâche est refusée (`409`) et le site l'affiche | Page du site, réponse de l'API |
| Une valeur de paramètre incorrecte est refusée | Par exemple une couleur inconnue : refus (`400`) et message clair | Page du site |
| L'API du robot est arrêtée | Le site affiche « API du robot injoignable » sans planter | Page du site |
| Le collecteur arrêté puis relancé ne perd rien | Les messages publiés pendant l'arrêt sont enregistrés au redémarrage | Terminal du collecteur, table `messages` |
| Les données sont cohérentes | Le nombre de cycles affiché par le site correspond à celui de la base | Page du site, `sqlite3` |
| Une page ou un indicateur propre à l'équipe | À COMPLÉTER | À COMPLÉTER |

À COMPLÉTER : écrire ci-dessous vos tests, un bloc par test, sur le modèle de la rubrique 4.


## 4. Modèle de test à copier

Copier ce bloc pour chaque test, en changeant l'identifiant (`T03`, `T04`...), et le placer dans la rubrique 3.

### T0X : À COMPLÉTER (titre court, qui dit ce que l'on vérifie)

| Champ | Contenu |
|---|---|
| Exigence | À COMPLÉTER (identifiant et intitulé, comme dans le dossier d'analyse) |
| Objectif | À COMPLÉTER (une phrase : ce que le test prouve) |
| Préconditions | À COMPLÉTER (programmes lancés, état du robot et de la base, réglages) |
| Durée estimée | À COMPLÉTER (2 à 3 minutes) |

| N° | Action | Résultat attendu |
|---|---|---|
| 1 | À COMPLÉTER (une action précise, commande écrite en entier) | À COMPLÉTER (ce que l'on voit, avec les valeurs) |
| 2 | À COMPLÉTER | À COMPLÉTER |
| 3 | À COMPLÉTER | À COMPLÉTER |

**Critère de conformité** : À COMPLÉTER (la condition précise qui rend le test conforme ; tout ce qui s'écarte rend le test non conforme).

**Le jour de la recette**

| Résultat obtenu | Conforme | Observation |
|---|---|---|
| À COMPLÉTER | Oui / Non | À COMPLÉTER |


## 5. Fiche de passage (le jour de la recette)

Tableau récapitulatif, rempli pendant l'évaluation. Une ligne par test du cahier.

| Test | Exigence | Conforme (Oui / Non) | Observation |
|---|---|---|---|
| T01 | E1 | | |
| T02 | E2 | | |
| T03 | À COMPLÉTER | | |
| T04 | À COMPLÉTER | | |
| T05 | À COMPLÉTER | | |
| T06 | À COMPLÉTER | | |
| T07 | À COMPLÉTER | | |
| T08 | À COMPLÉTER | | |

| Bilan | |
|---|---|
| Nombre de tests déroulés | |
| Nombre de tests conformes | |
| Date | |
| Signature de l'équipe | |
| Signature de l'enseignant | |


## 6. Vérification du cahier

Avant de rendre le cahier, cocher :

- [ ] Au moins 8 tests sont rédigés (T01 et T02 adaptés, plus au moins 6 autres)
- [ ] Chaque exigence du dossier d'analyse (rubrique 9) est vérifiée par au moins un test, et la rubrique 1 le montre
- [ ] Chaque test a une exigence, des préconditions, une procédure en étapes avec un résultat attendu **observable** à chaque étape, et un critère de conformité
- [ ] Chaque test a été **déroulé en entier** au moins une fois sur la cellule réelle, et se fait en 2 à 3 minutes
- [ ] Les commandes, adresses et ports écrits sont ceux de la cellule de l'équipe
- [ ] Toutes les cases `À COMPLÉTER` sont remplies (sauf les cases « Le jour de la recette » et la fiche de passage)
- [ ] Aucun mot de passe n'est écrit dans ce document
