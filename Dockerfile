# 1. Image de base
FROM python:3.11-slim

# 2. Installation de UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN mkdir -p assets

# 3. Copie du code
COPY . .

# 4. Création de l'environnement et installation des paquets
RUN uv venv && \
    uv pip install -r requirements.txt

EXPOSE 8501

# 5. Lancement de l'app & mail
CMD uv run python src/main.py && uv run streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0