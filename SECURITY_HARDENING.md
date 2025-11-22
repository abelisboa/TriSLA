# TriSLA — Guia de Segurança e Hardening

## 1. Política Geral de Segurança do TriSLA

### 1.1 Princípios Fundamentais

O TriSLA adota uma abordagem de **defesa em profundidade** (defense-in-depth) e **Zero Trust** para garantir a segurança de todos os componentes em produção. Os princípios fundamentais são:

1. **Nunca confiar, sempre verificar**: Todos os componentes devem autenticar e autorizar todas as requisições, independentemente da origem.
2. **Princípio do menor privilégio**: Cada componente recebe apenas as permissões mínimas necessárias para sua operação.
3. **Segregação de responsabilidades**: Módulos operam em isolamento com comunicação controlada.
4. **Criptografia em trânsito e em repouso**: Todas as comunicações e dados sensíveis são criptografados.
5. **Auditoria contínua**: Todas as ações são registradas e monitoradas para detecção de anomalias.
6. **Atualização e patching contínuos**: Vulnerabilidades são corrigidas proativamente.

### 1.2 Modelo de Ameaças

O TriSLA considera as seguintes ameaças em seu modelo de segurança:

- **Acesso não autorizado** a módulos e interfaces
- **Interceptação de comunicação** entre componentes
- **Injeção de dados maliciosos** via interfaces I-01 a I-07
- **Comprometimento de containers** e escalação de privilégios
- **Vazamento de secrets** e credenciais
- **Ataques à blockchain** e manipulação de smart contracts
- **Denial of Service (DoS)** em serviços críticos
- **Violação de integridade** de dados e decisões

### 1.3 Classificação de Dados

Os dados do TriSLA são classificados conforme sensibilidade:

| Classificação | Descrição | Exemplos | Proteção Requerida |
|---------------|-----------|----------|-------------------|
| **Crítico** | Dados que comprometem segurança ou operação | Tokens, senhas, chaves privadas | Criptografia forte, acesso restrito |
| **Confidencial** | Dados de negócio sensíveis | SLAs, intenções de tenant, decisões | Criptografia, controle de acesso |
| **Interno** | Dados operacionais | Métricas, logs, NESTs | Autenticação, logging |
| **Público** | Dados não sensíveis | Documentação, dashboards públicos | Sem proteção especial |

---

## 2. Zero Trust: Princípios Aplicados à Arquitetura

### 2.1 Visão Geral do Modelo Zero Trust no TriSLA

O modelo Zero Trust é aplicado em todas as camadas do TriSLA, garantindo que nenhum componente confie implicitamente em outro, mesmo dentro do mesmo namespace Kubernetes.

### 2.2 SEM-CSMF (Semantic Communication Service Management Function)

**Princípios Zero Trust aplicados:**

- **Autenticação obrigatória**: Todas as requisições devem incluir token JWT válido.
- **Autorização baseada em roles**: Tenants só podem acessar seus próprios intents e NESTs.
- **Validação de entrada**: Todos os intents são validados contra schema antes do processamento.
- **Isolamento de dados**: Banco de dados PostgreSQL com row-level security (RLS) por tenant.

**Implementação:**

```yaml
# Exemplo de configuração de segurança no deployment
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  seccompProfile:
    type: RuntimeDefault
```

**Autenticação JWT:**

```python
# Validação de token em cada requisição
@router.post("/api/v1/intents")
async def create_intent(
    intent: IntentRequest,
    token: str = Depends(get_token_from_header)
):
    # Verificar token
    payload = verify_jwt_token(token)
    # Verificar autorização do tenant
    if payload["tenant_id"] != intent.tenant_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    # Processar intent
    ...
```

### 2.3 ML-NSMF (Machine Learning Network Slice Management Function)

**Princípios Zero Trust aplicados:**

- **Validação de modelos**: Modelos ML são assinados e verificados antes do carregamento.
- **Sanitização de entrada**: Métricas recebidas são validadas e sanitizadas.
- **Isolamento de execução**: Modelos executam em sandbox com recursos limitados.
- **Auditoria de predições**: Todas as predições são registradas com contexto completo.

**Implementação:**

```yaml
# Limites de recursos para prevenir DoS
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

**Validação de modelos:**

```bash
# Verificar assinatura do modelo antes do carregamento
cosign verify-blob \
  --certificate-identity https://github.com/abelisboa/TriSLA \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  model.pkl \
  --signature model.pkl.sig
```

### 2.4 Decision Engine

**Princípios Zero Trust aplicados:**

- **Verificação de origem**: Todas as requisições são verificadas quanto à origem legítima.
- **Validação de decisões**: Decisões são validadas contra regras de negócio antes da execução.
- **Isolamento de contexto**: Cada decisão executa em contexto isolado.
- **Auditoria imutável**: Todas as decisões são registradas em blockchain.

**Implementação:**

```python
# Validação de origem em gRPC
def verify_grpc_context(context):
    """Verifica contexto gRPC para autenticação"""
    metadata = context.invocation_metadata()
    auth_header = None
    for key, value in metadata:
        if key == 'authorization':
            auth_header = value
            break
    
    if not auth_header:
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Missing authorization")
    
    # Verificar token
    token = auth_header.replace('Bearer ', '')
    if not verify_jwt_token(token):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
