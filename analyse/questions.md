# Questions de l'évaluation

Infrastructure client / serveur dans un contexte industriel

Le jour de l'évaluation, après le déroulé du cahier de recette (`cahier_recette.md`), l'enseignant pose à **chaque étudiant, individuellement,** quelques questions sur la cellule. Ce document est la **liste de ces questions** : 30 questions, à travailler **tout au long du projet**, pas la veille.

Elles portent sur la **compréhension** : à quoi sert chaque élément de la cellule, et comment ils échangent entre eux. On ne demande ni de réciter du code, ni de connaître des commandes : on demande d'expliquer **qui fait quoi, qui parle à qui, et pourquoi**.

## Comment s'en servir

- **Chaque membre de l'équipe doit pouvoir répondre à toutes les questions**, pas seulement à celles de sa partie. L'enseignant choisit les questions et la personne interrogée.
- Les réponses s'appuient sur **votre** cellule : votre process, vos messages, vos pages. Une réponse générale ne suffit pas ; il faut dire ce que fait **votre** installation.
- Pour répondre, **s'aider du schéma d'architecture** de l'équipe (`dossier_analyse.md`, rubrique 3.1) : savoir le refaire de mémoire et le commenter est la meilleure préparation. L'enseignant peut demander de **montrer** un échange sur le schéma, ou sur l'application en fonctionnement (la page du site, la liste des messages).
- La colonne « Pour répondre » indique où chercher. Les réponses ne sont **pas fournies** : les formuler soi-même, avec ses mots.
- La colonne « Mes notes » sert à préparer : écrire l'essentiel en deux ou trois phrases. On ne lit pas ses notes à l'oral.
- Les questions se rencontrent dans le désordre du projet : les noter dès qu'on se les pose, puis les reprendre au fil de l'avancement. Se les poser **les uns aux autres** dans l'équipe est le meilleur entraînement.
- D'autres questions, en lien avec vos choix, peuvent s'ajouter le jour de l'évaluation.


## 1. Le rôle de chaque élément

| N° | Question | Pour répondre | Mes notes |
|---|---|---|---|
| 1 | Quel problème la cellule supervisée résout-elle pour l'opérateur ? Donner un exemple de votre process pour chacun des trois besoins : **piloter** le robot, **être informé** de ce qu'il fait, **observer** ce qui s'est passé. | `README.md` (sections 2 et 4) | À COMPLÉTER |
| 2 | Citer les éléments de votre cellule (robot, convoyeur, broker, collecteur, base de données, API du robot, site web) et dire le rôle de chacun en une phrase. | `README.md` (section 5), `dossier_analyse.md` (3.1) | À COMPLÉTER |
| 3 | Sur quelle machine se trouve chaque élément : le robot, le serveur, le poste de l'opérateur ? Pourquoi à cet endroit ? | `dossier_analyse.md` (3) | À COMPLÉTER |
| 4 | Que fait le programme du robot ? Que connaît-il, et que ne connaît-il pas (par exemple : sait-il que la base ou le site existent) ? | `README.md` (section 5), `dossier_analyse.md` (2) | À COMPLÉTER |
| 5 | À quoi sert le broker ? Pourquoi le robot ne parle-t-il pas directement au collecteur ? | `README.md` (« Deux modes de communication ») | À COMPLÉTER |
| 6 | À quoi sert le collecteur ? Que perdrait-on s'il n'existait pas ? | `README.md` (section 5) | À COMPLÉTER |
| 7 | Pourquoi la cellule a-t-elle une base de données ? Que garde-t-on dedans, et pourquoi ne pas simplement afficher les informations à l'écran quand elles arrivent ? | `README.md` (section 5) | À COMPLÉTER |
| 8 | À quoi sert l'API du robot ? En quoi son rôle est-il différent de celui du broker ? | `README.md` (« Deux modes de communication ») | À COMPLÉTER |
| 9 | Que fait le site web ? D'où viennent les informations qu'il affiche, et à qui envoie-t-il les ordres de l'opérateur ? | `dossier_analyse.md` (8) | À COMPLÉTER |


## 2. Les échanges

