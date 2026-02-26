"""
XAI Logging e Evidências - v3.9.0
Logs separados e geração de CSV para explicações
"""
import logging
import csv
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone
import json

# Configurar logger XAI separado
xai_logger = logging.getLogger("trisla.ml-nsmf.xai")
xai_logger.setLevel(logging.INFO)

# Handler para arquivo XAI separado
xai_log_dir = os.getenv("XAI_LOG_DIR", "/app/logs/xai")
os.makedirs(xai_log_dir, exist_ok=True)

xai_file_handler = logging.FileHandler(
    os.path.join(xai_log_dir, "xai_explanations.log")
)
xai_file_handler.setLevel(logging.INFO)
xai_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
xai_file_handler.setFormatter(xai_formatter)
xai_logger.addHandler(xai_file_handler)

# Diretório para CSV
xai_csv_dir = os.getenv("XAI_CSV_DIR", "/app/evidence/xai")
os.makedirs(xai_csv_dir, exist_ok=True)

CSV_FILE = os.path.join(xai_csv_dir, "xai_explanations.csv")
CSV_HEADERS = [
    "timestamp",
    "slice_type",
    "nest_id",
    "prediction",
    "confidence",
    "model_used",
    "method",
    "explanation_available",
    "top_features",
    "feature_count"
]


def log_xai_explanation(explanation: Dict, slice_type: str, nest_id: Optional[str] = None):
    """
    Registra explicação XAI em log separado
    """
    try:
        method = explanation.get("method", "none")
        available = explanation.get("explanation_available", False)
        confidence = explanation.get("confidence", 0.0)
        prediction = explanation.get("prediction", "UNKNOWN")
        xai_logger.info(f"XAI Explanation - slice_type={slice_type}, nest_id={nest_id}, method={method}, available={available}, confidence={confidence:.2f}, prediction={prediction}")
        feature_importance = explanation.get("feature_importance", {})
        if feature_importance:
            top_features = explanation.get("top_features", [])
            xai_logger.info(
                f"Top Features: {', '.join(top_features[:5])}"
            )
    except Exception as e:
        xai_logger.error(f"Erro ao registrar log XAI: {e}")


def save_xai_to_csv(explanation: Dict, slice_type: str, nest_id: Optional[str] = None):
    """
    Salva explicação XAI em CSV para análise
    """
    try:
        file_exists = os.path.exists(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            
            if not file_exists:
                writer.writeheader()
            
            top_features = explanation.get("top_features", [])
            feature_importance = explanation.get("feature_importance", {})
            
            row = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "slice_type": slice_type,
                "nest_id": nest_id or "",
                "prediction": explanation.get("prediction", "UNKNOWN"),
                "confidence": f"{explanation.get('confidence', 0.0):.4f}",
                "model_used": str(explanation.get("model_used", False)),
                "method": explanation.get("method", "none"),
                "explanation_available": str(explanation.get("explanation_available", False)),
                "top_features": ",".join(top_features[:5]),
                "feature_count": len(feature_importance)
            }
            
            writer.writerow(row)
            xai_logger.debug(f"Explicação XAI salva em CSV: {row}")
            
    except Exception as e:
        xai_logger.error(f"Erro ao salvar XAI em CSV: {e}")


def get_xai_explanations_summary() -> Dict:
    """
    Retorna resumo das explicações XAI coletadas
    """
    try:
        if not os.path.exists(CSV_FILE):
            return {
                "total_explanations": 0,
                "csv_file": CSV_FILE,
                "status": "no_data"
            }
        
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            
        return {
            "total_explanations": len(rows),
            "csv_file": CSV_FILE,
            "status": "ok",
            "latest_explanation": rows[-1] if rows else None
        }
    except Exception as e:
        xai_logger.error(f"Erro ao ler resumo XAI: {e}")
        return {
            "total_explanations": 0,
            "csv_file": CSV_FILE,
            "status": "error",
            "error": str(e)
        }
