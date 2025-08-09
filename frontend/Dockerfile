# ComptaEBNL-IA Frontend Dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder

# Métadonnées
LABEL maintainer="ComptaEBNL-IA Team"
LABEL description="Frontend React pour plateforme de gestion EBNL OHADA"
LABEL version="1.0"

# Variables d'environnement pour le build
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production --prefer-offline --no-audit

# Copier le code source
COPY public/ ./public/
COPY src/ ./src/
COPY tsconfig.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Build de l'application
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Métadonnées
LABEL maintainer="ComptaEBNL-IA Team"
LABEL description="Frontend React pour ComptaEBNL-IA - Production"

# Installer curl pour health check
RUN apk add --no-cache curl

# Copier la configuration Nginx optimisée
COPY nginx.conf /etc/nginx/nginx.conf

# Copier les fichiers de build depuis le stage précédent
COPY --from=builder /app/build /usr/share/nginx/html

# Créer utilisateur non-root
RUN addgroup -g 1001 -S comptaebnl && \
    adduser -S comptaebnl -u 1001

# Ajuster les permissions
RUN chown -R comptaebnl:comptaebnl /var/cache/nginx && \
    chown -R comptaebnl:comptaebnl /var/log/nginx && \
    chown -R comptaebnl:comptaebnl /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R comptaebnl:comptaebnl /var/run/nginx.pid

# Basculer vers utilisateur non-root
USER comptaebnl

# Exposer le port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# Commande par défaut
CMD ["nginx", "-g", "daemon off;"]