```

### 2.5 BC-NSSMF (Blockchain Network Slice Subnet Management Function)

**Princípios Zero Trust aplicados:**

- **Verificação de smart contracts**: Contratos são verificados antes do deploy.
- **Assinatura de transações**: Todas as transações são assinadas com chaves privadas protegidas.
- **Validação de estado**: Estado da blockchain é verificado antes de cada operação.
- **Isolamento de chaves**: Chaves privadas nunca saem do ambiente seguro.

**Implementação:**

```yaml
# Secret para chaves privadas
apiVersion: v1
kind: Secret
metadata:
  name: blockchain-keys
  namespace: trisla
type: Opaque
stringData:
  private-key: <ENCRYPTED_PRIVATE_KEY>
```

**Proteção de chaves:**

```python
# Carregar chave privada de secret do Kubernetes
from kubernetes import client, config

def get_private_key():
    """Obtém chave privada de secret do Kubernetes"""
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("blockchain-keys", "trisla")
    encrypted_key = secret.data["private-key"]
    # Descriptografar usando KMS ou similar
    return decrypt_key(encrypted_key)
```

### 2.6 SLA-Agent Layer

**Princípios Zero Trust aplicados:**

- **Autenticação mútua**: Agentes autenticam com NASP e vice-versa.
- **Validação de métricas**: Métricas coletadas são validadas antes do processamento.
- **Isolamento por domínio**: Agentes RAN, Transport e Core operam isoladamente.
- **Rate limiting**: Coleta de métricas é limitada para prevenir abuso.

**Implementação:**

```python
# Rate limiting por domínio
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/minute")
async def collect_metrics(domain: str):
    """Coleta métricas com rate limiting"""
    ...
```

---

## 3. Controle de Acesso e RBAC Específico para Kubernetes/NASP

### 3.1 Service Accounts e Roles

Cada módulo do TriSLA possui um ServiceAccount dedicado com permissões mínimas:

```yaml
# ServiceAccount para SEM-CSMF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: sem-csmf-sa
  namespace: trisla
automountServiceAccountToken: true
```

**Role para SEM-CSMF:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: sem-csmf-role
  namespace: trisla
rules:
  # Permitir leitura de ConfigMaps e Secrets próprios
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    resourceNames: ["sem-csmf-config", "sem-csmf-secrets"]
    verbs: ["get", "list"]
  # Permitir leitura de endpoints de serviços
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list"]
```

**RoleBinding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: sem-csmf-binding
  namespace: trisla
subjects:
  - kind: ServiceAccount
    name: sem-csmf-sa
    namespace: trisla
roleRef:
  kind: Role
  name: sem-csmf-role
  apiGroup: rbac.authorization.k8s.io
```

### 3.2 Network Policies (Calico)

Políticas de rede restringem comunicação entre pods:

```yaml
# NetworkPolicy: SEM-CSMF só pode comunicar com Decision Engine e PostgreSQL
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sem-csmf-netpol
  namespace: trisla
spec:
  podSelector:
    matchLabels:
      app: sem-csmf
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Permitir apenas do Ingress Controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
  egress:
    # Permitir comunicação com Decision Engine (gRPC)
    - to:
        - podSelector:
            matchLabels:
              app: decision-engine
      ports:
        - protocol: TCP
          port: 50051
    # Permitir comunicação com PostgreSQL
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    # Permitir comunicação com Kafka
    - to:
        - podSelector:
            matchLabels:
              app: kafka
      ports:
        - protocol: TCP
          port: 9092
    # Permitir comunicação com OTLP Collector
    - to:
        - podSelector:
            matchLabels:
              app: otlp-collector
      ports:
        - protocol: TCP
          port: 4317
    # Permitir DNS
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
```

### 3.3 Pod Security Standards

Aplicação de Pod Security Standards do Kubernetes:

```yaml
# Namespace com Pod Security Standards
apiVersion: v1
kind: Namespace
metadata:
  name: trisla
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

**Conformidade com Restricted Policy:**

- Containers não executam como root
- Read-only root filesystem quando possível
- Capabilities desnecessárias removidas
- Seccomp profile obrigatório
- Sem escalação de privilégios

---

## 4. Segurança das Interfaces Internas I-01 a I-07

### 4.1 I-01: Intent Reception (SEM-CSMF → Decision Engine)

**Protocolo**: gRPC  
**Segurança**: mTLS obrigatório + JWT

**Configuração mTLS:**

```yaml
# Certificados para mTLS
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: sem-csmf-tls
  namespace: trisla
spec:
  secretName: sem-csmf-tls-secret
  issuerRef:
    name: trisla-issuer
    kind: ClusterIssuer
  dnsNames:
    - sem-csmf.trisla.svc.cluster.local
  usages:
    - digital signature
    - key encipherment
    - server auth
    - client auth
```

**Implementação gRPC com mTLS:**

```python
import grpc
from grpc import ssl_channel_credentials

# Carregar certificados
with open('/etc/tls/tls.crt', 'rb') as f:
    cert = f.read()
with open('/etc/tls/tls.key', 'rb') as f:
    key = f.read()
with open('/etc/tls/ca.crt', 'rb') as f:
    ca_cert = f.read()

# Criar credenciais mTLS
credentials = ssl_channel_credentials(
    root_certificates=ca_cert,
    private_key=key,
    certificate_chain=cert
)

# Criar canal seguro
channel = grpc.secure_channel(
    'decision-engine:50051',
    credentials
)
```

