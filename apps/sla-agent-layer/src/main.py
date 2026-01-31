"""
SLA-Agent Layer - Agentes Federados
Agent-RAN, Agent-Transport, Agent-Core
"""

from fastapi import FastAPI, HTTPException, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_ran import AgentRAN
from agent_transport import AgentTransport
from agent_core import AgentCore
from kafka_consumer import ActionConsumer
from agent_coordinator import AgentCoordinator

# OpenTelemetry (opcional em modo DEV)
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

if otlp_enabled:
    try:
        otlp_exporter = OTLPSpanExporter(endpoint="http://otlp-collector:4317", insecure=True)
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    except Exception as e:
        print(f"⚠️ OTLP não disponível, continuando sem observabilidade: {e}")

app = FastAPI(title="TriSLA SLA-Agent Layer", version="3.10.0")
FastAPIInstrumentor.instrument_app(app)

# Inicializar agentes
agent_ran = AgentRAN()
agent_transport = AgentTransport()
agent_core = AgentCore()
agents = [agent_ran, agent_transport, agent_core]

# Inicializar coordenador de agentes
agent_coordinator = AgentCoordinator(agents)

# Inicializar consumer Kafka
action_consumer = ActionConsumer(agents)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "sla-agent-layer",
        "agents": {
            "ran": agent_ran.is_healthy(),
            "transport": agent_transport.is_healthy(),
            "core": agent_core.is_healthy()
        }
    }


@app.get("/metrics")
async def metrics():
    """Expor métricas Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/v1/agents/ran/collect")
async def collect_ran_metrics():
    """Coleta métricas do domínio RAN"""
    return await agent_ran.collect_metrics()


@app.post("/api/v1/agents/ran/action")
async def execute_ran_action(action: dict):
    """Executa ação corretiva no RAN (I-06)"""
    return await agent_ran.execute_action(action)


@app.post("/api/v1/agents/transport/collect")
async def collect_transport_metrics():
    """Coleta métricas do domínio Transport"""
    return await agent_transport.collect_metrics()


@app.post("/api/v1/agents/transport/action")
async def execute_transport_action(action: dict):
    """Executa ação corretiva no Transport (I-06)"""
    return await agent_transport.execute_action(action)


@app.post("/api/v1/agents/core/collect")
async def collect_core_metrics():
    """Coleta métricas do domínio Core"""
    return await agent_core.collect_metrics()


@app.post("/api/v1/agents/core/action")
async def execute_core_action(action: dict):
    """Executa ação corretiva no Core (I-06)"""
    return await agent_core.execute_action(action)


@app.get("/api/v1/metrics/realtime")
async def get_realtime_metrics():
    """
    Retorna métricas em tempo real de todos os domínios
    Agrega métricas de RAN, Transport e Core
    """
    with tracer.start_as_current_span("get_realtime_metrics") as span:
        try:
            # Coletar métricas de todos os agentes
            ran_metrics = await agent_ran.collect_metrics()
            transport_metrics = await agent_transport.collect_metrics()
            core_metrics = await agent_core.collect_metrics()
            
            # Agregar métricas
            aggregated = {
                "timestamp": agent_ran._get_timestamp(),
                "domains": {
                    "ran": {**ran_metrics, "status": "healthy"},
                    "transport": {**transport_metrics, "status": "healthy"},
                    "core": {**core_metrics, "status": "healthy"}
                },
                "summary": {
                    "total_domains": 3,
                    "healthy_domains": 3
                }
            }
            
            span.set_attribute("metrics.domains", 3)
            return aggregated
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/slos")
async def get_slos():
    """
    Retorna SLOs (Service Level Objectives) configurados
    e status de compliance de cada domínio
    """
    with tracer.start_as_current_span("get_slos") as span:
        try:
            # Usar coordenador para avaliar todos os SLOs
            evaluation = await agent_coordinator.evaluate_all_slos()
            
            span.set_attribute("slos.overall_compliance", evaluation.get("overall_compliance", 0.0))
            return evaluation
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/coordinate")
async def coordinate_action(action: dict, target_domains: list = None):
    """
    Coordena ação entre múltiplos domínios (Interface I-06)
    
    Body:
        {
            "type": "action-type",
            "parameters": {...},
            "target_domains": ["RAN", "Transport", "Core"]  # Opcional
        }
    """
    with tracer.start_as_current_span("coordinate_action_i06") as span:
        try:
            result = await agent_coordinator.coordinate_action(action, target_domains)
            span.set_attribute("coordination.success_rate", result.get("success_rate", 0.0))
            return result
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/policies/federated")
async def apply_federated_policy(policy: dict):
    """
    Aplica política federada aos agentes (Interface I-06)
    
    Body:
        {
            "name": "policy-name",
            "priority": "high" | "medium" | "low",
            "domains": ["RAN", "Transport", "Core"],
            "actions": [
                {
                    "domain": "RAN",
                    "action": {...},
                    "depends_on": ["Transport"]  # Opcional
                }
            ]
        }
    """
    with tracer.start_as_current_span("apply_federated_policy_i06") as span:
        try:
            result = await agent_coordinator.apply_federated_policy(policy)
            span.set_attribute("policy.name", result.get("policy_name", "unknown"))
            span.set_attribute("policy.success_rate", result.get("success_rate", 0.0))
            return result
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))




@app.post("/api/v1/s29/create-snapshot")
async def create_snapshot_s29(request: dict):
    """Cria snapshot causal para um SLA (S29)"""
    sla_id = request.get("sla_id")
    slice_type = request.get("slice_type", "EMBB")
    sla_requirements = request.get("sla_requirements")
    
    if not sla_id:
        raise HTTPException(status_code=400, detail="sla_id é obrigatório")
    
    result = await agent_coordinator.create_causal_snapshot_for_sla(
        sla_id=sla_id,
        slice_type=slice_type,
        sla_requirements=sla_requirements
    )
    
    return result


@app.post("/api/v1/s29/generate-explanation")
async def generate_explanation_s29(request: dict):
    """Gera explicação causal para uma decisão (S29)"""
    sla_id = request.get("sla_id")
    decision = request.get("decision")
    slice_type = request.get("slice_type", "EMBB")
    sla_requirements = request.get("sla_requirements")
    
    if not sla_id or not decision:
        raise HTTPException(status_code=400, detail="sla_id e decision são obrigatórios")
    
    result = await agent_coordinator.generate_causal_explanation_for_decision(
        sla_id=sla_id,
        decision=decision,
        slice_type=slice_type,
        sla_requirements=sla_requirements
    )
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)

