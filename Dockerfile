# 1. Image de base
FROM python:3.11-slim

# 2. Installation des outils de compilation (indispensables pour Rust)
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Installation de Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 4. Installation de UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 5. Copie du code
COPY . .

# 6. Création de l'environnement et installation des paquets
# On installe manuellement les paquets comme dans ton workflow GitHub
RUN uv venv && \
    uv pip install maturin yfinance pandas numpy matplotlib seaborn openai streamlit

# 7. Compilation du module Rust
# Maturin va chercher le dossier avec le Cargo.toml (himid-core)
RUN cd himid-core && uv run maturin develop --release

# 8. Exposition du port Streamlit
EXPOSE 8501

# 9. Lancement de l'app
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]