**Validação JWT em gRPC:**

```python
def jwt_interceptor(secret_key):
    """Interceptor para validar JWT em requisições gRPC"""
    def intercept_call(continuation, handler_call_details):
        metadata = handler_call_details.metadata
        token = None
        for key, value in metadata:
            if key == 'authorization':
                token = value.replace('Bearer ', '')
                break
        
        if not token or not verify_jwt(token, secret_key):
            handler_call_details.invocation_metadata = []
            return grpc.unary_unary_rpc_method_handler(
                lambda request, context: _abort(context, grpc.StatusCode.UNAUTHENTICATED, "Invalid token")
            )
        
        return continuation(handler_call_details)
    
    return intercept_call
```

### 4.2 I-02: NEST Generation (SEM-CSMF → ML-NSMF)

**Protocolo**: REST HTTP  
**Segurança**: TLS 1.3 + JWT

**Configuração TLS:**

```yaml
# Ingress com TLS obrigatório
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ml-nsmf-ingress
  namespace: trisla
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - ml-nsmf.trisla.local
      secretName: ml-nsmf-tls
  rules:
    - host: ml-nsmf.trisla.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ml-nsmf
                port:
                  number: 8081
```

### 4.3 I-03: ML Prediction (ML-NSMF → Decision Engine)

**Protocolo**: Kafka  
**Segurança**: SASL/SCRAM + TLS

**Configuração Kafka com segurança:**

```yaml
# ConfigMap para configuração Kafka segura
apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-security-config
  namespace: trisla
data:
  server.properties: |
    # Autenticação SASL/SCRAM
    security.inter.broker.protocol=SASL_SSL
    sasl.mechanism.inter.broker.protocol=SCRAM-SHA-512
    sasl.enabled.mechanisms=SCRAM-SHA-512
    
    # TLS obrigatório
    listeners=SASL_SSL://:9093
    listener.security.protocol.map=SASL_SSL:SASL_SSL
    ssl.keystore.location=/etc/kafka/secrets/kafka.keystore.jks
    ssl.truststore.location=/etc/kafka/secrets/kafka.truststore.jks
    ssl.keystore.password=<FROM_SECRET>
    ssl.truststore.password=<FROM_SECRET>
    
    # ACLs para controle de acesso
    authorizer.class.name=kafka.security.authorizer.AclAuthorizer
    allow.everyone.if.no.acl.found=false
```

**Autenticação de clientes:**

```python
from kafka import KafkaProducer
from kafka.errors import KafkaError
import ssl

# Configuração de segurança
security_config = {
    'security_protocol': 'SASL_SSL',
    'sasl_mechanism': 'SCRAM-SHA-512',
    'sasl_plain_username': os.getenv('KAFKA_USERNAME'),
    'sasl_plain_password': os.getenv('KAFKA_PASSWORD'),
    'ssl_context': ssl.create_default_context(),
    'ssl_check_hostname': True
}

producer = KafkaProducer(
    bootstrap_servers=['kafka:9093'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    **security_config
)
```

### 4.4 I-04: Decision to BC-NSSMF (Decision Engine → BC-NSSMF)

**Protocolo**: Kafka  
**Segurança**: Mesma configuração de I-03 + validação de assinatura

**Validação de assinatura:**

```python
import hashlib
import hmac

def sign_decision(decision_data, secret_key):
    """Assina decisão antes de enviar para BC-NSSMF"""
    message = json.dumps(decision_data, sort_keys=True)
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return {
        'decision': decision_data,
        'signature': signature,
        'timestamp': time.time()
    }

def verify_decision_signature(signed_decision, secret_key):
    """Verifica assinatura de decisão recebida"""
    decision = signed_decision['decision']
    received_signature = signed_decision['signature']
    
    message = json.dumps(decision, sort_keys=True)
    expected_signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_signature, expected_signature)
```

### 4.5 I-05: Decision to SLA-Agents (Decision Engine → SLA-Agent Layer)

**Protocolo**: Kafka  
**Segurança**: Mesma configuração de I-03 + autorização por domínio

**Autorização por domínio:**

```python
def authorize_action(action, agent_domain):
    """Autoriza ação baseada no domínio do agente"""
    allowed_domains = {
        'RAN': ['provision_ran', 'scale_ran', 'reconfigure_ran'],
        'TRANSPORT': ['provision_transport', 'scale_transport'],
        'CORE': ['provision_core', 'scale_core']
    }
    
    if action not in allowed_domains.get(agent_domain, []):
        raise UnauthorizedError(f"Action {action} not allowed for domain {agent_domain}")
    
    return True
```

### 4.6 I-06: SLA-Agents Actions (SLA-Agent Layer → NASP)

**Protocolo**: REST HTTP  
**Segurança**: TLS + mTLS + OAuth2

**Configuração mTLS para NASP:**

```yaml
# Secret com certificados para mTLS com NASP
apiVersion: v1
kind: Secret
metadata:
  name: nasp-mtls-certs
  namespace: trisla
type: Opaque
data:
  client.crt: <BASE64_CLIENT_CERT>
  client.key: <BASE64_CLIENT_KEY>
  ca.crt: <BASE64_CA_CERT>
```

**Implementação com mTLS e OAuth2:**

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
import ssl

