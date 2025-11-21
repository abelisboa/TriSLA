"""
ML-NSMF - Machine Learning Network Slice Management Function
Aplicação principal FastAPI
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from predictor import RiskPredictor
from kafka_consumer import MetricsConsumer
from kafka_producer import PredictionProducer

# Configurar OpenTelemetry
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(
    endpoint="http://otlp-collector:4317",
    insecure=True
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

app = FastAPI(
    title="TriSLA ML-NSMF",
    description="Machine Learning Network Slice Management Function",
    version="1.0.0"
)

FastAPIInstrumentor.instrument_app(app)

# Inicializar componentes
predictor = RiskPredictor()
metrics_consumer = MetricsConsumer()
prediction_producer = PredictionProducer()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "module": "ml-nsmf"}


@app.post("/api/v1/predict")
async def predict_risk(metrics: dict):
    """
    Recebe métricas e retorna previsão de risco
    """
    with tracer.start_as_current_span("predict_risk") as span:
        # Normalizar métricas
        normalized = await predictor.normalize(metrics)
        
        # Prever risco
        prediction = await predictor.predict(normalized)
        
        # Explicar (XAI)
        explanation = await predictor.explain(prediction, normalized)
        
        # Enviar para Decision Engine via Kafka (I-03)
        await prediction_producer.send_prediction(prediction, explanation)
        
        span.set_attribute("prediction.risk", prediction.get("risk_level"))
        return {
            "prediction": prediction,
            "explanation": explanation
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

