# projet5

# Projet de Migration de Données Médicales - NoSQL

Ce projet a pour objectif de migrer un dataset de dossiers patients d'un format tabulaire (CSV) vers une base de données **MongoDB** scalable, orchestrée via **Docker**.

## 🏗️ Architecture Technique
L'application utilise **Docker Compose** pour orchestrer deux services :
1. **MongoDB** : Base de données NoSQL pour le stockage des dossiers médicaux.
2. **Migrator** : Un conteneur éphémère basé sur Python qui automatise l'importation et la transformation du dataset CSV en documents JSON.



## 📋 Prérequis
* Docker et Docker Compose installés.
* Le dataset `healthcare_dataset.csv` placé dans le dossier `/data`.

## 🚀 Installation et Lancement

1. **Cloner le repository** :
   ```bash
   git clone <ton-url-github>
   cd projet5
