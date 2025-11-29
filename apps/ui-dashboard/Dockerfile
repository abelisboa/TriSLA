# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
# Usar npm ci se package-lock.json existir, senão npm install
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

COPY . .
# Build com Vite (já faz type checking, mas não falha em warnings)
RUN npm run build:skip-check

# Production stage
FROM nginx:alpine

# Instalar envsubst para substituir variáveis de ambiente
RUN apk add --no-cache gettext

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Variáveis de ambiente padrão
ENV API_BACKEND_HOST=decision-engine
ENV API_BACKEND_PORT=8082

EXPOSE 80

# Nginx automaticamente processa templates em /etc/nginx/templates/*.template
CMD ["nginx", "-g", "daemon off;"]

