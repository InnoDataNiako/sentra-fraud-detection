# Étape 1 : Builder Python
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --user --no-cache-dir -r requirements.txt

# Étape 2 : Image finale
FROM python:3.11-slim

WORKDIR /app

# Installer uniquement les outils nécessaires
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances installées depuis le builder
COPY --from=builder /root/.local /root/.local

# Ajouter le répertoire .local au PATH
ENV PATH=/root/.local/bin:$PATH

# Copier le code source
COPY . .

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Créer un utilisateur non-root pour plus de sécurité
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exposer le port
EXPOSE 8000

# Health check pour Render
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Commande de démarrage OPTIMISÉE POUR RENDER
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]