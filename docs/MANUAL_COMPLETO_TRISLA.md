# 📖 MANUAL COMPLETO DO TRISLA
## Guia Teórico e Prático do Ecossistema 5G/O-RAN, Network Slicing e SLA

**Autor:** Abel José Rodrigues Lisboa  
**Versão:** 1.0  
**Data:** 2025-12-05  
**Licença:** MIT

---

## 📋 SUMÁRIO

### PARTE I: FUNDAMENTAÇÃO TEÓRICA

1. [Capítulo 1: Introdução ao 5G e O-RAN](#capítulo-1-introdução-ao-5g-e-o-ran)
2. [Capítulo 2: Network Slicing - Conceitos e Aplicações](#capítulo-2-network-slicing)
3. [Capítulo 3: Service Level Agreements (SLA)](#capítulo-3-service-level-agreements)
4. [Capítulo 4: Inteligência Artificial e Machine Learning](#capítulo-4-inteligência-artificial)
5. [Capítulo 5: Ontologias Semânticas](#capítulo-5-ontologias-semânticas)
6. [Capítulo 6: Blockchain e Smart Contracts](#capítulo-6-blockchain)
7. [Capítulo 7: Observabilidade e Monitoramento](#capítulo-7-observabilidade)

### PARTE II: ARQUITETURA TRISLA

8. [Capítulo 8: Visão Geral da Arquitetura TriSLA](#capítulo-8-arquitetura-trisla)
9. [Capítulo 9: Módulo SEM-CSMF - Interpretação Semântica](#capítulo-9-sem-csmf)
10. [Capítulo 10: Módulo ML-NSMF - Predição com IA](#capítulo-10-ml-nsmf)
11. [Capítulo 11: Decision Engine - Motor de Decisão](#capítulo-11-decision-engine)
12. [Capítulo 12: BC-NSSMF - Blockchain](#capítulo-12-bc-nssmf)
13. [Capítulo 13: SLA-Agent Layer - Agentes Federados](#capítulo-13-sla-agent-layer)
14. [Capítulo 14: NASP Adapter - Integração](#capítulo-14-nasp-adapter)
15. [Capítulo 15: UI Dashboard - Interface Visual](#capítulo-15-ui-dashboard)

### PARTE III: OPERAÇÃO E MANUTENÇÃO

16. [Capítulo 16: Deploy e Configuração](#capítulo-16-deploy)
17. [Capítulo 17: Monitoramento e Observabilidade](#capítulo-17-monitoramento)
18. [Capítulo 18: Troubleshooting](#capítulo-18-troubleshooting)
19. [Capítulo 19: Casos de Uso Práticos](#capítulo-19-casos-de-uso)
20. [Capítulo 20: Futuras Evoluções](#capítulo-20-futuras-evoluções)

---

## 📚 PARTE I: FUNDAMENTAÇÃO TEÓRICA

### Capítulo 1: Introdução ao 5G e O-RAN

#### 1.1 O que é 5G?

**5G** (quinta geração de redes móveis) representa uma evolução revolucionária das redes de telecomunicações. Diferente das gerações anteriores (2G, 3G, 4G), o 5G não é apenas sobre velocidade de internet mais rápida. É sobre criar uma **infraestrutura de comunicação inteligente e flexível** que pode atender a uma ampla gama de necessidades.

**Características Principais do 5G:**

1. **Alta Velocidade (eMBB - Enhanced Mobile Broadband)**
   - Velocidades de até 20 Gbps (teórico)
   - Permite streaming de vídeo 4K/8K em tempo real
   - Download de arquivos grandes em segundos

2. **Baixa Latência (URLLC - Ultra-Reliable Low-Latency Communication)**
   - Latência de menos de 1 milissegundo
   - Essencial para aplicações críticas:
     - Cirurgia remota
     - Veículos autônomos
     - Controle industrial em tempo real

3. **Massiva Conectividade (mMTC - Massive Machine-Type Communication)**
   - Suporte a milhões de dispositivos por km²
   - Internet das Coisas (IoT) em escala
   - Cidades inteligentes

**Analogia Simples:**
Imagine que o 4G é como uma estrada de duas pistas onde todos os carros (dados) precisam seguir na mesma velocidade. O 5G é como uma **cidade inteligente com múltiplas estradas especializadas**:
- Uma estrada super rápida para vídeos (eMBB)
- Uma estrada com semáforos perfeitos para cirurgia remota (URLLC)
- Uma estrada larga para milhões de sensores (mMTC)

#### 1.2 O que é O-RAN?

**O-RAN** (Open Radio Access Network) é uma **arquitetura aberta** para redes de acesso de rádio. Tradicionalmente, as redes de telecomunicações eram "caixas pretas" - você comprava equipamento de um único fornecedor e ficava preso a ele.

**Princípios do O-RAN:**

1. **Abertura**
   - Interfaces padronizadas entre componentes
   - Múltiplos fornecedores podem interoperar
   - Reduz dependência de fornecedor único

2. **Inteligência**
   - RAN Intelligent Controller (RIC)
   - Aplicações (xApps, rApps) podem otimizar a rede
   - Machine Learning para otimização automática

3. **Virtualização**
   - Software rodando em hardware genérico
   - Reduz custos de infraestrutura
   - Facilita atualizações e manutenção

**Analogia:**
Pense em smartphones. Antes, cada marca tinha seu próprio sistema fechado. Agora, temos Android (aberto) onde diferentes fabricantes podem criar dispositivos compatíveis. O-RAN faz o mesmo para redes de telecomunicações.

#### 1.3 Por que 5G e O-RAN são Importantes?

**Para Operadoras:**
- **Redução de Custos**: Hardware genérico é mais barato
- **Flexibilidade**: Escolher melhores componentes de diferentes fornecedores
- **Inovação**: Desenvolver soluções customizadas

**Para Usuários:**
- **Melhor Experiência**: Aplicações que antes eram impossíveis
- **Novos Serviços**: Realidade aumentada, veículos autônomos, etc.
- **Confiabilidade**: Redes mais robustas e inteligentes

**Para Desenvolvedores:**
- **APIs Abertas**: Criar aplicações que interagem com a rede
- **Oportunidades**: Novos modelos de negócio baseados em 5G

---

### Capítulo 2: Network Slicing

#### 2.1 O Conceito de Network Slicing

**Network Slicing** (Fatiamento de Rede) é uma das tecnologias mais revolucionárias do 5G. Permite **criar múltiplas redes virtuais** sobre a mesma infraestrutura física.

**Analogia do Prédio:**
Imagine um prédio comercial:
- **Infraestrutura Física**: O prédio em si (5G)
- **Andares Especializados**: Cada andar serve um propósito diferente
  - Andar 1: Loja de roupas (eMBB - vídeo streaming)
  - Andar 2: Hospital (URLLC - baixa latência)
  - Andar 3: Escritórios (mMTC - muitos dispositivos)

Cada "andar" (slice) tem suas próprias regras, recursos e garantias, mas compartilha a mesma infraestrutura física.

#### 2.2 Como Funciona o Network Slicing?

**Processo em 3 Etapas:**

1. **Solicitação (Intent)**
   - Um tenant (empresa, aplicação) solicita um slice
   - Exemplo: "Preciso de um slice para cirurgia remota com latência < 5ms"

2. **Criação (Provisioning)**
   - O sistema cria uma "fatia virtual" da rede
   - Aloca recursos específicos (banda, processamento, etc.)
   - Configura regras de qualidade de serviço

3. **Operação (Assurance)**
   - Monitora continuamente o slice
   - Garante que os requisitos sejam atendidos
   - Ajusta recursos automaticamente se necessário

**Exemplo Prático:**

**Cenário:** Um hospital quer fazer cirurgia remota

1. **Intent**: "Slice para cirurgia remota, latência < 1ms, confiabilidade 99.999%"
2. **Criação**: Sistema cria slice dedicado com:
   - Banda garantida: 100 Mbps
   - Prioridade máxima no roteamento
   - Redundância automática
3. **Operação**: Sistema monitora continuamente:
   - Se latência > 1ms → Alerta e ajusta
   - Se conexão cai → Ativa backup automaticamente

#### 2.3 Benefícios do Network Slicing

**Para Operadoras:**
- **Otimização de Recursos**: Usa infraestrutura de forma eficiente
- **Novos Modelos de Negócio**: Vende slices como serviço
- **Diferenciação**: Oferece serviços especializados

**Para Tenants:**
- **Garantias de Qualidade**: SLA específico para sua aplicação
- **Custo-Efetividade**: Paga apenas pelo que precisa
- **Flexibilidade**: Ajusta recursos conforme demanda

**Para Usuários Finais:**
- **Melhor Experiência**: Cada aplicação tem recursos otimizados
- **Confiabilidade**: Aplicações críticas não são afetadas por tráfego normal

---

### Capítulo 3: Service Level Agreements (SLA)

#### 3.1 O que é um SLA?

**SLA (Service Level Agreement)** é um **contrato formal** entre um provedor de serviço e um cliente que define:
- **O que** será entregue
- **Como** será medido
- **Consequências** se não for cumprido

**Exemplo do Dia a Dia:**
Quando você contrata internet residencial:
- **SLA**: "Velocidade de 100 Mbps, disponibilidade 99.9%"
- **Medição**: Testes de velocidade mensais
- **Consequência**: Se não cumprir, desconto na fatura

#### 3.2 Componentes de um SLA

**1. Métricas de Performance (KPIs)**

**Latência:**
- **O que é**: Tempo que leva para um dado ir do ponto A ao B
- **Exemplo**: 5ms significa que em 5 milissegundos o dado chega
- **Por que importa**: Para cirurgia remota, cada milissegundo conta

**Throughput (Taxa de Transferência):**
- **O que é**: Quantidade de dados por segundo
- **Exemplo**: 100 Mbps = 100 milhões de bits por segundo
- **Por que importa**: Determina quantos vídeos você pode assistir simultaneamente

**Disponibilidade:**
- **O que é**: Porcentagem do tempo que o serviço está funcionando
- **Exemplo**: 99.9% = serviço disponível 99.9% do tempo (8.76 horas de downtime por ano)
- **Por que importa**: Para aplicações críticas, cada minuto de downtime custa dinheiro

**Confiabilidade:**
- **O que é**: Probabilidade de o serviço funcionar corretamente
- **Exemplo**: 99.999% = apenas 1 falha em 100.000 tentativas
- **Por que importa**: Para sistemas críticos, falhas podem ser fatais

**2. SLOs (Service Level Objectives)**

**SLO** é o **objetivo específico** dentro do SLA:
- SLA: "Serviço de alta qualidade"
- SLO: "Latência < 5ms, disponibilidade > 99.9%"

**3. SLIs (Service Level Indicators)**

**SLI** é a **métrica que mede** o SLO:
- SLO: "Latência < 5ms"
- SLI: "Latência média medida: 4.2ms"

#### 3.3 Desafios dos SLAs em 5G

**Complexidade:**
- Múltiplos domínios (RAN, Transport, Core)
- Múltiplos slices com requisitos diferentes
- Recursos compartilhados

**Dinamicidade:**
- Condições de rede mudam constantemente
- Demanda varia ao longo do tempo
- Requer ajustes automáticos

**Garantia:**
- Como garantir que um slice atenderá seus requisitos?
- Como prever problemas antes que aconteçam?
- Como corrigir automaticamente?

**É aqui que o TriSLA entra!**

---

### Capítulo 4: Inteligência Artificial e Machine Learning

#### 4.1 IA e ML: Conceitos Básicos

**Inteligência Artificial (IA)** é a capacidade de máquinas **simularem inteligência humana**:
- Aprender com dados
- Reconhecer padrões
- Tomar decisões
- Melhorar com experiência

**Machine Learning (ML)** é um **subconjunto da IA** onde máquinas aprendem **automaticamente** a partir de dados, sem programação explícita.

**Analogia:**
- **Programação Tradicional**: Você ensina o computador passo a passo
  - "Se latência > 5ms, então alertar"
- **Machine Learning**: Você mostra exemplos e o computador aprende
  - Mostra 1000 casos de "latência alta = problema"
  - Computador aprende a identificar padrões sozinho

#### 4.2 Como ML Funciona no TriSLA

**Problema:**
Como saber se um Network Slice atenderá seus requisitos de SLA antes de criá-lo?

**Solução com ML:**

1. **Treinamento:**
   - Coleta dados históricos de slices
   - Exemplos: "Slice com configuração X teve latência Y"
   - Modelo aprende padrões

2. **Predição:**
   - Novo slice é proposto
   - Modelo analisa características
   - Prediz: "Este slice terá latência de 4.2ms com 92% de confiança"

3. **Explicação (XAI):**
   - Modelo explica **por que** fez essa predição
   - "Latência baixa porque densidade de células é alta"
   - "Risco médio porque carga de rede está aumentando"

#### 4.3 Random Forest: O Algoritmo do TriSLA

**Random Forest** é um algoritmo de ML que funciona como um **comitê de especialistas**:

**Analogia:**
Imagine que você quer prever se vai chover:
- **Árvore 1**: Olha temperatura → "Vai chover"
- **Árvore 2**: Olha umidade → "Não vai chover"
- **Árvore 3**: Olha pressão → "Vai chover"
- **Árvore 4**: Olha vento → "Vai chover"
- **Resultado**: 3 de 4 dizem que vai chover → **Vai chover**

**No TriSLA:**
- **Árvore 1**: Analisa latência → "SLA viável"
- **Árvore 2**: Analisa throughput → "SLA viável"
- **Árvore 3**: Analisa confiabilidade → "SLA não viável"
- **Resultado**: Maioria diz viável → **Aprovar slice**

**Vantagens:**
- **Precisão**: Múltiplas opiniões são mais confiáveis
- **Robustez**: Se uma árvore erra, outras compensam
- **Explicabilidade**: Pode ver por que cada árvore decidiu

#### 4.4 XAI (Explainable AI) - IA Explicável

**Por que XAI é Importante?**

Em aplicações críticas (como cirurgia remota), não basta o modelo dizer "vai funcionar". Precisamos saber **por quê**.

**Exemplo:**
- **Sem XAI**: "SLA viável com 90% de confiança" ❓
- **Com XAI**: 
  - "SLA viável porque:
    - Densidade de células é alta (garante latência baixa)
    - UPF está no edge (reduz latência de transporte)
    - Carga de rede está baixa (recursos disponíveis)
  - Riscos:
    - Carga pode aumentar (monitorar)"

**No TriSLA:**
- Modelo prediz viabilidade
- XAI explica fatores principais
- Operador entende e confia na decisão

---

### Capítulo 5: Ontologias Semânticas

#### 5.1 O que são Ontologias?

**Ontologia** é uma **representação formal do conhecimento** sobre um domínio. É como um "dicionário inteligente" que define:
- **Conceitos**: O que são as coisas
- **Relações**: Como as coisas se relacionam
- **Regras**: O que pode e não pode acontecer

**Analogia:**
Pense em um dicionário tradicional:
- **Palavra**: "Carro"
- **Definição**: "Veículo com 4 rodas"

Uma ontologia vai além:
- **Conceito**: "Carro"
- **É um tipo de**: "Veículo"
- **Tem propriedade**: "Número de rodas = 4"
- **Pode fazer**: "Transportar pessoas"
- **Relaciona-se com**: "Estrada", "Motorista", "Combustível"

#### 5.2 Por que Ontologias no TriSLA?

**Problema:**
Como converter uma intenção humana ("Quero um slice para cirurgia remota") em configuração técnica complexa?

**Solução com Ontologia:**

1. **Intenção Humana:**
   - "Slice para cirurgia remota"
   - "Latência muito baixa"
   - "Alta confiabilidade"

2. **Ontologia Entende:**
   - "Cirurgia remota" → Requisitos específicos
   - "Latência muito baixa" → < 1ms
   - "Alta confiabilidade" → 99.999%

3. **Gera Configuração Técnica:**
   - Densidade de células: alta
   - UPF location: edge
   - Redundância: ativa
   - Prioridade: máxima

#### 5.3 OWL (Web Ontology Language)

**OWL** é a linguagem padrão para criar ontologias. No TriSLA, usamos **OWL 2.0** em formato **Turtle (.ttl)**.

**Exemplo Simplificado:**

```turtle
# Definir que "CirurgiaRemota" é um tipo de "AplicacaoCritica"
:CirurgiaRemota a :AplicacaoCritica ;
    :requerLatencia :LatenciaMuitoBaixa ;
    :requerConfiabilidade :ConfiabilidadeMuitoAlta .

# Definir valores específicos
:LatenciaMuitoBaixa :valorMaximo "1"^^xsd:integer ;
    :unidade "ms" .

:ConfiabilidadeMuitoAlta :valorMinimo "0.99999"^^xsd:decimal .
```

**No TriSLA:**
- Ontologia define todos os conceitos de Network Slicing
- SEM-CSMF usa ontologia para interpretar intenções
- Gera NEST (Network Slice Template) baseado em regras semânticas

---

### Capítulo 6: Blockchain e Smart Contracts

#### 6.1 O que é Blockchain?

**Blockchain** é uma **tecnologia de registro distribuído** onde informações são armazenadas em "blocos" que são:
- **Imutáveis**: Não podem ser alterados depois de criados
- **Distribuídos**: Múltiplas cópias em diferentes lugares
- **Transparentes**: Todos podem ver (mas não alterar)

**Analogia:**
Imagine um livro de registros público:
- Cada página (bloco) contém transações
- Páginas são numeradas e ligadas
- Múltiplas cópias existem em diferentes lugares
- Se alguém tentar alterar uma página, outras cópias detectam

#### 6.2 Por que Blockchain no TriSLA?

**Problema:**
Como garantir que um SLA foi realmente criado e não pode ser alterado depois?

**Solução com Blockchain:**

1. **Registro Imutável:**
   - Quando um SLA é aprovado, é registrado no blockchain
   - Hash único identifica o registro
   - Não pode ser alterado ou deletado

2. **Auditoria:**
   - Qualquer pessoa pode verificar o registro
   - Histórico completo de todos os SLAs
   - Prova de que um SLA existiu em determinado momento

3. **Conformidade:**
   - Reguladores podem verificar compliance
   - Tenants podem provar que SLA foi acordado
   - Operadora pode provar que cumpriu compromissos

#### 6.3 Smart Contracts

**Smart Contract** é um **programa que executa automaticamente** quando condições são atendidas.

**Analogia:**
Pense em uma máquina de venda automática:
- Você coloca dinheiro (condição)
- Máquina libera produto (ação automática)
- Não precisa de pessoa intermediária

**No TriSLA:**

**Smart Contract: SLARegistry**

```solidity
// Quando um SLA é aprovado, registra automaticamente
function registerSLA(
    string memory intentId,
    uint256 latencyMs,
    uint256 throughputMbps
) public {
    // Registra no blockchain
    slas[intentId] = SLA({
        latencyMs: latencyMs,
        throughputMbps: throughputMbps,
        timestamp: block.timestamp,
        isActive: true
    });
    
    // Emite evento (todos podem ver)
    emit SLARegistered(intentId, block.timestamp);
}
```

**Benefícios:**
- **Automação**: Registro automático, sem intervenção manual
- **Confiabilidade**: Código executado exatamente como escrito
- **Transparência**: Qualquer um pode ver o código e os registros

---

### Capítulo 7: Observabilidade e Monitoramento

#### 7.1 O que é Observabilidade?

**Observabilidade** é a capacidade de **entender o estado interno de um sistema** através de suas saídas externas.

**Três Pilares da Observabilidade:**

1. **Métricas (Metrics)**
   - Números que medem comportamento
   - Exemplo: "Latência média: 4.2ms"
   - Exemplo: "Requisições por segundo: 1000"

2. **Logs**
   - Registros de eventos
   - Exemplo: "2025-12-05 10:00:00 - Intent processado: intent-123"

3. **Traces (Rastreamento)**
   - Seguir uma requisição através do sistema
   - Exemplo: "Requisição X passou por: SEM-CSMF → ML-NSMF → Decision Engine"

**Analogia:**
Pense em um carro:
- **Métricas**: Velocímetro, tacômetro, temperatura
- **Logs**: Histórico de manutenções
- **Traces**: GPS mostra rota completa

#### 7.2 Prometheus: Coleta de Métricas

**Prometheus** é um sistema de **coleta e armazenamento de métricas**.

**Como Funciona:**

1. **Exposição:**
   - Cada módulo expõe métricas em `/metrics`
   - Formato padrão legível por humanos

2. **Coleta (Scraping):**
   - Prometheus "raspa" métricas periodicamente
   - Armazena em banco de dados de séries temporais

3. **Consulta:**
   - Linguagem de consulta (PromQL)
   - Exemplo: "Qual a latência média nos últimos 5 minutos?"

**No TriSLA:**
- Cada módulo expõe métricas
- ServiceMonitors configuram coleta automática
- Prometheus armazena e permite consultas

#### 7.3 OpenTelemetry: Rastreamento Distribuído

**OpenTelemetry** é um padrão para **coleta de traces** em sistemas distribuídos.

**Problema:**
Em sistemas complexos, uma requisição passa por múltiplos serviços. Como rastrear?

**Solução:**
- Cada serviço cria um "span" (trecho)
- Spans são conectados formando um "trace" (rastreamento completo)
- Contexto é propagado entre serviços

**Exemplo Visual:**

```
Requisição: Criar Slice
│
├─ SEM-CSMF (100ms)
│  └─ Parse Intent (50ms)
│  └─ Generate NEST (50ms)
│
├─ ML-NSMF (200ms)
│  └─ Extract Features (50ms)
│  └─ Predict (150ms)
│
└─ Decision Engine (50ms)
   └─ Evaluate Rules (50ms)
   
Total: 350ms
```

**No TriSLA:**
- Cada módulo cria spans
- Contexto propagado via HTTP headers
- OTEL Collector coleta e envia para Jaeger/Tempo
- Visualização completa do fluxo

---

## 🏗️ PARTE II: ARQUITETURA TRISLA

### Capítulo 8: Arquitetura TriSLA

#### 8.1 Visão Geral

O **TriSLA** (Trustworthy, Reasoned and Intelligent SLA Architecture) é uma arquitetura completa para **gerenciamento automatizado de SLAs** em redes 5G/O-RAN com Network Slicing.

**Princípios de Design:**

1. **Trustworthy (Confiável)**
   - Blockchain para registro imutável
   - Validação em múltiplas camadas
   - Transparência total

2. **Reasoned (Raciocinado)**
   - Decisões baseadas em regras claras
   - Explicações para cada decisão
   - Rastreabilidade completa

3. **Intelligent (Inteligente)**
   - Machine Learning para predição
   - Automação completa
   - Adaptação dinâmica

#### 8.2 Fluxo Completo

**Cenário: Tenant solicita slice para cirurgia remota**

```
1. INTENT (I-01)
   Tenant → SEM-CSMF
   "Quero slice para cirurgia remota, latência < 1ms"

2. INTERPRETAÇÃO SEMÂNTICA
   SEM-CSMF usa ontologia para entender
   Gera NEST (Network Slice Template)

3. PREDIÇÃO (I-02 → I-03)
   SEM-CSMF → ML-NSMF (via Kafka)
   ML-NSMF prediz viabilidade: "92% de confiança, latência prevista: 0.8ms"

4. DECISÃO (I-04)
   ML-NSMF → Decision Engine (via Kafka)
   Decision Engine avalia: "Aprovar com monitoramento"

5. REGISTRO BLOCKCHAIN (I-05)
   Decision Engine → BC-NSSMF (via gRPC)
   BC-NSSMF registra no blockchain

6. EXECUÇÃO (I-06 → I-07)
   Decision Engine → SLA-Agent Layer (via Kafka)
   SLA-Agent Layer → NASP Adapter (via REST)
   NASP Adapter provisiona slice no NASP

7. MONITORAMENTO
   Observabilidade coleta métricas e traces
   Prometheus armazena métricas
   Jaeger visualiza traces
```

#### 8.3 Módulos do TriSLA

**7 Módulos Principais:**

1. **SEM-CSMF**: Interpretação semântica
2. **ML-NSMF**: Predição com IA
3. **Decision Engine**: Motor de decisão
4. **BC-NSSMF**: Blockchain
5. **SLA-Agent Layer**: Agentes federados
6. **NASP Adapter**: Integração NASP
7. **UI Dashboard**: Interface visual

**Cada módulo:**
- É independente (pode ser desenvolvido separadamente)
- Comunica via APIs padronizadas
- Expõe métricas e traces
- Pode escalar horizontalmente

---

### Capítulo 9: SEM-CSMF - Interpretação Semântica

#### 9.1 Função do Módulo

O **SEM-CSMF** (Semantic CSMF) é o **ponto de entrada** do TriSLA. Recebe intenções de alto nível e as converte em configurações técnicas.

**Analogia:**
Pense em um tradutor profissional:
- **Entrada**: "Quero um slice rápido para vídeo"
- **Processamento**: Entende contexto, requisitos, preferências
- **Saída**: Configuração técnica detalhada

#### 9.2 Como Funciona

**1. Recepção de Intent**

```json
{
  "intent_id": "intent-001",
  "tenant_id": "hospital-abc",
  "service_type": "URLLC",
  "sla_requirements": {
    "latency": "1ms",
    "reliability": 0.99999
  }
}
```

**2. Parse Semântico**

- Ontologia OWL analisa o intent
- Identifica conceitos: "URLLC", "latency", "reliability"
- Entende relações: "URLLC requer latência baixa"

**3. Geração de NEST**

```json
{
  "nest_id": "nest-intent-001",
  "slice_type": "URLLC",
  "requirements": {
    "latency_ms": 1,
    "reliability": 0.99999
  },
  "domain_config": {
    "ran": {
      "cell_density": "high",
      "mimo_layers": 4
    },
    "core": {
      "upf_location": "edge"
    }
  }
}
```

#### 9.3 Tecnologias Utilizadas

- **FastAPI**: Framework web Python
- **OWLReady2**: Biblioteca para ontologias OWL
- **spaCy**: Processamento de linguagem natural
- **Prometheus**: Métricas
- **OpenTelemetry**: Traces

---

### Capítulo 10: ML-NSMF - Predição com IA

#### 10.1 Função do Módulo

O **ML-NSMF** (Machine Learning NSMF) **prediz a viabilidade** de um Network Slice atender seus requisitos de SLA antes de ser criado.

**Por que é Importante?**

Criar um slice e depois descobrir que não funciona é:
- **Caro**: Recursos desperdiçados
- **Lento**: Tempo perdido
- **Arriscado**: Pode afetar outros slices

**Solução:**
Predizer antes de criar!

#### 10.2 Como Funciona

**1. Recebe NEST**

```json
{
  "nest_id": "nest-001",
  "requirements": {
    "latency_ms": 1,
    "throughput_mbps": 100
  },
  "domain_config": {
    "ran": {"cell_density": "high"},
    "core": {"upf_location": "edge"}
  }
}
```

**2. Extrai Features**

- Converte configuração em números
- Exemplo: [latency_target, throughput_target, cell_density, ...]
- 13 features no total

**3. Predição**

- Modelo Random Forest analisa
- Prediz: "Viável com 92% de confiança"
- Prediz valores: "Latência prevista: 0.8ms"

**4. Explicação (XAI)**

```json
{
  "viability": {
    "is_viable": true,
    "confidence": 0.92,
    "predicted_latency_ms": 0.8
  },
  "xai_explanation": {
    "key_factors": [
      {
        "factor": "cell_density",
        "impact": "high",
        "reason": "Alta densidade garante latência baixa"
      }
    ],
    "risk_factors": [
      {
        "factor": "network_congestion",
        "risk_level": "low"
      }
    ]
  }
}
```

#### 10.3 Modelo Random Forest

**Treinamento:**
- Dataset histórico de slices
- Features: configuração do slice
- Labels: resultado real (viável/não viável, latência real)

**Predição:**
- 100 árvores de decisão
- Cada árvore vota
- Resultado: maioria vence

**Vantagens:**
- Alta precisão
- Robusto a outliers
- Explicável (pode ver decisão de cada árvore)

---

### Capítulo 11: Decision Engine - Motor de Decisão

#### 11.1 Função do Módulo

O **Decision Engine** é o **cérebro** do TriSLA. Analisa predições e decide:
- **Aprovar** slice
- **Rejeitar** slice
- **Aprovar com condições** (monitoramento extra)

#### 11.2 Regras de Decisão

**Exemplo de Regra:**

```yaml
rule: approve_high_confidence
condition: |
  prediction.viability.is_viable == true and
  prediction.viability.confidence >= 0.9
action: approve
actions:
  - type: provision_slice
    domain: RAN
  - type: provision_slice
    domain: Core
  - type: register_blockchain
```

**Lógica:**
- Se viável E confiança alta → Aprovar diretamente
- Se viável E confiança média → Aprovar com monitoramento
- Se não viável OU confiança baixa → Rejeitar

#### 11.3 Ações Geradas

**Tipos de Ações:**

1. **provision_slice**: Criar slice
2. **monitor_sla**: Monitorar continuamente
3. **register_blockchain**: Registrar no blockchain
4. **notify_tenant**: Notificar tenant

**Exemplo:**

```json
{
  "decision_id": "dec-001",
  "action": "approve_with_monitoring",
  "actions": [
    {
      "type": "provision_slice",
      "domain": "RAN",
      "config": {
        "cell_density": "high",
        "mimo_layers": 4
      }
    },
    {
      "type": "monitor_sla",
      "interval": 300,
      "metrics": ["latency", "throughput"]
    }
  ]
}
```

---

### Capítulo 12: BC-NSSMF - Blockchain

#### 12.1 Função do Módulo

O **BC-NSSMF** (Blockchain NSSMF) **registra SLAs no blockchain** para:
- **Imutabilidade**: Não pode ser alterado
- **Auditoria**: Histórico completo
- **Conformidade**: Prova de compliance

#### 12.2 Smart Contract

**Função Principal:**

```solidity
function registerSLA(
    string memory intentId,
    string memory nestId,
    uint256 latencyMs,
    uint256 throughputMbps,
    uint256 reliability
) public {
    // Cria registro
    SLA memory newSLA = SLA({
        intentId: intentId,
        nestId: nestId,
        latencyMs: latencyMs,
        throughputMbps: throughputMbps,
        reliability: reliability,
        timestamp: block.timestamp,
        isActive: true
    });
    
    // Armazena
    slas[intentId] = newSLA;
    
    // Emite evento
    emit SLARegistered(intentId, nestId, block.timestamp);
}
```

**Resultado:**
- SLA registrado no blockchain
- Hash único identifica o registro
- Qualquer um pode verificar

#### 12.3 Integração

**Fluxo:**
1. Decision Engine aprova SLA
2. Envia para BC-NSSMF via gRPC
3. BC-NSSMF chama smart contract
4. Smart contract registra no blockchain
5. Retorna hash da transação

**Benefícios:**
- Prova de que SLA foi acordado
- Histórico completo para auditoria
- Conformidade com regulamentações

---

### Capítulo 13: SLA-Agent Layer - Agentes Federados

#### 13.1 Função do Módulo

O **SLA-Agent Layer** contém **agentes especializados** que executam ações em diferentes domínios:
- **RAN Agent**: Gerencia acesso de rádio
- **Transport Agent**: Gerencia transporte de rede
- **Core Agent**: Gerencia núcleo da rede

**Analogia:**
Pense em uma empresa com departamentos:
- **RAN Agent**: Departamento de vendas (primeiro contato)
- **Transport Agent**: Departamento de logística (transporte)
- **Core Agent**: Departamento central (processamento)

#### 13.2 Agentes Federados

**Federado** significa que cada agente:
- **Opera independentemente** em seu domínio
- **Coordena** com outros agentes
- **Compartilha** informações quando necessário

**Exemplo:**

**Ação: Provisionar slice**

1. **RAN Agent** recebe comando
   - Configura células de rádio
   - Aloca recursos de espectro

2. **Transport Agent** recebe comando
   - Configura roteamento
   - Aloca banda de transporte

3. **Core Agent** recebe comando
   - Configura UPF (User Plane Function)
   - Aloca recursos de processamento

**Coordenação:**
- Agentes comunicam status
- Se um falhar, outros são notificados
- Rollback automático se necessário

---

### Capítulo 14: NASP Adapter - Integração

#### 14.1 Função do Módulo

O **NASP Adapter** é a **ponte** entre o TriSLA e o ambiente NASP (Network Automation and Service Platform).

**NASP** é a plataforma real que controla:
- RAN controllers
- Transport controllers
- Core controllers

#### 14.2 Como Funciona

**Fluxo:**

1. **SLA-Agent Layer** gera ação
   ```json
   {
     "action": "provision_slice",
     "domain": "RAN",
     "config": {...}
   }
   ```

2. **NASP Adapter** traduz para formato NASP
   - Converte para API do NASP
   - Adiciona autenticação
   - Trata erros

3. **NASP** executa ação real
   - Provisiona slice
   - Retorna status

4. **NASP Adapter** retorna resultado
   - Converte resposta
   - Notifica SLA-Agent Layer

#### 14.3 Abstração

**Benefício:**
- TriSLA não precisa conhecer detalhes do NASP
- Mudanças no NASP não afetam outros módulos
- Facilita testes (pode simular NASP)

---

### Capítulo 15: UI Dashboard - Interface Visual

#### 15.1 Função do Módulo

O **UI Dashboard** é a **interface visual** para operadores gerenciarem o TriSLA.

**Funcionalidades:**

1. **Overview**
   - Status de todos os módulos
   - Métricas principais
   - Alertas

2. **Health Monitoring**
   - Tabela de saúde de cada módulo
   - Latência por módulo
   - Status de conectividade

3. **Slice Management**
   - Criar novos slices
   - Visualizar slices existentes
   - Histórico de operações

4. **Metrics Visualization**
   - Gráficos de métricas
   - Dashboards Prometheus
   - Análise de tendências

#### 15.2 Tecnologias

- **Next.js 14**: Framework React
- **TypeScript**: Tipagem estática
- **TailwindCSS**: Estilização
- **ECharts**: Gráficos
- **Axios**: Cliente HTTP

---

## 🔧 PARTE III: OPERAÇÃO E MANUTENÇÃO

### Capítulo 16: Deploy e Configuração

#### 16.1 Pré-requisitos

**Ambiente:**
- Kubernetes cluster (1.26+)
- Helm (3.14+)
- Docker registry (GHCR)

**Acesso:**
- kubectl configurado
- Acesso ao cluster
- Permissões de deploy

#### 16.2 Processo de Deploy

**1. Preparar Valores**

Editar `helm/trisla/values-nasp.yaml`:
- Endpoints NASP
- Recursos por módulo
- Configurações de rede

**2. Validar Helm Chart**

```bash
helm lint ./helm/trisla -f ./helm/trisla/values-nasp.yaml
```

**3. Deploy**

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

**4. Verificar**

```bash
kubectl get pods -n trisla
kubectl get svc -n trisla
kubectl get servicemonitors -n trisla
```

#### 16.3 Configuração Pós-Deploy

**Variáveis de Ambiente:**
- OTLP_ENDPOINT: Endpoint do OTEL Collector
- KAFKA_BROKERS: Brokers do Kafka
- DATABASE_URL: URL do banco de dados

**ServiceMonitors:**
- Configurados automaticamente
- Prometheus descobre automaticamente

---

### Capítulo 17: Monitoramento e Observabilidade

#### 17.1 Acessar Prometheus

```bash
kubectl port-forward -n monitoring \
  svc/monitoring-kube-prometheus-prometheus 9090:9090
```

Acessar: http://localhost:9090

#### 17.2 Acessar Grafana

```bash
kubectl port-forward -n monitoring \
  svc/monitoring-grafana 3000:3000
```

Acessar: http://localhost:3000

#### 17.3 Métricas Importantes

**Latência:**
```
trisla_http_request_duration_seconds{endpoint="/api/v1/intents"}
```

**Throughput:**
```
rate(trisla_http_requests_total[5m])
```

**Health:**
```
trisla_health_status{module="sem-csmf"}
```

---

### Capítulo 18: Troubleshooting

#### 18.1 Pods Não Iniciam

**Verificar logs:**
```bash
kubectl logs -n trisla deployment/trisla-sem-csmf
```

**Verificar eventos:**
```bash
kubectl describe pod -n trisla <pod-name>
```

**Causas Comuns:**
- Imagem não encontrada (ImagePullBackOff)
- Erro na aplicação (CrashLoopBackOff)
- Recursos insuficientes

#### 18.2 Métricas Não Aparecem

**Verificar endpoint:**
```bash
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080
curl http://localhost:8080/metrics
```

**Verificar ServiceMonitor:**
```bash
kubectl get servicemonitor -n trisla
```

#### 18.3 Traces Não Aparecem

**Verificar OTEL Collector:**
```bash
kubectl logs -n trisla deployment/trisla-otel-collector
```

**Verificar conectividade:**
```bash
kubectl exec -n trisla deployment/trisla-sem-csmf -- \
  curl -v http://trisla-otel-collector.trisla.svc.cluster.local:4317
```

---

### Capítulo 19: Casos de Uso Práticos

#### 19.1 Caso 1: Cirurgia Remota

**Requisitos:**
- Latência < 1ms
- Confiabilidade 99.999%
- Banda garantida 100 Mbps

**Fluxo TriSLA:**
1. Intent recebido
2. SEM-CSMF gera NEST com configuração de alta prioridade
3. ML-NSMF prediz: "Viável com 95% de confiança"
4. Decision Engine aprova
5. BC-NSSMF registra no blockchain
6. SLA-Agent Layer provisiona
7. NASP Adapter executa no NASP

**Resultado:**
- Slice criado em ~30 segundos
- Latência medida: 0.8ms
- SLA cumprido

#### 19.2 Caso 2: Streaming de Vídeo 4K

**Requisitos:**
- Throughput > 50 Mbps
- Latência < 50ms
- Disponibilidade 99.9%

**Fluxo TriSLA:**
1. Intent recebido
2. SEM-CSMF gera NEST para eMBB
3. ML-NSMF prediz: "Viável com 88% de confiança"
4. Decision Engine aprova com monitoramento
5. Slice provisionado
6. Monitoramento contínuo

**Resultado:**
- Slice criado
- Throughput medido: 55 Mbps
- Monitoramento ativo

---

### Capítulo 20: Futuras Evoluções

#### 20.1 Melhorias Planejadas

**ML Avançado:**
- Deep Learning para predições mais precisas
- Reinforcement Learning para otimização automática

**Blockchain:**
- Integração com múltiplas blockchains
- Smart contracts mais complexos

**Observabilidade:**
- AIOps (IA para operações)
- Predição de falhas
- Auto-healing

#### 20.2 Expansões

**Novos Domínios:**
- Edge computing
- Fog computing
- Multi-cloud

**Novas Funcionalidades:**
- SLA negotiation automática
- Pricing dinâmico
- Marketplace de slices

---

## 📝 CONCLUSÃO

O **TriSLA** representa uma solução completa e inovadora para gerenciamento de SLAs em redes 5G/O-RAN. Combinando:

- **Inteligência Artificial** para predição
- **Ontologias Semânticas** para interpretação
- **Blockchain** para confiabilidade
- **Observabilidade** para monitoramento
- **Automação** para eficiência

O sistema oferece uma arquitetura **confiável, raciocinada e inteligente** que garante SLAs de forma automática e transparente.

---

## 📚 REFERÊNCIAS

- **3GPP**: Especificações 5G
- **O-RAN Alliance**: Especificações O-RAN
- **ETSI**: Network Slicing
- **Prometheus**: Documentação oficial
- **OpenTelemetry**: Documentação oficial

---

## 👤 AUTOR

**Abel José Rodrigues Lisboa**

Desenvolvedor e pesquisador do projeto TriSLA.  
Este manual foi criado como parte da dissertação de mestrado em Engenharia de Sistemas e Computação.

---

**FIM DO MANUAL**

**Versão:** 1.0  
**Data:** 2025-12-05  
**Licença:** MIT








