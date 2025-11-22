"""
Gerador de NEST - SEM-CSMF
Pipeline: GST → NEST → Subset
"""

from typing import Dict, Any, Optional
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.nest import NEST, NetworkSlice, NetworkSliceStatus

tracer = trace.get_tracer(__name__)


class NESTGenerator:
    """Gera NEST a partir de GST"""
    
    def __init__(self, db_session=None):
        """
        Inicializa gerador de NEST
        Se db_session for fornecido, usa persistência em banco
        Caso contrário, usa storage em memória (fallback)
        """
        self.db_session = db_session
        self.nests: Dict[str, NEST] = {}  # Fallback em memória
    
    async def generate_nest(self, gst: Dict[str, Any]) -> NEST:
        """
        Gera NEST a partir de GST
        GST → NEST
        """
        with tracer.start_as_current_span("generate_nest") as span:
            span.set_attribute("gst.id", gst.get("gst_id"))
            
            nest_id = f"nest-{gst['intent_id']}"
            
            # Gerar network slices baseado no template GST
            network_slices = self._generate_network_slices(gst)
            
            nest = NEST(
                nest_id=nest_id,
                intent_id=gst["intent_id"],
                status=NetworkSliceStatus.GENERATED,
                network_slices=network_slices,
                gst_id=gst["gst_id"],
                metadata={
                    "gst": gst,
                    "generated_at": self._get_timestamp()
                }
            )
            
            # Armazenar NEST (banco ou memória)
            if self.db_session:
                # Se tiver sessão de banco, salvar será feito pelo repository
                pass
            else:
                # Fallback: armazenar em memória
                self.nests[nest_id] = nest
            
            span.set_attribute("nest.id", nest_id)
            span.set_attribute("nest.slices_count", len(network_slices))
            
            return nest
    
    def _generate_network_slices(self, gst: Dict[str, Any]) -> list[NetworkSlice]:
        """Gera network slices baseado no template GST"""
        slices = []
        template = gst.get("template", {})
        slice_type = template.get("slice_type", "eMBB")
        
        # Gerar slice principal
        main_slice = NetworkSlice(
            slice_id=f"slice-{gst['intent_id']}-001",
            slice_type=slice_type,
            resources=self._calculate_resources(template),
            status=NetworkSliceStatus.GENERATED,
            metadata={"primary": True}
        )
        slices.append(main_slice)
        
        # Gerar slices adicionais se necessário
        if slice_type == "eMBB":
            # eMBB pode ter múltiplos slices para diferentes áreas
            pass
        elif slice_type == "URLLC":
            # URLLC pode ter slices redundantes
            redundant_slice = NetworkSlice(
                slice_id=f"slice-{gst['intent_id']}-002",
                slice_type=slice_type,
                resources=self._calculate_resources(template),
                status=NetworkSliceStatus.GENERATED,
                metadata={"redundant": True}
            )
            slices.append(redundant_slice)
        
        return slices
    
    def _calculate_resources(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula recursos necessários baseado no template GST
        Usa valores do template (que vem da ontologia) em vez de hardcoded
        """
        slice_type = template.get("slice_type", "eMBB")
        qos = template.get("qos", {})
        sla = template.get("sla", {})
        
        # Recursos base (podem ser ajustados conforme necessidade)
        resources = {
            "cpu": "2",
            "memory": "4Gi",
            "storage": "10Gi"
        }
        
        # Usar valores do template GST (que vem da ontologia validada)
        # Ajustar baseado no tipo de slice e requisitos reais
        if slice_type == "eMBB":
            # eMBB: alta taxa de dados
            resources.update({
                "bandwidth": qos.get("maximum_bitrate") or sla.get("throughput") or "1Gbps",
                "cpu": "4",  # Mais CPU para processamento de alta taxa
                "memory": "8Gi",  # Mais memória para buffers
                "latency": sla.get("latency") or qos.get("latency") or "50ms"
            })
        elif slice_type == "URLLC":
            # URLLC: baixa latência e alta confiabilidade
            resources.update({
                "latency": qos.get("latency") or sla.get("latency") or "1ms",
                "reliability": qos.get("reliability") or sla.get("reliability") or 0.99999,
                "jitter": qos.get("jitter") or sla.get("jitter") or "1ms",
                "cpu": "2",  # CPU suficiente para processamento rápido
                "memory": "4Gi"  # Memória para buffers de baixa latência
            })
        elif slice_type == "mMTC":
            # mMTC: alta densidade de dispositivos
            resources.update({
                "device_density": qos.get("device_density") or "1000000/km²",
                "data_rate": qos.get("data_rate") or "160bps",
                "latency": sla.get("latency") or "1000ms",  # Latência pode ser maior
                "cpu": "1",  # Menos CPU (dispositivos de baixa taxa)
                "memory": "2Gi"  # Menos memória
            })
        
        # Adicionar outros recursos do SLA se especificados
        if sla.get("coverage"):
            resources["coverage"] = sla["coverage"]
        if sla.get("reliability"):
            resources["reliability"] = sla["reliability"]
        
        return resources
    
    async def get_nest(self, nest_id: str) -> Optional[NEST]:
        """Retorna NEST por ID"""
        if self.db_session:
            # Buscar do banco
            from repository import NESTRepository
            db_nest = NESTRepository.get_by_id(self.db_session, nest_id)
            if db_nest:
                return NESTRepository.convert_to_pydantic(db_nest)
        # Fallback: memória
        return self.nests.get(nest_id)
    
    async def list_all_nests(self) -> list[NEST]:
        """Retorna todos os NESTs armazenados"""
        if self.db_session:
            # Buscar do banco
            from repository import NESTRepository
            db_nests = NESTRepository.list_all(self.db_session)
            return [NESTRepository.convert_to_pydantic(db_nest) for db_nest in db_nests]
        # Fallback: memória
        return list(self.nests.values())
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

