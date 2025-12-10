from typing import List, Any
from src.services.prometheus import PrometheusService

prometheus_service = PrometheusService()


class SLOService:
    async def list_slos(self) -> List[Any]:
        """Lista todos os SLOs"""
        # Query Prometheus para SLOs
        slos = []
        modules = ["sem-csmf", "ml-nsmf", "decision-engine", "bc-nssmf", "sla-agent-layer"]
        
        for module in modules:
            try:
                # Latência P95
                query = f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{job="{module}"}}[5m]))'
                result = await prometheus_service.query(query)
                if result.get("data", {}).get("result"):
                    latency_p95 = float(result["data"]["result"][0]["value"][1])
                    slos.append({
                        "name": f"{module}_latency_p95",
                        "module": module,
                        "target": 0.1,  # 100ms
                        "current": latency_p95,
                        "status": "MET" if latency_p95 < 0.1 else "VIOLATED",
                    })
            except Exception:
                pass
        
        return slos

    async def get_summary(self) -> dict[str, Any]:
        """Retorna resumo de SLOs"""
        slos = await self.list_slos()
        total = len(slos)
        met = sum(1 for slo in slos if slo["status"] == "MET")
        violated = total - met
        
        return {
            "total": total,
            "met": met,
            "violated": violated,
            "compliance_rate": met / total if total > 0 else 0,
        }

    async def get_module_slos(self, module: str) -> List[Any]:
        """Retorna SLOs de um módulo"""
        slos = await self.list_slos()
        return [slo for slo in slos if slo["module"] == module]

    async def get_module_violations(self, module: str) -> List[Any]:
        """Retorna violações de SLO de um módulo"""
        slos = await self.get_module_slos(module)
        return [slo for slo in slos if slo["status"] == "VIOLATED"]