| N° | Question | Pour répondre | Mes notes |
|---|---|---|---|
| 10 | Suivre une **fin de cycle** : qui produit l'information, par quels éléments elle passe, et qui la reçoit finalement ? Montrer le trajet sur le schéma. | `README.md` (« Les échanges »), `dossier_analyse.md` (3.1, 5) | À COMPLÉTER |
| 11 | Suivre un **ordre de l'opérateur** (un clic sur un bouton) : par quels éléments passe-t-il jusqu'au robot ? Montrer le trajet sur le schéma. | `README.md` (« Les échanges »), `dossier_analyse.md` (3.1, 7) | À COMPLÉTER |
| 12 | Votre cellule a deux sortes d'échanges : les **ordres** que l'on envoie au robot, et les **messages** que le robot diffuse. En quoi sont-ils différents ? Donner un exemple de chaque. | `README.md` (« Deux modes de communication ») | À COMPLÉTER |
| 13 | Pour chaque message de votre cellule (cycle, état, défaut, tâche, et les vôtres) : qui l'émet, qui le reçoit, et à quel moment ? | `dossier_analyse.md` (5.1) | À COMPLÉTER |
| 14 | Pourquoi celui qui émet un message n'a-t-il pas besoin de savoir qui l'écoute ? Qu'est-ce que cela permet (ajouter un récepteur, remplacer un élément) ? | `README.md` (« Deux modes de communication ») | À COMPLÉTER |
| 15 | Quelles informations contient un message de fin de cycle, et à quoi sert chacune (pièce, durée, zone, heure) ? | `dossier_analyse.md` (5.2) | À COMPLÉTER |
| 16 | Pourquoi l'**état actuel** du robot (que fait-il maintenant ?) et l'**historique** (qu'a-t-il fait ?) ne viennent-ils pas du même endroit ? | `README.md` (« Deux modes de communication ») | À COMPLÉTER |
| 17 | Après un ordre, comment l'opérateur sait-il que le robot l'a exécuté ? Quels éléments le lui disent, et par quels moyens ? | `site_web/README.md` (« Comment il fonctionne ») | À COMPLÉTER |
| 18 | Pourquoi le robot refuse-t-il un ordre quand il est déjà occupé ? Qu'est-ce que l'opérateur voit alors ? | `api_robot/README.md` | À COMPLÉTER |
| 19 | Sur la page du site : d'où vient chaque information affichée (l'état du robot, la liste des derniers messages, le résultat d'une commande) ? | `site_web/README.md` | À COMPLÉTER |


## 3. Les pannes et la fiabilité

| N° | Question | Pour répondre | Mes notes |
|---|---|---|---|
| 20 | Si un élément tombe en panne (le collecteur, l'API du robot, le serveur, le réseau), qu'est-ce qui continue de fonctionner, qu'est-ce qui s'arrête, et qu'est-ce qui est perdu ? | `collecteur/README.md`, `cours/collecteur_MQTT.md` | À COMPLÉTER |
| 21 | Pourquoi le robot doit-il pouvoir continuer son cycle même quand toute la supervision est arrêtée ? | `README.md` (section 1) | À COMPLÉTER |
| 22 | Un message incorrect arrive au collecteur. Que doit-il en faire ? Pourquoi ne doit-il surtout pas s'arrêter ? | `collecteur/README.md` | À COMPLÉTER |
| 23 | Un événement du robot n'apparaît pas sur le site. Dans quel ordre vérifie-t-on les éléments de la chaîne, et que cherche-t-on à chaque étape ? | `collecteur/README.md` | À COMPLÉTER |
| 24 | Pourquoi développe-t-on d'abord avec des simulateurs, avant d'utiliser le robot ? Qu'est-ce qui reste identique pour le reste de la cellule quand on passe du simulateur au vrai robot ? | `README.md` (section 7), `simulateurs/README.md` | À COMPLÉTER |


## 4. Votre cellule, sa recette et son évolution

| N° | Question | Pour répondre | Mes notes |
|---|---|---|---|
| 25 | Expliquer votre process et le cycle du robot en termes simples : que se passe-t-il, dans quel ordre, et quels sont les cas de défaut ? | `dossier_analyse.md` (2) | À COMPLÉTER |
| 26 | Prendre votre schéma d'architecture, choisir un échange et l'expliquer : qui parle à qui, pour dire quoi, et pourquoi. | `dossier_analyse.md` (3.1) | À COMPLÉTER |
| 27 | Choisir un test de votre cahier de recette : quelle exigence vérifie-t-il, que prouve-t-il, et qu'est-ce qui le rendrait non conforme ? | `cahier_recette.md` | À COMPLÉTER |
| 28 | Que faudrait-il changer pour superviser **4 robots** au lieu d'un ? Quels éléments serviraient à tous, lesquels seraient à multiplier ? | `README.md` | À COMPLÉTER |
| 29 | Quelle évolution ajouteriez-vous à la cellule (une alerte, un compteur de production, une nouvelle commande) ? Quels éléments et quels échanges seraient touchés ? | `site_web/README.md` (« Pistes pour aller plus loin ») | À COMPLÉTER |
| 30 | Quelle partie avez-vous réalisée vous-même ? Quel est son rôle dans l'ensemble, qu'est-ce qu'elle reçoit des autres éléments et que leur fournit-elle ? Quelle difficulté avez-vous rencontrée ? | votre expérience du projet | À COMPLÉTER |


## 5. Suivi de la préparation

Cocher une section quand **chaque membre** de l'équipe sait répondre à toutes ses questions.

| Section | Prête |
|---|---|
| 1. Le rôle de chaque élément | |
| 2. Les échanges | |
| 3. Les pannes et la fiabilité | |
| 4. Votre cellule, sa recette et son évolution | |
