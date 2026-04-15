# === TRISLA_OBSERVABILITY_BEGIN ===
import os
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

TRISLA_HTTP_REQUESTS_TOTAL = Counter(
    "trisla_http_requests_total",
    "Total de requisições HTTP por serviço e rota",
    ["service", "method", "path", "status"]
)

TRISLA_HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "trisla_http_request_duration_seconds",
    "Duração de requisições HTTP em segundos por serviço e rota",
    ["service", "method", "path"]
)

TRISLA_PROCESS_CPU_SECONDS_TOTAL = Gauge(
    "trisla_process_cpu_seconds_total",
    "CPU seconds placeholder",
    ["service"]
)

def _trisla_setup_otel(service_name: str):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://trisla-otel-collector.trisla.svc.cluster.local:4317"
        )

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)

        return FastAPIInstrumentor

    except Exception:
        return None


def _trisla_attach_observability(app: FastAPI, service_name: str):

    @app.middleware("http")
    async def _trisla_prom_mw(request: Request, call_next):
        method = request.method
        path = request.url.path

        with TRISLA_HTTP_REQUEST_DURATION_SECONDS.labels(
            service=service_name,
            method=method,
            path=path
        ).time():
            response = await call_next(request)

        TRISLA_HTTP_REQUESTS_TOTAL.labels(
            service=service_name,
            method=method,
            path=path,
            status=str(response.status_code)
        ).inc()

        return response


    @app.get("/metrics")
    async def _metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    instr = _trisla_setup_otel(service_name)
    if instr:
        try:
            instr.instrument_app(app)
        except Exception:
            pass

# === TRISLA_OBSERVABILITY_END ===


"""
ML-NSMF
"""

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from predictor import RiskPredictor
from slice_risk_adjustment import compute_slice_adjusted_risk
from kafka_consumer import MetricsConsumer
from kafka_producer import PredictionProducer
from nasp_prometheus_client import PrometheusClient


app = FastAPI(
    title="TriSLA ML-NSMF",
    description="Machine Learning Network Slice Management Function",
    version="3.10.0"
)

# attach observability AFTER app creation
_trisla_attach_observability(
    app,
    os.getenv("TRISLA_SERVICE_NAME", "ml-nsmf")
)

FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)


def _risk_level_from_score(risk: float) -> str:
    if risk > 0.7:
        return "high"
    if risk > 0.4:
        return "medium"
    return "low"


predictor = RiskPredictor()
metrics_consumer = MetricsConsumer()
prediction_producer = PredictionProducer()
prometheus_client = PrometheusClient()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "module": "ml-nsmf"
    }


@app.post("/api/v1/predict")
async def predict_risk(metrics: dict):

    with tracer.start_as_current_span("predict_risk"):
        iid = (metrics or {}).get("intent_id") or (metrics or {}).get("sla_id")
        if iid:
            st = (metrics or {}).get("service_type") or (metrics or {}).get("slice_type")
            print(f"[ML_PREDICT] intent_id={iid} service_type={st}", flush=True)

        normalized = predictor.normalize(metrics)
        prediction = predictor.predict(normalized)
        clf_out = predictor.predict_decision_class(metrics)
        prediction["predicted_decision_class"] = clf_out.get("predicted_decision_class")
        prediction["classifier_confidence"] = float(clf_out.get("confidence_score") or 0.0)
        prediction["confidence_score"] = float(clf_out.get("confidence_score") or 0.0)
        prediction["classifier_loaded"] = bool(clf_out.get("classifier_loaded", False))
        class_probs = clf_out.get("class_probabilities") or {}
        prediction["class_probabilities"] = class_probs

        # Multiclass calibrated risk formulation (v7):
        # risk = min(1, 0.5 * P(RENEGOTIATE) + 1.0 * P(REJECT))
        p_reneg = float(class_probs.get("RENEGOTIATE", 0.0))
        p_reject = float(class_probs.get("REJECT", 0.0))
        risk_multiclass = min(1.0, (0.5 * p_reneg) + (1.0 * p_reject))
        risk_from_regression = float(prediction.get("risk_score", 0.5))
        raw_risk = (
            float(risk_multiclass)
            if prediction.get("classifier_loaded")
            else risk_from_regression
        )
        prediction["risk_score_regression"] = risk_from_regression
        prediction["risk_formula"] = "v7_calibrated"
        adj_bundle = compute_slice_adjusted_risk(raw_risk, metrics)
        prediction["raw_risk_score"] = adj_bundle["raw_risk_score"]
        prediction["slice_adjusted_risk_score"] = adj_bundle["slice_adjusted_risk_score"]
        prediction["risk_score"] = raw_risk
        prediction["risk_level"] = _risk_level_from_score(adj_bundle["slice_adjusted_risk_score"])
        prediction["slice_domain_xai"] = {
            "dominant_domain": adj_bundle["dominant_domain"],
            "top_factors": adj_bundle["top_factors"],
            "domain_contribution": adj_bundle.get("domain_contribution", {}),
        }

        explanation = predictor.explain(prediction, normalized)
        explanation["raw_risk_score"] = adj_bundle["raw_risk_score"]
        explanation["slice_adjusted_risk_score"] = adj_bundle["slice_adjusted_risk_score"]
        explanation["dominant_domain"] = adj_bundle["dominant_domain"]
        explanation["top_factors"] = adj_bundle["top_factors"]
        if explanation.get("reasoning"):
            explanation["reasoning"] = (
                f"{explanation['reasoning']} | adjusted_risk={adj_bundle['slice_adjusted_risk_score']:.3f} "
                f"dominant_domain={adj_bundle['dominant_domain']}"
            )

        await prediction_producer.send_prediction(prediction, explanation)

        return {
            "latency_ms": prediction.get("prediction_latency_ms"),
            "prediction": prediction,
            "explanation": explanation,
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
