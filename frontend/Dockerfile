# frontend/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Copier les fichiers package.json et package-lock.json depuis le dossier frontend
COPY frontend/package*.json ./
RUN npm install

# Copier tout le reste du frontend
COPY frontend/ ./

# Build
RUN npm run build

# Serveur Nginx
FROM nginx:alpine

# Copier les fichiers buildés
COPY --from=build /app/dist /usr/share/nginx/html

# Copier la config Nginx depuis le dossier frontend
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
