# Rappels de SQL : cours simple

Infrastructure client / serveur dans un contexte industriel

SQL est le langage standard pour interroger et modifier une base de données relationnelle ; ce rappel couvre l'essentiel en dix étapes, avec une même base d'exemple : les cycles de production de la cellule robotisée.

## Objectifs et mise en place

À la fin, vous saurez créer des tables, y écrire, les interroger, les relier et les utiliser depuis Python.

**Outil : SQLite**

SQLite est une base de données contenue dans un simple fichier, déjà incluse dans Python (module `sqlite3`) : rien à installer ni à configurer. La syntaxe SQL vue ici est valable pour la plupart des bases (PostgreSQL, MySQL) ; les rares différences sont signalées.

Pour s'entraîner en ligne de commande : `sqlite3 cellule.db`. Quelques commandes utiles : `.tables` (lister les tables), `.schema` (voir la structure), `.quit` (quitter).

**La base d'exemple**

On suit les robots Ned2 des équipes et les cycles de production qu'ils effectuent (prise d'une pièce sur le convoyeur, dépose dans une zone). Ce sont les données publiées par le robot en MQTT et enregistrées par le collecteur présenté dans l'autre document, puis affichées par le site web Flask.

| Table | Contenu |
| --- | --- |
| `robots` | Un robot par ligne : identifiant, nom, équipe, adresse IP |
| `cycles` | Un cycle par ligne : robot, début, durée, zone de dépose, statut (`ok` ou `defaut`) |

**Conventions**

- Les mots-clés SQL (`SELECT`, `FROM`) s'écrivent en majuscules par habitude ; SQL accepte aussi les minuscules.
- Chaque instruction se termine par un point-virgule.
- Un commentaire commence par `--`.

## Le modèle relationnel

Une base relationnelle range les données dans des tables ; chaque table est un tableau de lignes (les enregistrements) et de colonnes (les champs), et les tables sont reliées par des clés.

**Vocabulaire**

| Terme | Sens | Exemple |
| --- | --- | --- |
| Table | Un ensemble de données de même nature | `robots` |
| Ligne (enregistrement) | Un élément de la table | Le robot « ned2-g1 » |
| Colonne (champ) | Une propriété, avec un type | `adresse_ip` |
| Clé primaire | Colonne qui identifie chaque ligne de façon unique | `robots.id` |
| Clé étrangère | Colonne qui référence la clé primaire d'une autre table | `cycles.robot_id` |

**Exemple de contenu**

`robots`

| id | nom | equipe | adresse\_ip |
| --- | --- | --- | --- |
| 1 | ned2-g1 | g1 | 192.168.1.21 |
| 2 | ned2-g2 | g2 | 192.168.1.22 |

`cycles`

| id | robot\_id | debut | duree | zone | statut |
| --- | --- | --- | --- | --- | --- |
| 1 | 1 | 2026-11-17 08:30:00 | 18.2 | A | ok |
| 2 | 1 | 2026-11-17 08:30:25 | 17.9 | B | ok |
| 3 | 2 | 2026-11-17 08:30:05 | 22.1 | A | defaut |

La colonne `robot_id` de `cycles` indique quel robot a effectué chaque cycle : on évite de répéter le nom, l'équipe et l'adresse du robot sur chaque ligne.

**Pourquoi séparer en plusieurs tables ?**

- Pas de répétition : l'adresse IP d'un robot est écrite une seule fois, et non sur chacun de ses milliers de cycles.
- Pas d'incohérence : changer l'adresse se fait à un seul endroit.
- Les jointures (voir plus loin) reconstituent l'ensemble quand on en a besoin.

## Définir la structure

Le langage de définition (DDL) crée et modifie les tables ; on le fait en général une seule fois, au démarrage du projet.

