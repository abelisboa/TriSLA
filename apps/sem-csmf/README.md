# SEM-CSMF - Semantic-enhanced Communication Service Management Function

Module responsible for receiving intents, semantically validating them, and generating NEST.

## Structure

```
apps/sem-csmf/
├── src/
│   ├── main.py              # FastAPI application
│   ├── grpc_server.py       # gRPC server (I-01)
│   ├── intent_processor.py  # Intent processing
│   ├── ontology/
│   │   ├── parser.py        # Ontology parser
│   │   └── matcher.py       # Semantic matching
│   ├── nest_generator.py    # NEST generation
│   └── models/
│       ├── intent.py        # Intent models
│       └── nest.py          # NEST models
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Pipeline

1. Intent → Ontology (semantic validation)
2. Ontology → GST (Generation Service Template)
3. GST → NEST (Network Slice Template)
4. NEST → Subset (module-specific subset)
5. Metadata → I-01 → Decision Engine

## Interface I-01

- **Protocolo**: gRPC
- **Endpoint**: Intent intake
- **Metadata**: Sent to Decision Engine

