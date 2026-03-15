

# Projet de Migration de Données Médicales (CSV vers MongoDB NoSQL)
Ce projet permet d'automatiser la migration d'un dataset de 55 500 patients hospitaliers depuis un format plat (CSV) vers une base de données NoSQL (MongoDB), tout en garantissant la portabilité grâce à l'orchestration Docker.

## 1. Configuration de l'Environnement de Travail

### Installation de Git et Sécurisation SSH
Avant de manipuler le code, l'environnement Git sous Debian (Trixie/WSL) doit être configuré :

0) Installer git si cela n'est pas déjà fait : sudo apt install git

1) Cloner le repository (déjà crée sur le site de github) : git  clone https://github.com/AxelFB1992/projet5.git

2) Faire le test d'états des lieux, afin de voir si rien n'a été modifié depuis le clone : git status

3) Au cas ou un push serait nécessaire, il faut s'authifier pour se connecter au repository distant :
git config --global user.name "Votre Nom" et git config --global user.email "votre@email.com".

4) Si on souhaite faire les pull et les push plus facilement, une connexion en SSH est plus adaptée.
- Génération d'une clé SSH (via keygen) : ssh-keygen -t ed25519. 
- afficher la valeur de la clé : cat ~/.ssh/id_ed25519.pub (normalement présent dans /home/user/.ssh)
- Copier/coller la valeur de cette clé dans GitHub (dans Settings/SSH and GPG keys/New SSH keys)
- modifier l'url par défaut du repostory (pour passer de hTTPS à SHH - git@github.com:AxelFB1992/projet5.git) :
  git remote set-url origin  git@github.com:AxelFB1992/projet5.git
- Faire un premier push ou pull (pour s'assurer que tout est ok) : git push -u origin main / git pull

Cette procédure permet de s'authentifier sans mot de passe sur GitHub.

5) Gestion de la Passphrase SSH : Sur Debian, pour éviter de retaper la passphrase à chaque interaction, nous utilisons keychain :
- Installation : sudo apt install keychain
- Configuration : Ajouter eval  $(keychain --eval --agents ssh id_ed25519) dans le fichier ~/.bashrc.

### Environnement de Développement (Local)
Pour tester le script sans lancer de conteneur durant la phase de développement :

1) Venv : Création d'un environnement virtuel pour isoler les dépendances : python3 -m venv venv.

2) Créer et renseigner les dépendances du requirements.txt : nano requirements.txt puis y écrire les dépendances python
Exemples de dépendances :
dnspython==2.8.0
numpy==2.4.2
pandas==3.0.1
pymongo==4.16.0
python-dateutil==2.9.0.post0
six==1.17.0
kagglehub

3) Activation de l'environnement venv : source venv/bin/activate.

### Gitignore : Enlever certains dossiers et documents de la branche git.

Par exemple,  dossier venv/ et les fichiers temporaires (ex: Zone.Identifier sous WSL) doivent être exclus des branches git.
Cela permet d'éviter de les envoyer/recevoir vers le/du dépot git alors qu'ils ne sont pas propres au projet du repository.
Cela peut se faire via le fichier .gitignore.

1) Créer le fichier .gitignore : nano .gitignore

2) Renseigner les dossiers et documents qui seront ignorés par git lors des différents push/pull :
Exemples : 
venv/
healthcare_dataset.csv:Zone.Identifier
docker/.env

Ces dossiers et fichiers seront desormais exclus de la branche courante !

##  2. Architecture du Projet
Le projet est organisé de manière modulaire pour séparer les données, la logique et l'infrastructure :

/data : Contient le dataset source healthcare_dataset.csv et potentiellement d'autres documents qui pourraient être utilisés par
le service de migration conteneurisé (migrator)

/scripts : Contient importcsv.py et importscsv2.py, les script Python de migration. Il s'agit de deux versions d'un même script,
utilisant des dépendances différentes (csvreader pour l'un et panda pour l'autre). Le script actuellement utilisé est importcsv2.py.

/docker : Regroupe l'intelligence de déploiement : tous les documents permettants de créer les conteneurs (migrator et mongodb) et 
de les orchestrer pour qu'ils puissent échanger des informations.

- Dockerfile : Recette de construction de l'image Python du conteneur 'Migrator' (le script de migration).
- docker-compose.yml : Chef d'orchestre des services. Permet de générer les conteneurs et de les configurer.
- mongo-init.js : Script de configuration automatique utilisateurs et rôles.

