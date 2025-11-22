# 26 – Adapter NASP

Prompt para integração TriSLA → NASP em PRODUÇÃO REAL.
# PROMPT — IMPLEMENTAÇÃO DO ADAPTADOR TRI-SLA ↔ NASP (I-07) - PRODUÇÃO REAL

**⚠️ OBJETIVO**: O adaptador deve conectar a **SERVIÇOS REAIS do NASP**, processar **DADOS REAIS** e executar **AÇÕES REAIS**. **NÃO usar mocks, stubs ou simulações em produção.**

Gerar:

1) Estrutura do adaptador para produção real
2) API REST I-07 conectando a serviços NASP reais:
   - Endpoints reais do NASP (RAN, Transport, Core controllers)
   - Autenticação real
   - Validação de conectividade com serviços reais
3) Payloads de entrada/saída (dados reais)
4) Mapeamento:
   - traceId (de requisições reais)
   - module (módulos reais do TriSLA)
   - métricas (métricas reais coletadas do NASP)
5) Coleta de métricas REAIS:
   - Métricas reais de dispositivos RAN
   - Métricas reais de transporte
   - Métricas reais do core
   - NÃO usar dados sintéticos
6) Execução de ações REAIS:
   - Modificar configurações reais
   - Aplicar políticas reais
   - Atualizar slices reais
   - NÃO simular ações
7) Logs OTLP (de operações reais)
8) Validação de produção real:
   - Verificar que está conectado a serviços reais
   - Detectar e alertar se em modo simulação
   - Validar que dados são reais
9) Testes unitários + integração (com serviços reais em ambiente de teste)
10) Código Python com flags de produção real