# Configurar mTLS
session = requests.Session()
adapter = HTTPAdapter()
adapter.init_poolmanager(
    ssl_context=ssl.create_default_context(
        cafile='/etc/nasp/ca.crt'
    ),
    cert=('/etc/nasp/client.crt', '/etc/nasp/client.key')
)
session.mount('https://', adapter)

# Obter token OAuth2
def get_oauth_token():
    """Obtém token OAuth2 do NASP"""
    response = requests.post(
        'https://nasp.local/oauth/token',
        auth=('client_id', 'client_secret'),
        data={'grant_type': 'client_credentials'},
        verify='/etc/nasp/ca.crt'
    )
    return response.json()['access_token']

# Fazer requisição autenticada
token = get_oauth_token()
response = session.post(
    'https://nasp.local/api/v1/actions',
    headers={'Authorization': f'Bearer {token}'},
    json=action_data
)
```

### 4.7 I-07: NASP Adapter Interface

**Protocolo**: REST HTTP  
**Segurança**: TLS + JWT + Rate Limiting

**Rate Limiting:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=lambda: get_remote_address(),
    default_limits=["100 per minute"]
)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

@limiter.limit("10/minute")
@router.post("/api/v1/provision")
async def provision_slice(
    request: Request,
    provision_request: ProvisionRequest,
    token: str = Depends(verify_jwt)
):
    ...
```

---

## 5. Proteção dos Serviços Expostos

### 5.1 gRPC Services

**Configuração de segurança gRPC:**

```yaml
# ConfigMap com configuração de segurança gRPC
apiVersion: v1
kind: ConfigMap
metadata:
  name: grpc-security-config
  namespace: trisla
data:
  grpc.conf: |
    # Exigir TLS
    GRPC_TLS_ENABLED=true
    GRPC_TLS_CERT=/etc/tls/tls.crt
    GRPC_TLS_KEY=/etc/tls/tls.key
    GRPC_TLS_CA=/etc/tls/ca.crt
    
    # Exigir autenticação
    GRPC_AUTH_REQUIRED=true
    GRPC_AUTH_METHOD=jwt
    
    # Timeout para prevenir DoS
    GRPC_KEEPALIVE_TIME=30s
    GRPC_KEEPALIVE_TIMEOUT=5s
    GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS=false
    GRPC_MAX_CONNECTION_IDLE=300s
    GRPC_MAX_CONNECTION_AGE=3600s
    GRPC_MAX_CONNECTION_AGE_GRACE=30s
```

### 5.2 HTTP/REST Services

**Proteção HTTP:**

```python
from fastapi import FastAPI, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Redirecionar HTTP para HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

# Restringir hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["trisla.local", "*.trisla.local"]
)

# Security scheme
security = HTTPBearer()

@app.get("/api/v1/health")
async def health_check(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Verificar token
    if not verify_jwt(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"status": "healthy"}
```

**Headers de segurança:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trisla.local"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)

# Adicionar headers de segurança
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 5.3 Kafka Services

**Proteção Kafka (detalhado na seção 4.3):**

- SASL/SCRAM para autenticação
- TLS para criptografia
- ACLs para autorização
- Quotas para prevenir abuso

---

## 6. Segurança da Blockchain (Besu / Smart Contracts)

### 6.1 Verificação de Smart Contracts

**Verificação antes do deploy:**

```bash
# Verificar contrato com Slither
slither contracts/SLAContract.sol

# Verificar com Mythril
mythril analyze contracts/SLAContract.sol --execution-timeout 300

# Verificar com Solhint
solhint contracts/SLAContract.sol
```

**Assinatura de contratos:**

```bash
# Assinar contrato compilado
cosign sign-blob \
  --key cosign.key \
  contracts/SLAContract.sol
```

### 6.2 Proteção de Chaves Privadas

**Armazenamento seguro:**

```yaml
# Usar External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: blockchain-private-key
  namespace: trisla
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: blockchain-keys
    creationPolicy: Owner
  data:
    - secretKey: private-key
      remoteRef:
        key: blockchain/keys
        property: private-key
```

**Uso de HSM (Hardware Security Module):**

```python
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Carregar chave de HSM (exemplo conceitual)
def load_key_from_hsm(key_id):
    """Carrega chave privada de HSM"""
    # Implementação específica do HSM
    # Nunca exportar chave privada
    return hsm_client.get_key(key_id)
```

### 6.3 Validação de Transações

**Validação antes de enviar:**

```python
def validate_transaction(tx_data):
    """Valida transação antes de enviar para blockchain"""
    # Verificar assinatura
    if not verify_signature(tx_data):
        raise ValueError("Invalid signature")
    
    # Verificar nonce
    if tx_data['nonce'] != get_next_nonce():
        raise ValueError("Invalid nonce")
    
    # Verificar gas limit
    if tx_data['gas'] > MAX_GAS_LIMIT:
        raise ValueError("Gas limit too high")
    
    # Verificar valor
    if tx_data['value'] < 0:
        raise ValueError("Invalid value")
    
    return True
```

### 6.4 Proteção contra Reentrancy

**Padrão Checks-Effects-Interactions:**

