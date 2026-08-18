# Problématique
Le plus grand défi des chercheurs aujourd'hui est de rester à jour face au nombre croissant de nouvelles publications scientifiques. Bien qu'il existe des outils permettant d'envoyer des alertes quotidiennes, le problème persiste : les utilisateurs se sentent de plus en plus submergés par le volume d'e-mails reçus chaque jour ainsi que par la présence d'articles peu pertinents (articles ne correspondant pas à leur profil, provenant de sources moins fiables, etc.).

# Objectif
Afin de répondre à cette problématique, mon stage avait pour objectif de concevoir et développer une application web de veille scientifique intelligente dédiée aux chercheurs de l'Hôpital Erasme. Les principaux objectifs étaient les suivants :
- concevoir une application permettant la gestion du profil de l'utilisateur ;
- collecter des données provenant de bases de données spécialisées ;
- utiliser l'intelligence artificielle pour affiner la recherche selon le profil de l'utilisateur ;
- mettre en place un système de recommandation combinant la recherche sémantique et la recherche par mots-clés ;
- automatiser l'envoi de notifications périodiques contenant un résumé des tendances ;
- afficher les résultats dans le tableau de bord de l'utilisateur.

# Fonctionnement
L'utilisateur doit créer un compte en renseignant ses informations personnelles, telles que son nom, son adresse e-mail et un mot de passe, ainsi que son profil professionnel et la cadence à laquelle il souhaite rechercher de nouveaux articles (hebdomadaire ou mensuelle).

Une fois le profil de l'utilisateur validé, le système lui propose un ensemble de questions de manière progressive. La première question est générée uniquement à partir du profil de l'utilisateur. Les deux questions suivantes sont générées en se basant sur le profil professionnel ainsi que sur l'historique des questions et des réponses précédentes. À partir du profil et des réponses fournies, 15 requêtes de recherche sont ensuite générées pour interroger trois bases de données externes : PubMed, Semantic Scholar et Clinical Trials.

Après la création du compte, une première recherche est automatiquement lancée. Par la suite, en fonction de la cadence choisie par l'utilisateur, une nouvelle recherche est effectuée chaque semaine ou chaque mois.

# Installation

Le projet est disponible sur GitHub et peut être cloné à l'aide de la commande suivante :

```bash
git clone https://github.com/rihabsem/veille_scientifique.git
```

Une fois le projet cloné, se placer dans le dossier du projet :

```bash
cd veille_scientifique
```
## Backend et services Docker

Pour construire les images Docker et démarrer les différents services, exécuter :

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Cette commande permet de démarrer les services nécessaires au fonctionnement de l'application notamment le backend, PostgreSQL et ChromaDB.

## Création de la base de données

La base de données PostgreSQL est créée automatiquement lors du démarrage du service postgres.

Pour créer les tables et appliquer les migrations Alembic, exécuter la commande suivante depuis le dossier parent du projet :

```bash
docker exec fastapi_backend alembic upgrade head
```

## Frontend

Pour installer les dépendances du frontend, se placer dans le dossier frontend :

```bash
cd frontend
```

Puis exécuter :

```bash
npm install
```

Une fois les dépendances installées, le frontend peut être lancé avec :

```bash
npm run dev
```

# Backend
## Architecture du code
L'architecture considérée pour le backend est la suivante :

- **`/backend`** : le dossier global
  - **`/app`** : le dossier contenant tout le code du backend ainsi que le code pour la création de la base de données
    - **`/models`** : le dossier contenant les définitions des tables
  - **`/migrations`** : le dossier contenant les fichiers de migrations
  - **`/tests`** : le dossier contenant les fichiers de tests

## Role de chaque fichier

