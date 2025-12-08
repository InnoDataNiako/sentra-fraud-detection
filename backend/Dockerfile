FROM python:3.11-slim
WORKDIR /app

# Copier les requirements depuis le sous-dossier backend/
COPY backend/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le dossier backend dans l'image
COPY backend/ .

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
