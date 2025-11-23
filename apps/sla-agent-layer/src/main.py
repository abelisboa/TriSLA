"""
SLA-Agent Layer - Agentes Federados
Agent-RAN, Agent-Transport, Agent-Core
"""

from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_ran import AgentRAN
from agent_transport import AgentTransport
from agent_core import AgentCore
from kafka_consumer import ActionConsumer

# OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(endpoint="http://otlp-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(title="TriSLA SLA-Agent Layer", version="1.0.0")
FastAPIInstrumentor.instrument_app(app)

# Inicializar agentes
agent_ran = AgentRAN()
agent_transport = AgentTransport()
agent_core = AgentCore()
action_consumer = ActionConsumer([agent_ran, agent_transport, agent_core])


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
            # Obter SLOs de cada agente
            ran_slos = await agent_ran.get_slos()
            transport_slos = await agent_transport.get_slos()
            core_slos = await agent_core.get_slos()
            
            all_slos = {
                "timestamp": agent_ran._get_timestamp(),
                "slos": {
                    "ran": ran_slos,
                    "transport": transport_slos,
                    "core": core_slos
                },
                "compliance": {
                    "ran": ran_slos.get("compliance_rate", 0.0),
                    "transport": transport_slos.get("compliance_rate", 0.0),
                    "core": core_slos.get("compliance_rate", 0.0)
                },
                "overall_compliance": (
                    ran_slos.get("compliance_rate", 0.0) +
                    transport_slos.get("compliance_rate", 0.0) +
                    core_slos.get("compliance_rate", 0.0)
                ) / 3.0
            }
            
            span.set_attribute("slos.count", len(all_slos["slos"]))
            return all_slos
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8084)

