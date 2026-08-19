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
- **`api_logic`** : fichier responsable de la gestion des appels vers les bases de données distantes.

- **`user_query`** : fichier responsable de la génération des questions à partir du profil de l’utilisateur, ainsi que de la génération des requêtes de recherche à partir du profil et des réponses aux questions.

- **`data_cleaning`** : fichier responsable du prétraitement des données, notamment du nettoyage des données, de la génération des tokens et des embeddings.

- **`model`** : fichier contenant les fonctions permettant de communiquer avec la base de données relationnelle.

- **`coord`** : fichier responsable de vérifier chaque jour les utilisateurs qui doivent recevoir leur mise à jour. Il regroupe ces utilisateurs dans une file d’attente de type FIFO et applique, pour chaque utilisateur, les différentes étapes de recherche des documents, de nettoyage des documents et d’enregistrement dans les bases de données vectorielle et relationnelle.

- **`email_service`** : fichier responsable de la génération du résumé des tendances à partir des titres et des résumés des documents récupérés lors de la recherche, puis de l’envoi d’un e-mail à l’utilisateur afin de le notifier des nouvelles publications disponibles.

- **`password`** : fichier contenant les fonctions permettant de sécuriser les mots de passe, notamment leur hachage et leur vérification.

- **`vector_db_creation`** : fichier contenant le code permettant de créer les collections `_users_collection` et `_articles_collection` dans la base de données vectorielle, ainsi que les fonctions nécessaires pour manipuler ces collections.

- **`database`** : fichier permettant de configurer la connexion entre l’application Python/FastAPI et la base de données PostgreSQL.

- **`init_db`** : fichier permettant d’initialiser la base de données en créant automatiquement les tables correspondant aux modèles `User`, `Article`, `Keyword`, `PasswordResetToken` et `Query`. La fonction `init_db()` utilise `Base.metadata.create_all(bind=engine)` pour créer dans PostgreSQL les tables définies avec SQLAlchemy lorsqu’elles n’existent pas encore.

- **`auth`** : fichier responsable de la gestion de l’authentification et de l’accès des utilisateurs à l’application. Il crée une clé temporaire lors de la connexion, valable pendant 24 heures, permettant ensuite de reconnaître l’utilisateur lors de ses différentes actions. Le code vérifie que cette clé est valide et récupère l’identifiant de l’utilisateur. Si la clé est absente, incorrecte ou expirée, l’accès est refusé.

- **`main.py`** : fichier principal du backend de l’application. Il gère l’inscription et la connexion des utilisateurs, leurs profils et préférences de veille, la génération des questions pour affiner leur profil, le lancement des recherches d’articles, l’affichage des résultats, la modification du profil et la réinitialisation du mot de passe. Il organise également les recherches automatiques à intervalles réguliers et assure la communication entre le frontend et le backend.

## Deploiement
Le déploiement du backend a été réalisé sur une machine virtuelle **Google Cloud**, disposant de **8 Go de RAM**, du système **Ubuntu 24.04 LTS** et d’un **disque SSD d’une capacité minimale de 30 Go**. Afin de mettre en place un **reverse proxy**, **Nginx** a été utilisé pour rediriger les requêtes provenant du nom de domaine HTTPS vers le serveur local de l’application. Enfin, un **certificat SSL a été configuré à l’aide de Certbot** afin de sécuriser les échanges entre les utilisateurs et le serveur via le protocole HTTPS.

## Mise à jour

Pour que le système prenne en compte les modifications réalisées, il faut d’abord mettre à jour le dépôt GitHub depuis le PC local contenant le projet. Ensuite, depuis la machine virtuelle, il faut récupérer les dernières modifications avec `git pull`, puis reconstruire et redémarrer les services Docker à l’aide de la commande 

`docker compose -f docker-compose.prod.yml up --build -d`.



# Frontend
## Architecture du code
L'architecture considérée pour le backend est la suivante :

- **`/frontend`** : le dossier global
  - **`/node_modules`** : le dossier qui stocke toutes les bibliothèques et dépendances tierces
  - **`/public`** : le dossier qui stock les fichier statiques
  - **`/src`** : le dossier contenant tout le code pour les interfaces
    - **`/assets`** : stocke les fichiers statique qui doivent être traiter par l’application
    - **`/components`** : stocke les codes des interfaces réutilisable
    - **`/css`** : stocke les fichiers résponsable de la décoration de l’interface
    - **`/i18n`** : contenant les fichiers résponsable de la traduction rendant l’interface plus accéssible
    - **`/theme`** : responsable du thème (light ou dark) de l’interface
    - **`api.js`** : le fichier responsable de créer une instance Axios pour gérer la communication entre le frontend et le backend

## Role de chaque fichier
- **`Login`** : code responsable de l’interface de connexion.

- **`Register`** : code responsable de l’interface de création de compte.

- **`Questions`** : code responsable de l’interface d’affichage des questions générées par le backend et de la saisie des réponses de l’utilisateur.

- **`Dashboard`** : code responsable de l’interface du tableau de bord, permettant d’afficher les documents récupérés par le système.

- **`UserData`** : code responsable de l’interface de consultation et de mise à jour du profil de l’utilisateur.

- **`ForgotPassword`** : code responsable de l’interface permettant à l’utilisateur de saisir son adresse e-mail afin de recevoir un lien de réinitialisation de son mot de passe.

- **`ResetPassword`** : code responsable de l’interface permettant à l’utilisateur de définir un nouveau mot de passe.

- **`App`** : fichier responsable de la définition et de la gestion des routes publiques et privées de l’application.

## Deploiement
Le déploiement du frontend est réalisé sur le service Vercel à partir du dépôt GitHub, en utilisant uniquement le dossier `frontend`, qui contient l’ensemble du code dédié à l’interface utilisateur.

## Mise à jour

Pour que le serveur prenne en compte les modifications réalisées, il est nécessaire d’effectuer un `git push` vers le dépôt GitHub. Le serveur récupère ensuite les dernières modifications afin de mettre à jour l’application.
