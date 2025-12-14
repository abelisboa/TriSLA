# ---- Build Stage ----
FROM node:18-alpine AS build

WORKDIR /app

# Aceitar ARG para NEXT_PUBLIC_TRISLA_API_BASE_URL (browser/client-side)
# Default Kubernetes-safe: usa Service interno (pode ser sobrescrito no build)
# Para desenvolvimento local via túnel SSH, passar: --build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1
ARG NEXT_PUBLIC_TRISLA_API_BASE_URL=http://trisla-portal-backend:8001/api/v1
ENV NEXT_PUBLIC_TRISLA_API_BASE_URL=$NEXT_PUBLIC_TRISLA_API_BASE_URL

# Aceitar ARG para INTERNAL_API_URL (SSR/server-side - cluster interno)
ARG INTERNAL_API_URL=http://trisla-portal-backend:8001/api/v1
ENV INTERNAL_API_URL=$INTERNAL_API_URL

COPY package.json package-lock.json ./

RUN npm install

COPY . .

RUN npm run build

# Preparar public para cópia condicional no runner
# Se public não existir, criar um diretório vazio para evitar erro no COPY
RUN if [ ! -d /app/public ] || [ ! "$(ls -A /app/public 2>/dev/null)" ]; then \
      mkdir -p /app/public && \
      touch /app/public/.keep; \
    fi

# ---- Runner Stage ----
FROM node:18-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copiar arquivos standalone do build
COPY --from=build /app/.next/standalone ./standalone
COPY --from=build /app/.next/static ./standalone/.next/static

# Public é opcional — copiar sempre (diretório vazio se não existir)
COPY --from=build /app/public ./standalone/public

# Remover arquivo .keep se existir (indicava diretório vazio)
RUN rm -f ./standalone/public/.keep 2>/dev/null || true

EXPOSE 3000

CMD ["node", "standalone/server.js"]
