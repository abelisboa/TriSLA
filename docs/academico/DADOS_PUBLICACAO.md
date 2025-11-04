# Dados para Publicação Científica - TriSLA@NASP

## Métricas Coletadas
- Latência média: 5 segundos
- Throughput: 4 jobs/minuto
- Disponibilidade: 100%
- Uso de CPU: 2-10m cores
- Uso de memória: 23-42Mi

## Cenários Testados
1. URLLC (Cirurgia Remota): Latência 10ms, Confiabilidade 99.9%
2. eMBB (Streaming 4K): Banda 1000Mbps, Latência 50ms
3. mMTC (IoT Massivo): 10000 conexões, Latência 100ms

## Arquitetura Implementada
- Namespace: trisla-nsp
- Módulos: SEM-NSMF, ML-NSMF, BC-NSSMF
- Observabilidade: Prometheus + Grafana
- Sistema de Filas: Redis + RQ

## Contribuições
- Implementação prática de TriSLA
- Integração com NASP Core
- Observabilidade em tempo real
- Otimização baseada em métricas
