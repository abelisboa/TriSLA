#!/bin/bash
# Script para configurar port-forward do Grafana em background

echo "Configurando port-forward do Grafana..."

# Matar port-forwards anteriores na porta 3000
pkill -f "kubectl port-forward.*3000" || true
sleep 1

# Configurar port-forward em background
nohup kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 > /tmp/grafana-pf.log 2>&1 &
PORT_FORWARD_PID=$!

sleep 3

# Verificar se está funcionando
if curl -f -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Port-forward configurado com sucesso!"
    echo ""
    echo "PID: $PORT_FORWARD_PID"
    echo "Logs: /tmp/grafana-pf.log"
    echo ""
    echo "🌐 Acesse o Grafana:"
    echo "   http://localhost:3000"
    echo ""
    echo "📊 Dashboard TriSLA:"
    echo "   http://localhost:3000/d/b8468b62-2aea-4261-9807-3979303485f0/trisla-portal-overview"
    echo ""
    echo "🔐 Credenciais:"
    echo "   Usuário: admin"
    echo "   Senha: C30zAwgGdxm4JKUuNEK3WlUeBw765RplgDApTFFc"
    echo ""
    echo "📝 Para parar o port-forward:"
    echo "   kill $PORT_FORWARD_PID"
    echo "   ou"
    echo "   pkill -f 'kubectl port-forward.*3000'"
else
    echo "❌ Erro ao configurar port-forward"
    echo "Verificar logs: cat /tmp/grafana-pf.log"
    exit 1
fi




