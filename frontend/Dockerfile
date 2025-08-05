# Dockerfile pour Frontend ComptaEBNL-IA
# Stage 1: Build
FROM node:18-alpine AS build

# Métadonnées
LABEL maintainer="ComptaEBNL-IA Team"
LABEL description="Frontend React pour ComptaEBNL-IA - Interface comptabilité EBNL"

# Répertoire de travail
WORKDIR /app

# Copie des fichiers de configuration
COPY package*.json ./

# Installation des dépendances
RUN npm ci --only=production

# Copie du code source
COPY . .

# Arguments de build
ARG REACT_APP_API_URL=http://localhost:5001
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

# Build de production
RUN npm run build

# Stage 2: Production avec Nginx
FROM nginx:alpine

# Installation de curl pour health check
RUN apk add --no-cache curl

# Copie de la configuration Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers buildés
COPY --from=build /app/build /usr/share/nginx/html

# Port d'exposition
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# Commande de démarrage
CMD ["nginx", "-g", "daemon off;"]