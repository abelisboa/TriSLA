from datetime import datetime
from typing import List
from src.schemas.health import HealthResponse, ModuleStatus
from src.services.prometheus import PrometheusService
from src.config import settings

prometheus_service = PrometheusService()

# Lista de módulos TriSLA
TRISLA_MODULES = [
    "sem-csmf",
    "ml-nsmf",
    "decision-engine",
    "bc-nssmf",
    "sla-agent-layer",
    "nasp-adapter",
    "ui-dashboard",
]


class HealthService:
    async def get_global_health(self) -> HealthResponse:
        """Retorna saúde global do TriSLA"""
        modules = await self.get_modules()
        
        # Determinar status global
        all_up = all(m.status == "UP" for m in modules)
        status = "healthy" if all_up else "unhealthy"

        return HealthResponse(
            status=status,
            modules=modules,
            timestamp=datetime.utcnow(),
        )

    async def get_modules(self) -> List[ModuleStatus]:
        """Retorna status de todos os módulos"""
        modules = []
        for module_name in TRISLA_MODULES:
            try:
                # Query Prometheus para status do módulo
                query = f'up{{job="{module_name}"}}'
                result = await prometheus_service.query(query)
                
                # Processar resultado
                status = "UP"
                if result.get("data", {}).get("result"):
                    value = result["data"]["result"][0].get("value", [None, "0"])[1]
                    if value == "0":
                        status = "DOWN"
                
                modules.append(
                    ModuleStatus(
                        name=module_name,
                        status=status,
                    )
                )
            except Exception:
                modules.append(
                    ModuleStatus(
                        name=module_name,
                        status="DOWN",
                    )
                )
        
        return modules


