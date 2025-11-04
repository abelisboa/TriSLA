# TESTS_CONTRACT_TEMPLATE.md

[TESTS FOR CONTRACTS]

Use este template para pedir à IA testes de contrato baseados nas interfaces I-*.

**Instruções:**  
1. Colar `SESSION HEADER` + `TASK SPEC`.  
2. Identificar a interface alvo (ex: I-02, I-04).  
3. Pedir cobertura para:  
   - Validação de esquema (OpenAPI / Protobuf / Avro).  
   - Autenticação (mTLS, JWT, OAuth2).  
   - RBAC e autorização.  
   - SLOs: latência p99, taxa de erro.  
   - Casos válidos e inválidos.  
4. A IA deve fornecer:  
   - Código de testes automatizados (Pytest, Postman, etc.).  
   - Scripts de execução e critérios de aprovação.  
   - Logs de execução em formato compatível com Apêndice H.  
