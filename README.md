🏥 Projet de Migration de Données Médicales (CSV vers MongoDB NoSQL)

Ce projet permet d'automatiser la migration d'un dataset de 55 500 patients hospitaliers depuis un format plat (CSV) vers une base de données NoSQL (MongoDB), tout en garantissant la portabilité et la sécurité grâce à l'orchestration Docker.

🛠️ 1. Configuration de l'Environnement de Travail

Installation de Git et Sécurisation SSH

Avant de manipuler le code sous Debian (Trixie/WSL), l'environnement doit être configuré :

Installation : sudo apt update && sudo apt install git

Clonage : git clone https://github.com/AxelFB1992/projet5.git

Identité :

git config --global user.name "Axel F.B."

git config --global user.email "votre@email.com"

Connexion SSH (Recommandé pour faciliter les push/pull) :

Générer la clé : ssh-keygen -t ed25519

Afficher la clé publique : cat ~/.ssh/id_ed25519.pub

Ajouter la clé sur GitHub (Settings > SSH keys).

Basculer l'URL en SSH : git remote set-url origin git@github.com:AxelFB1992/projet5.git

Gestion de la Passphrase (Keychain) :

sudo apt install keychain

Ajouter eval $(keychain --eval --agents ssh id_ed25519) dans votre ~/.bashrc.

Environnement de Développement (Local)

Pour tester les scripts hors conteneur :

Venv : python3 -m venv venv puis source venv/bin/activate

Dépendances : pip install -r requirements.txt (incluant pymongo, pandas, dnspython).

Gitignore : Exclusion du dossier venv/, du fichier .env et des fichiers temporaires WSL (Zone.Identifier).

📂 2. Architecture du Projet

/data : Contient le dataset source healthcare_dataset.csv.

/scripts : Contient les versions du script de migration (importcsv.py et importcsv2.py).

/docker : Regroupe l'intelligence de déploiement :

Dockerfile : Construction de l'image Python pour le service migrator.

docker-compose.yml : Orchestrateur des services MongoDB et Migration.

init-db.js : Configuration automatique du RBAC (Role-Based Access Control).

🔐 3. Sécurité et Gestion des Rôles (RBAC)

Nous appliquons le Principe du Moindre Privilège en segmentant les accès. Les mots de passe sont hachés nativement par MongoDB via le mécanisme SCRAM-SHA-256.

Utilisateur

Rôle

Base Cible

Usage

root

root

admin

Administration totale (Infrastructure).

migration_user

readWrite

healthcare_db

Utilisé par le script Python pour l'import.

analyst_user

read

healthcare_db

Consultation en lecture seule (Audit).

Note importante : Les identifiants sont gérés via un fichier .env local (exclu de Git) pour éviter toute fuite de secrets.

🐍 4. Le Script de Migration (importcsv2.py)

Logique Interne

Connexion : Utilisation d'une URI dynamique ciblant le service mongodb sur le réseau Docker.

Nettoyage : Utilisation de healthcol.drop() pour réinitialiser la collection et garantir l'idempotence (pas de doublons).

Transformation : Conversion du format plat CSV en documents JSON complexes avec sous-objets.

Optimisation : Insertion en masse (insert_many) pour traiter les 55 500 lignes efficacement.

Schéma de Données (Format Document)

Champ

Type

Description

_id

ObjectId

Identifiant unique MongoDB.

name

String

Nom complet du patient.

medical_info

Object

Sous-document : Condition, Médicament, Résultats.

hospitalization

Object

Sous-document : Dates, Chambre, Docteur, Hôpital.

billing

Object

Sous-document : Assurance, Montant facturé.

🐳 5. Conteneurisation et Orchestration

Services Docker

mongodb : Base de données officielle. Utilise un volume nommé mongo-data pour la persistance des données.

migrator : Conteneur basé sur Python 3.12-slim. Il monte le CSV via un volume et exécute le script après le démarrage de la base.

Réseau

Les services communiquent via un réseau privé bridge (my_network). Le script contacte la base via le nom d'hôte mongodb.

🚀 6. Procédure de Lancement

Créer le fichier .env dans /docker (voir section 3 pour les variables).

Lancer l'infrastructure :

docker compose -f docker/docker-compose.yml up --build


Étapes : Docker construit l'image de migration, MongoDB initialise les rôles via init-db.js, puis le script effectue la migration.

🧪 7. Vérification et Contrôle des Données

Via le Terminal (Shell MongoDB)

# Connexion avec le compte root pour vérification globale
docker exec -it docker-mongodb-1 mongosh -u root -p examplepassword --authSource admin

# Commandes de vérification
use healthcare_db;
db.patients.countDocuments(); // Résultat attendu : 55500


Via MongoDB Compass

Connectez-vous avec l'URI suivante :
mongodb://root:examplepassword@localhost:27017/?authSource=admin

💡 8. Justification des Choix Techniques

MongoDB : Choisi pour sa scalabilité horizontale et sa flexibilité de schéma (indispensable pour des données médicales variées).

Docker : Garantit que le projet fonctionnera exactement de la même manière sur n'importe quel OS (Debian, Windows, AWS).

Python/Pandas : Permet une manipulation de données puissante et rapide pour les gros datasets.
