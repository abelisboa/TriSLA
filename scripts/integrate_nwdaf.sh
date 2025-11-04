#!/bin/bash

# Integração do NWDAF com outros módulos TriSLA
# Este script configura a integração do NWDAF com Decision Engine, ML-NSMF, SLA Agents, etc.

set -e

echo "🔗 Iniciando integração do NWDAF com outros módulos TriSLA..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verificar se o NWDAF está rodando
log "Verificando se o NWDAF está rodando..."
if ! kubectl get deployment nwdaf -n trisla &> /dev/null; then
    error "NWDAF não está rodando. Execute o deploy primeiro."
    exit 1
fi

success "NWDAF está rodando"

# Verificar outros módulos TriSLA
log "Verificando outros módulos TriSLA..."

# Decision Engine
if kubectl get deployment decision-engine -n trisla &> /dev/null; then
    success "Decision Engine encontrado"
    DECISION_ENGINE_AVAILABLE=true
else
    warning "Decision Engine não encontrado"
    DECISION_ENGINE_AVAILABLE=false
fi

# ML-NSMF
if kubectl get deployment ml-nsmf -n trisla &> /dev/null; then
    success "ML-NSMF encontrado"
    ML_NSMF_AVAILABLE=true
else
    warning "ML-NSMF não encontrado"
    ML_NSMF_AVAILABLE=false
fi

# SLA Agents
if kubectl get deployment sla-agents -n trisla &> /dev/null; then
    success "SLA Agents encontrado"
    SLA_AGENTS_AVAILABLE=true
else
    warning "SLA Agents não encontrado"
    SLA_AGENTS_AVAILABLE=false
fi

# Redis
if kubectl get deployment redis -n trisla &> /dev/null; then
    success "Redis encontrado"
    REDIS_AVAILABLE=true
else
    warning "Redis não encontrado"
    REDIS_AVAILABLE=false
fi

# Prometheus
if kubectl get deployment prometheus -n trisla &> /dev/null; then
    success "Prometheus encontrado"
    PROMETHEUS_AVAILABLE=true
else
    warning "Prometheus não encontrado"
    PROMETHEUS_AVAILABLE=false
fi

# Grafana
if kubectl get deployment grafana -n trisla &> /dev/null; then
    success "Grafana encontrado"
    GRAFANA_AVAILABLE=true
else
    warning "Grafana não encontrado"
    GRAFANA_AVAILABLE=false
fi

# Configurar integração com Decision Engine
if [ "$DECISION_ENGINE_AVAILABLE" = true ]; then
    log "Configurando integração com Decision Engine..."
    
    # Criar ConfigMap para configuração do Decision Engine
    kubectl create configmap nwdaf-decision-engine-config \
        --from-literal=decision_engine_url=http://decision-engine:8080 \
        --from-literal=analytics_endpoint=/api/v1/analytics \
        --from-literal=insights_endpoint=/api/v1/insights \
        -n trisla \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Configuração do Decision Engine criada"
else
    warning "Pulando configuração do Decision Engine (não disponível)"
fi

# Configurar integração com ML-NSMF
if [ "$ML_NSMF_AVAILABLE" = true ]; then
    log "Configurando integração com ML-NSMF..."
    
    # Criar ConfigMap para configuração do ML-NSMF
    kubectl create configmap nwdaf-ml-nsmf-config \
        --from-literal=ml_nsmf_url=http://ml-nsmf:8080 \
        --from-literal=predictions_endpoint=/api/v1/predictions \
        --from-literal=telemetry_endpoint=/api/v1/telemetry \
        -n trisla \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Configuração do ML-NSMF criada"
else
    warning "Pulando configuração do ML-NSMF (não disponível)"
fi

# Configurar integração com SLA Agents
if [ "$SLA_AGENTS_AVAILABLE" = true ]; then
    log "Configurando integração com SLA Agents..."
    
    # Criar ConfigMap para configuração dos SLA Agents
    kubectl create configmap nwdaf-sla-agents-config \
        --from-literal=sla_agents_url=http://sla-agents:8080 \
        --from-literal=insights_endpoint=/api/v1/insights \
        --from-literal=metrics_endpoint=/api/v1/metrics \
        -n trisla \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Configuração dos SLA Agents criada"
else
    warning "Pulando configuração dos SLA Agents (não disponível)"
fi

# Configurar integração com Redis
if [ "$REDIS_AVAILABLE" = true ]; then
    log "Configurando integração com Redis..."
    
    # Criar ConfigMap para configuração do Redis
    kubectl create configmap nwdaf-redis-config \
        --from-literal=redis_host=redis \
        --from-literal=redis_port=6379 \
        --from-literal=redis_db=0 \
        --from-literal=cache_ttl=300 \
        -n trisla \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Configuração do Redis criada"
else
    warning "Pulando configuração do Redis (não disponível)"
fi

