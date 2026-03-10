# Utiliser une image Python légère
# Dans docker/Dockerfile#
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier des dépendances et les installer
COPY requirements.txt .
COPY scripts/importcsv.py .

RUN pip install --no-cache-dir -r requirements.txt

# Commande par défaut pour lancer le script
CMD ["python", "importcsv.py"]
