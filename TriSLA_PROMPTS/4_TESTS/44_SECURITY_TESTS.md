# 44 – Testes de Segurança (AAA, Tokens, ACL, Hardening, DoS)  

**TriSLA – Validação de Segurança, Autenticação, Autorização e Resiliência a Ataques**

---

## 🎯 Objetivo Geral

Implementar uma **suite completa de testes de segurança** para validar:

- **Autenticação (Authentication)** - JWT, OAuth2, mTLS
- **Autorização (Authorization)** - RBAC, ACL, permissões
- **Auditoria (Auditing)** - Logs de segurança, rastreabilidade
- **Hardening** - Configurações seguras, secrets management
- **Resiliência a Ataques** - DoS, DDoS, injection, XSS, CSRF
- **Comunicação Segura** - TLS/SSL, certificados, criptografia

---

## 📋 Escopo dos Testes

### 1. Autenticação (Authentication)

- ✅ Validação de **JWT tokens**
- ✅ **Refresh tokens** e renovação
- ✅ **OAuth2** flow (se aplicável)
- ✅ **mTLS** para comunicação gRPC
- ✅ **Rate limiting** para prevenção de brute force
- ✅ **Expiração** de tokens
- ✅ **Revogação** de tokens

### 2. Autorização (Authorization)

- ✅ **RBAC (Role-Based Access Control)**
- ✅ **ACL (Access Control Lists)** por recurso
- ✅ **Multi-tenant isolation**
- ✅ **Permissões granulares** (read, write, delete)
- ✅ **Privilege escalation** prevention

### 3. Auditoria (Auditing)

- ✅ **Logs de autenticação** (sucesso/falha)
- ✅ **Logs de autorização** (acesso negado/permitido)
- ✅ **Rastreabilidade** de ações (quem, o quê, quando)
- ✅ **Integridade** de logs (tamper-proof)
- ✅ **Retenção** de logs de segurança

### 4. Hardening

- ✅ **Secrets management** (Vault, Kubernetes Secrets)
- ✅ **Configurações seguras** (HTTPS obrigatório, headers de segurança)
- ✅ **Princípio do menor privilégio**
- ✅ **Network policies** (Kubernetes)
- ✅ **Container security** (non-root user, read-only filesystem)

### 5. Resiliência a Ataques

- ✅ **DoS/DDoS** - Rate limiting, circuit breakers
- ✅ **SQL Injection** - Validação de inputs, prepared statements
- ✅ **XSS (Cross-Site Scripting)** - Sanitização de outputs
- ✅ **CSRF (Cross-Site Request Forgery)** - Tokens CSRF
- ✅ **Path Traversal** - Validação de caminhos
- ✅ **Command Injection** - Sanitização de comandos
- ✅ **XXE (XML External Entity)** - Desabilitação de entidades externas

### 6. Comunicação Segura

- ✅ **TLS/SSL** - Certificados válidos, versões seguras
- ✅ **Criptografia** - Dados em trânsito e em repouso
- ✅ **Certificate validation** - Verificação de CA
- ✅ **Perfect Forward Secrecy** - Cipher suites adequados

---

## 🏗️ Estrutura dos Testes

```
tests/security/
├── test_authentication.py      # Testes de autenticação
├── test_authorization.py        # Testes de autorização
├── test_auditing.py             # Testes de auditoria
├── test_hardening.py            # Testes de hardening
├── test_dos_protection.py       # Testes de DoS/DDoS
├── test_injection.py             # Testes de injection
├── test_xss_csrf.py             # Testes XSS/CSRF
├── test_tls_ssl.py              # Testes TLS/SSL
├── test_secrets.py              # Testes de secrets
└── fixtures/
    ├── malicious_payloads.json   # Payloads maliciosos
    └── test_users.json          # Usuários de teste
```

---

## 🔧 Implementação dos Testes

### 1. Testes de Autenticação

```python
import pytest
import jwt
from datetime import datetime, timedelta

def test_jwt_token_validation():
    """Testa validação de JWT token válido"""
    token = generate_jwt_token(user_id="user123", role="admin")
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert decoded["user_id"] == "user123"
    assert decoded["role"] == "admin"

def test_jwt_token_expiration():
    """Testa expiração de JWT token"""
    token = generate_jwt_token(
        user_id="user123",
        expires_in=timedelta(seconds=-1)  # Expirado
    )
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

def test_jwt_token_invalid_signature():
    """Testa token com assinatura inválida"""
    token = generate_jwt_token(user_id="user123")
    invalid_secret = "wrong_secret"
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(token, invalid_secret, algorithms=["HS256"])

def test_rate_limiting_authentication():
    """Testa rate limiting para prevenção de brute force"""
    for i in range(10):
        response = authenticate(username="user", password="wrong")
        if i >= 5:
            assert response.status_code == 429  # Too Many Requests
```

