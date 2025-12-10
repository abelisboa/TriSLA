"""
Rotas REAIS para SLA - SEM SIMULAÇÕES
Todas as respostas vêm do NASP real (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF)
"""
from fastapi import APIRouter, HTTPException
from src.schemas.sla import (
    SLAInterpretRequest,
    SLASubmitRequest,
    SLAStatusResponse,
    SLAMetricsResponse,
    SLASubmitResponse,
)
from src.services.nasp import NASPService
from src.utils.text_processing import corrigir_erros_ortograficos, inferir_tipo_slice, extrair_parametros_tecnicos
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
nasp_service = NASPService()


@router.post("/interpret")
async def interpret_sla(request: SLAInterpretRequest):
    """
    Interpretação PLN → Ontologia (REAL)
    
    Chama módulo SEM-CSMF REAL do NASP:
    - Retorna tipo de slice
    - Retorna parâmetros técnicos interpretados
    - Retorna mensagens de erro semânticas quando houver
    - Nunca aceita entrada inválida
    """
    try:
        # Validação básica de entrada
        if not request.intent_text or not request.intent_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Intent text não pode ser vazio"
            )
        
        if not request.tenant_id or not request.tenant_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Tenant ID não pode ser vazio"
            )
        
        # ETAPA 1: Corrigir erros ortográficos (Cap. 5 - PNL)
        intent_text_corrigido = corrigir_erros_ortograficos(request.intent_text.strip())
        
        # ETAPA 2: Inferir tipo de slice se necessário
        tipo_slice_inferido = inferir_tipo_slice(intent_text_corrigido)
        
        # ETAPA 3: Extrair parâmetros técnicos do texto
        parametros_extraidos = extrair_parametros_tecnicos(intent_text_corrigido)
        
        # Chamada REAL ao SEM-CSMF do NASP
        result = await nasp_service.call_sem_csmf(
            intent_text=intent_text_corrigido,
            tenant_id=request.tenant_id.strip()
        )
        
        # Enriquecer resposta com informações processadas localmente
        if not result.get("service_type") and tipo_slice_inferido != "AUTO":
            result["service_type"] = tipo_slice_inferido
        
        # Mesclar parâmetros extraídos com resposta do SEM-CSMF
        if parametros_extraidos:
            sla_req = result.get("sla_requirements", {})
            sla_req.update(parametros_extraidos)
            result["sla_requirements"] = sla_req
        
        # Verificar se há erros semânticos na resposta
        if result.get("error") or result.get("semantic_error"):
            raise HTTPException(
                status_code=422,
                detail=result.get("error") or result.get("semantic_error")
            )
        
        # Retornar resposta REAL do SEM-CSMF com parâmetros técnicos sugeridos
        # Conforme Capítulo 5 - SEM-CSMF deve retornar parâmetros técnicos editáveis
        service_type_final = result.get("service_type") or result.get("slice_type") or tipo_slice_inferido
        
        # Construir parâmetros técnicos sugeridos (ETAPA 2)
        technical_parameters = result.get("technical_parameters", {})
        if parametros_extraidos:
            technical_parameters.update(parametros_extraidos)
        
        # Se SEM-CSMF não retornou parâmetros, usar valores padrão baseados no tipo de slice
        if not technical_parameters and service_type_final:
            if service_type_final.upper() == "URLLC":
                technical_parameters = {
                    "latency_maxima_ms": 10,
                    "disponibilidade_percent": 99.99,
                    "confiabilidade_percent": 99.99,
                    "numero_dispositivos": 10
                }
            elif service_type_final.upper() == "EMBB":
                technical_parameters = {
                    "latency_maxima_ms": 50,
                    "disponibilidade_percent": 99.9,
                    "confiabilidade_percent": 99.9,
                    "throughput_min_dl_mbps": 100,
                    "throughput_min_ul_mbps": 50
                }
            elif service_type_final.upper() == "MMTC":
                technical_parameters = {
                    "latency_maxima_ms": 100,
                    "disponibilidade_percent": 95,
                    "confiabilidade_percent": 95,
                    "numero_dispositivos": 1000
                }
        
        return {
            "intent_id": result.get("intent_id") or result.get("id"),
            "service_type": service_type_final,
            "sla_requirements": result.get("sla_requirements", {}),
            "sla_id": result.get("intent_id") or result.get("id"),
            "status": "processing",
            "tenant_id": request.tenant_id,
            "nest_id": result.get("nest_id"),
            "slice_type": service_type_final,
            "technical_parameters": technical_parameters,  # Parâmetros técnicos sugeridos (ETAPA 2)
            "created_at": result.get("created_at") or result.get("timestamp") or None,
            "message": "SLA interpretado pelo SEM-CSMF com sucesso. Ajuste os parâmetros técnicos na próxima etapa."
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao interpretar SLA: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=SLASubmitResponse)
async def submit_sla_template(request: SLASubmitRequest):
    """
    Submissão com TODOS os módulos TriSLA
    
    Fluxo REAL completo:
    1. SEM-CSMF: Interpreta template e gera NEST
    2. ML-NSMF: Avalia capacidades e recursos
    3. Decision Engine: Decisão final (ACCEPT/REJECT)
    4. BC-NSSMF: Registro no blockchain
    
    Resposta padronizada conforme especificação
    """
    try:
        # Validação básica
        if not request.template_id or not request.template_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Template ID não pode ser vazio"
            )
        
        if not request.form_values:
            raise HTTPException(
                status_code=400,
                detail="Form values não podem ser vazios"
            )
        
        # Construir template NEST a partir do template_id e form_values
        # Extrair service_type dos form_values (pode vir em type, slice_type, ou service_type)
        service_type_from_form = (
            request.form_values.get("type") or
            request.form_values.get("slice_type") or
            request.form_values.get("service_type") or
            None
        )
        
        nest_template = {
            "sla_requirements": request.form_values,
            "tenant_id": request.tenant_id,
            "template_id": request.template_id
        }
        
        # Incluir type/slice_type se existir nos form_values
        if service_type_from_form:
            nest_template["type"] = service_type_from_form
            nest_template["slice_type"] = service_type_from_form
        
        # Enviar ao NASP com TODOS os módulos (sequência completa)
        result = await nasp_service.submit_template_to_nasp(
            nest_template=nest_template,
            tenant_id=request.tenant_id
        )
        
        # Garantir que decision é ACCEPT ou REJECT
        # A normalização já foi feita em nasp.py, mas validamos novamente por segurança
        decision = result.get("decision", "").upper()
        if decision not in ["ACCEPT", "REJECT"]:
            logger.error(f"❌ /submit: Decisão inválida após processamento - {decision}. Dados: {result}")
            raise HTTPException(
                status_code=500,
                detail=f"Formato inesperado retornado pelo Decision Engine. Decisão '{decision}' não é ACCEPT ou REJECT. Verifique a estrutura JSON."
            )
        
        # Retornar resposta padronizada (incluindo campos unificados)
        # Incluir sla_hash conforme Capítulo 6
        return SLASubmitResponse(
            decision=decision,
            reason=result.get("reason") or result.get("justification", ""),
            justification=result.get("justification") or result.get("reason", ""),
            sla_id=result.get("sla_id"),
            timestamp=result.get("timestamp") or None,
            intent_id=result.get("intent_id"),
            service_type=result.get("service_type"),
            sla_requirements=result.get("sla_requirements"),
            ml_prediction=result.get("ml_prediction"),
            blockchain_tx_hash=result.get("blockchain_tx_hash") or result.get("tx_hash"),
            tx_hash=result.get("tx_hash") or result.get("blockchain_tx_hash"),
            sla_hash=result.get("sla_hash"),  # Hash SHA-256 do SLA-aware
            status=result.get("status", "ok"),
            sem_csmf_status=result.get("sem_csmf_status", "ERROR"),
            ml_nsmf_status=result.get("ml_nsmf_status", "ERROR"),
            bc_status=result.get("bc_status", "ERROR"),
            sla_agent_status=result.get("sla_agent_status", "SKIPPED"),
            block_number=result.get("block_number"),
            nest_id=result.get("nest_id")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao submeter SLA: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar submissão do SLA: {str(e)}"
        )


