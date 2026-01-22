import httpx
import json
import csv
from typing import Any, List
from datetime import datetime
from fastapi import UploadFile
from src.config import settings
from src.schemas.slas import SLATemplate, BatchJob, BatchResult
from src.services.trisla import TriSLAService

trisla_service = TriSLAService()


class SLAService:
    async def create_pln(self, intent_text: str, tenant_id: str) -> dict[str, Any]:
        """Cria SLA via PLN"""
        # FASE 3 (C3): Capturar timestamp de submissão
        t_submit = datetime.utcnow().isoformat() + 'Z'
        
        # Chama SEM-CSMF para processar intent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.trisla_sem_csmf_url}/api/v1/intents",
                json={"intent_text": intent_text, "tenant_id": tenant_id},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            
            # Adicionar timestamp de submissão
            result["t_submit"] = t_submit
            return result

    async def validate_pln(self, intent_text: str) -> dict[str, Any]:
        """Valida intent PLN"""
        # Validação básica
        return {"valid": True, "message": "Intent válido"}

    async def get_templates(self) -> List[SLATemplate]:
        """Lista templates NEST disponíveis"""
        return [
            SLATemplate(
                template_id="urllc-basic",
                name="URLLC Basic",
                description="Template básico para slice URLLC",
                service_type="URLLC",
                nest_template={
                    "slice_type": "URLLC",
                    "sla_requirements": {
                        "latency": {"max": "{{latency_max}}"},
                        "reliability": "{{reliability}}",
                    },
                },
            ),
            SLATemplate(
                template_id="embb-basic",
                name="eMBB Basic",
                description="Template básico para slice eMBB",
                service_type="eMBB",
                nest_template={
                    "slice_type": "eMBB",
                    "sla_requirements": {
                        "throughput": {"min": "{{throughput_min}}"},
                    },
                },
            ),
        ]

    async def get_template(self, template_id: str) -> SLATemplate:
        """Retorna detalhes de um template"""
        templates = await self.get_templates()
        for template in templates:
            if template.template_id == template_id:
                return template
        raise ValueError(f"Template {template_id} not found")

    async def create_template(
        self, template_id: str, form_values: dict[str, Any], tenant_id: str
    ) -> dict[str, Any]:
        """Cria SLA via template"""
        # FASE 3 (C3): Capturar timestamp de submissão
        t_submit = datetime.utcnow().isoformat() + 'Z'
        
        template = await self.get_template(template_id)
        # Substituir placeholders no template
        nest = template.nest_template.copy()
        # Processar form_values e substituir no nest
        # Chama SEM-CSMF para criar intent
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.trisla_sem_csmf_url}/api/v1/intents",
                json={"nest": nest, "tenant_id": tenant_id},
                timeout=30.0,
            )
            response.raise_for_status()
            result = response.json()
            
            # Adicionar timestamp de submissão
            result["t_submit"] = t_submit
            return result

    async def create_batch(
        self, file: UploadFile, tenant_id: str
    ) -> BatchJob:
        """Cria SLAs em lote"""
        import uuid
        batch_id = str(uuid.uuid4())
        
        # Ler arquivo
        content = await file.read()
        file_extension = file.filename.split(".")[-1].lower()

        results = []
        if file_extension == "csv":
            # Processar CSV
            csv_content = content.decode("utf-8")
            reader = csv.DictReader(csv_content.splitlines())
            for idx, row in enumerate(reader):
                try:
                    result = await self.create_pln(row.get("intent_text", ""), tenant_id)
                    results.append(
                        BatchResult(
                            sla_index=idx,
                            tenant_id=tenant_id,
                            status="success",
                            intent_id=result.get("intent_id"),
                            nest_id=result.get("nest_id"),
                        )
                    )
                except Exception as e:
                    results.append(
                        BatchResult(
                            sla_index=idx,
                            tenant_id=tenant_id,
                            status="error",
                            error=str(e),
                        )
                    )
        elif file_extension == "json":
            # Processar JSON
            json_data = json.loads(content)
            for idx, item in enumerate(json_data):
                try:
                    result = await self.create_pln(item.get("intent_text", ""), tenant_id)
                    results.append(
                        BatchResult(
                            sla_index=idx,
                            tenant_id=tenant_id,
                            status="success",
                            intent_id=result.get("intent_id"),
                            nest_id=result.get("nest_id"),
                        )
                    )
                except Exception as e:
                    results.append(
                        BatchResult(
                            sla_index=idx,
                            tenant_id=tenant_id,
                            status="error",
                            error=str(e),
                        )
                    )

        return BatchJob(
            batch_id=batch_id,
            tenant_id=tenant_id,
            total_slas=len(results),
            processed_slas=len(results),
            successful_slas=sum(1 for r in results if r.status == "success"),
            failed_slas=sum(1 for r in results if r.status == "error"),
            status="COMPLETED",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            results=results,
        )

    async def get_batch_status(self, batch_id: str) -> BatchJob:
        """Retorna status de um batch job"""
        # Em produção, buscar do banco de dados ou cache
        raise ValueError(f"Batch {batch_id} not found")

    async def get_batch_results(self, batch_id: str) -> List[BatchResult]:
        """Retorna resultados de um batch job"""
        batch = await self.get_batch_status(batch_id)
        return batch.results


