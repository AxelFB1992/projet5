#🏥 Projet de Migration de Données Médicales (CSV vers MongoDB NoSQL)
Ce projet permet d'automatiser la migration d'un dataset de 55 500 patients hospitaliers depuis un format plat (CSV) vers une base de données NoSQL (MongoDB), tout en garantissant la portabilité grâce à l'orchestration Docker.

##🛠 1. Configuration de l'Environnement de Travail
Installation de Git et Sécurisation SSH
Avant de manipuler le code, l'environnement Debian (Trixie/WSL) doit être configuré :

Identité Git : git config --global user.name "Votre Nom" et git config --global user.email "votre@email.com".

Clé SSH : Génération via ssh-keygen -t ed25519. Cela permet de s'authentifier sans mot de passe sur GitHub.

Gestion de la Passphrase : Sur Debian, pour éviter de retaper la passphrase à chaque interaction, nous utilisons keychain :

Installation : sudo apt install keychain

Configuration : Ajouter eval  $(keychain --eval --agents ssh id_ed25519) dans le fichier ~/.bashrc.

Environnement de Développement (Local)
Pour tester le script sans Docker durant la phase de développement :

Venv : Création d'un environnement virtuel pour isoler les dépendances : python3 -m venv venv.

Activation : source venv/bin/activate.

Gitignore : Le dossier venv/ et les fichiers temporaires (ex: Zone.Identifier sous WSL) sont exclus via le fichier .gitignore.

## 📂 2. Architecture du Projet
Le projet est organisé de manière modulaire :

/data : Contient le dataset source healthcare_dataset.csv.

/scripts : Contient importcsv.py, le script Python de migration.

/docker : Regroupe l'intelligence de déploiement :

Dockerfile : Recette de construction de l'image Python.

docker-compose.yml : Chef d'orchestre des services.

## 🐍 3. Le Script de Migration (importcsv.py)
Le script utilise la bibliothèque pymongo. Sa logique interne est la suivante :

Connexion : Il cible le service mongodb sur le port 27017 avec les identifiants root / examplepassword.

Nettoyage : Utilisation de healthcol.drop() pour réinitialiser la collection et éviter les doublons en cas de relance.

Transformation : Lecture du CSV via DictReader. Chaque ligne est transformée en un document JSON complexe avec des sous-objets (medical_info, hospitalization, billing).

Interactivité : Une pause input() est intégrée pour permettre à l'utilisateur de déclencher la migration manuellement.

## 🐳 4. Conteneurisation et Orchestration
Le Dockerfile
Il construit une image personnalisée pour le script :

Base : python:3.12-slim.

Installation des dépendances via requirements.txt.

Montage du code source.

Le Docker Compose
Il définit deux services essentiels :

mongodb : Utilise l'image mongo:latest.

Volumes : Un volume nommé mongo-data est créé pour que les données persistent même si le conteneur est supprimé.

migrator : Notre script Python.

Interactif : Les options stdin_open: true et tty: true sont activées pour permettre l'interaction clavier (input()).

Réseau : Les deux services communiquent via un bridge network privé.

## 🚀 5. Procédure de Lancement
Depuis la racine du projet, exécutez la commande suivante (le flag -f est nécessaire car le fichier est dans le dossier /docker) :

Bash
docker compose -f docker/docker-compose.yml up --build
Étapes du lancement :

Docker télécharge l'image MongoDB.

Docker construit l'image de migration (étape de pip install).

MongoDB démarre en tâche de fond.

Le script de migration affiche un message et attend que vous appuyiez sur [ENTRÉE].

## 🧪 6. Vérification et Contrôle des Données
Via le Terminal (Shell MongoDB)
Pour vérifier que les 55 500 documents sont présents :

Bash
docker exec -it docker-mongodb-1 mongosh -u root -p examplepassword
use healthcare_db
db.patients.countDocuments()
Via l'interface graphique (MongoDB Compass)
Installez MongoDB Compass sur votre hôte.

Connectez-vous avec l'URI : mongodb://root:examplepassword@localhost:27017/.

Naviguez dans la base healthcare_db pour visualiser les documents imbriqués.

Maintenance
Arrêt : docker compose -f docker/docker-compose.yml down.

Relance de la BDD seule : docker compose -f docker/docker-compose.yml up -d mongodb.
