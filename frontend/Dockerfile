# le docker file du frontend

# Étape 1 : Builder Node.js
FROM node:18-alpine as builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./

# Installer les dépendances
RUN npm ci --silent

# Copier le code source
COPY . .

# Build de l'application
RUN npm run build

# Étape 2 : Serveur Nginx pour servir les fichiers statiques
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=builder /app/dist /usr/share/nginx/html

# Copier la configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposition du port
EXPOSE 80
# Health check pour Render
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Commande de démarrage
CMD ["nginx", "-g", "daemon off;"]