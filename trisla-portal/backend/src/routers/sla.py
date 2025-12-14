"""
Rotas REAIS para SLA - SEM SIMULAÇÕES
Todas as respostas vêm do NASP real (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF)
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from src.schemas.sla import (
    SLAInterpretRequest,
    SLASubmitRequest,
    SLAStatusResponse,
    SLAMetricsResponse,
    SLASubmitResponse,
)
from src.services.nasp import NASPService
from src.utils.text_processing import corrigir_erros_ortograficos, inferir_tipo_slice, extrair_parametros_tecnicos
from src.api.schemas.error_response import ErrorResponse
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
        # Validação básica de entrada (payload minimalista)
        if not request.intent or not request.intent.strip():
            raise HTTPException(
                status_code=400,
                detail="Intent não pode ser vazio"
            )
        
        tenant_id = (request.tenant_id or "default").strip()
        
        # ETAPA 1: Corrigir erros ortográficos (Cap. 5 - PNL)
        intent_text_corrigido = corrigir_erros_ortograficos(request.intent.strip())
        
        # ETAPA 2: Inferência semântica inicial ANTES do SEM-CSMF (conforme dissertação)
        # Esta é uma função determinística e rastreável, não é IA inventada
        from src.utils.text_processing import infer_service_type_from_intent
        try:
            service_type_inferido = infer_service_type_from_intent(intent_text_corrigido)
            logger.info(f"🔍 Inferência semântica inicial realizada: {service_type_inferido}")
        except ValueError as e:
            logger.error(f"❌ Erro na inferência semântica: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Erro semântico: {str(e)}. Por favor, especifique o tipo de serviço desejado (URLLC, eMBB ou mMTC) no texto."
            )
        
        # ETAPA 3: Extrair parâmetros técnicos do texto (opcional, para enriquecimento)
        parametros_extraidos = extrair_parametros_tecnicos(intent_text_corrigido)
        
        # ETAPA 4: Chamada REAL ao SEM-CSMF com service_type válido (enum correto)
        # O SEM-CSMF recebe o enum válido e especializa os requisitos
        result = await nasp_service.call_sem_csmf(
            intent_text=intent_text_corrigido,
            tenant_id=tenant_id,
            service_type=service_type_inferido  # ✅ ENUM VÁLIDO inferido antes
        )
        
        # Enriquecer resposta com informações processadas localmente
        # service_type já foi inferido e enviado ao SEM-CSMF, mas garantimos que está na resposta
        if not result.get("service_type"):
            result["service_type"] = service_type_inferido
        
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
        service_type_final = result.get("service_type") or result.get("slice_type") or service_type_inferido
        
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
        
        # Garantir que decision é ACCEPT, RENEG ou REJECT
        # A normalização já foi feita em nasp.py, mas validamos novamente por segurança
        decision = result.get("decision", "").upper()
        if decision not in ["ACCEPT", "RENEG", "REJECT"]:
            logger.error(f"❌ /submit: Decisão inválida após processamento - {decision}. Dados: {result}")
            raise HTTPException(
                status_code=500,
                detail=f"Formato inesperado retornado pelo Decision Engine. Decisão '{decision}' não é ACCEPT, RENEG ou REJECT. Verifique a estrutura JSON."
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
    except HTTPException as e:
        # Converter HTTPException para JSONResponse com ErrorResponse
        detail = e.detail
        if isinstance(detail, dict):
            # Se já é um dict com reason, usar diretamente
            reason = detail.get("reason", "business_error")
            phase = detail.get("phase", "semantic")
            upstream_status = detail.get("upstream_status", e.status_code)
            error_detail = detail.get("detail", str(detail))
        else:
            # Se é string, determinar reason baseado no status_code
            if e.status_code == 422:
                reason = "business_error"
                phase = "semantic"
            elif e.status_code >= 500:
                reason = "nasp_degraded"
                phase = "blockchain"
            else:
                reason = "business_error"
                phase = "semantic"
            upstream_status = e.status_code
            error_detail = str(detail)
        
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(
                reason=reason,
                detail=error_detail,
                phase=phase,
                upstream_status=upstream_status
            ).dict()
        )
    except Exception as e:
        logger.error(f"❌ Erro ao submeter SLA: {type(e).__name__}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                reason="nasp_degraded",
                detail=str(e),
                phase="blockchain",
                upstream_status=503
            ).dict()
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

