"""
SEM-CSMF - Semantic-enhanced Communication Service Management Function
Aplicação principal FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intent_processor import IntentProcessor
from nest_generator_db import NESTGeneratorDB
from models.intent import Intent, IntentRequest, IntentResponse, SliceType, SLARequirements
from models.nest import NEST
from models.db_models import IntentModel
from database import get_db, init_db
from decision_engine_client import DecisionEngineHTTPClient
from auth import get_current_user, is_auth_enabled, get_current_user_optional
from services.semantic_generator import generate_default_sla
import logging
import uuid

logger = logging.getLogger(__name__)

# Configurar OpenTelemetry (opcional em modo DEV)
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

if otlp_enabled:
    try:
        # OTLP endpoint via variável de ambiente ou padrão
        otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://otlp-collector:4317")
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    except Exception as e:
        print(f"⚠️ OTLP não disponível, continuando sem observabilidade: {e}")
else:
    print("ℹ️ SEM-CSMF: Modo DEV - OTLP desabilitado (OTLP_ENABLED=false)")

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

# Rotas estão definidas diretamente neste arquivo (main.py)
# Não há necessidade de importar router externo

# Inicializar processadores
intent_processor = IntentProcessor()

# Cliente HTTP para Decision Engine
# Usa DECISION_ENGINE_URL (padrão: http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate)
decision_engine_client = DecisionEngineHTTPClient()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "module": "sem-csmf"}


@app.get("/metrics")
async def metrics():
    """Expor métricas Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/v1/interpret")
async def interpret_intent(
    request: dict,
    db: Session = Depends(get_db),
    current_user: str = get_current_user_optional()
):
    """
    Endpoint minimalista para interpretação PNL
    Aceita apenas { "intent": "texto" } e infere service_type e sla_requirements
    """
    from models.intent import Intent, SliceType, SLARequirements
    import uuid
    
    intent_text = request.get("intent")
    if not intent_text or not intent_text.strip():
        raise HTTPException(status_code=400, detail="Campo 'intent' é obrigatório")
    
    tenant_id = request.get("tenant_id", "default")
    
    with tracer.start_as_current_span("interpret_intent") as span:
        span.set_attribute("intent.text", intent_text[:100])  # Primeiros 100 chars
        
        try:
            # 1. Processar texto com NLP para inferir service_type e sla_requirements
            nlp_result = None
            if intent_processor.nlp_parser:
                try:
                    nlp_result = intent_processor.nlp_parser.parse_intent_text(intent_text)
                except Exception as e:
                    logger.warning(f"NLP parser error: {e}")
            
            # 2. Inferir service_type
            inferred_service_type = SliceType.EMBB  # Default
            if nlp_result and nlp_result.get("slice_type"):
                try:
                    inferred_service_type = SliceType[nlp_result["slice_type"].upper()]
                except (KeyError, AttributeError):
                    # Fallback: inferir do texto
                    intent_upper = intent_text.upper()
                    if "URLLC" in intent_upper or "LATENCIA" in intent_upper or "LATENCY" in intent_upper or "CIRURGIA" in intent_upper or "SURGERY" in intent_upper:
                        inferred_service_type = SliceType.URLLC
                    elif "MMTC" in intent_upper or "IOT" in intent_upper or "DEVICE" in intent_upper or "SENSOR" in intent_upper:
                        inferred_service_type = SliceType.MMTC
                    elif "EMBB" in intent_upper or "BROADBAND" in intent_upper or "BANDA" in intent_upper:
                        inferred_service_type = SliceType.EMBB
            
            # 3. Construir SLA requirements a partir do NLP ou valores padrão
            sla_req_dict = {}
            if nlp_result and nlp_result.get("requirements"):
                sla_req_dict = nlp_result["requirements"]
            else:
                # Valores padrão baseados no service_type
                if inferred_service_type == SliceType.URLLC:
                    sla_req_dict = {
                        "latency": "10ms",
                        "reliability": 0.99999,
                        "jitter": "5ms"
                    }
                elif inferred_service_type == SliceType.MMTC:
                    sla_req_dict = {
                        "device_density": 10000,  # IoT massivo
                        "coverage": "Urban"
                    }
                else:  # eMBB
                    sla_req_dict = {
                        "throughput": "100Mbps",
                        "reliability": 0.99
                    }
            
            sla_requirements = SLARequirements(**sla_req_dict)
            
            # 4. Criar Intent completo
            intent_id = str(uuid.uuid4())
            intent = Intent(
                intent_id=intent_id,
                tenant_id=tenant_id,
                service_type=inferred_service_type,
                sla_requirements=sla_requirements
            )
            
            # 5. Validar semanticamente
            validated_intent = await intent_processor.validate_semantic(intent, intent_text)
            
            # 6. Gerar GST e NEST
            gst = await intent_processor.generate_gst(validated_intent)
            nest_generator = NESTGeneratorDB(db)
            nest = await nest_generator.generate_nest(gst)
            
            span.set_attribute("intent.id", intent_id)
            span.set_attribute("nest.id", nest.nest_id)
            span.set_attribute("service_type", validated_intent.service_type.value)
            
            # 7. Retornar resposta padronizada
            return {
                "intent_id": intent_id,
                "nest_id": nest.nest_id,
                "service_type": validated_intent.service_type.value,
                "slice_type": validated_intent.service_type.value,  # Compatibilidade
                "sla_requirements": validated_intent.sla_requirements.model_dump(),
                "status": "accepted",
                "message": "Intent interpretado e NEST gerado com sucesso"
            }
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            logger.error(f"Erro ao interpretar intent: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro ao interpretar intent: {str(e)}")