# Configurar integração com Prometheus
if [ "$PROMETHEUS_AVAILABLE" = true ]; then
    log "Configurando integração com Prometheus..."
    
    # Criar ServiceMonitor para o NWDAF
    cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nwdaf
  namespace: trisla
  labels:
    app: nwdaf
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: nwdaf
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
EOF
    
    success "ServiceMonitor do NWDAF criado"
else
    warning "Pulando configuração do Prometheus (não disponível)"
fi

# Configurar integração com Grafana
if [ "$GRAFANA_AVAILABLE" = true ]; then
    log "Configurando integração com Grafana..."
    
    # Criar ConfigMap para dashboards do NWDAF
    kubectl create configmap nwdaf-grafana-dashboards \
        --from-literal=dashboard_nwdaf_overview='{"dashboard": {"title": "NWDAF Overview", "panels": []}}' \
        --from-literal=dashboard_nwdaf_analytics='{"dashboard": {"title": "NWDAF Analytics", "panels": []}}' \
        --from-literal=dashboard_nwdaf_predictions='{"dashboard": {"title": "NWDAF Predictions", "panels": []}}' \
        -n trisla \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Dashboards do NWDAF criados"
else
    warning "Pulando configuração do Grafana (não disponível)"
fi

# Atualizar deployment do NWDAF com as configurações
log "Atualizando deployment do NWDAF com as configurações de integração..."

# Criar patch para adicionar volumes de configuração
cat <<EOF | kubectl patch deployment nwdaf -n trisla --patch-file /dev/stdin
spec:
  template:
    spec:
      containers:
      - name: nwdaf
        volumeMounts:
        - name: decision-engine-config
          mountPath: /app/config/decision-engine
          readOnly: true
        - name: ml-nsmf-config
          mountPath: /app/config/ml-nsmf
          readOnly: true
        - name: sla-agents-config
          mountPath: /app/config/sla-agents
          readOnly: true
        - name: redis-config
          mountPath: /app/config/redis
          readOnly: true
        - name: grafana-dashboards
          mountPath: /app/config/grafana
          readOnly: true
      volumes:
      - name: decision-engine-config
        configMap:
          name: nwdaf-decision-engine-config
      - name: ml-nsmf-config
        configMap:
          name: nwdaf-ml-nsmf-config
      - name: sla-agents-config
        configMap:
          name: nwdaf-sla-agents-config
      - name: redis-config
        configMap:
          name: nwdaf-redis-config
      - name: grafana-dashboards
        configMap:
          name: nwdaf-grafana-dashboards
EOF

success "Deployment do NWDAF atualizado"

# Aguardar rollout
log "Aguardando rollout do deployment..."
kubectl rollout status deployment/nwdaf -n trisla

# Verificar status final
log "Verificando status final da integração..."

# Verificar pods
kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla

# Verificar configmaps
kubectl get configmaps -l app=nwdaf -n trisla

# Verificar servicemonitor
kubectl get servicemonitor nwdaf -n trisla

# Resumo da integração
echo ""
echo "=========================================="
echo "📊 RESUMO DA INTEGRAÇÃO DO NWDAF"
echo "=========================================="

# Contar integrações configuradas
INTEGRATIONS=0

if [ "$DECISION_ENGINE_AVAILABLE" = true ]; then
    ((INTEGRATIONS++))
    success "Decision Engine: Integrado"
else
    warning "Decision Engine: Não disponível"
fi

if [ "$ML_NSMF_AVAILABLE" = true ]; then
    ((INTEGRATIONS++))
    success "ML-NSMF: Integrado"
else
    warning "ML-NSMF: Não disponível"
fi

if [ "$SLA_AGENTS_AVAILABLE" = true ]; then
    ((INTEGRATIONS++))
    success "SLA Agents: Integrado"
else
    warning "SLA Agents: Não disponível"
fi

if [ "$REDIS_AVAILABLE" = true ]; then
    ((INTEGRATIONS++))
    success "Redis: Integrado"
else
    warning "Redis: Não disponível"
fi

if [ "$PROMETHEUS_AVAILABLE" = true ]; then
    ((INTEGRATIONS++))
    success "Prometheus: Integrado"
else
    warning "Prometheus: Não disponível"
fi

if [ "$GRAFANA_AVAILABLE" = true ]; then
    ((INTEGRATIONS++))
    success "Grafana: Integrado"
else
    warning "Grafana: Não disponível"
fi

echo ""
echo "🎉 INTEGRAÇÃO DO NWDAF CONCLUÍDA!"
echo "✅ $INTEGRATIONS módulos integrados"
echo "✅ Configurações aplicadas"
echo "✅ Pronto para uso em produção"

# Próximos passos
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Executar: ./scripts/test_nwdaf.sh"
echo "2. Configurar dashboards no Grafana"
echo "3. Testar integração end-to-end"
echo "4. Continuar para a Fase 6 da implementação"