@router.get("/status/{sla_id}", response_model=SLAStatusResponse)
async def get_sla_status(sla_id: str):
    """
    Status do SLA
    
    Consulta em tempo real ao NASP - SEM cache local
    """
    try:
        result = await nasp_service.get_sla_status(sla_id)
        
        return SLAStatusResponse(
            sla_id=sla_id,
            status=result.get("status", "unknown"),
            tenant_id=result.get("tenant_id", ""),
            intent_id=result.get("intent_id"),
            nest_id=result.get("nest_id"),
            created_at=result.get("created_at"),
            updated_at=result.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        if "não encontrado" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        logger.error(f"Erro ao obter status do SLA {sla_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{sla_id}", response_model=SLAMetricsResponse)
async def get_sla_metrics(sla_id: str):
    """
    Métricas Reais do NASP (SLOs)
    
    Retorna métricas REAIS padronizadas:
    - latency_ms
    - jitter_ms
    - throughput_ul
    - throughput_dl
    - packet_loss
    - availability
    - slice_status (ACTIVE | FAILED | PENDING | TERMINATED)
    - last_update (ISO8601)
    
    Consulta REAL a cada chamada - SEM cache local
    Se NASP offline → erro 503
    """
    try:
        result = await nasp_service.call_metrics(sla_id)
        
        # Retornar resposta padronizada
        return SLAMetricsResponse(
            sla_id=sla_id,
            slice_status=result.get("slice_status"),
            latency_ms=result.get("latency_ms"),
            jitter_ms=result.get("jitter_ms"),
            throughput_ul=result.get("throughput_ul"),
            throughput_dl=result.get("throughput_dl"),
            packet_loss=result.get("packet_loss"),
            availability=result.get("availability"),
            last_update=result.get("last_update"),
            tenant_id=result.get("tenant_id"),
            metrics=result.get("metrics")
        )
    except HTTPException:
        raise
    except Exception as e:
        if "não encontrado" in str(e).lower() or "not found" in str(e).lower() or "404" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        logger.error(f"Erro ao obter métricas do SLA {sla_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