@app.post("/api/v1/intents", response_model=IntentResponse)
async def create_intent(
    request: IntentRequest,
    db: Session = Depends(get_db),
    current_user: str = get_current_user_optional()
):
    """
    Recebe intent e processa através do pipeline:
    Intent → Ontology → GST → NEST → Database → Decision Engine (I-01)
    
    Aceita payload mínimo: service_type + intent
    sla_requirements será gerado internamente se não fornecido
    """
    # current_user será None se autenticação estiver desabilitada
    
    # Converter service_type string para enum
    # Mapear "eMBB" para "EMBB" (enum interno)
    try:
        if request.service_type == "eMBB":
            service_type_enum = SliceType.EMBB
        elif request.service_type == "URLLC":
            service_type_enum = SliceType.URLLC
        elif request.service_type == "mMTC":
            service_type_enum = SliceType.MMTC
        else:
            raise HTTPException(status_code=400, detail=f"service_type inválido: {request.service_type}. Deve ser URLLC, eMBB ou mMTC")
    except (KeyError, AttributeError) as e:
        raise HTTPException(status_code=400, detail=f"service_type inválido: {request.service_type}. Deve ser URLLC, eMBB ou mMTC. Erro: {str(e)}")
    
    # Gerar intent_id se não fornecido
    intent_id = str(uuid.uuid4())
    tenant_id = request.tenant_id or "default"
    
    # FASE 3: Gerar sla_requirements se não fornecido
    if request.sla_requirements is None:
        sla_req_dict = generate_default_sla(request.service_type)
        logger.info(f"🔧 Gerando sla_requirements default para {request.service_type}: {sla_req_dict}")
    else:
        sla_req_dict = request.sla_requirements
    
    # Converter dict para SLARequirements
    sla_requirements = SLARequirements(**sla_req_dict)
    
    # Construir Intent completo
    intent = Intent(
        intent_id=intent_id,
        tenant_id=tenant_id,
        service_type=service_type_enum,
        sla_requirements=sla_requirements,
        intent_text=request.intent,
        metadata={}
    )
    
    with tracer.start_as_current_span("process_intent") as span:
        span.set_attribute("intent.id", intent.intent_id)
        span.set_attribute("intent.type", intent.service_type.value)
        
        try:
            # 1. Persistir Intent no banco de dados
            intent_model = IntentModel(
                intent_id=intent.intent_id,
                tenant_id=intent.tenant_id,
                service_type=intent.service_type.value,
                sla_requirements=intent.sla_requirements.model_dump() if intent.sla_requirements else {},
                extra_metadata=intent.metadata
            )
            db.add(intent_model)
            db.commit()
            
            # 3. Validar intent semanticamente (Ontology)
            # Se intent_text foi fornecido, usar para enriquecimento semântico
            validated_intent = await intent_processor.validate_semantic(intent, intent_text=intent.intent_text)
            
            # 4. Gerar GST (Generation Service Template)
            gst = await intent_processor.generate_gst(validated_intent)
            
            # 5. Gerar NEST (Network Slice Template) com persistência
            nest_generator = NESTGeneratorDB(db)
            nest = await nest_generator.generate_nest(gst)
            
            # 6. Gerar metadados para Decision Engine
            metadata = await intent_processor.generate_metadata(intent, nest)
            
            # 7. Enviar metadados via I-01 (HTTP) para Decision Engine
            decision_response = await decision_engine_client.send_nest_metadata(
                intent_id=intent.intent_id,
                nest_id=nest.nest_id,
                tenant_id=intent.tenant_id,
                service_type=intent.service_type.value,
                sla_requirements=intent.sla_requirements.model_dump() if intent.sla_requirements else {},
                nest_status=nest.status.value,
                metadata=metadata
            )
            
            span.set_attribute("nest.id", nest.nest_id)
            span.set_attribute("nest.status", "generated")
            if decision_response.get("decision_id"):
            span.set_attribute("decision.id", decision_response.get("decision_id"))
            span.set_attribute("decision_engine.success", decision_response.get("success", False))
            
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
    # Validação: NEST existe no banco de dados (via repository)
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