### 2. Testes de Autorização

```python
def test_rbac_admin_access():
    """Testa acesso de admin a recursos protegidos"""
    token = generate_jwt_token(role="admin")
    response = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_rbac_user_denied():
    """Testa negação de acesso de usuário comum a recursos admin"""
    token = generate_jwt_token(role="user")
    response = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403  # Forbidden

def test_multi_tenant_isolation():
    """Testa isolamento entre tenants"""
    token_tenant1 = generate_jwt_token(tenant_id="tenant1")
    token_tenant2 = generate_jwt_token(tenant_id="tenant2")
    
    # Criar recurso no tenant1
    create_resource(tenant_id="tenant1", resource_id="res1", token=token_tenant1)
    
    # Tentar acessar recurso do tenant1 com token do tenant2
    response = client.get("/api/v1/resources/res1", headers={"Authorization": f"Bearer {token_tenant2}"})
    assert response.status_code == 404  # Not Found (isolamento)
```

### 3. Testes de Auditoria

```python
def test_audit_log_authentication_success():
    """Testa log de autenticação bem-sucedida"""
    authenticate(username="user", password="correct")
    logs = get_audit_logs(user_id="user", action="LOGIN")
    assert len(logs) > 0
    assert logs[0]["status"] == "SUCCESS"
    assert logs[0]["ip_address"] is not None
    assert logs[0]["timestamp"] is not None

def test_audit_log_authentication_failure():
    """Testa log de autenticação falhada"""
    authenticate(username="user", password="wrong")
    logs = get_audit_logs(user_id="user", action="LOGIN_FAILED")
    assert len(logs) > 0
    assert logs[0]["status"] == "FAILED"

def test_audit_log_authorization_denied():
    """Testa log de autorização negada"""
    token = generate_jwt_token(role="user")
    client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    logs = get_audit_logs(action="ACCESS_DENIED")
    assert len(logs) > 0
    assert logs[0]["resource"] == "/api/v1/admin/users"
```

### 4. Testes de Hardening

```python
def test_https_required():
    """Testa que HTTPS é obrigatório"""
    response = client.get("http://api/v1/intents")  # HTTP
    assert response.status_code == 301  # Redirect to HTTPS
    # ou
    assert response.status_code == 400  # Bad Request

def test_security_headers():
    """Testa presença de headers de segurança"""
    response = client.get("/api/v1/intents")
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
    assert "Strict-Transport-Security" in response.headers

def test_secrets_not_in_logs():
    """Testa que secrets não aparecem em logs"""
    client.post("/api/v1/login", json={"username": "user", "password": "secret123"})
    logs = get_application_logs()
    assert "secret123" not in logs
    assert "password" not in logs.lower()
```

### 5. Testes de DoS/DDoS

```python
import asyncio
import aiohttp

async def test_dos_rate_limiting():
    """Testa rate limiting para proteção contra DoS"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1000):  # 1000 requisições simultâneas
            task = session.get("http://api/v1/intents")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verificar que algumas requisições foram bloqueadas
        rate_limited = sum(1 for r in responses if hasattr(r, 'status') and r.status == 429)
        assert rate_limited > 0

def test_circuit_breaker():
    """Testa circuit breaker para proteção contra falhas em cascata"""
    # Simular falhas repetidas
    for i in range(10):
        response = client.get("/api/v1/external-service")
        if i >= 5:
            # Circuit breaker deve abrir
            assert response.status_code == 503  # Service Unavailable
```

### 6. Testes de Injection

```python
def test_sql_injection_prevention():
    """Testa prevenção de SQL injection"""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "1' UNION SELECT * FROM users--"
    ]
    
    for malicious_input in malicious_inputs:
        response = client.get(f"/api/v1/users?name={malicious_input}")
        # Não deve retornar dados não autorizados
        assert response.status_code in [400, 404, 500]  # Erro, não execução

def test_command_injection_prevention():
    """Testa prevenção de command injection"""
    malicious_inputs = [
        "; rm -rf /",
        "| cat /etc/passwd",
        "&& ls -la",
        "$(whoami)"
    ]
    
    for malicious_input in malicious_inputs:
        response = client.post("/api/v1/execute", json={"command": malicious_input})
        assert response.status_code == 400  # Bad Request

def test_path_traversal_prevention():
    """Testa prevenção de path traversal"""
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/etc/shadow",
        "....//....//etc/passwd"
    ]
    
    for malicious_path in malicious_paths:
        response = client.get(f"/api/v1/files?path={malicious_path}")
        assert response.status_code in [400, 403, 404]
```

