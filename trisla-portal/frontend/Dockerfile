# Frontend Dockerfile - Portal TriSLA
# Build stage
FROM node:20 AS builder

WORKDIR /app

# Copiar arquivos de dependências
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar código fonte
COPY . .

# Build da aplicação Next.js
RUN npm run build

# Production stage com nginx
FROM nginx:alpine

# Copiar arquivos estáticos do build
# Para Next.js standalone, copiamos os arquivos necessários
COPY --from=builder /app/.next/standalone /usr/share/nginx/html
COPY --from=builder /app/.next/static /usr/share/nginx/html/_next/static

# Criar script de entrada para gerar env.js dinamicamente
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'set -e' >> /entrypoint.sh && \
    echo 'BACKEND_URL="${BACKEND_URL:-http://trisla-portal-backend:8001/api/v1}"' >> /entrypoint.sh && \
    echo 'cat > /usr/share/nginx/html/env.js << EOF' >> /entrypoint.sh && \
    echo 'window.__ENV__ = {' >> /entrypoint.sh && \
    echo '  BACKEND_URL: "'"'"'${BACKEND_URL}'"'"'"' >> /entrypoint.sh && \
    echo '};' >> /entrypoint.sh && \
    echo 'EOF' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Configuração nginx para servir Next.js e env.js
RUN echo 'server {' > /etc/nginx/conf.d/default.conf && \
    echo '    listen 80;' >> /etc/nginx/conf.d/default.conf && \
    echo '    server_name _;' >> /etc/nginx/conf.d/default.conf && \
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    index index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Servir env.js' >> /etc/nginx/conf.d/default.conf && \
    echo '    location = /env.js {' >> /etc/nginx/conf.d/default.conf && \
    echo '        add_header Content-Type application/javascript;' >> /etc/nginx/conf.d/default.conf && \
    echo '        add_header Cache-Control "no-cache";' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Arquivos estáticos do Next.js' >> /etc/nginx/conf.d/default.conf && \
    echo '    location /_next/static {' >> /etc/nginx/conf.d/default.conf && \
    echo '        alias /usr/share/nginx/html/_next/static;' >> /etc/nginx/conf.d/default.conf && \
    echo '        add_header Cache-Control "public, max-age=31536000, immutable";' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Arquivos públicos' >> /etc/nginx/conf.d/default.conf && \
    echo '    location /public {' >> /etc/nginx/conf.d/default.conf && \
    echo '        alias /usr/share/nginx/html/public;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Proxy para API backend' >> /etc/nginx/conf.d/default.conf && \
    echo '    location /api {' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_pass http://trisla-portal-backend:8001;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header Host $host;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header X-Real-IP $remote_addr;' >> /etc/nginx/conf.d/default.conf && \
    echo '        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '' >> /etc/nginx/conf.d/default.conf && \
    echo '    # Servir aplicação Next.js' >> /etc/nginx/conf.d/default.conf && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf && \
    echo '    }' >> /etc/nginx/conf.d/default.conf && \
    echo '}' >> /etc/nginx/conf.d/default.conf

# Variável de ambiente padrão (pode ser sobrescrita via Helm)
ENV BACKEND_URL=http://trisla-portal-backend:8001/api/v1

# Expor porta
EXPOSE 80

# Usar entrypoint customizado
ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

