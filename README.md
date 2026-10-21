# Twitch Analytics

Application web développée en **Python, Flask et MySQL** permettant d'explorer et de visualiser les statistiques d'audience des jeux vidéo sur Twitch.

## Présentation

**Twitch Analytics** est un projet personnel de développement web et d'analyse de données consacré à la plateforme de streaming Twitch.

L'objectif est d'exploiter des données statistiques historiques afin d'étudier la popularité des jeux vidéo, de comparer leurs performances et d'analyser l'évolution de leurs audiences au fil du temps.

Ce projet met en pratique plusieurs compétences :

- Développement d'une application web avec Flask
- Stockage et interrogation de données avec MySQL
- Manipulation et analyse de données avec Pandas
- Création de visualisations statistiques et interactives
- Exploitation de données historiques pour produire des indicateurs décisionnels

## Fonctionnalités

### Tableau de bord global

- Consultation des statistiques générales de Twitch
- Analyse des heures visionnées par année
- Comparaison des audiences moyennes
- Visualisation des indicateurs et records d'audience
- Navigation entre différentes représentations graphiques

### Analyse par jeu vidéo

- Consultation des statistiques d'un jeu spécifique
- Évolution du nombre moyen de spectateurs par année et par mois
- Analyse des heures diffusées et visionnées
- Comparaison des pics d'audience
- Consultation de l'historique des performances
- Ajout et modification des jeux référencés

### Analyse temporelle

- Visualisation de l'évolution des jeux les plus populaires
- Classements animés des jeux vidéo
- Comparaison des performances mensuelles et annuelles
- Graphiques interactifs réalisés avec Plotly

## Technologies utilisées

| Technologie | Utilisation |
|---|---|
| Python | Développement backend |
| Flask | Framework web et gestion des routes |
| MySQL | Stockage des données |
| Pandas | Traitement et analyse des données |
| Matplotlib | Graphiques statistiques |
| Plotly | Visualisations interactives |
| Raceplotly | Animations de classements |
| HTML / CSS / JavaScript | Interface utilisateur |
| WampServer | Environnement MySQL local de développement |

## Base de données

L'application repose sur une base de données MySQL nommée `twitch`.

Elle contient **17 487 enregistrements**, répartis dans deux tables :

| Table | Enregistrements | Description |
|---|---:|---|
| `game_data` | 17 400 | Statistiques mensuelles des jeux vidéo |
| `global_data` | 87 | Statistiques mensuelles globales de Twitch |

Les données couvrent la période de **janvier 2016 à mars 2023**.

Les indicateurs disponibles comprennent notamment :

- Heures visionnées (*hours watched*)
- Heures diffusées (*hours streamed*)
- Pic de spectateurs (*peak viewers*)
- Nombre de streamers
- Nombre moyen de spectateurs
- Classements mensuels des jeux

## Architecture du projet

```text
twitch_project/
│
├── controllers/
│   └── global_controller.py
│
├── models/
│   └── global_model.py
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── accueil.html
│   ├── annee.html
│   ├── base.html
│   ├── global.html
│   ├── jeu.html
│   ├── jeu_update.html
│   ├── listJeu.html
│   └── timeline.html
│
├── database/
│   └── twitch.sql
│
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

Le projet utilise une organisation séparant les routes Flask, les contrôleurs, les modèles d'accès aux données et les templates HTML.

## Installation et démarrage

### 1. Prérequis

- Python 3.11 ou version compatible
- MySQL 8
- Git
- Un serveur MySQL local, par exemple WampServer

### 2. Cloner le dépôt

```bash
git clone https://github.com/Carneiro-David/twitch_project.git
cd twitch_project
```

### 3. Créer un environnement virtuel

```bash
python -m venv .venv
```

Sur Windows, activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

### 5. Configurer MySQL

Démarrer le serveur MySQL.

Depuis phpMyAdmin ou un autre outil de gestion MySQL :

1. Créer une base de données nommée `twitch`
2. Utiliser l'encodage `utf8mb4`
3. Sélectionner la base de données
4. Importer le fichier `database/twitch.sql`
5. Vérifier la présence des tables `game_data` et `global_data`

### 6. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet à partir de `.env.example`.

Exemple de configuration :

```dotenv
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=twitch
MYSQL_PORT=3306
SECRET_KEY=your_generated_secret_key
```

Adapter les paramètres de connexion à l'environnement MySQL utilisé.

Générer une clé secrète Flask avec :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Le fichier `.env` est exclu du dépôt Git pour protéger les informations de connexion.

### 7. Démarrer l'application

```bash
python main.py
```

Accéder ensuite à :

http://127.0.0.1:5000

## Axes d'amélioration

- Déploiement de l'application sur un hébergement web
- Modernisation de l'interface utilisateur
- Optimisation des requêtes SQL
- Ajout de nouveaux indicateurs statistiques
- Automatisation de l'actualisation des données
- Ajout de tests automatisés

## Auteur

**David Carneiro**

Projet personnel de développement web et d'analyse de données.

GitHub : https://github.com/Carneiro-David