```sql
CREATE TABLE robots (
    id          INTEGER PRIMARY KEY,
    nom         TEXT NOT NULL UNIQUE,
    equipe      TEXT NOT NULL,
    adresse_ip  TEXT
);

CREATE TABLE cycles (
    id        INTEGER PRIMARY KEY,
    robot_id  INTEGER NOT NULL REFERENCES robots(id),
    debut     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duree     REAL NOT NULL,                  -- en secondes
    zone      TEXT,                           -- zone de dépose : A ou B
    statut    TEXT NOT NULL DEFAULT 'ok'      -- ok ou defaut
);
```

**Types courants (SQLite)**

| Type | Usage |
| --- | --- |
| `INTEGER` | Entiers |
| `REAL` | Nombres décimaux |
| `TEXT` | Texte (dates incluses, au format `AAAA-MM-JJ HH:MM:SS`) |
| `BLOB` | Données binaires |

PostgreSQL et MySQL proposent des types plus nombreux (`TIMESTAMP`, `NUMERIC`, `VARCHAR`), mais les idées sont les mêmes.

**Contraintes**

- `PRIMARY KEY` : identifiant unique de la ligne
- `NOT NULL` : la valeur est obligatoire
- `UNIQUE` : pas deux fois la même valeur dans la colonne
- `DEFAULT` : valeur prise si on n'en donne pas
- `REFERENCES table(colonne)` : clé étrangère, la valeur doit exister dans l'autre table (SQLite ne vérifie ce point que si l'on active `PRAGMA foreign_keys = ON;`)

Les contraintes protègent la base : elle refuse elle-même une ligne invalide, quel que soit le programme qui écrit.

**Modifier ou supprimer une table**

```sql
ALTER TABLE robots ADD COLUMN modele TEXT;    -- ajouter une colonne
DROP TABLE cycles;                            -- supprimer la table et ses données
```

`DROP TABLE` est irréversible : vérifiez deux fois avant de l'exécuter.

## Lire les données : SELECT

`SELECT` choisit les colonnes à afficher, `FROM` la table, `WHERE` filtre les lignes : c'est l'instruction la plus utilisée.

```sql
-- Toutes les colonnes, toutes les lignes
SELECT * FROM cycles;

-- Quelques colonnes seulement
SELECT robot_id, duree FROM cycles;

-- Filtrer : les cycles lents
SELECT * FROM cycles WHERE duree > 20;

-- Combiner des conditions
SELECT * FROM cycles
WHERE robot_id = 1 AND debut >= '2026-11-17 08:00:00';

-- Trier (DESC = du plus grand au plus petit), limiter : les 10 derniers cycles
SELECT * FROM cycles ORDER BY debut DESC LIMIT 10;
```

**Les clauses, dans l'ordre où on les écrit**

| Clause | Rôle |
| --- | --- |
| `SELECT` | Les colonnes à renvoyer |
| `FROM` | La table lue |
| `WHERE` | Garde les lignes qui respectent une condition |
| `ORDER BY` | Trie le résultat (`ASC` par défaut, `DESC` pour inverser) |
| `LIMIT` | Garde les N premières lignes |

**Opérateurs de condition**

- Comparaisons : `=`, `<>` (différent), `<`, `>`, `<=`, `>=`
- Logique : `AND`, `OR`, `NOT`
- `BETWEEN 15 AND 25` : valeur comprise entre deux bornes
- `IN ('A', 'B')` : valeur parmi une liste
- `LIKE 'ned2-%'` : texte qui commence par `ned2-` (`%` remplace n'importe quels caractères)
- `IS NULL` / `IS NOT NULL` : tester l'absence de valeur (on n'écrit jamais `= NULL`)

**Alias**

```sql
SELECT duree AS duree_s FROM cycles;
```

**Dates et heures**

SQLite stocke les dates en texte au format `AAAA-MM-JJ HH:MM:SS` : ce format se trie et se compare correctement comme du texte. Quelques fonctions utiles :