```solidity
// Contrato seguro contra reentrancy
contract SLAContract {
    mapping(address => uint256) private balances;
    bool private locked;
    
    modifier noReentrant() {
        require(!locked, "ReentrancyGuard: reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    function withdraw(uint256 amount) external noReentrant {
        // Checks
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Effects
        balances[msg.sender] -= amount;
        
        // Interactions
        payable(msg.sender).transfer(amount);
    }
}
```

---

## 7. Secrets & Tokens: Armazenamento Seguro

### 7.1 Armazenamento de Secrets no Kubernetes

**Uso de Secrets nativos (criptografados em repouso):**

```yaml
# Secret para JWT
apiVersion: v1
kind: Secret
metadata:
  name: jwt-secret
  namespace: trisla
type: Opaque
stringData:
  secret-key: <GENERATE_RANDOM_32_BYTES>
```

**Criptografia em repouso (etcd encryption):**

```yaml
# Configuração de criptografia do etcd
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <BASE64_ENCODED_32_BYTE_KEY>
      - identity: {}
```

### 7.2 External Secrets Operator

**Integração com Vault:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: trisla
spec:
  provider:
    vault:
      server: "https://vault.trisla.local:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "trisla-role"
          serviceAccountRef:
            name: external-secrets-sa
```

**Sincronização de secrets:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: nasp-credentials
  namespace: trisla
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: nasp-credentials
    creationPolicy: Owner
  data:
    - secretKey: auth-token
      remoteRef:
        key: nasp/credentials
        property: auth-token
```

### 7.3 GHCR + GitHub Actions + Kubernetes

**GitHub Actions com secrets:**

```yaml
# .github/workflows/build-and-push.yml
name: Build and Push Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Log in to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ghcr.io/abelisboa/trisla-sem-csmf:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Sign image
        uses: sigstore/cosign-installer@v2
      
      - name: Sign container image
        run: |
          cosign sign --yes \
            --key env://COSIGN_PRIVATE_KEY \
            --cert env://COSIGN_PUBLIC_KEY \
            ghcr.io/abelisboa/trisla-sem-csmf:${{ github.sha }}
        env:
          COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
          COSIGN_PUBLIC_KEY: ${{ secrets.COSIGN_PUBLIC_KEY }}
```

**Kubernetes usando imagePullSecrets:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ghcr-secret
  namespace: trisla
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <BASE64_DOCKER_CONFIG>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sem-csmf
  namespace: trisla
spec:
  template:
    spec:
      imagePullSecrets:
        - name: ghcr-secret
      containers:
        - name: sem-csmf
          image: ghcr.io/abelisboa/trisla-sem-csmf:latest
```

### 7.4 Rotação de Credenciais

**Script de rotação automática:**

```bash
#!/bin/bash
# rotate-secrets.sh

# Gerar novo secret
NEW_SECRET=$(openssl rand -base64 32)

# Atualizar no Kubernetes
kubectl create secret generic jwt-secret \
  --from-literal=secret-key="$NEW_SECRET" \
  --namespace=trisla \
  --dry-run=client -o yaml | kubectl apply -f -

# Reiniciar pods para usar novo secret
kubectl rollout restart deployment -n trisla

# Aguardar rollout
kubectl rollout status deployment -n trisla --timeout=5m
```

**Rotação via External Secrets:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: rotating-secret
  namespace: trisla
spec:
  refreshInterval: 24h  # Rotacionar diariamente
  secretStoreRef:
    name: vault-backend
  target:
    name: rotating-secret
  data:
    - secretKey: token
      remoteRef:
        key: secrets/rotating
        property: token
```

---

## 8. Imagens Seguras: Assinatura e Verificação

### 8.1 Assinatura com Cosign/Sigstore

**Assinatura de imagens:**

```bash
# Gerar par de chaves
cosign generate-key-pair

# Assinar imagem
cosign sign --key cosign.key \
  ghcr.io/abelisboa/trisla-sem-csmf:latest

# Verificar assinatura
cosign verify --key cosign.pub \
  ghcr.io/abelisboa/trisla-sem-csmf:latest
```

**Assinatura com OIDC (GitHub Actions):**

```bash
# Assinar com OIDC
cosign sign \
  --oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity https://github.com/abelisboa/TriSLA/.github/workflows/build.yml@refs/heads/main \
  ghcr.io/abelisboa/trisla-sem-csmf:latest
```

### 8.2 Verificação de Integridade

**Verificação no Kubernetes:**

```yaml
# Admission Controller para verificar assinaturas
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: cosign-verification
spec:
  webhooks:
    - name: cosign-verification.trisla.local
      clientConfig:
        service:
          name: cosign-verification-service
          namespace: trisla
          path: "/verify"
      rules:
        - operations: ["CREATE", "UPDATE"]
          apiGroups: [""]
          apiVersions: ["v1"]
          resources: ["pods"]
      admissionReviewVersions: ["v1"]
      sideEffects: None
```

**Verificação em runtime:**

```python
import subprocess
import json

def verify_image_signature(image_ref, public_key_path):
    """Verifica assinatura de imagem antes do uso"""
    result = subprocess.run(
        [
            'cosign', 'verify',
            '--key', public_key_path,
            '--output', 'json',
            image_ref
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise ValueError(f"Image signature verification failed: {result.stderr}")
    
    verification = json.loads(result.stdout)
    return verification
```

### 8.3 Scanning de Vulnerabilidades

**Scanning com Trivy:**

