#!/bin/sh
set -e

echo "=== TriSLA UI Dashboard Entrypoint ==="

# Aguardar DNS estar disponível
echo "[1/3] Aguardando DNS estar disponível..."
RESOLVER=${NGINX_RESOLVER:-kube-dns.kube-system.svc.cluster.local}
# Se resolver é um IP (Docker: 127.0.0.11), não tentar nslookup
if echo "$RESOLVER" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "[1/3] Resolver é IP ($RESOLVER) - DNS do Docker, pulando verificação"
else
    for i in $(seq 1 30); do
        if nslookup "$RESOLVER" >/dev/null 2>&1; then
            echo "[1/3] DNS disponível após $i tentativas"
            break
        fi
        sleep 1
    done
fi

# Aguardar backend estar resolvível
echo "[2/3] Aguardando backend estar resolvível..."
BACKEND_HOST=${API_BACKEND_HOST}
# Se backend é localhost ou IP, não tentar nslookup (ambiente Docker/local)
if echo "$BACKEND_HOST" | grep -qE '^(localhost|127\.0\.0\.1|[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)$'; then
    echo "[2/3] Backend é localhost/IP ($BACKEND_HOST) - pulando verificação DNS"
else
    for i in $(seq 1 30); do
        if nslookup "$BACKEND_HOST" >/dev/null 2>&1; then
            echo "[2/3] Backend resolvível após $i tentativas"
            break
        fi
        sleep 1
    done
fi

# Modificar nginx.conf gerado para usar variáveis em runtime
echo "[3/3] Ajustando configuração nginx para resolver DNS dinamicamente..."
if [ -f /etc/nginx/conf.d/default.conf ]; then
    # Substituir proxy_pass direto por variável
    sed -i 's|proxy_pass http://${API_BACKEND_HOST}:${API_BACKEND_PORT};|set $backend ${API_BACKEND_HOST}:${API_BACKEND_PORT};\n        proxy_pass http://$backend;|' /etc/nginx/conf.d/default.conf
    # Adicionar resolver se não existir
    if ! grep -q "resolver" /etc/nginx/conf.d/default.conf; then
        sed -i "/^server {/a\    resolver ${NGINX_RESOLVER:-kube-dns.kube-system.svc.cluster.local} valid=10s;\n    resolver_timeout 5s;" /etc/nginx/conf.d/default.conf
    fi
fi

# Validar configuração nginx
echo "[3/3] Validando configuração nginx..."
for i in $(seq 1 5); do
    if nginx -t 2>&1; then
        echo "[3/3] Configuração nginx válida"
        break
    fi
    if [ $i -eq 5 ]; then
        echo "[3/3] ERRO: Falha na validação do nginx"
        cat /etc/nginx/conf.d/default.conf
        exit 1
    fi
    sleep 2
done

echo "=== Iniciando nginx ==="
# Executar entrypoint padrão do nginx
exec /docker-entrypoint.sh nginx -g 'daemon off;'

