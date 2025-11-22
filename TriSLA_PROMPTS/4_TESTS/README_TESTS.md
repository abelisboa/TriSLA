# README - Testes TriSLA

**Documentação Completa da Suite de Testes**

---

## 🎯 Função dos Testes

Os testes garantem:

1. **Qualidade** do código e funcionalidades
2. **Integridade** do fluxo entre módulos
3. **Conformidade** com especificações 3GPP
4. **Segurança** e resiliência
5. **Performance** sob carga
6. **Evidências** para validação científica

---

## 📥 Entradas

### 1. Código dos Módulos

- SEM-CSMF
- ML-NSMF
- Decision Engine
- BC-NSSMF
- NASP Adapter
- SLA-Agent Layer

### 2. Dados de Teste

- Intenções sintéticas
- NESTs de exemplo
- Métricas simuladas
- Cenários de violação

---

## 📤 Saídas

### 1. Relatórios de Testes

- **Unit Tests** - Cobertura de código
- **Integration Tests** - Validação de interfaces
- **E2E Tests** - Fluxo completo
- **Security Tests** - Vulnerabilidades
- **Load Tests** - Performance
- **Blockchain Tests** - Resiliência

### 2. Evidências

- Screenshots
- Logs
- Traces
- Métricas
- Transações blockchain

---

## 🔗 Integrações

### Testes Unitários

- Testam **cada módulo isoladamente**
- Não requerem integração com outros módulos

### Testes de Integração

- Testam **comunicação entre módulos**
- Requerem interfaces I-01 a I-07

### Testes E2E

- Testam **fluxo completo**
- Requerem stack completo funcionando

---

## 🎯 Responsabilidades

1. **Validação funcional** de cada módulo
2. **Validação de interfaces** I-01 a I-07
3. **Validação de segurança** (AAA, DoS, Injection)
4. **Validação de performance** (carga, stress)
5. **Validação de resiliência** (blockchain, falhas)
6. **Geração de evidências** para dissertação

---

## 🔄 Relação com Decision Engine

Os testes **validam** a integração com o Decision Engine:

- **Testam:** Comunicação via I-01, I-02, I-03
- **Validam:** Decisões geradas
- **Verificam:** Chamadas para I-04, I-06, I-07

---

## 📋 Requisitos Técnicos

### Tecnologias

- **Python 3.12+**
- **pytest** - Framework de testes
- **Locust / K6** - Testes de carga
- **Bandit / Semgrep** - Testes de segurança
- **Docker Compose** - Ambiente de testes
- **PostgreSQL** - Banco de dados de teste
- **Kafka** - Message broker de teste

### Dependências

- **Todos os módulos** - Para testes de integração e E2E
- **Infraestrutura** - Para testes de carga e stress

---

## 📚 Referências à Dissertação

- **Capítulo 5** - Implementação e Validação
- **Testes** - Validação científica
- **Evidências** - Prova de funcionamento

---

## 📁 Estrutura de Testes

```
tests/
├── unit/              # Testes unitários
├── integration/       # Testes de integração
├── e2e/              # Testes end-to-end
├── security/         # Testes de segurança
├── load/             # Testes de carga
└── blockchain/      # Testes de blockchain
```

---

## ✔ Suite de Testes Completa e Documentada