```bash
# Scan de vulnerabilidades
trivy image ghcr.io/abelisboa/trisla-sem-csmf:latest

# Scan com saída JSON
trivy image --format json \
  --output trivy-report.json \
  ghcr.io/abelisboa/trisla-sem-csmf:latest
```

**Integração no CI/CD:**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  pull_request:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/abelisboa/trisla-sem-csmf:latest
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## 9. Hardening dos Containers

### 9.1 Non-Root Execution

**Configuração no deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sem-csmf
  namespace: trisla
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
        - name: sem-csmf
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            runAsUser: 1000
            capabilities:
              drop:
                - ALL
```

**Dockerfile otimizado:**

```dockerfile
FROM python:3.11-slim

# Criar usuário não-root
RUN groupadd -r trisla && useradd -r -g trisla trisla

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=trisla:trisla . /app
WORKDIR /app

# Mudar para usuário não-root
USER trisla

# Expor porta
EXPOSE 8080

# Comando
CMD ["python", "src/main.py"]
```

### 9.2 Capabilities Removidas

**Lista de capabilities permitidas (mínimo):**

```yaml
securityContext:
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE  # Apenas se necessário para bind em porta < 1024
```

### 9.3 Seccomp e AppArmor

**Seccomp Profile:**

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "accept", "bind", "connect", "listen", "socket",
        "read", "write", "open", "close", "fstat",
        "poll", "epoll_wait", "epoll_ctl", "fcntl",
        "getpid", "getuid", "getgid", "geteuid", "getegid",
        "clock_gettime", "nanosleep", "exit", "exit_group"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

**Aplicação do profile:**

```yaml
securityContext:
  seccompProfile:
    type: Localhost
    localhostProfile: profiles/trisla-seccomp.json
```

**AppArmor Profile:**

```apparmor
# /etc/apparmor.d/trisla-sem-csmf
#include <tunables/global>

profile trisla-sem-csmf flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  
  # Permitir leitura de arquivos
  /app/** r,
  /etc/tls/** r,
  
  # Permitir escrita apenas em /tmp
  /tmp/** rw,
  
  # Negar acesso a sistema
  /proc/sys/** r,
  /sys/** r,
  
  # Negar execução de binários
  deny /bin/** x,
  deny /usr/bin/** x,
}
```

**Aplicação do profile:**

```yaml
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/sem-csmf: localhost/trisla-sem-csmf
```

### 9.4 Read-Only Root Filesystem

**Configuração:**

```yaml
securityContext:
  readOnlyRootFilesystem: true
  volumes:
    - name: tmp
      emptyDir: {}
    - name: var-run
      emptyDir: {}
```

**Montagem de volumes:**

```yaml
containers:
  - name: sem-csmf
    volumeMounts:
      - name: tmp
        mountPath: /tmp
      - name: var-run
        mountPath: /var/run
```

---

## 10. Hardening da Comunicação

### 10.1 TLS Obrigatório

**Configuração TLS 1.3:**

```yaml
# ConfigMap com configuração TLS
apiVersion: v1
kind: ConfigMap
metadata:
  name: tls-config
  namespace: trisla
data:
  tls.conf: |
    # TLS 1.3 obrigatório
    ssl_protocols TLSv1.3;
    ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
```

**Certificados com cert-manager:**

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: trisla-tls
  namespace: trisla
spec:
  secretName: trisla-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - trisla.local
    - *.trisla.local
  usages:
    - digital signature
    - key encipherment
    - server auth
```

### 10.2 mTLS Opcional

**Configuração mTLS para comunicação interna:**

```yaml
# Istio ServiceMesh para mTLS automático
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: trisla
spec:
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: trisla-authz
  namespace: trisla
spec:
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/trisla/sa/sem-csmf-sa"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/*"]
```

**Implementação manual (sem ServiceMesh):**

```python
import ssl
import grpc
from grpc import ssl_channel_credentials

# Configurar mTLS
def create_mtls_channel(server_address, cert_file, key_file, ca_file):
    """Cria canal gRPC com mTLS"""
    with open(cert_file, 'rb') as f:
        cert = f.read()
    with open(key_file, 'rb') as f:
        key = f.read()
    with open(ca_file, 'rb') as f:
        ca_cert = f.read()
    
    credentials = ssl_channel_credentials(
        root_certificates=ca_cert,
        private_key=key,
        certificate_chain=cert
    )
    
    return grpc.secure_channel(server_address, credentials)
```

### 10.3 Cipher Suites Seguros

**Configuração de cipher suites:**

```python
# Python SSL context
import ssl

context = ssl.create_default_context()
context.minimum_version = ssl.TLSVersion.TLSv1_3
context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
context.options |= ssl.OP_NO_SSLv2
context.options |= ssl.OP_NO_SSLv3
context.options |= ssl.OP_NO_TLSv1
context.options |= ssl.OP_NO_TLSv1_1
```

---

## 11. Segurança do Pipeline CI/CD

### 11.1 GitHub Actions Security

**Boas práticas:**

```yaml
# .github/workflows/secure-build.yml
name: Secure Build

on:
  push:
    branches: [main]

# Limitar permissões
permissions:
  contents: read
  packages: write
  id-token: write  # Para OIDC

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Para análise de segurança
      
      # Verificar secrets no código
      - name: Detect secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
      
      # Scan de dependências
      - name: Dependency scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      # Build seguro
      - name: Build
        run: |
          docker build \
            --build-arg BUILDKIT_INLINE_CACHE=1 \
            -t ghcr.io/abelisboa/trisla-sem-csmf:${{ github.sha }} \
            apps/sem-csmf/
      
      # Assinar imagem
      - name: Sign image
        uses: sigstore/cosign-installer@v2
      
      - name: Sign with OIDC
        run: |
          cosign sign \
            --oidc-issuer https://token.actions.githubusercontent.com \
            --certificate-identity ${{ github.event.repository.owner }}@${{ github.event.repository.name }}.github.workflows.build.yml@refs/heads/main \
            ghcr.io/abelisboa/trisla-sem-csmf:${{ github.sha }}
```

### 11.2 Proteção de Secrets no CI/CD

**Nunca expor secrets:**

```yaml
# ❌ ERRADO
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  run: echo "Secret: $SECRET_KEY"  # NUNCA FAZER ISSO

# ✅ CORRETO
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  run: |
    # Usar secret sem expor
    python script.py --secret "$SECRET_KEY"
    # Ou usar arquivo temporário
    echo "$SECRET_KEY" > /tmp/secret.txt
    python script.py --secret-file /tmp/secret.txt
    rm /tmp/secret.txt
```

### 11.3 Validação de Código

**Análise estática:**

```yaml
- name: Lint code
  run: |
    pylint apps/**/*.py
    flake8 apps/
    bandit -r apps/ -f json -o bandit-report.json

