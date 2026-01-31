"""
ML-NSMF - Machine Learning Network Slice Management Function
Aplicação principal FastAPI
"""

from fastapi import FastAPI, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from predictor import RiskPredictor
from kafka_consumer import MetricsConsumer
from kafka_producer import PredictionProducer
from nasp_prometheus_client import PrometheusClient

# Configurar OpenTelemetry (opcional em modo DEV)
otlp_enabled = os.getenv("OTLP_ENABLED", "false").lower() == "true"
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

if otlp_enabled:
    try:
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://otlp-collector:4317",
            insecure=True
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
    except Exception as e:
        print(f"⚠️ OTLP não disponível, continuando sem observabilidade: {e}")

app = FastAPI(
    title="TriSLA ML-NSMF",
    description="Machine Learning Network Slice Management Function",
    version="3.10.0"
)

FastAPIInstrumentor.instrument_app(app)

# Inicializar componentes
predictor = RiskPredictor()
metrics_consumer = MetricsConsumer()  # Kafka opcional
prediction_producer = PredictionProducer()  # Kafka opcional
prometheus_client = PrometheusClient()  # FASE C2: Cliente Prometheus real


@app.get("/health")
async def health():
    """Health check endpoint"""
    kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
    kafka_status = "enabled" if kafka_enabled else "offline"
    
    return {
        "status": "healthy",
        "module": "ml-nsmf",
        "kafka": kafka_status,
        "predictor": "ready" if predictor else "not_ready"
    }


@app.get("/metrics")
async def metrics():
    """Expor métricas Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/api/v1/predict")
async def predict_risk(metrics: dict):
    """
    Recebe métricas e retorna previsão de risco baseada em dados reais do NASP
    
    FASE C2: Coleta métricas reais do Prometheus antes de fazer predição
    """
    import logging
    logger = logging.getLogger(__name__)
    
    with tracer.start_as_current_span("predict_risk") as span:
        # FASE C2: Coletar métricas reais do Prometheus
        slice_id = metrics.get("slice_id") or metrics.get("nest_id")
        time_range_minutes = int(metrics.get("time_range_minutes", 10))
        from datetime import timedelta
        time_range = timedelta(minutes=time_range_minutes)
        
        logger.info(f"🔍 FASE C2: Coletando métricas reais do Prometheus (slice_id={slice_id}, janela={time_range_minutes}min)")
        
        # Coletar métricas reais do NASP
        real_metrics = await prometheus_client.collect_all_metrics(slice_id, time_range)
        
        # Mesclar métricas reais com métricas fornecidas (métricas reais têm prioridade)
        if real_metrics:
            logger.info(f"✅ Métricas reais coletadas: {list(real_metrics.keys())}")
            # Atualizar métricas com valores reais
            for key, value in real_metrics.items():
                if value is not None:
                    metrics[key] = value
                    span.set_attribute(f"metrics.real.{key}", value)
        else:
            logger.warning("⚠️ Nenhuma métrica real coletada do Prometheus - usando métricas fornecidas")
            span.set_attribute("metrics.real_collected", False)
        
        # Normalizar métricas (agora com dados reais)
        normalized = predictor.normalize(metrics)
        
        # Prever risco baseado em métricas reais
        prediction = predictor.predict(normalized)
        
        # Marcar que métricas reais foram usadas
        prediction["metrics_used"] = {
            "real_metrics_count": len(real_metrics),
            "real_metrics": list(real_metrics.keys()) if real_metrics else [],
            "time_range_minutes": time_range_minutes
        }
        
        # Explicar (XAI)
        explanation = predictor.explain(prediction, normalized)
        
        # Enviar para Decision Engine via Kafka (I-03)
        await prediction_producer.send_prediction(prediction, explanation)
        
        span.set_attribute("prediction.risk", prediction.get("risk_level"))
        span.set_attribute("prediction.metrics_real", bool(real_metrics))
        
        logger.info(f"✅ Predição gerada: risk_level={prediction.get('risk_level')}, risk_score={prediction.get('risk_score'):.2f}")
        
        return {
            "prediction": prediction,
            "explanation": explanation,
            "metrics_used": prediction["metrics_used"]
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

