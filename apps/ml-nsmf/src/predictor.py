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
import time
import re
from pathlib import Path
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

MODEL_PATH_DEFAULT = "/app/models/viability_model.pkl"


def _derived_sla_features_v3(fd: Dict[str, Any]) -> Dict[str, float]:
    """Features derivadas alinhadas ao dataset v3 (treino local). RTT não disponível no dataset legado."""
    eps = 0.001
    lat = float(fd.get("latency", 0) or 0)
    thr = float(fd.get("throughput", 0) or 0)
    rel = float(fd.get("reliability", 0.99) or 0)
    jit = float(fd.get("jitter", 0) or 0)
    pl = float(fd.get("packet_loss", 0.001) or 0)
    cpu = float(fd.get("cpu_utilization", 0.5) or 0)
    mem = float(fd.get("memory_utilization", 0.5) or 0)
    bw = float(fd.get("network_bandwidth_available", thr) or thr)
    try:
        ste = int(float(fd.get("slice_type_encoded", 2)))
    except (TypeError, ValueError):
        ste = 2

    nlat = max(0.0, min(1.0, lat / 200.0))
    njit = max(0.0, min(1.0, jit / 100.0))
    npl = max(0.0, min(1.0, pl * 5.0))
    ran_p = (nlat + njit) / 2.0
    trans_p = (njit + npl) / 2.0
    core_p = (cpu + mem) / 2.0
    domain_pressure_score = max(0.0, min(1.0, (ran_p + trans_p + core_p) / 3.0))
    transport_instability_score = max(0.0, min(1.0, (njit + npl + nlat) / 3.0))
    core_pressure_score = max(0.0, min(1.0, core_p))
    te = thr / (bw + eps)
    throughput_efficiency_score = max(0.0, min(1.0, te))
    sla_stringency_score = max(
        0.0,
        min(1.0, (nlat + max(0.0, 1.0 - rel) + max(0.0, min(1.0, 1.0 - thr / max(bw, eps)))) / 3.0),
    )
    if ste == 1:
        slice_domain_fit_score = max(0.0, min(1.0, 1.0 - (nlat * 0.5 + njit * 0.3 + npl * 0.2)))
    elif ste == 3:
        slice_domain_fit_score = max(0.0, min(1.0, rel * max(0.0, 1.0 - core_p)))
    else:
        slice_domain_fit_score = max(0.0, min(1.0, throughput_efficiency_score * 0.6 + (1.0 - nlat) * 0.4))

    return {
        "domain_pressure_score": domain_pressure_score,
        "transport_instability_score": transport_instability_score,
        "core_pressure_score": core_pressure_score,
        "throughput_efficiency_score": throughput_efficiency_score,
        "sla_stringency_score": sla_stringency_score,
        "slice_domain_fit_score": slice_domain_fit_score,
    }


SCALER_PATH_DEFAULT = "/app/models/scaler.pkl"
REGISTRY_DIR_DEFAULT = "/app/models/registry"