### 7. Testes XSS/CSRF

```python
def test_xss_prevention():
    """Testa prevenção de XSS"""
    malicious_inputs = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>"
    ]
    
    for malicious_input in malicious_inputs:
        response = client.post("/api/v1/comments", json={"text": malicious_input})
        # Input deve ser sanitizado
        assert "<script>" not in response.json()["text"]
        assert "javascript:" not in response.json()["text"]

def test_csrf_protection():
    """Testa proteção CSRF"""
    # Requisição sem token CSRF
    response = client.post("/api/v1/intents", json={"intent": "test"})
    assert response.status_code == 403  # Forbidden
    
    # Requisição com token CSRF válido
    csrf_token = get_csrf_token()
    response = client.post(
        "/api/v1/intents",
        json={"intent": "test"},
        headers={"X-CSRF-Token": csrf_token}
    )
    assert response.status_code == 200
```

### 8. Testes TLS/SSL

```python
import ssl
import socket

def test_tls_version():
    """Testa que apenas versões seguras de TLS são aceitas"""
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    with socket.create_connection(("api.example.com", 443)) as sock:
        with context.wrap_socket(sock, server_hostname="api.example.com") as ssock:
            assert ssock.version() in ["TLSv1.2", "TLSv1.3"]

def test_certificate_validation():
    """Testa validação de certificados"""
    context = ssl.create_default_context()
    # Deve validar certificado contra CA
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    
    # Tentar conectar com certificado inválido deve falhar
    with pytest.raises(ssl.SSLError):
        with socket.create_connection(("invalid-cert.example.com", 443)) as sock:
            context.wrap_socket(sock, server_hostname="invalid-cert.example.com")
```

---

## 📊 Relatórios e Evidências

### Relatório de Segurança

Gerar relatório contendo:

- ✅ **Resumo executivo** - Status geral de segurança
- ✅ **Vulnerabilidades encontradas** - Lista de issues
- ✅ **Recomendações** - Ações corretivas
- ✅ **Métricas** - Taxa de sucesso/falha dos testes
- ✅ **Evidências** - Screenshots, logs, traces

### Formato do Relatório

```json
{
  "test_suite": "Security Tests",
  "timestamp": "2025-01-19T10:30:00Z",
  "summary": {
    "total_tests": 50,
    "passed": 45,
    "failed": 5,
    "severity": {
      "critical": 1,
      "high": 2,
      "medium": 2,
      "low": 0
    }
  },
  "vulnerabilities": [
    {
      "id": "SEC-001",
      "severity": "critical",
      "description": "SQL Injection vulnerability in user search",
      "recommendation": "Use parameterized queries",
      "evidence": "..."
    }
  ]
}
```

---

## ✅ Critérios de Sucesso

- ✅ **100% dos testes de autenticação** passando
- ✅ **100% dos testes de autorização** passando
- ✅ **0 vulnerabilidades críticas** encontradas
- ✅ **TLS/SSL** configurado corretamente
- ✅ **Rate limiting** funcionando
- ✅ **Logs de auditoria** completos
- ✅ **Secrets** não expostos em logs/código
- ✅ **Headers de segurança** presentes
- ✅ **Proteção contra injection** validada
- ✅ **Proteção contra XSS/CSRF** validada

---

## 🚀 Execução dos Testes

### Comando pytest

```bash
# Executar todos os testes de segurança
pytest tests/security/ -v

# Executar apenas testes de autenticação
pytest tests/security/test_authentication.py -v

# Executar com relatório HTML
pytest tests/security/ --html=reports/security_report.html
```

### Integração CI/CD

```yaml
# .github/workflows/security-tests.yml
name: Security Tests

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run security tests
        run: pytest tests/security/ -v
      - name: Generate report
        run: pytest tests/security/ --html=reports/security_report.html
```

---

## 📚 Referências

- OWASP Top 10 - Top 10 Web Application Security Risks
- OWASP Testing Guide - Web Application Security Testing
- NIST Cybersecurity Framework
- CWE (Common Weakness Enumeration)
- CVE (Common Vulnerabilities and Exposures)

---

## ✔ Pronto para implementação no Cursor