```sql
SELECT * FROM cycles WHERE date(debut) = '2026-11-17';          -- les cycles d'un jour
SELECT * FROM cycles WHERE date(debut) = date('now');           -- les cycles d'aujourd'hui (UTC)
SELECT * FROM cycles WHERE debut >= datetime('now', '-1 hour'); -- la dernière heure
SELECT strftime('%H', debut) AS heure FROM cycles;              -- extraire l'heure
```

`'now'` est en temps universel (UTC) ; ajoutez `'localtime'` (`date('now', 'localtime')`) pour l'heure locale. Choisissez une convention (UTC ou heure locale) pour tout le projet, et tenez-vous-y du robot jusqu'au site web.

## Écrire les données : INSERT, UPDATE, DELETE

Trois instructions modifient le contenu des tables : `INSERT` ajoute, `UPDATE` change, `DELETE` retire.

```sql
-- Ajouter
INSERT INTO robots (nom, equipe, adresse_ip) VALUES ('ned2-g1', 'g1', '192.168.1.21');
INSERT INTO robots (nom, equipe, adresse_ip) VALUES ('ned2-g2', 'g2', '192.168.1.22');

INSERT INTO cycles (robot_id, duree, zone) VALUES (1, 18.2, 'A'), (1, 17.9, 'B');
INSERT INTO cycles (robot_id, duree, zone, statut) VALUES (2, 22.1, 'A', 'defaut');

-- Modifier
UPDATE robots SET adresse_ip = '192.168.1.31' WHERE nom = 'ned2-g1';

-- Supprimer
DELETE FROM cycles WHERE duree < 0;
```

**Le `WHERE` est vital**

Sans `WHERE`, `UPDATE` et `DELETE` s'appliquent à toutes les lignes de la table : `DELETE FROM cycles;` vide la table entière : toute la production enregistrée est perdue. Habituez-vous à écrire d'abord le `SELECT` avec la même condition pour vérifier les lignes concernées.

```sql
SELECT * FROM cycles WHERE duree < 0;   -- 1. je vérifie
DELETE FROM cycles WHERE duree < 0;     -- 2. j'applique
```

**Bonnes habitudes**

