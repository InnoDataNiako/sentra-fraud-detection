# frontend/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Copier les fichiers du frontend
COPY frontend/package*.json ./
RUN npm install

# Copier tout le dossier frontend
COPY frontend/ ./

# Build
RUN npm run build

# Serveur Nginx
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=build /app/dist /usr/share/nginx/html

#  CHEMIN CORRIGÉ : depuis le dossier frontend
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]