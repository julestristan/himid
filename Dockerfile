FROM n8nio/n8n:latest

USER root

# Installation de Python 3 et de l'environnement virtuel pour éviter les conflits
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# On redonne les droits à l'utilisateur par défaut de n8n
USER node