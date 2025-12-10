from typing import Any
from src.services.prometheus import PrometheusService
from src.config import settings
import httpx

prometheus_service = PrometheusService()


class ModuleService:
    async def list_modules(self) -> list[Any]:
        """Lista todos os módulos"""
        # Retornar lista básica de módulos
        return [
            {"name": "sem-csmf", "status": "UP"},
            {"name": "ml-nsmf", "status": "UP"},
            {"name": "decision-engine", "status": "UP"},
            {"name": "bc-nssmf", "status": "UP"},
            {"name": "sla-agent-layer", "status": "UP"},
            {"name": "nasp-adapter", "status": "UP"},
            {"name": "ui-dashboard", "status": "UP"},
        ]

    async def get_module(self, module: str) -> dict[str, Any]:
        """Retorna detalhes de um módulo"""
        # Query Prometheus para métricas do módulo
        try:
            query = f'up{{job="{module}"}}'
            result = await prometheus_service.query(query)
            return {
                "name": module,
                "status": "UP" if result.get("data", {}).get("result") else "DOWN",
            }
        except Exception:
            return {"name": module, "status": "DOWN"}

    async def get_module_metrics(self, module: str) -> dict[str, Any]:
        """Retorna métricas de um módulo"""
        # Query múltiplas métricas do Prometheus
        metrics = {}
        try:
            # Exemplo: latência
            query = f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{job="{module}"}}[5m]))'
            result = await prometheus_service.query(query)
            if result.get("data", {}).get("result"):
                metrics["latency_p95"] = float(result["data"]["result"][0]["value"][1])
        except Exception:
            pass

        return metrics

    async def get_module_status(self, module: str) -> dict[str, Any]:
        """Retorna status (pods, deployments) de um módulo"""
        # Em produção, consultaria Kubernetes API
        # Por enquanto, retornar estrutura básica
        return {
            "pods": [
                {"name": f"{module}-pod-1", "status": "Running", "ready": True, "restarts": 0}
            ],
            "deployments": [{"name": module, "replicas": 1, "ready_replicas": 1}],
        }


