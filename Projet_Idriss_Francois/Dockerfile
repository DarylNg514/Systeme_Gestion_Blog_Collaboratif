# Utiliser une image de base Python
FROM python:3.11-slim

# Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Copier les fichiers du projet vers le conteneur
COPY . /app/

# Installer les dépendances du projet
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel Django fonctionnera
EXPOSE 8000

# Lancer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
