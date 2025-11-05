#!/bin/bash
set -e

echo "Validating TriSLA production endpoints..."

NODE_IP=${1:-"localhost"}

echo "Testing SEM-NSMF (Port 8081)..."
curl -X POST "http://${NODE_IP}:8081/semantic/interpret" \
  -H "Content-Type: application/json" \
  -d '{"descricao": "Criar slice URLLC com prioridade alta e latência 5ms"}' \
  || echo "SEM-NSMF endpoint not responding"

echo -e "\nTesting ML-NSMF (Port 8080)..."
curl -X POST "http://${NODE_IP}:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"slice_type": "URLLC", "priority": "alta", "qos": {"latency": 5.0}}' \
  || echo "ML-NSMF endpoint not responding"

echo -e "\nTesting BC-NSSMF (Port 8051)..."
curl -X POST "http://${NODE_IP}:8051/contracts/register" \
  -H "Content-Type: application/json" \
  -d '{"sla_id": "SLA-TEST-001", "slice_type": "URLLC", "decision": "ACCEPT", "compliance": "0.95"}' \
  || echo "BC-NSSMF endpoint not responding"

echo -e "\nTesting NWDAF-like (Port 8090)..."
curl "http://${NODE_IP}:8090/metrics" \
  || echo "NWDAF-like endpoint not responding"

echo -e "\nValidation complete!"