class RiskPredictor:
    """Previsor de risco usando ML. Modelo e scaler obrigatórios (S34.2)."""

    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        model_path, scaler_path = self._resolve_model_paths(model_path, scaler_path)
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.model_metadata = None
        self.model_path = model_path
        self.scaler_path = scaler_path

        self.model = self._load_model(model_path)
        self.scaler = self._load_scaler(scaler_path)
        self._load_metadata()
        self.classifier_bundle: Optional[Dict[str, Any]] = None
        self._load_decision_classifier_optional()

    def _load_decision_classifier_optional(self) -> None:
        """Carrega decision_classifier.pkl se existir (FASE 11 — híbrido). Opcional."""
        candidates = []
        env = os.getenv("ML_DECISION_CLASSIFIER_PATH")
        if env:
            candidates.append(env)
        candidates.append("/app/models/decision_classifier.pkl")
        # Dev tree: apps/ml-nsmf/src/predictor.py → parents[3] = repo root. In image /app/src only → parents[3] invalid.
        try:
            candidates.append(str(Path(__file__).resolve().parents[3] / "artifacts" / "decision_classifier.pkl"))
        except IndexError:
            pass
        for p in candidates:
            if not p or not os.path.isfile(p):
                continue
            try:
                logger.info("[ML] Loading decision classifier from %s", p)
                with open(p, "rb") as f:
                    self.classifier_bundle = pickle.load(f)
                logger.info("[ML] Decision classifier loaded successfully")
                return
            except Exception as exc:
                logger.warning("[ML] Falha ao carregar classificador em %s: %s", p, exc)
        logger.error("[ML] Decision classifier NOT found")

    def _feature_dict_from_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Constrói dict de features (base + derivadas v3) a partir de métricas brutas."""
        epsilon = 0.001
        latency = metrics.get("latency", 0)
        throughput = metrics.get("throughput", 0)
        reliability = metrics.get("reliability", 0.99)
        jitter = metrics.get("jitter", 0)
        packet_loss = metrics.get("packet_loss", 0.001)
        slice_type = metrics.get("slice_type", "eMBB")
        enc_raw = metrics.get("slice_type_encoded")
        if isinstance(enc_raw, (int, float)) and not (isinstance(enc_raw, bool)):
            slice_type_encoded = int(enc_raw)
        else:
            slice_type_encoded = {"URLLC": 1, "eMBB": 2, "mMTC": 3}.get(str(slice_type), 2)

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
        v3_extra = _derived_sla_features_v3(feature_dict)
        feature_dict.update(v3_extra)
        return feature_dict

    def predict_decision_class(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classificação de decisão (ACCEPT/RENEGOTIATE/REJECT) com probabilidade da classe escolhida.
        Requer decision_classifier.pkl treinado; caso contrário retorna confidence 0.
        """
        if not self.classifier_bundle:
            return {
                "predicted_decision_class": None,
                "confidence_score": 0.0,
                "classifier_loaded": False,
                "class_probabilities": {},
            }
        logger.info("[ML] Running classifier prediction")
        clf_cols = self.classifier_bundle.get("feature_columns") or []
        feature_dict = self._feature_dict_from_metrics(metrics)
        row = {c: float(feature_dict.get(c, 0)) for c in clf_cols}
        df = pd.DataFrame([row], columns=clf_cols)
        scaler = self.classifier_bundle["scaler"]
        model = self.classifier_bundle["model"]
        le = self.classifier_bundle["label_encoder"]
        Xs = scaler.transform(df)
        proba = model.predict_proba(Xs)[0]
        idx = int(np.argmax(proba))
        label = str(le.classes_[idx])
        conf = float(proba[idx])
        class_probabilities = {
            str(le.classes_[i]): float(proba[i]) for i in range(len(proba))
        }
        logger.info("[ML] predicted_decision=%s confidence=%.3f", label, conf)
        return {
            "predicted_decision_class": label,
            "confidence_score": conf,
            "classifier_loaded": True,
            "class_probabilities": class_probabilities,
        }

    def _resolve_model_paths(
        self, model_path: Optional[str], scaler_path: Optional[str]
    ) -> tuple[str, str]:
        if model_path is not None or scaler_path is not None:
            return model_path or MODEL_PATH_DEFAULT, scaler_path or SCALER_PATH_DEFAULT

        registry_dir = os.getenv("ML_MODEL_REGISTRY_DIR", REGISTRY_DIR_DEFAULT)
        current_model_path = os.path.join(registry_dir, "current_model.txt")

        if not os.path.exists(current_model_path):
            logger.warning("[ML] Registry pointer not found; using legacy model/scaler")
            return MODEL_PATH_DEFAULT, SCALER_PATH_DEFAULT

        try:
            current_model_name = open(current_model_path, "r", encoding="utf-8").read().strip()
        except Exception as exc:
            logger.warning("[ML] Failed to read registry pointer: %s", exc)
            return MODEL_PATH_DEFAULT, SCALER_PATH_DEFAULT

        if not current_model_name:
            logger.warning("[ML] Empty registry pointer; using legacy model/scaler")
            return MODEL_PATH_DEFAULT, SCALER_PATH_DEFAULT

        registry_model_path = os.path.join(registry_dir, current_model_name)
        scaler_name = "scaler.pkl"
        match = re.search(r"_v(\d+)\.pkl$", current_model_name)
        if match:
            scaler_name = f"scaler_v{match.group(1)}.pkl"
        registry_scaler_path = os.path.join(registry_dir, scaler_name)

        if os.path.exists(registry_model_path) and os.path.exists(registry_scaler_path):
            logger.info(
                "[ML] Using registry model=%s scaler=%s",
                registry_model_path,
                registry_scaler_path,
            )
            return registry_model_path, registry_scaler_path

        logger.warning(
            "[ML] Registry artifacts missing (model=%s scaler=%s); using legacy model/scaler",
            registry_model_path,
            registry_scaler_path,
        )
        return MODEL_PATH_DEFAULT, SCALER_PATH_DEFAULT

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
        metadata_candidates = []

        registry_dir = os.getenv("ML_MODEL_REGISTRY_DIR", REGISTRY_DIR_DEFAULT)
        model_name = os.path.basename(self.model_path or "")
        match = re.search(r"_v(\d+)\.pkl$", model_name)
        if match:
            metadata_candidates.append(os.path.join(registry_dir, f"metadata_v{match.group(1)}.json"))

        metadata_candidates.extend(
            [
                os.path.join(base_dir, "models", "model_metadata.json"),
                "/app/models/model_metadata.json",
            ]
        )

        for metadata_path in metadata_candidates:
            if not os.path.exists(metadata_path):
                continue
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    self.model_metadata = json.load(f)
                self.feature_columns = self.model_metadata.get("feature_columns", [])
                logger.info("Metadados carregados de %s: %d features", metadata_path, len(self.feature_columns))
                return
            except Exception as e:
                logger.warning("Erro ao carregar metadados em %s: %s", metadata_path, e)

    def normalize(self, metrics: Dict[str, Any]) -> np.ndarray:
        with tracer.start_as_current_span("normalize_metrics") as span:
            feature_dict = self._feature_dict_from_metrics(metrics)

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
            t0 = time.time()
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

            prediction_latency_ms = (time.time() - t0) * 1000
            prediction = {
                "risk_score": float(risk_score),
                "risk_level": risk_level,
                "viability_score": float(viability_score),
                "confidence": float(confidence),
                "prediction_latency_ms": float(prediction_latency_ms),
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
