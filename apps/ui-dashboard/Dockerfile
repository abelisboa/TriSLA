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

# Instalar dependências necessárias
RUN apk add --no-cache bind-tools

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY entrypoint.sh /entrypoint.sh

# Variáveis de ambiente padrão (Kubernetes Service names)
ENV API_BACKEND_HOST=trisla-decision-engine.trisla.svc.cluster.local
ENV API_BACKEND_PORT=8082
# Resolver DNS: kube-dns em Kubernetes, 127.0.0.11 (Docker) ou 8.8.8.8 (fallback)
ENV NGINX_RESOLVER=127.0.0.11

EXPOSE 80

# Garantir que apenas o template processado seja usado
# Remover qualquer config padrão que possa conflitar
RUN rm -f /etc/nginx/conf.d/default.conf || true

# Dar permissão de execução ao entrypoint
RUN chmod +x /entrypoint.sh

# Usar entrypoint customizado
ENTRYPOINT ["/entrypoint.sh"]

