# ==========================================
# 🧩 TriSLA Portal — Docker Compose Repair + Hybrid NASP Fix
# ==========================================
# Corrige formatação YAML e garante compatibilidade com modo híbrido NASP.
# ==========================================

echo "🛠️ Repairing docker-compose.yaml..."

# Backup preventivo
cp docker-compose.yaml docker-compose.bak_$(date +%H%M%S)

# Reescrever arquivo limpo e padronizado
cat > docker-compose.yaml <<'YAML'
services:
  api:
    build: ./apps/api
    container_name: trisla-api
    ports:
      - "8000:8000"
    environment:
      - TRISLA_MODE=auto
      - PROM_URL=http://nasp-prometheus.monitoring.svc.cluster.local:9090/api/v1/query
    depends_on:
      - redis
    networks:
      - trisla-net

  ui:
    build: ./apps/ui
    container_name: trisla-ui
    ports:
      - "5173:80"
    depends_on:
      - api
    networks:
      - trisla-net

  worker:
    build: ./apps/api
    container_name: trisla-worker
    command: ["python", "-m", "jobs.worker"]
    depends_on:
      - redis
    networks:
      - trisla-net

  redis:
    image: redis:7
    container_name: trisla-redis
    ports:
      - "6379:6379"
    networks:
      - trisla-net

  prometheus:
    image: prom/prometheus:latest
    container_name: trisla-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - trisla-net

networks:
  trisla-net:
    driver: bridge
YAML

echo "✅ docker-compose.yaml successfully repaired."
echo "➡️  Next steps:"
echo "   1️⃣ docker compose build api ui"
echo "   2️⃣ docker compose up -d"