3 utilisateurs mongodb sont définis par cette architecture :
- root : l'administrateur qui a tous les droits (lecture / écrire / ajout / suppression / modification)
- migration_user : l'utilisateur qui peut lire et écrire dans une base de données pour, par exemple, réaliser une migration. C'est avec
cet utilisateur que notre script va se connecter au conteneur mongodb pour procéder à la migration.
- analyst_user : l'utilisateur qui ne peut que lire dans une base de données. Typiquement, l'analyste.

Ces 3 roles sont définis dans le fichier init-db.js et utilisé par le docker-compose (ainsi que par le script de migration importcsv2.py)
pour définir les utilisateurs et roles de l'environnement. Les logins et mots de passe de ces 3 'utilisateurs' sont définis dans le
fichier /.env par les appellations suivantes :

- MONGO_ROOT_USER : login root
- MONGO_ROOT_PASSWORD : mot de passe root
- MONGO_WRITE_USER : login migration_user
- MONGO_WRITE_USER_PASSWORD : mot de passe migration_user
- MONGO_READ_USER : login analyst_user
- MONGO_READ_USER_PASSWORD : mot de passe analyst_user
- MONGO_HOST=mongodb

Remarque : a noter que ce fichier est "ignoré" par git, il doit donc être présent sur chaque machine en local et crée à l'initiative
de l'utilisateur qui récupère le projet depuis github et souhaite le faire fonctionner sur sa machine.

##  3. Le Script de Migration (importcsv2.py)

### Fonctionnement du script 
Le script utilise la bibliothèque pymongo. Sa logique interne est la suivante :

1)Connexion : Il cible le service mongodb sur le port 27017 avec les identifiants root / examplepassword.
Il utilise pour cela l'URI suivante : uri = f"mongodb://{mongo_write_user}:{mongo_write_user_password}@localhsot:27017/"

2)Nettoyage : Le script de migration va systématiquement supprimer les éléments présents dans la collection visée. Cela permet de s'assurer du bon déroulement de la migration en n'observant que les éléments prévus (et non des éléments qui seraient déjà présents avant la migration)
	--> Utilisation de healthcol.drop() pour réinitialiser la collection et éviter les doublons en cas de relance.

3)Transformation : Lecture du CSV via panda. Transformation en tant que DataFrame. Puis de Data Frame en tant que tableau de document.
Chaque ligne est transformée en un document JSON complexe avec des sous-objets (medical_info, hospitalization, billing).

4)Insertion dans la base de données conteneurisée (Mongodb) : Le tableau de documents est alors inséré dans la base de données grâce à la connexion déjà établi avec le conteneur Mongodb. Dès lors, les 55 500 patients sont intégrés avec succès dans la base de données.

Remarques :

Interactivité : Une pause interactive via input() a été implémentée, mais la gestion de l'entrée standard (stdin) dans un environnement conteneurisé peut varier selon le terminal utilisé (WSL vs Debian natif). Pour garantir la fiabilité de la démonstration, nous avons préféré opter pour une exécution directe ou séquencée..

### Format de données

Contrairement au format CSV d'origine, les données sont restructurées dans MongoDB sous forme de documents JSON imbriqués. Cette approche permet de regrouper logiquement les informations liées à un même domaine (médical, hospitalier, facturation).

Ci-dessous le schémas de la base de données tel qu'il est structuré suite à la migration vers mongodb. Chaque objet enregistré sera sous le format ci dessous, qu'on appelle également 'document' (format JSON). Chaque document est stockée dans une collection (ici 'patients'), elle-même stockée dans une bonne de donnée propre (healthcare_db) :

| Champ | Type | Description |
| :--- | :--- | :--- |
| `_id` | ObjectId | Identifiant unique généré automatiquement par MongoDB. |
| `name` | String | Nom et prénom du patient. |
| `age` | Integer | Âge du patient lors de l'admission. |
| `gender` | String | Genre du patient (Male/Female). |
| `blood_type` | String | Groupe sanguin du patient. |
| **`medical_info`** | **Object** | **Sous-document contenant les données cliniques :** |
| ∟ `condition` | String | Pathologie ou condition médicale diagnostiquée. |
| ∟ `medication` | String | Médicament prescrit au patient. |
| ∟ `test_results` | String | Résultat des examens (Normal, Abnormal, etc.). |
| **`hospitalization`** | **Object** | **Sous-document relatif au séjour à l'hôpital :** |
| ∟ `admission_date` | String | Date d'entrée dans l'établissement. |
| ∟ `discharge_date` | String | Date de sortie de l'établissement. |
| ∟ `type` | String | Type d'admission (Emergency, Elective, Urgent). |
| ∟ `room` | Integer | Numéro de la chambre assignée. |
| ∟ `doctor` | String | Nom du médecin responsable. |
| ∟ `hospital` | String | Nom de l'établissement de santé. |
| **`billing`** | **Object** | **Sous-document financier :** |
| ∟ `provider` | String | Nom de la compagnie d'assurance. |
| ∟ `amount` | Float | Montant total facturé pour le séjour. |