- name: Security scan
  uses: github/super-linter@v4
  env:
    DEFAULT_BRANCH: main
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    VALIDATE_ALL_CODEBASE: false
    VALIDATE_PYTHON: true
```

---

## 12. Auditoria Contínua

### 12.1 Logs

**Estrutura de logs:**

```python
import logging
import json
from datetime import datetime

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)

def audit_log(event_type, user, action, resource, result, metadata=None):
    """Registra evento de auditoria"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user': user,
        'action': action,
        'resource': resource,
        'result': result,
        'metadata': metadata or {},
        'source_ip': request.client.host if 'request' in globals() else None
    }
    logging.info(json.dumps(log_entry))
```

**Retenção de logs:**

```yaml
# ConfigMap para configuração de retenção
apiVersion: v1
kind: ConfigMap
metadata:
  name: log-retention-config
  namespace: trisla
data:
  retention.yaml: |
    retention:
      days: 90
      max_size: 10Gi
      compression: gzip
```

### 12.2 SLO Reports

**Geração de relatórios de segurança:**

```python
def generate_security_slo_report():
    """Gera relatório de SLO de segurança"""
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'security_metrics': {
            'failed_auth_attempts': get_failed_auth_count(),
            'tls_handshake_failures': get_tls_failures(),
            'rate_limit_hits': get_rate_limit_hits(),
            'blockchain_tx_failures': get_bc_tx_failures()
        },
        'compliance': {
            'tls_enabled': check_tls_enabled(),
            'mTLS_enabled': check_mtls_enabled(),
            'secrets_encrypted': check_secrets_encryption(),
            'containers_hardened': check_container_hardening()
        }
    }
    return report
```

### 12.3 Detecção de Anomalias

**Monitoramento de anomalias:**

```python
from prometheus_client import Counter, Histogram
import numpy as np

# Métricas
auth_failures = Counter('trisla_auth_failures_total', 'Total authentication failures')
request_latency = Histogram('trisla_request_latency_seconds', 'Request latency')

def detect_anomalies():
    """Detecta anomalias em métricas de segurança"""
    # Verificar taxa de falhas de autenticação
    failure_rate = auth_failures._value.get() / time_window
    
    if failure_rate > threshold:
        alert('HIGH_AUTH_FAILURE_RATE', {
            'rate': failure_rate,
            'threshold': threshold
        })
    
    # Verificar latência anormal
    p99_latency = np.percentile(request_latency._buckets, 99)
    if p99_latency > max_latency:
        alert('HIGH_LATENCY', {
            'p99': p99_latency,
            'max': max_latency
        })
```

**Alertas Prometheus:**

```yaml
# monitoring/prometheus/rules/security-alerts.yml
groups:
  - name: security
    rules:
      - alert: HighAuthFailureRate
        expr: rate(trisla_auth_failures_total[5m]) > 10
        for: 5m
        annotations:
          summary: "High authentication failure rate detected"
          description: "Authentication failure rate is {{ $value }} failures/sec"
      
      - alert: TLSHandshakeFailure
        expr: rate(trisla_tls_handshake_failures_total[5m]) > 5
        for: 5m
        annotations:
          summary: "TLS handshake failures detected"
          description: "TLS handshake failure rate is {{ $value }} failures/sec"
```

---

## 13. Checklist Final de Segurança

### 13.1 Checklist de Deploy (30+ Itens)

#### Infraestrutura e Cluster

- [ ] Kubernetes versão ≥ 1.26 com patches de segurança aplicados
- [ ] RBAC habilitado e configurado corretamente
- [ ] Network Policies (Calico) aplicadas para todos os pods
- [ ] Pod Security Standards configurados (restricted)
- [ ] etcd encryption at rest habilitado
- [ ] Audit logging habilitado no cluster
- [ ] Ingress Controller configurado com TLS obrigatório
- [ ] StorageClass configurada com encryption

#### Secrets e Credenciais

- [ ] Todos os secrets armazenados em Kubernetes Secrets (nunca em código)
- [ ] Secrets criptografados em repouso (etcd encryption)
- [ ] External Secrets Operator configurado (se usando Vault/externo)
- [ ] Rotação de secrets configurada e testada
- [ ] GHCR token criado com permissões mínimas (read:packages)
- [ ] imagePullSecrets configurado em todos os deployments
- [ ] JWT secret gerado com 32+ bytes aleatórios
- [ ] NASP auth token armazenado em Secret (não em values.yaml)
- [ ] Blockchain private keys armazenadas em Secret ou HSM
- [ ] PostgreSQL password gerado com 16+ caracteres aleatórios

#### Imagens e Containers

- [ ] Todas as imagens assinadas com Cosign/Sigstore
- [ ] Verificação de assinatura configurada (admission controller ou manual)
- [ ] Scanning de vulnerabilidades executado (Trivy/Snyk)
- [ ] Imagens atualizadas com patches de segurança
- [ ] Containers executam como non-root (runAsNonRoot: true)
- [ ] Read-only root filesystem habilitado quando possível
- [ ] Capabilities desnecessárias removidas (drop: ALL)
- [ ] Seccomp profile aplicado
- [ ] AppArmor profile aplicado (se disponível)
- [ ] Resources limits configurados para prevenir DoS

#### Comunicação e Rede

- [ ] TLS 1.3 obrigatório para todas as comunicações HTTP/gRPC
- [ ] mTLS configurado para comunicação interna (I-01, I-06)
- [ ] Certificados gerenciados via cert-manager
- [ ] Cipher suites seguros configurados
- [ ] Kafka configurado com SASL/SCRAM + TLS
- [ ] Network Policies restringem comunicação entre pods
- [ ] Ingress configurado com TLS e HSTS
- [ ] Rate limiting configurado em todos os endpoints públicos

#### Interfaces I-01 a I-07

- [ ] I-01 (gRPC): mTLS + JWT implementado
- [ ] I-02 (REST): TLS + JWT implementado
- [ ] I-03 (Kafka): SASL/SCRAM + TLS implementado
- [ ] I-04 (Kafka): Validação de assinatura implementada
- [ ] I-05 (Kafka): Autorização por domínio implementada
- [ ] I-06 (REST): mTLS + OAuth2 implementado
- [ ] I-07 (REST): TLS + JWT + Rate limiting implementado

#### Blockchain

- [ ] Smart contracts verificados com Slither/Mythril
- [ ] Contratos assinados antes do deploy
- [ ] Chaves privadas armazenadas em Secret ou HSM
- [ ] Validação de transações antes de enviar
- [ ] Proteção contra reentrancy implementada
- [ ] Gas limits configurados corretamente

#### CI/CD

- [ ] GitHub Actions com permissões mínimas
- [ ] Secrets nunca expostos em logs
- [ ] Análise estática de código (pylint, bandit, flake8)
- [ ] Scanning de dependências (Trivy, Snyk)
- [ ] Assinatura automática de imagens no CI/CD
- [ ] Validação de pull requests antes de merge

#### Monitoramento e Auditoria

- [ ] Logging estruturado implementado
- [ ] Logs não contêm informações sensíveis
- [ ] Retenção de logs configurada (90+ dias)
- [ ] Métricas de segurança exportadas (Prometheus)
- [ ] Alertas configurados para eventos de segurança
- [ ] SLO reports gerados regularmente
- [ ] Detecção de anomalias configurada

#### Documentação e Processos

- [ ] Documentação de segurança atualizada
- [ ] Runbooks de incidentes criados
- [ ] Processo de resposta a incidentes definido
- [ ] Testes de segurança executados regularmente
- [ ] Revisão de código de segurança realizada
- [ ] Treinamento de equipe em segurança realizado

### 13.2 Validação Contínua

**Script de validação automática:**

```bash
#!/bin/bash
# validate-security.sh

echo "🔒 Validando segurança do TriSLA..."

# Verificar secrets
echo "1. Verificando secrets..."
kubectl get secrets -n trisla | grep -q jwt-secret || exit 1

# Verificar network policies
echo "2. Verificando network policies..."
kubectl get networkpolicies -n trisla | wc -l | grep -q "^[0-9]\+$" || exit 1

# Verificar TLS
echo "3. Verificando certificados TLS..."
kubectl get certificates -n trisla | grep -q trisla-tls || exit 1

# Verificar non-root
echo "4. Verificando containers non-root..."
kubectl get pods -n trisla -o jsonpath='{.items[*].spec.securityContext.runAsNonRoot}' | grep -q true || exit 1

# Verificar imagePullSecrets
echo "5. Verificando imagePullSecrets..."
kubectl get deployments -n trisla -o jsonpath='{.items[*].spec.template.spec.imagePullSecrets[*].name}' | grep -q ghcr-secret || exit 1

echo "✅ Validação de segurança concluída"
```

---

## Conclusão

Este guia fornece uma base sólida para implementar segurança e hardening no TriSLA. A segurança é um processo contínuo, e este documento deve ser revisado e atualizado regularmente conforme novas ameaças são identificadas e novas práticas de segurança são desenvolvidas.

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão do TriSLA:** 1.0.0

**Referências:**
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

