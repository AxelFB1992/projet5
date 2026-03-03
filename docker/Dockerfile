# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier ton script de migration
COPY importcsv2.py .

# Commande par défaut pour lancer le script
CMD ["python", "importcsv2.py"]
