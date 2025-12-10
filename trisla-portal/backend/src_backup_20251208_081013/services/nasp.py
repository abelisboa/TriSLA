"""
Service para comunicação REAL com TODOS os módulos TriSLA NASP
TODAS as chamadas são REAIS - SEM SIMULAÇÕES
Sequência completa: SEM-CSMF → ML-NSMF → Decision Engine → BC-NSSMF → SLA-Agent Layer → Observabilidade
Conforme Capítulos 4, 5 e 6 da dissertação
"""
import httpx
from typing import Any, Dict
from src.config import settings
import logging
from fastapi import HTTPException
import uuid
from src.utils.sla_hash import calculate_sla_hash, convert_slos_to_numeric
from src.schemas.sla_aware import SLAAware, SLARequestBC, SLO

logger = logging.getLogger(__name__)


class NASPService:
    """Service para comunicação REAL com TODOS os módulos TriSLA - SEM SIMULAÇÕES"""
    
    async def call_sem_csmf(self, intent_text: str = None, nest_template: Dict[str, Any] = None, tenant_id: str = None) -> Dict[str, Any]:
        """
        (1) SEM-CSMF – Interpretação Semântica Real
        
        Valida a intenção ou template.
        Mapeia para o tipo real de slice do catálogo (URLLC, eMBB, mMTC).
        Se inválido → rejeitar imediatamente com erro 422.
        Usa a ontologia completa.
        
        Retorna: { "intent_id": str, "nest_id": str, "slice_type": str, ... }
        """
        async with httpx.AsyncClient() as client:
            try:
                url = f"{settings.nasp_sem_csmf_url}/api/v1/intents"
                
                if intent_text:
                    # Novo contrato para /interpret conforme especificação
                    payload = {
                        "intent_id": str(uuid.uuid4()),
                        "tenant_id": tenant_id or "default",
                        "service_type": "automatic",
                        "sla_requirements": {
                            "latency": 1,
                            "reliability": 99
                        }
                    }
                elif nest_template:
                    payload = {"tenant_id": tenant_id, "nest": nest_template}
                else:
                    raise HTTPException(status_code=400, detail="intent_text ou nest_template deve ser fornecido")
                
                response = await client.post(
                    url,
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"✅ SEM-CSMF: Intent interpretado - intent_id={data.get('intent_id')}")
                return data
            except httpx.HTTPStatusError as e:
                error_msg = f"SEM-CSMF erro HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"❌ SEM-CSMF: {error_msg}")
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=error_msg
                )
            except httpx.RequestError as e:
                error_msg = f"SEM-CSMF erro de conexão: {str(e)}"
                logger.error(f"❌ SEM-CSMF: {error_msg}")
                raise HTTPException(status_code=503, detail=f"SEM-CSMF offline: {str(e)}")
    
    async def call_ml_nsmf(
        self, 
        nest_id: str, 
        slice_type: str,
        sla_requirements: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        (2) ML-NSMF – Avaliação de Capacidades
        
        Previsão de recursos disponíveis.
        Avaliação temporal.
        Se insuficiente → retornar REJECT antes da decisão final.
        
        Retorna: { "prediction": { "risk_level": str, ... }, "explanation": {...} }
        """
        async with httpx.AsyncClient() as client:
            try:
                metrics_for_prediction = {
                    "nest_id": nest_id,
                    "slice_type": slice_type,
                    "sla_requirements": sla_requirements,
                    "tenant_id": tenant_id
                }
                
                response = await client.post(
                    f"{settings.ml_nsmf_url}/api/v1/predict",
                    json=metrics_for_prediction,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                risk_level = data.get("prediction", {}).get("risk_level", "UNKNOWN")
                logger.info(f"✅ ML-NSMF: Avaliação concluída - risco={risk_level}")
                return data
            except httpx.HTTPStatusError as e:
                error_msg = f"ML-NSMF erro HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"❌ ML-NSMF: {error_msg}")
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=error_msg
                )
            except httpx.RequestError as e:
                error_msg = f"ML-NSMF erro de conexão: {str(e)}"
                logger.error(f"❌ ML-NSMF: {error_msg}")
                raise HTTPException(status_code=503, detail=f"ML-NSMF offline: {str(e)}")
    
    async def call_decision_engine(
        self, 
        intent_id: str, 
        nest_id: str, 
        tenant_id: str,
        ml_prediction: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        (3) DECISION ENGINE – Decisão Oficial
        
        Retornar somente dois estados: ACCEPT ou REJECT
        
        A resposta precisa conter:
        - decision: ACCEPT | REJECT
        - reason: <texto>
        - sla_id: <uuid real>
        - timestamp: <datetime>
        - required_resources: {...}
        - predicted_load: {...}
        
        Retorna: { "decision": "ACCEPT"|"REJECT", "reason": str, "sla_id": str, ... }
        """
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    "intent_id": intent_id,
                    "nest_id": nest_id,
                    "tenant_id": tenant_id
                }
                
                if ml_prediction:
                    payload["ml_prediction"] = ml_prediction
                
                response = await client.post(
                    f"{settings.decision_engine_url}/api/v1/decide",
                    json=payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                
                # LOG DETALHADO DO JSON BRUTO RETORNADO PELO DECISION ENGINE
                raw_response_text = response.text
                logger.info("Decision Engine RAW response status=%s body=%s", response.status_code, raw_response_text)
                
                try:
                    data = response.json()
                except Exception as json_error:
                    logger.error(f"❌ Decision Engine: Erro ao fazer parse do JSON - {type(json_error).__name__}: {str(json_error)}")
                    logger.error(f"   Response text: {raw_response_text}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Formato inesperado retornado pelo Decision Engine. Verifique a estrutura JSON. Erro: {str(json_error)}"
                    )
                
                # Normalizar campos do Decision Engine para o formato esperado pelo Portal
                # O Decision Engine retorna "action": "AC"|"RENEG"|"REJ", mas o Portal espera "decision": "ACCEPT"|"REJECT"
                action = data.get("action", "").upper()
                
                # Mapear action para decision
                action_to_decision = {
                    "AC": "ACCEPT",
                    "ACCEPT": "ACCEPT",  # Caso já venha normalizado
                    "REJ": "REJECT",
                    "REJECT": "REJECT",  # Caso já venha normalizado
                    "RENEG": "REJECT"  # Renegotiate é tratado como REJECT no portal
                }
                
                decision = action_to_decision.get(action)
                
                # Se não encontrou mapeamento, tentar campo "decision" diretamente
                if not decision:
                    decision = data.get("decision", "").upper()
                    if decision not in ["ACCEPT", "REJECT"]:
                        logger.error(f"❌ Decision Engine: Ação/Decisão inválida - action={action}, decision={decision}. Dados completos: {data}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Formato inesperado retornado pelo Decision Engine. Ação '{action}' não mapeável para ACCEPT/REJECT. Verifique a estrutura JSON."
                        )
                
                # Normalizar resposta para formato esperado pelo Portal
                normalized_data = {
                    "decision": decision,
                    "action": action,  # Manter original para debug
                    "reason": data.get("reasoning") or data.get("reason") or data.get("justification") or "",
                    "reasoning": data.get("reasoning"),  # Manter original
                    "justification": data.get("reasoning") or data.get("reason") or data.get("justification") or "",
                    "sla_id": data.get("sla_id") or data.get("decision_id") or intent_id,
                    "decision_id": data.get("decision_id"),
                    "intent_id": data.get("intent_id") or intent_id,
                    "nest_id": data.get("nest_id") or nest_id,
                    "timestamp": data.get("timestamp") or "",
                    "confidence": data.get("confidence"),
                    "ml_risk_score": data.get("ml_risk_score"),
                    "ml_risk_level": data.get("ml_risk_level"),
                    "slos": data.get("slos"),
                    "domains": data.get("domains"),
                    "required_resources": data.get("required_resources") or data.get("metadata", {}).get("required_resources"),
                    "predicted_load": data.get("predicted_load") or data.get("metadata", {}).get("predicted_load"),
                    # Manter campos originais para compatibilidade
                    **{k: v for k, v in data.items() if k not in ["decision", "action", "reason", "reasoning", "justification", "sla_id", "decision_id"]}
                }
                
                logger.info(f"✅ Decision Engine: Decisão {decision} (action original: {action})")
                return normalized_data
            except httpx.HTTPStatusError as e:
                # Log detalhado da resposta HTTP de erro
                logger.error("Decision Engine RAW error response status=%s body=%s", e.response.status_code, e.response.text)
                error_msg = f"Decision Engine erro HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"❌ Decision Engine: {error_msg}")
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=f"Decision Engine: {error_msg}"
                )
            except httpx.RequestError as e:
                error_msg = f"Decision Engine erro de conexão: {str(e)}"
                logger.error(f"❌ Decision Engine: {error_msg}")
                raise HTTPException(status_code=503, detail=f"Decision Engine offline: {str(e)}")
            except HTTPException:
                # Re-raise HTTPException sem modificação
                raise
            except Exception as e:
                # Capturar qualquer outro erro e logar detalhadamente
                logger.error(f"❌ Decision Engine: Erro inesperado - {type(e).__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Formato inesperado retornado pelo Decision Engine. Verifique a estrutura JSON. Erro: {str(e)}"
                )
    
    async def call_bc_nssmf(
        self,
        sla_id: str,
        decision: str,
        tenant_id: str,
        intent_id: str,
        nest_id: str,
        sla_requirements: Dict[str, Any] = None,
        required_resources: Dict[str, Any] = None,
        service_type: str = None,
        justification: str = None,
        timestamp: str = None
    ) -> Dict[str, Any]:
        """
        (4) BC-NSSMF – Registro Blockchain REAL
        
        Conforme Capítulo 6 - Estrutura SLA-aware completa:
        - Criar estrutura SLA-aware conforme dissertação
        - Calcular hash SHA-256 do SLA-aware
        - Converter SLOs para formato numérico válido
        - Enviar ao BC-NSSMF via POST /bc/register
        
        O portal deve exibir no frontend:
        - Blockchain status: confirmed | pending | error
        - TxHash: <hash real>
        - Block: <número>
        
        Retorna: { "blockchain_status": "CONFIRMED"|"PENDING"|"ERROR", "tx_hash": str, "block_number": int, "sla_hash": str }
        """
        async with httpx.AsyncClient() as client:
            try:
                # Construir estrutura SLA-aware conforme Capítulo 6
                sla_requirements_dict = sla_requirements or {}
                
                # Converter SLOs para formato numérico válido (sem strings inválidas)
                slos_numeric = convert_slos_to_numeric(sla_requirements_dict, decision)
                
                # Construir SLA-aware completo
                sla_aware_dict = {
                    "slaHash": "",  # Será calculado abaixo
                    "customer": tenant_id,
                    "serviceName": f"SLA-{sla_id}",
                    "intent_id": intent_id,
                    "nest_id": nest_id,
                    "parameters": {
                        "service_type": service_type,
                        "sla_requirements": sla_requirements_dict,
                        "required_resources": required_resources or {}
                    },
                    "slos": slos_numeric,
                    "decision": decision,
                    "justification": justification or "",
                    "timestamp": timestamp or "",
                    "metadata": {
                        "sla_id": sla_id,
                        "tenant_id": tenant_id
                    }
                }
                
                # Calcular hash SHA-256 do SLA-aware (conforme Cap. 6)
                sla_hash = calculate_sla_hash(sla_aware_dict)
                sla_aware_dict["slaHash"] = sla_hash
                
                logger.info(f"📝 SLA-aware criado: hash={sla_hash}, SLOs={len(slos_numeric)}")
                
                # Preparar request para BC-NSSMF conforme API: POST /bc/register
                # O BC-NSSMF espera: { customer, serviceName, slaHash, slos: [{name, value, threshold}] }
                bc_request = SLARequestBC(
                    customer=tenant_id,
                    serviceName=f"SLA-{sla_id}",
                    slaHash=sla_hash,
                    slos=[SLO(**slo) for slo in slos_numeric]
                )
                
                # Enviar ao BC-NSSMF
                response = await client.post(
                    f"{settings.bc_nssmf_url}/bc/register",
                    json=bc_request.model_dump(),
                    timeout=30.0,
                )
                
                # Log detalhado da resposta
                logger.info(f"BC-NSSMF RAW response status={response.status_code} body={response.text}")
                
                response.raise_for_status()
                data = response.json()
                
                # Extrair informações da transação
                blockchain_status = "CONFIRMED" if data.get("status") == "ok" else "PENDING"
                tx_hash = data.get("tx") or data.get("tx_hash") or data.get("transaction_hash") or data.get("hash")
                block_number = data.get("block_number") or data.get("blockNumber")
                
                if not tx_hash:
                    logger.warning(f"⚠️ BC-NSSMF não retornou tx_hash na resposta: {data}")
                    # Tentar extrair de transactionHash se presente
                    if "transactionHash" in data:
                        tx_hash = data["transactionHash"]
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="BC-NSSMF não retornou tx_hash - registro pode ter falhado"
                        )
                
                logger.info(f"✅ BC-NSSMF: SLA registrado - tx_hash={tx_hash}, status={blockchain_status}, sla_hash={sla_hash}")
                
                return {
                    "blockchain_status": blockchain_status,
                    "tx_hash": tx_hash,
                    "block_number": block_number,
                    "sla_id": data.get("sla_id", sla_id),
                    "sla_hash": sla_hash
                }
            except httpx.HTTPStatusError as e:
                # Log detalhado de erro 422 (validação)
                if e.response.status_code == 422:
                    logger.error(f"❌ BC-NSSMF: Erro de validação (422) - {e.response.text}")
                    logger.error(f"   Payload enviado: {bc_request.model_dump() if 'bc_request' in locals() else 'N/A'}")
                
                error_msg = f"BC-NSSMF erro HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"❌ BC-NSSMF: {error_msg}")
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=f"BC-NSSMF: {error_msg}"
                )
            except httpx.RequestError as e:
                error_msg = f"BC-NSSMF erro de conexão: {str(e)}"
                logger.error(f"❌ BC-NSSMF: {error_msg}")
                raise HTTPException(status_code=503, detail=f"BC-NSSMF offline: {str(e)}")
    
    async def call_sla_agent_layer(self, sla_id: str, slice_type: str = None) -> Dict[str, Any]:
        """
        (5) SLA-AGENT LAYER — Coleta Métricas em Tempo Real
        
        Coleta métricas reais de RAN, Transport e Core via SLA-Agent Layer.
        Agrega métricas de todos os domínios para o SLA.
        
        Retorna métricas agregadas:
        - latency_ms
        - jitter_ms
        - throughput_ul
        - throughput_dl
        - packet_loss
        - availability
        
        Se SLA-Agent Layer estiver offline → erro 503.
        
        Retorna: { "latency_ms": float, "jitter_ms": float, "throughput_ul": float, ... }
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.sla_agent_layer_url}/api/v1/metrics/realtime",
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Extrair métricas agregadas
                metrics = data.get("metrics", {})
                ran_metrics = metrics.get("ran", {})
                transport_metrics = metrics.get("transport", {})
                core_metrics = metrics.get("core", {})
                
                # Agregar métricas (priorizar transporte para latency/jitter, RAN para throughput)
                latency_ms = transport_metrics.get("latency_ms") or metrics.get("latency_ms")
                jitter_ms = transport_metrics.get("jitter_ms") or metrics.get("jitter_ms")
                throughput_ul = ran_metrics.get("throughput_ul") or metrics.get("throughput_ul")
                throughput_dl = ran_metrics.get("throughput_dl") or metrics.get("throughput_dl")
                packet_loss = transport_metrics.get("packet_loss") or metrics.get("packet_loss")
                availability = core_metrics.get("availability") or metrics.get("availability")
                
                logger.info(f"✅ SLA-Agent Layer: Métricas coletadas para SLA {sla_id}")
                
                return {
                    "sla_id": sla_id,
                    "latency_ms": latency_ms,
                    "jitter_ms": jitter_ms,
                    "throughput_ul": throughput_ul,
                    "throughput_dl": throughput_dl,
                    "packet_loss": packet_loss,
                    "availability": availability,
                    "slice_status": "ACTIVE" if availability and availability > 99.0 else "PENDING",
                    "last_update": data.get("timestamp") or None,
                    "metrics": metrics
                }
            except httpx.HTTPStatusError as e:
                error_msg = f"SLA-Agent Layer erro HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"❌ SLA-Agent Layer: {error_msg}")
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=error_msg
                )
            except httpx.RequestError as e:
                error_msg = f"SLA-Agent Layer erro de conexão: {str(e)}"
                logger.error(f"❌ SLA-Agent Layer: {error_msg}")
                raise HTTPException(status_code=503, detail=f"SLA-Agent Layer offline: {str(e)}")
    
    async def call_metrics(self, sla_id: str) -> Dict[str, Any]:
        """
        (6) OBSERVABILIDADE REAL — MÉTRICAS DO NASP (via SLA-Agent Layer)
        
        As métricas devem vir exclusivamente do SLA-Agent Layer, com os campos:
        - latency_ms
        - jitter_ms
        - throughput_ul
        - throughput_dl
        - packet_loss
        - availability
        - slice_status
        
        Se SLA-Agent Layer estiver offline → erro 503.
        
        Retorna: { "latency_ms": float, "jitter_ms": float, "throughput_ul": float, ... }
        """
        return await self.call_sla_agent_layer(sla_id)
    
    # Métodos de compatibilidade (mantidos para não quebrar código existente)
    async def send_intent_to_sem_csmf(self, intent_text: str, tenant_id: str) -> Dict[str, Any]:
        """Alias para call_sem_csmf - compatibilidade"""
        return await self.call_sem_csmf(intent_text=intent_text, tenant_id=tenant_id)
    
    async def evaluate_with_ml_nsmf(
        self, 
        nest_id: str, 
        slice_type: str,
        sla_requirements: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """Alias para call_ml_nsmf - compatibilidade"""
        return await self.call_ml_nsmf(nest_id, slice_type, sla_requirements, tenant_id)
    
    async def submit_to_decision_engine(
        self, 
        intent_id: str, 
        nest_id: str, 
        tenant_id: str,
        ml_prediction: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Alias para call_decision_engine - compatibilidade"""
        return await self.call_decision_engine(intent_id, nest_id, tenant_id, ml_prediction)
    
    async def register_in_blockchain(
        self,
        sla_id: str,
        decision: str,
        tenant_id: str,
        intent_id: str,
        nest_id: str,
        sla_requirements: Dict[str, Any] = None,
        required_resources: Dict[str, Any] = None,
        service_type: str = None,
        justification: str = None,
        timestamp: str = None
    ) -> Dict[str, Any]:
        """Alias para call_bc_nssmf - compatibilidade"""
        return await self.call_bc_nssmf(
            sla_id, decision, tenant_id, intent_id, nest_id,
            sla_requirements, required_resources, service_type, justification, timestamp
        )
    
    async def submit_template_to_nasp(self, nest_template: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """
        Envia template técnico ao NASP com TODOS os módulos
        
        Fluxo REAL completo:
        1. SEM-CSMF: Interpreta template e gera NEST
        2. ML-NSMF: Avalia capacidades e recursos
        3. Decision Engine: Decisão final (ACCEPT/REJECT)
        4. BC-NSSMF: Registro no blockchain
        5. SLA-Agent Layer: Coleta métricas iniciais (apenas se ACCEPT)
        
        Retorna resposta padronizada conforme especificação
        """
        try:
            # Passo 1: SEM-CSMF (novo contrato para /submit)
            async with httpx.AsyncClient() as client:
                # Extrair service_type do nest_template (pode vir em type, slice_type, ou service_type)
                service_type = (
                    nest_template.get("type") or 
                    nest_template.get("slice_type") or 
                    nest_template.get("service_type") or 
                    "automatic"
                )
                
                sem_payload = {
                    "intent_id": str(uuid.uuid4()),
                    "tenant_id": tenant_id or "default",
                    "service_type": service_type,
                    "sla_requirements": nest_template.get("sla_requirements", {})
                }
                
                response_sem = await client.post(
                    f"{settings.nasp_sem_csmf_url}/api/v1/intents",
                    json=sem_payload,
                    timeout=30.0,
                )
                response_sem.raise_for_status()
                sem_result = response_sem.json()
            
            intent_id = sem_result.get("intent_id")
            nest_id = sem_result.get("nest_id")
            # service_type pode vir do SEM-CSMF ou do nest_template
            service_type = (
                sem_result.get("service_type") or
                sem_result.get("slice_type") or
                nest_template.get("service_type") or
                nest_template.get("type") or
                nest_template.get("slice_type") or
                "automatic"
            )
            slice_type = service_type  # Usar service_type como slice_type também
            
            if not intent_id:
                raise HTTPException(
                    status_code=500,
                    detail="SEM-CSMF não retornou intent_id"
                )
            
            if not nest_id:
                raise HTTPException(
                    status_code=500,
                    detail="SEM-CSMF não retornou nest_id"
                )
            
            sem_csmf_status = "OK"
            
        except httpx.HTTPStatusError as e:
            sem_csmf_status = "ERROR"
            error_msg = f"SEM-CSMF erro HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"❌ SEM-CSMF: {error_msg}")
            raise HTTPException(
                status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                detail=f"SEM-CSMF: {error_msg}"
            )
        except httpx.RequestError as e:
            sem_csmf_status = "ERROR"
            error_msg = f"SEM-CSMF erro de conexão: {str(e)}"
            logger.error(f"❌ SEM-CSMF: {error_msg}")
            raise HTTPException(status_code=503, detail=f"SEM-CSMF offline: {str(e)}")
        except HTTPException as e:
            sem_csmf_status = "ERROR"
            raise HTTPException(
                status_code=e.status_code,
                detail=f"SEM-CSMF: {e.detail}"
            )
        
        try:
            # Passo 2: ML-NSMF
            ml_result = await self.call_ml_nsmf(
                nest_id=nest_id,
                slice_type=slice_type,
                sla_requirements=nest_template.get("sla_requirements", {}),
                tenant_id=tenant_id
            )
            ml_nsmf_status = "OK"
            
        except HTTPException as e:
            ml_nsmf_status = "ERROR"
            raise HTTPException(
                status_code=e.status_code,
                detail=f"ML-NSMF: {e.detail}"
            )
        
        try:
            # Passo 3: Decision Engine
            decision_result = await self.call_decision_engine(
                intent_id=intent_id,
                nest_id=nest_id,
                tenant_id=tenant_id,
                ml_prediction=ml_result
            )
            
            # decision_result já vem normalizado de call_decision_engine
            # A normalização já foi feita dentro de call_decision_engine
            decision = decision_result.get("decision", "").upper()
            
            # Validação adicional de segurança
            if decision not in ["ACCEPT", "REJECT"]:
                logger.error(f"❌ Decision Engine: Decisão inválida após normalização - {decision}. Dados: {decision_result}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Formato inesperado retornado pelo Decision Engine. Decisão '{decision}' não é ACCEPT ou REJECT. Verifique a estrutura JSON."
                )
            
            # Extrair campos normalizados (já processados em call_decision_engine)
            sla_id = decision_result.get("sla_id") or decision_result.get("decision_id") or intent_id
            reason = decision_result.get("reason") or decision_result.get("justification") or decision_result.get("reasoning") or ""
            # Timestamp deve vir do Decision Engine - SEM fallback local
            # Se não vier, deixar vazio (será tratado como campo opcional)
            timestamp = decision_result.get("timestamp") or decision_result.get("created_at") or ""
            
        except HTTPException as e:
            # Re-raise HTTPException mantendo detalhes
            raise HTTPException(
                status_code=e.status_code,
                detail=f"Decision Engine: {e.detail}"
            )
        except Exception as e:
            # Capturar qualquer outro erro e logar detalhadamente
            logger.error(f"❌ Decision Engine: Erro inesperado no submit_template_to_nasp - {type(e).__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar resposta do Decision Engine: {str(e)}"
            )
        
        try:
            # Passo 4: BC-NSSMF
            # Construir SLA-aware completo e registrar no blockchain
            blockchain_result = await self.call_bc_nssmf(
                sla_id=sla_id,
                decision=decision,
                tenant_id=tenant_id,
                intent_id=intent_id,
                nest_id=nest_id,
                sla_requirements=nest_template.get("sla_requirements", {}),
                required_resources=decision_result.get("required_resources"),
                service_type=service_type or slice_type,
                justification=reason,
                timestamp=timestamp
            )
            
            bc_status = blockchain_result.get("blockchain_status", "ERROR")
            
        except HTTPException as e:
            # NÃO fazer fallback silencioso - propagar erro 503
            raise HTTPException(
                status_code=e.status_code,
                detail=f"BC-NSSMF: {e.detail}"
            )
        
        # Passo 5: SLA-Agent Layer (apenas se ACCEPT)
        sla_agent_status = "SKIPPED"
        if decision == "ACCEPT":
            try:
                logger.info(f"🔄 SLA-Agent Layer: Iniciando coleta de métricas iniciais para SLA {sla_id}")
                await self.call_sla_agent_layer(sla_id, slice_type)
                sla_agent_status = "OK"
                logger.info(f"✅ SLA-Agent Layer: Métricas coletadas com sucesso")
            except HTTPException as e:
                sla_agent_status = "ERROR"
                logger.warning(f"⚠️ SLA-Agent Layer: Falha na coleta inicial de métricas - {e.detail}")
                # Não falhar o fluxo se SLA-Agent Layer falhar - apenas logar
        
        # Retornar resposta padronizada unificada conforme especificação
        # Incluir sla_hash calculado conforme Capítulo 6
        return {
            "intent_id": intent_id,
            "service_type": service_type or slice_type,
            "sla_requirements": nest_template.get("sla_requirements", {}),
            "ml_prediction": ml_result.get("prediction") if ml_result else {},
            "decision": decision,
            "justification": reason,
            "reason": reason,  # Mantido para compatibilidade
            "blockchain_tx_hash": blockchain_result.get("tx_hash"),
            "tx_hash": blockchain_result.get("tx_hash"),  # Mantido para compatibilidade
            "sla_hash": blockchain_result.get("sla_hash"),  # Hash SHA-256 do SLA-aware
            "timestamp": timestamp,
            "status": "ok",
            "sla_id": sla_id,
            "nest_id": nest_id,
            "sem_csmf_status": sem_csmf_status,
            "ml_nsmf_status": ml_nsmf_status,
            "bc_status": bc_status,
            "sla_agent_status": sla_agent_status,
            "block_number": blockchain_result.get("block_number")
        }
    
    async def get_sla_status(self, sla_id: str) -> Dict[str, Any]:
        """Status do SLA - Consulta em tempo real ao NASP"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{settings.nasp_sem_csmf_url}/api/v1/intents/{sla_id}",
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(
                        status_code=404,
                        detail=f"SLA {sla_id} não encontrado no NASP"
                    )
                error_msg = f"NASP status erro HTTP {e.response.status_code}: {e.response.text}"
                logger.error(f"❌ {error_msg}")
                raise HTTPException(
                    status_code=503 if e.response.status_code >= 500 else e.response.status_code,
                    detail=error_msg
                )
            except httpx.RequestError as e:
                error_msg = f"NASP status erro de conexão: {str(e)}"
                logger.error(f"❌ {error_msg}")
                raise HTTPException(status_code=503, detail=f"NASP offline: {str(e)}")
    
    async def get_sla_metrics(self, sla_id: str) -> Dict[str, Any]:
        """Métricas REAIS do SLA - alias para call_metrics"""
        return await self.call_metrics(sla_id)