- Nommez toujours les colonnes dans `INSERT INTO table (colonnes)` : le code reste correct si la table évolue.
- Les colonnes omises prennent leur valeur `DEFAULT` (ici l'heure courante pour `debut`, `ok` pour `statut`) ou `NULL` s'il n'y en a pas.
- Une contrainte violée (`NOT NULL`, `UNIQUE`, clé étrangère) fait échouer l'instruction avec une erreur : rien n'est écrit.

## Agréger : fonctions et GROUP BY

Une fonction d'agrégation résume plusieurs lignes en une seule valeur ; `GROUP BY` permet de calculer ce résumé séparément pour chaque groupe.

**Fonctions d'agrégation**

| Fonction | Résultat |
| --- | --- |
| `COUNT(*)` | Nombre de lignes |
| `SUM(col)` | Somme |
| `AVG(col)` | Moyenne |
| `MIN(col)`, `MAX(col)` | Plus petite, plus grande valeur |

```sql
-- Sur toute la table
SELECT COUNT(*) AS nb, AVG(duree) AS moyenne FROM cycles;

-- Par robot
SELECT robot_id,
       COUNT(*)   AS nb_cycles,
       AVG(duree) AS moyenne,
       MAX(duree) AS maximum
FROM cycles
GROUP BY robot_id;
```

Résultat avec les données d'exemple :

| robot\_id | nb\_cycles | moyenne | maximum |
| --- | --- | --- | --- |
| 1 | 2 | 18.05 | 18.2 |
| 2 | 1 | 22.1 | 22.1 |

**Compter selon une condition**

En SQLite, une comparaison vaut 1 (vrai) ou 0 (faux) : `SUM(statut = 'defaut')` compte donc les cycles en défaut. Version portable vers les autres bases : `SUM(CASE WHEN statut = 'defaut' THEN 1 ELSE 0 END)`.

```sql
SELECT robot_id,
       COUNT(*)                                         AS nb_cycles,
       SUM(statut = 'defaut')                           AS nb_defauts,
       ROUND(100.0 * SUM(statut = 'defaut') / COUNT(*), 1) AS taux_defaut
FROM cycles
GROUP BY robot_id;
```

**WHERE contre HAVING**

`WHERE` filtre les lignes avant le regroupement ; `HAVING` filtre les groupes après le calcul.

```sql
SELECT robot_id, AVG(duree) AS moyenne
FROM cycles
WHERE debut >= '2026-11-17'           -- 1. on garde les cycles du jour
GROUP BY robot_id                     -- 2. on regroupe
HAVING AVG(duree) > 20;               -- 3. on garde les robots dont la durée moyenne dépasse 20 s
```

**Ordre d'exécution logique**

`FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY` → `LIMIT`. C'est pourquoi on ne peut pas utiliser un calcul d'agrégat dans un `WHERE`.

## Relier les tables : JOIN

Une jointure combine les lignes de deux tables à partir d'une condition, le plus souvent l'égalité entre une clé étrangère et la clé primaire qu'elle référence.

```sql
SELECT r.nom, r.equipe, c.debut, c.duree
FROM cycles AS c
JOIN robots AS r ON r.id = c.robot_id
WHERE r.equipe = 'g2'
ORDER BY c.debut;
```

`c` et `r` sont des alias de table : ils raccourcissent l'écriture et lèvent l'ambiguïté quand deux tables ont une colonne de même nom (`id`).

**Les types de jointure utiles**

| Jointure | Résultat |
| --- | --- |
| `JOIN` (ou `INNER JOIN`) | Seulement les lignes qui ont une correspondance dans les deux tables |
| `LEFT JOIN` | Toutes les lignes de la table de gauche, avec `NULL` quand il n'y a pas de correspondance |

**Exemple de LEFT JOIN : repérer un robot muet**

```sql
SELECT r.nom, COUNT(c.id) AS nb_cycles
FROM robots AS r
LEFT JOIN cycles AS c ON c.robot_id = r.id
GROUP BY r.id
HAVING COUNT(c.id) = 0;
```

Un robot qui n'a jamais remonté de cycle (programme arrêté, broker injoignable, mauvais topic MQTT) n'apparaîtrait pas avec un simple `JOIN` ; le `LEFT JOIN` le conserve avec un compte à zéro.

**Astuce de lecture**

Pour comprendre une jointure, lisez-la comme « pour chaque cycle, trouve le robot dont l'`id` vaut `robot_id` ». Chaque ligne du résultat est une paire (cycle, robot) qui satisfait la condition `ON`.

## Index et transactions

Un index accélère les recherches sur une colonne, et une transaction regroupe plusieurs écritures en un bloc qui réussit ou échoue en entier.

**Index**

Sans index, la base lit toutes les lignes de la table pour répondre à un `WHERE`. Avec un index sur la colonne filtrée, elle va directement aux lignes concernées, comme l'index d'un livre.

```sql
CREATE INDEX idx_cycles_robot_debut ON cycles (robot_id, debut);
```

- Indexez les colonnes souvent utilisées dans `WHERE`, `JOIN` et `ORDER BY`.
- Les clés primaires et les colonnes `UNIQUE` sont indexées automatiquement.
- Un index accélère les lectures mais ralentit un peu les écritures et occupe de la place : n'en créez pas partout.

**Transactions**

Une transaction garantit que plusieurs instructions sont appliquées toutes ensemble ou pas du tout.

```sql
BEGIN;
INSERT INTO cycles (robot_id, duree, zone) VALUES (1, 18.6, 'A');
INSERT INTO cycles (robot_id, duree, zone) VALUES (2, 21.4, 'B');
COMMIT;      -- valide tout
-- ROLLBACK; -- ou annule tout
```

En cas de panne au milieu, la base revient à l'état d'avant `BEGIN`. Écrire plusieurs lignes dans une seule transaction est aussi bien plus rapide que de valider chaque ligne séparément : on s'en servira pour le collecteur MQTT.

## SQL depuis Python

Le module `sqlite3` de la bibliothèque standard exécute du SQL depuis un programme ; la règle essentielle est de ne jamais construire une requête en collant des valeurs dans le texte.

```python
import sqlite3

conn = sqlite3.connect("cellule.db")         # crée le fichier s'il n'existe pas
conn.execute("PRAGMA foreign_keys = ON")

conn.executescript("""
    CREATE TABLE IF NOT EXISTS robots (
        id INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE,
        equipe TEXT NOT NULL, adresse_ip TEXT);
    CREATE TABLE IF NOT EXISTS cycles (
        id INTEGER PRIMARY KEY, robot_id INTEGER NOT NULL REFERENCES robots(id),
        debut TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, duree REAL NOT NULL,
        zone TEXT, statut TEXT NOT NULL DEFAULT 'ok');
""")

# Écrire : le bloc 'with conn' valide (commit) à la sortie, ou annule en cas d'erreur
with conn:
    conn.execute("INSERT INTO robots (nom, equipe, adresse_ip) VALUES (?, ?, ?)",
                 ("ned2-g1", "g1", "192.168.1.21"))

# Écrire plusieurs lignes d'un coup
lignes = [(1, 18.2, "A"), (1, 17.9, "B"), (1, 18.6, "A")]
with conn:
    conn.executemany("INSERT INTO cycles (robot_id, duree, zone) VALUES (?, ?, ?)", lignes)

# Lire
conn.row_factory = sqlite3.Row                # accès aux colonnes par nom
for ligne in conn.execute("SELECT nom, adresse_ip FROM robots WHERE equipe = ?", ("g1",)):
    print(ligne["nom"], ligne["adresse_ip"])

conn.close()
```

**Points clés**

- Les `?` sont des paramètres : on passe les valeurs séparément, dans un tuple, même pour une seule valeur : `(valeur,)`.
- `executemany` répète une même instruction pour une liste de lignes.
- Sans `commit`, les écritures ne sont pas enregistrées ; le bloc `with conn:` s'en charge.
- Fermez la connexion en fin de programme.

**Pourquoi jamais de concaténation : l'injection SQL**

```python
# DANGEREUX : la valeur est collée dans la requête
equipe = request.args.get("equipe")          # valeur venue de l'URL, dans une vue Flask
conn.execute(f"SELECT * FROM robots WHERE equipe = '{equipe}'")

# Si l'URL contient :  ?equipe=x' OR '1'='1   la condition devient toujours vraie.
# Pire : un message MQTT forgé dont la charge contient  x'; DROP TABLE cycles; --
```

Avec les paramètres `?`, la valeur reste une simple donnée, jamais interprétée comme du SQL. Cela vaut pour toute donnée venue de l'extérieur : saisie d'un utilisateur, formulaire, message MQTT. Les noms de tables et de colonnes ne peuvent pas être des paramètres : s'ils varient, vérifiez-les contre une liste de valeurs autorisées.

## Exercices corrigés

Essayez chaque exercice avant de lire la correction ; elles s'appliquent à la base d'exemple, que ce script crée et remplit.

```sql
CREATE TABLE robots (
    id INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE,
    equipe TEXT NOT NULL, adresse_ip TEXT
);
CREATE TABLE cycles (
    id INTEGER PRIMARY KEY,
    robot_id INTEGER NOT NULL REFERENCES robots(id),
    debut TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duree REAL NOT NULL,
    zone TEXT,
    statut TEXT NOT NULL DEFAULT 'ok'
);

INSERT INTO robots (nom, equipe, adresse_ip) VALUES
    ('ned2-g1', 'g1', '192.168.1.21'),
    ('ned2-g2', 'g2', '192.168.1.22'),
    ('ned2-g3', 'g3', '192.168.1.23');

INSERT INTO cycles (robot_id, debut, duree, zone, statut) VALUES
    (1, '2026-11-17 08:30:00', 18.2, 'A', 'ok'),
    (1, '2026-11-17 08:30:25', 17.9, 'B', 'ok'),
    (1, '2026-11-17 08:30:50', 24.6, 'A', 'defaut'),
    (2, '2026-11-17 08:30:05', 22.1, 'A', 'ok'),
    (2, '2026-11-17 08:30:35', 21.8, 'B', 'ok'),
    (2, '2026-11-17 09:15:00', -1.0, 'A', 'ok');
```

**Exercice 1.** Afficher les cycles de plus de 20 secondes, du plus long au plus court.

```sql
SELECT * FROM cycles WHERE duree > 20 ORDER BY duree DESC;
```

**Exercice 2.** Compter les cycles de chaque robot.

```sql
SELECT robot_id, COUNT(*) AS nb FROM cycles GROUP BY robot_id;
```

**Exercice 3.** Afficher le nom du robot et la durée moyenne de cycle, pour chaque robot qui a des cycles.

```sql
SELECT r.nom, AVG(c.duree) AS moyenne
FROM robots AS r
JOIN cycles AS c ON c.robot_id = r.id
GROUP BY r.id;
```

**Exercice 4.** Trouver le robot qui n'a remonté aucun cycle.

```sql
SELECT r.nom
FROM robots AS r
LEFT JOIN cycles AS c ON c.robot_id = r.id
WHERE c.id IS NULL;
```

**Exercice 5.** Afficher le dernier cycle de chaque robot (nom, début, durée).

```sql
SELECT r.nom, c.debut, c.duree
FROM robots AS r
JOIN cycles AS c ON c.robot_id = r.id
WHERE c.debut = (SELECT MAX(debut) FROM cycles WHERE robot_id = r.id);
```

La sous-requête entre parenthèses calcule, pour chaque robot, le début de cycle le plus récent.

**Exercice 6.** Le cycle de durée `-1.0` est aberrant (horloge mal réglée ou message mal formé). Le repérer, puis le supprimer.

```sql
SELECT * FROM cycles WHERE duree <= 0 OR duree > 120;   -- vérifier d'abord
DELETE FROM cycles WHERE duree <= 0 OR duree > 120;
```

**Exercice 7.** Calculer, pour chaque robot, le nombre de cycles en défaut et le taux de défaut en pourcentage.

```sql
SELECT r.nom,
       SUM(c.statut = 'defaut') AS nb_defauts,
       ROUND(100.0 * SUM(c.statut = 'defaut') / COUNT(*), 1) AS taux_defaut
FROM robots AS r
JOIN cycles AS c ON c.robot_id = r.id
GROUP BY r.id;
```

**Exercice 8.** Compter les cycles par heure de la journée (production horaire).

```sql
SELECT strftime('%H', debut) AS heure, COUNT(*) AS nb
FROM cycles
GROUP BY heure
ORDER BY heure;
```

**Exercice 9 (Python).** Écrire une fonction `ajouter_cycle(conn, equipe, duree, zone)` qui insère un cycle à partir de l'équipe du robot (c'est ce que fait le collecteur à la réception d'un message MQTT `cellule/<equipe>/cycle`), avec des paramètres `?`.

```python
def ajouter_cycle(conn, equipe, duree, zone):
    with conn:
        conn.execute(
            "INSERT INTO cycles (robot_id, duree, zone) "
            "SELECT id, ?, ? FROM robots WHERE equipe = ?",
            (duree, zone, equipe),
        )
```

Si l'équipe n'existe pas, la sous-requête ne renvoie aucune ligne et rien n'est inséré.
