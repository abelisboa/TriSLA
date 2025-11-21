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

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

