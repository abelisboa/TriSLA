# SEM-CSMF - Semantic-enhanced Communication Service Management Function

Módulo responsável por receber intents, validar semanticamente e gerar NEST.

## Estrutura

```
apps/sem-csmf/
├── src/
│   ├── main.py              # Aplicação FastAPI
│   ├── grpc_server.py       # Servidor gRPC (I-01)
│   ├── intent_processor.py  # Processamento de intents
│   ├── ontology/
│   │   ├── parser.py        # Parser de ontologias
│   │   └── matcher.py       # Match semântico
│   ├── nest_generator.py    # Geração de NEST
│   └── models/
│       ├── intent.py        # Modelos de intent
│       └── nest.py          # Modelos de NEST
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Pipeline

1. Intent → Ontology (validação semântica)
2. Ontology → GST (Generation Service Template)
3. GST → NEST (Network Slice Template)
4. NEST → Subset (subconjunto para módulos)
5. Metadados → I-01 → Decision Engine

## Interface I-01

- **Protocolo**: gRPC
- **Endpoint**: Recepção de intents
- **Metadados**: Enviados para Decision Engine

