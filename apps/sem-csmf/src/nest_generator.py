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
from nest_generator_base import NESTGeneratorBase

tracer = trace.get_tracer(__name__)


class NESTGenerator(NESTGeneratorBase):
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
    
    # Métodos _generate_network_slices, _calculate_resources e helpers
    # agora são herdados de NESTGeneratorBase (sem duplicidade)
    
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
    
    # Método _get_timestamp herdado de NESTGeneratorBase

