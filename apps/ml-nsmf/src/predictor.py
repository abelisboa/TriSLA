"""
Risk Predictor - ML-NSMF
Previsão de risco usando modelo Random Forest (ou LSTM/GRU)
S34.2: Modelo e scaler obrigatórios. Sem fallback. Logs [ML] explícitos.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
import pickle
import os
import json
import logging
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

MODEL_PATH_DEFAULT = "/app/models/viability_model.pkl"
SCALER_PATH_DEFAULT = "/app/models/scaler.pkl"


class RiskPredictor:
    """Previsor de risco usando ML. Modelo e scaler obrigatórios (S34.2)."""

    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        if model_path is None:
            model_path = MODEL_PATH_DEFAULT
        if scaler_path is None:
            scaler_path = SCALER_PATH_DEFAULT
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.model_metadata = None

        self.model = self._load_model(model_path)
        self.scaler = self._load_scaler(scaler_path)
        self._load_metadata()

    def _load_model(self, model_path: str):
        """Carrega modelo treinado. Falha explícita se ausente ou erro (S34.2)."""
        logger.info("[ML] Loading trained model from %s", model_path)
        if not os.path.exists(model_path):
            logger.error("[ML] Model not found at %s", model_path)
            raise FileNotFoundError(f"Modelo não encontrado em {model_path}")
        try:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
            logger.info("[ML] Model loaded successfully")
            return model
        except Exception as e:
            logger.exception("[ML] Model load failed: %s", e)
            raise RuntimeError(f"Falha crítica no carregamento do modelo: {e}") from e

    def _load_scaler(self, scaler_path: str):
        """Carrega scaler. Abortar se ausente ou erro (S34.2). Sem fallback."""
        if not os.path.exists(scaler_path):
            logger.error("[ML] Scaler not found at %s", scaler_path)
            raise FileNotFoundError(f"Scaler não encontrado em {scaler_path}")
        try:
            with open(scaler_path, "rb") as f:
                scaler = pickle.load(f)
            logger.info("[ML] Scaler loaded successfully")
            return scaler
        except Exception as e:
            logger.exception("[ML] Scaler load failed: %s", e)
            raise RuntimeError(f"Falha crítica no carregamento do scaler: {e}") from e

    def _load_metadata(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        metadata_path = os.path.join(base_dir, "models", "model_metadata.json")
        if not os.path.isabs(base_dir) or not os.path.exists(metadata_path):
            metadata_path = "/app/models/model_metadata.json"
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r") as f:
                    self.model_metadata = json.load(f)
                self.feature_columns = self.model_metadata.get("feature_columns", [])
                logger.info("Metadados carregados: %d features", len(self.feature_columns))
            except Exception as e:
                logger.warning("Erro ao carregar metadados: %s", e)

    def normalize(self, metrics: Dict[str, Any]) -> np.ndarray:
        with tracer.start_as_current_span("normalize_metrics") as span:
            epsilon = 0.001
            latency = metrics.get("latency", 0)
            throughput = metrics.get("throughput", 0)
            reliability = metrics.get("reliability", 0.99)
            jitter = metrics.get("jitter", 0)
            packet_loss = metrics.get("packet_loss", 0.001)
            slice_type = metrics.get("slice_type", "eMBB")
            slice_type_encoded = {"URLLC": 1, "eMBB": 2, "mMTC": 3}.get(slice_type, 2)

            latency_throughput_ratio = latency / (throughput + epsilon)
            reliability_packet_loss_ratio = reliability / (packet_loss + epsilon)
            jitter_latency_ratio = jitter / (latency + epsilon) if latency > 0 else 0

            feature_dict = {
                "latency": latency,
                "throughput": throughput,
                "reliability": reliability,
                "jitter": jitter,
                "packet_loss": packet_loss,
                "cpu_utilization": metrics.get("cpu_utilization", 0.5),
                "memory_utilization": metrics.get("memory_utilization", 0.5),
                "network_bandwidth_available": metrics.get("network_bandwidth_available", 500),
                "active_slices_count": metrics.get("active_slices_count", 1),
                "slice_type_encoded": slice_type_encoded,
                "latency_throughput_ratio": latency_throughput_ratio,
                "reliability_packet_loss_ratio": reliability_packet_loss_ratio,
                "jitter_latency_ratio": jitter_latency_ratio,
            }

            cols = self.feature_columns or [
                "latency", "throughput", "reliability", "jitter", "packet_loss",
                "cpu_utilization", "memory_utilization", "network_bandwidth_available",
                "active_slices_count", "slice_type_encoded",
                "latency_throughput_ratio", "reliability_packet_loss_ratio", "jitter_latency_ratio",
            ]
            row = {c: feature_dict.get(c, 0) for c in cols if c in feature_dict}
            for c in cols:
                if c not in row:
                    row[c] = feature_dict.get(c, 0)
            df = pd.DataFrame([row], columns=cols)
            normalized = self.scaler.transform(df)[0]
            span.set_attribute("metrics.normalized", True)
            span.set_attribute("metrics.features_count", len(normalized))
            return normalized

    def predict(self, normalized_metrics: np.ndarray) -> Dict[str, Any]:
        with tracer.start_as_current_span("predict_risk") as span:
            cols = self.feature_columns or [
                "latency", "throughput", "reliability", "jitter", "packet_loss",
                "cpu_utilization", "memory_utilization", "network_bandwidth_available",
                "active_slices_count", "slice_type_encoded",
                "latency_throughput_ratio", "reliability_packet_loss_ratio", "jitter_latency_ratio",
            ]
            X = pd.DataFrame(normalized_metrics.reshape(1, -1), columns=cols)
            try:
                viability_score = float(self.model.predict(X)[0])
            except Exception as e:
                logger.exception("Erro na predição: %s", e)
                span.record_exception(e)
                raise RuntimeError(f"Falha na inferência: {e}") from e

            risk_score = max(0.0, min(1.0, 1.0 - viability_score))
            confidence = 1.0 - abs(viability_score - 0.5) * 2
            confidence = max(0.5, min(1.0, confidence))

            if risk_score > 0.7:
                risk_level = "high"
            elif risk_score > 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"

            prediction = {
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "viability_score": float(viability_score),
                "confidence": float(confidence),
                "timestamp": self._get_timestamp(),
                "model_used": True,
            }
            span.set_attribute("prediction.risk_level", risk_level)
            span.set_attribute("prediction.risk_score", risk_score)
            span.set_attribute("prediction.confidence", prediction["confidence"])
            span.set_attribute("prediction.model_used", True)
            return prediction

    def explain(self, prediction: Dict[str, Any], metrics: np.ndarray, model=None) -> Dict[str, Any]:
        with tracer.start_as_current_span("explain_prediction") as span:
            explanation = {
                "method": "XAI",
                "features_importance": {},
                "reasoning": "",
                "shap_available": False,
                "lime_available": False,
            }
            m = model if model is not None else self.model
            feature_names = self.feature_columns or [
                "latency", "throughput", "reliability", "jitter", "packet_loss",
                "cpu_utilization", "memory_utilization", "network_bandwidth_available",
                "active_slices_count", "slice_type_encoded",
                "latency_throughput_ratio", "reliability_packet_loss_ratio", "jitter_latency_ratio",
            ]
            feature_names = feature_names[: int(metrics.size)]

            try:
                import shap
                shap_available = True
            except ImportError:
                shap_available = False
                shap = None

            try:
                from lime import lime_tabular
                lime_available = True
            except ImportError:
                lime_available = False
                lime_tabular = None

            if shap_available and m is not None and hasattr(m, "feature_importances_"):
                try:
                    explainer = shap.TreeExplainer(m)
                    X = pd.DataFrame(metrics.reshape(1, -1), columns=feature_names)
                    shap_values = explainer.shap_values(X)
                    if isinstance(shap_values, list):
                        shap_values = shap_values[0] if shap_values else shap_values
                    if hasattr(shap_values, "shape") and len(shap_values.shape) > 1:
                        shap_values = shap_values[0]
                    names = feature_names[: len(shap_values)]
                    explanation["features_importance"] = {
                        n: float(abs(v)) for n, v in zip(names, shap_values)
                    }
                    total = sum(explanation["features_importance"].values())
                    if total > 0:
                        explanation["features_importance"] = {
                            k: v / total for k, v in explanation["features_importance"].items()
                        }
                    explanation["shap_available"] = True
                    explanation["method"] = "SHAP"
                    span.set_attribute("explanation.method", "SHAP")
                except Exception as e:
                    logger.warning("SHAP explain failed: %s", e)
                    span.set_attribute("explanation.shap_error", str(e))

            if lime_available and not explanation.get("shap_available") and m is not None:
                try:
                    n = len(feature_names)
                    training_data = np.random.rand(100, n).astype(np.float32)
                    explainer = lime_tabular.LimeTabularExplainer(
                        training_data, feature_names=feature_names, mode="regression", discretize_continuous=True
                    )
                    explain = explainer.explain_instance(
                        metrics, m.predict, num_features=min(n, 10)
                    )
                    explanation["features_importance"] = {k: abs(v) for k, v in explain.as_list()}
                    total = sum(explanation["features_importance"].values())
                    if total > 0:
                        explanation["features_importance"] = {
                            k: v / total for k, v in explanation["features_importance"].items()
                        }
                    explanation["lime_available"] = True
                    explanation["method"] = "LIME"
                    span.set_attribute("explanation.method", "LIME")
                except Exception as e:
                    logger.warning("LIME explain failed: %s", e)
                    span.set_attribute("explanation.lime_error", str(e))

            if not explanation["features_importance"] and self.model_metadata:
                fimp = self.model_metadata.get("training_history", {}).get("feature_importance")
                if fimp:
                    explanation["features_importance"] = {k: float(v) for k, v in fimp.items()}
                    explanation["method"] = "feature_importance"
            if explanation["features_importance"]:
                sorted_f = sorted(
                    explanation["features_importance"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
                top = sorted_f[0]
                explanation["reasoning"] = (
                    f"Risk level {prediction['risk_level']} (score: {prediction['risk_score']:.2f}). "
                    f"Principal fator: {top[0]} ({top[1]:.1%})."
                )
            else:
                explanation["reasoning"] = f"Risk level {prediction['risk_level']} (score: {prediction['risk_score']:.2f})."

            span.set_attribute("explanation.method", explanation["method"])
            return explanation

    def _get_timestamp(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
