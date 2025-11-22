"""
SEM-CSMF - Semantic-enhanced Communication Service Management Function
Aplicação principal FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intent_processor import IntentProcessor
from nest_generator_db import NESTGeneratorDB
from models.intent import Intent, IntentResponse
from models.nest import NEST
from models.db_models import IntentModel
from database import get_db, init_db
from grpc_client import DecisionEngineClient
from grpc_client_retry import DecisionEngineClientWithRetry
from kafka_producer_retry import KafkaProducerWithRetry
from auth import get_current_user, is_auth_enabled, get_current_user_optional

# Importar router do novo módulo SEM-CSMF
try:
    # Adicionar caminho para src/ na raiz do projeto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    src_path = os.path.join(project_root, "src")
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from sem_csmf.api_rest import router as sem_router
    app.include_router(sem_router)
except ImportError as e:
    # Se o módulo não estiver disponível, continuar sem ele
    print(f"Aviso: Não foi possível importar router do sem_csmf: {e}")
except Exception as e:
    print(f"Aviso: Erro ao registrar router do sem_csmf: {e}")

# Configurar OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# OTLP endpoint via variável de ambiente ou padrão
otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://otlp-collector:4317")
otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    insecure=True
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(
    title="TriSLA SEM-CSMF",
    description="Semantic-enhanced Communication Service Management Function",
    version="1.0.0"
)

# Security Middleware
from security import RateLimitMiddleware, SecurityHeadersMiddleware

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrumentar FastAPI com OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Inicializar banco de dados
init_db()

# Importar e registrar router do novo módulo SEM-CSMF
try:
    # Adicionar caminho para src/ na raiz do projeto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    src_path = os.path.join(project_root, "src")
    if os.path.exists(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from sem_csmf.api_rest import router as sem_router
    app.include_router(sem_router)
    print("Router do sem_csmf registrado com sucesso")
except ImportError as e:
    # Se o módulo não estiver disponível, continuar sem ele
    print(f"Aviso: Não foi possível importar router do sem_csmf: {e}")
except Exception as e:
    print(f"Aviso: Erro ao registrar router do sem_csmf: {e}")

# Inicializar processadores
# Carregar caminho da ontologia OWL (padrão: trisla.owl no diretório ontology/)
ontology_path = os.getenv(
    "TRISLA_ONTOLOGY_PATH",
    os.path.join(os.path.dirname(__file__), "ontology", "trisla.owl")
)
intent_processor = IntentProcessor(ontology_path=ontology_path)

# Cliente gRPC para Decision Engine (com retry)
# Usar cliente com retry em produção, cliente simples em desenvolvimento
USE_RETRY_CLIENT = os.getenv("USE_GRPC_RETRY", "true").lower() == "true"
if USE_RETRY_CLIENT:
    grpc_client = DecisionEngineClientWithRetry()
else:
    grpc_client = DecisionEngineClient()

# Kafka Producer para I-02 (SEM-CSMF → ML-NSMF)
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:29092"  # Porta mapeada do docker-compose
).split(",")
KAFKA_TOPIC_I02 = os.getenv("KAFKA_TOPIC_I02", "I-02-intent-to-ml")
kafka_producer = None
try:
    kafka_producer = KafkaProducerWithRetry(KAFKA_BOOTSTRAP_SERVERS)
    print(f"Kafka Producer inicializado para tópico: {KAFKA_TOPIC_I02}")
except Exception as e:
    print(f"Aviso: Não foi possível inicializar Kafka Producer: {e}")
    print("Publicação no Kafka será ignorada")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "module": "sem-csmf"}


@app.post("/api/v1/intents", response_model=IntentResponse)
async def create_intent(
    intent: Intent,
    db: Session = Depends(get_db),
    current_user: str = get_current_user_optional()
):
    """
    Recebe intent e processa através do pipeline:
    Intent → Ontology → GST → NEST → Database → Decision Engine (I-01)
    """
    # current_user será None se autenticação estiver desabilitada
    with tracer.start_as_current_span("process_intent") as span:
        span.set_attribute("intent.id", intent.intent_id)
        span.set_attribute("intent.type", intent.service_type.value)
        
        try:
            # 1. Persistir Intent no banco de dados
            intent_model = IntentModel(
                intent_id=intent.intent_id,
                tenant_id=intent.tenant_id,
                service_type=intent.service_type.value,
                sla_requirements=intent.sla_requirements.dict(),
                extra_metadata=intent.metadata
            )
            db.add(intent_model)
            db.commit()
            
            # 2. Validar intent semanticamente (Ontology)
            validated_intent = await intent_processor.validate_semantic(intent)
            
            # 3. Gerar GST (Generation Service Template)
            gst = await intent_processor.generate_gst(validated_intent)
            
            # 4. Gerar NEST (Network Slice Template) com persistência
            nest_generator = NESTGeneratorDB(db)
            nest = await nest_generator.generate_nest(gst)
            
            # 5. Publicar NEST no Kafka (I-02: SEM-CSMF → ML-NSMF)
            kafka_success = False
            if kafka_producer:
                try:
                    # Preparar mensagem para I-02
                    i02_message = {
                        "interface": "I-02",
                        "source": "sem-csmf",
                        "destination": "ml-nsmf",
                        "intent_id": intent.intent_id,
                        "nest_id": nest.nest_id,
                        "tenant_id": intent.tenant_id,
                        "service_type": intent.service_type.value,
                        "semantic_validation": "success",
                        "gst": gst,
                        "nest": {
                            "nest_id": nest.nest_id,
                            "intent_id": nest.intent_id,
                            "status": nest.status.value,
                            "network_slices": [
                                {
                                    "slice_id": slice.slice_id,
                                    "slice_type": slice.slice_type,
                                    "resources": slice.resources,
                                    "status": slice.status.value if hasattr(slice.status, 'value') else str(slice.status),
                                    "metadata": slice.metadata
                                }
                                for slice in nest.network_slices
                            ],
                            "metadata": nest.metadata
                        },
                        "sla_requirements": intent.sla_requirements.dict(),
                        "timestamp": metadata.get("timestamp", "")
                    }
                    
                    kafka_success = await kafka_producer.send_with_retry(
                        topic=KAFKA_TOPIC_I02,
                        value=i02_message,
                        key=intent.intent_id  # Usar intent_id como chave para particionamento
                    )
                    span.set_attribute("kafka.i02.success", kafka_success)
                    span.set_attribute("kafka.i02.topic", KAFKA_TOPIC_I02)
                    if kafka_success:
                        print(f"✅ NEST publicado no Kafka (I-02): {nest.nest_id}")
                    else:
                        print(f"⚠️ Falha ao publicar NEST no Kafka (I-02): {nest.nest_id}")
                except Exception as kafka_error:
                    span.record_exception(kafka_error)
                    span.set_attribute("kafka.i02.success", False)
                    print(f"⚠️ Erro ao publicar no Kafka (I-02): {kafka_error}")
            else:
                print("⚠️ Kafka Producer não disponível - publicação I-02 ignorada")
            
            # 6. Gerar metadados para Decision Engine
            metadata = await intent_processor.generate_metadata(intent, nest)
            
            # 7. Enviar metadados via I-01 (gRPC) para Decision Engine
            decision_response = await grpc_client.send_nest_metadata(
                intent_id=intent.intent_id,
                nest_id=nest.nest_id,
                tenant_id=intent.tenant_id,
                service_type=intent.service_type.value,
                sla_requirements=intent.sla_requirements.dict(),
                nest_status=nest.status.value,
                metadata=metadata
            )
            
            span.set_attribute("nest.id", nest.nest_id)
            span.set_attribute("nest.status", "generated")
            span.set_attribute("decision.id", decision_response.get("decision_id"))
            span.set_attribute("grpc.success", decision_response.get("success", False))
            
            return IntentResponse(
                intent_id=intent.intent_id,
                status="accepted",
                nest_id=nest.nest_id,
                message=f"Intent processed and NEST generated. Decision Engine: {decision_response.get('message', 'N/A')}"
            )
            
        except Exception as e:
            db.rollback()
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/nest")
async def create_nest(
    nest_data: dict,
    db: Session = Depends(get_db),
    current_user: str = get_current_user_optional()
):
    """Cria ou atualiza um NEST (Interface I-02)"""
    with tracer.start_as_current_span("create_nest") as span:
        nest_id = nest_data.get("nest_id")
        span.set_attribute("nest.id", nest_id)
        
        try:
            # Processar criação de NEST
            # Em produção, isso viria do Decision Engine via I-01
            return {
                "status": "created",
                "nest_id": nest_id,
                "message": "NEST created successfully"
            }
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/auth/login")
async def login(credentials: dict):
    """
    Endpoint de login (gera token JWT)
    Em produção, validar credenciais contra banco de dados
    """
    from auth import create_access_token, verify_password
    from datetime import timedelta
    
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username e password são obrigatórios")
    
    # Autenticação simples (em produção, buscar do banco de dados)
    # TODO: Implementar validação real contra banco de dados
    # Por enquanto, usar credenciais mock para desenvolvimento
    if username and password:
        # Gerar token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 1800  # 30 minutos
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas"
        )


@app.get("/api/v1/nests/{nest_id}", response_model=NEST)
async def get_nest(
    nest_id: str,
    db: Session = Depends(get_db),
    current_user: str = get_current_user_optional()
):
    """Retorna NEST gerado do banco de dados"""
    with tracer.start_as_current_span("get_nest") as span:
        span.set_attribute("nest.id", nest_id)
        
        nest_generator = NESTGeneratorDB(db)
        nest = await nest_generator.get_nest(nest_id)
        if not nest:
            raise HTTPException(status_code=404, detail="NEST not found")
        
        return nest


@app.get("/api/v1/slices")
async def list_slices(
    db: Session = Depends(get_db),
    current_user: str = get_current_user_optional()
):
    """
    Lista todos os network slices ativos do banco de dados
    Retorna slices de todos os NESTs gerados
    """
    with tracer.start_as_current_span("list_slices") as span:
        try:
            # Obter todos os NESTs do banco
            nest_generator = NESTGeneratorDB(db)
            all_nests = await nest_generator.list_all_nests()
            
            # Extrair todos os slices
            all_slices = []
            for nest in all_nests:
                for network_slice in nest.network_slices:
                    slice_data = {
                        "slice_id": network_slice.slice_id,
                        "nest_id": nest.nest_id,
                        "intent_id": nest.intent_id,
                        "slice_type": network_slice.slice_type,
                        "status": network_slice.status.value if hasattr(network_slice.status, 'value') else str(network_slice.status),
                        "resources": network_slice.resources,
                        "metadata": network_slice.metadata
                    }
                    all_slices.append(slice_data)
            
            span.set_attribute("slices.count", len(all_slices))
            return {
                "slices": all_slices,
                "total": len(all_slices),
                "active": len([s for s in all_slices if s["status"] == "active"]),
                "generated": len([s for s in all_slices if s["status"] == "generated"])
            }
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