##  4. Conteneurisation et Orchestration

1) Le Dockerfile
Il construit une image personnalisée pour le service migrator, basé sur le script :

Base : python:3.12-slim.

Installation des dépendances via requirements.txt.

Montage du code source via le mécanisme du DockerFile.

2) Le Docker Compose
Il définit deux services essentiels :

- mongodb : Utilise l'image mongo:latest.
	Volumes :
	Un volume d'entrée est crée pour que le fichier mongo-init.js puisse être transmis de la machine local vers le conteneur pour éxécution de l'environnement d'authentification.
	Un volume de sortie nommé 'mongo-data' est créé pour que les données persistent même si le conteneur est supprimé.
	Environnement :
	Les variables MONGO_ROOT_USER et MONGO_ROOT_PASSWORD sont utilisés pour l'initialisation du conteneur : un premier compte doit impérativement être crée.
	
- migrator : Notre script Python.
	Volumes :
	Un volume d'entrée est crée pour que le fichier healthcare_dataset.csv puisse être transmis de la machine local vers le conteneur pour migration.
	Environnement :
	Les variables MONGO_ROOT_USER, MONGO_ROOT_PASSWORD, MONGO_WRITE_USER, MONGO_WRITE_USER_PASSWORD, MONGO_READ_USER,
	MONGO_READ_USER_PASSWORD, MONGO_HOST sont utilisés pour se connecter à la base de données sous différents utilisation avec différents roles.

Réseau : Les deux services communiquent via un bridge network privé (my_network).

##  5. Procédure de Lancement
Depuis la racine du projet, exécutez la commande suivante (le flag -f est nécessaire car le fichier est dans le dossier /docker) :

Bash
docker compose -f docker/docker-compose.yml up --build
Étapes du lancement :

Docker télécharge l'image MongoDB.

Docker construit l'image de migration (étape de pip install).

MongoDB démarre en tâche de fond.

Le script de migration affiche un message qui indique si la migration a réussi ou non.

##  6. Vérification et Contrôle des Données

Pour vérifier seulement les données, il faut que le conteneur mongodb soit en cours d'execution. Il y a deux cas possibles :

- Soit l'application global (embarquant les deux conteneurs : mongodb et migrator) tourne encore, auquel cas c'est nécessairement que mongodb est encore en execution.

- Soit l'application global s'est arrêté auquel cas il faut relancer le conteneur mongodb. 
	Pour relancer seulement le conteneur mongodb (sans le conteneur migrator), on peut utiliser cette commande : docker compose -f docker/docker-compose.yml up -d mongodb.
	Celle ci permet notamment de lancer le conteneur mongodb en tâche de fond, sans bloquer le terminal.
	Pour arrêter le conteneur, on utilisera la commande suivante : Arrêt : docker compose -f docker/docker-compose.yml down.

1) Via le Terminal (Shell MongoDB)
Pour vérifier que les 55 500 documents sont présents :

Bash
docker exec -it docker-mongodb-1 mongosh -u root -p examplepassword

--> On entre dans le shell mongosh, dans lequel on peut éxecuter les commandes suivantes :
use healthcare_db
db.patients.countDocuments()
	--> Devrait afficher le nombre de patients ajoutés, soit 55500 si la migration s'est bien déroulée.


2) Via l'interface graphique (MongoDB Compass)
Installez MongoDB Compass sur votre hôte.

Connectez-vous avec l'URI : mongodb://root:examplepassword@localhost:27017/.

Naviguez dans la base healthcare_db pour visualiser les documents imbriqués.

Maintenance - Rappels 
Arrêt : docker compose -f docker/docker-compose.yml down.

Relance de la BDD seule : docker compose -f docker/docker-compose.yml up -d mongodb.
