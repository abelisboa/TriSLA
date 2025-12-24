"""
Gerador de NEST com Persistência - SEM-CSMF
Versão com banco de dados
"""

from typing import Dict, Any, Optional, List
from opentelemetry import trace
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.nest import NEST, NetworkSlice, NetworkSliceStatus
from models.db_models import NESTModel, NetworkSliceModel
from nest_generator_base import NESTGeneratorBase

tracer = trace.get_tracer(__name__)


class NESTGeneratorDB(NESTGeneratorBase):
    """Gera NEST com persistência em banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_nest(self, gst: Dict[str, Any]) -> NEST:
        """
        Gera NEST a partir de GST e persiste no banco de dados
        GST → NEST → Database
        """
        with tracer.start_as_current_span("generate_nest_db") as span:
            span.set_attribute("gst.id", gst.get("gst_id"))
            
            nest_id = f"nest-{gst['intent_id']}"
            
            # Gerar network slices
            network_slices = self._generate_network_slices(gst)
            
            # Criar objeto NEST
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
            
            # Persistir NEST no banco
            nest_model = NESTModel(
                nest_id=nest.nest_id,
                intent_id=nest.intent_id,
                status=nest.status.value,
                gst_id=nest.gst_id,
                gst_data=gst,
                extra_metadata=nest.metadata
            )
            self.db.add(nest_model)
            
            # Persistir network slices
            for network_slice in network_slices:
                slice_model = NetworkSliceModel(
                    slice_id=network_slice.slice_id,
                    nest_id=nest.nest_id,
                    slice_type=network_slice.slice_type,
                    resources=network_slice.resources,
                    status=network_slice.status.value,
                    extra_metadata=network_slice.metadata
                )
                self.db.add(slice_model)
            
            self.db.commit()
            self.db.refresh(nest_model)
            
            span.set_attribute("nest.id", nest_id)
            span.set_attribute("nest.slices_count", len(network_slices))
            
            return nest
    
    # Métodos _generate_network_slices e _calculate_resources
    # agora são herdados de NESTGeneratorBase (sem duplicidade)
    # A versão base inclui mapeamento completo 3GPP TS 28.541
    
    async def get_nest(self, nest_id: str) -> Optional[NEST]:
        """Retorna NEST por ID do banco de dados"""
        nest_model = self.db.query(NESTModel).filter(NESTModel.nest_id == nest_id).first()
        if not nest_model:
            return None
        
        # IMPORTANTE: Expirar todas as sessões e fazer refresh explícito
        # Isso garante que não há referências cached ao MetaData do SQLAlchemy
        try:
            self.db.expire_all()  # Expirar todas as sessões
            self.db.refresh(nest_model)  # Recarregar o modelo
            
            # Verificar relacionamentos lazy - forçar carregamento
            # Isso evita problemas com lazy loading que podem causar referências ao MetaData
            if hasattr(nest_model, 'network_slices'):
                _ = list(nest_model.network_slices)  # Forçar carregamento do relacionamento
            if hasattr(nest_model, 'intent'):
                _ = nest_model.intent  # Forçar carregamento do relacionamento
            
            # Forçar acesso aos atributos antes de usar
            _ = nest_model.nest_id
            _ = nest_model.intent_id
            _ = nest_model.status
            _ = nest_model.gst_id
            # Acessar extra_metadata explicitamente para carregar
            _ = getattr(nest_model, 'extra_metadata', None)
        except Exception:
            pass  # Se refresh falhar, continuar
        
        # Buscar slices
        slice_models = self.db.query(NetworkSliceModel).filter(
            NetworkSliceModel.nest_id == nest_id
        ).all()
        
        # Converter para objetos NEST
        network_slices = []
        for slice_model in slice_models:
            # Garantir que metadata seja dict ou None
            slice_metadata = getattr(slice_model, 'extra_metadata', None)
            if slice_metadata is None:
                slice_metadata = {}
            elif not isinstance(slice_metadata, dict):
                # Se não for dict, converter ou usar vazio
                try:
                    import json
                    if hasattr(slice_metadata, '__dict__'):
                        slice_metadata = dict(slice_metadata.__dict__)
                    else:
                        slice_metadata = json.loads(str(slice_metadata)) if slice_metadata else {}
                except:
                    slice_metadata = {}
            
            # Garantir que resources seja dict
            slice_resources = getattr(slice_model, 'resources', {})
            if not isinstance(slice_resources, dict):
                slice_resources = {}
            
            network_slice = NetworkSlice(
                slice_id=slice_model.slice_id,
                slice_type=slice_model.slice_type,
                resources=slice_resources,
                status=NetworkSliceStatus(slice_model.status),
                metadata=slice_metadata
            )
            network_slices.append(network_slice)
        
        # IMPORTANTE: Usar getattr para evitar problemas com lazy loading
        # Garantir que metadata seja dict ou None
        nest_metadata = getattr(nest_model, 'extra_metadata', None)
        
        # Verificar se não é MetaData do SQLAlchemy
        if nest_metadata is not None:
            from sqlalchemy import MetaData as SQLMetaData
            if isinstance(nest_metadata, SQLMetaData):
                nest_metadata = {}
            elif not isinstance(nest_metadata, dict):
                # Tentar converter para dict
                try:
                    import json
                    if hasattr(nest_metadata, '__dict__'):
                        nest_metadata = dict(nest_metadata.__dict__)
                    else:
                        nest_metadata = json.loads(str(nest_metadata)) if nest_metadata else {}
                except:
                    nest_metadata = {}
        
        # Garantir que é None ou dict
        if nest_metadata is None:
            nest_metadata = {}
        elif not isinstance(nest_metadata, dict):
            nest_metadata = {}
        
        # Criar cópia explícita do dict para evitar problemas de referência
        try:
            import copy
            nest_metadata = copy.deepcopy(nest_metadata) if isinstance(nest_metadata, dict) else {}
        except Exception:
            try:
                nest_metadata = dict(nest_metadata) if isinstance(nest_metadata, dict) else {}
            except Exception:
                nest_metadata = {}
        
        # Garantir que é realmente um dict antes de passar para Pydantic
        if not isinstance(nest_metadata, dict):
            nest_metadata = {}
        
        # SERIALIZAÇÃO MANUAL COMPLETA: Criar dict completamente independente do SQLAlchemy
        # Isso evita qualquer referência ao MetaData do SQLAlchemy
        import json
        
        # Serializar metadata para JSON e deserializar (garante dict puro)
        try:
            if nest_metadata:
                nest_metadata_str = json.dumps(nest_metadata)
                nest_metadata = json.loads(nest_metadata_str)
            else:
                nest_metadata = {}
        except Exception:
            nest_metadata = {}
        
        # Criar dict explícito para network_slices com serialização completa
        nest_slices_data = []
        for ns in network_slices:
            # Serializar cada campo individualmente
            slice_dict = {
                "slice_id": str(ns.slice_id),
                "slice_type": str(ns.slice_type),
                "resources": json.loads(json.dumps(ns.resources)) if ns.resources else {},
                "status": ns.status.value if hasattr(ns.status, 'value') else str(ns.status),
                "metadata": json.loads(json.dumps(ns.metadata)) if ns.metadata else {}
            }
            nest_slices_data.append(slice_dict)
        
        # Converter de volta para objetos NetworkSlice (validação do Pydantic)
        nest_slices_objs = []
        for ns_data in nest_slices_data:
            try:
                nest_slices_objs.append(NetworkSlice(**ns_data))
            except Exception as e:
                # Se falhar, criar com valores padrão
                nest_slices_objs.append(NetworkSlice(
                    slice_id=ns_data.get("slice_id", ""),
                    slice_type=ns_data.get("slice_type", ""),
                    resources=ns_data.get("resources", {}),
                    status=NetworkSliceStatus(ns_data.get("status", "generated")),
                    metadata=ns_data.get("metadata", {})
                ))
        
        # Criar dict final para NEST (tudo serializado)
        nest_dict = {
            "nest_id": str(nest_model.nest_id),
            "intent_id": str(nest_model.intent_id),
            "status": NetworkSliceStatus(nest_model.status),
            "network_slices": nest_slices_objs,
            "gst_id": str(nest_model.gst_id) if nest_model.gst_id else None,
            "metadata": nest_metadata  # Já serializado acima
        }
        
        # CORREÇÃO CIRÚRGICA: Garantir que metadata é dict válido ANTES de passar para Pydantic
        # O problema é que mesmo após serialização JSON, o Pydantic pode acessar o atributo original
        # durante validação. Vamos criar o dict final SEM metadata e adicionar depois usando model_dump
        
        # Criar dict SEM metadata primeiro
        nest_dict_no_meta = {
            "nest_id": str(nest_model.nest_id),
            "intent_id": str(nest_model.intent_id),
            "status": NetworkSliceStatus(nest_model.status),
            "network_slices": nest_slices_objs,
            "gst_id": str(nest_model.gst_id) if nest_model.gst_id else None
        }
        
        # Criar NEST sem metadata primeiro (isso evita validação do metadata)
        try:
            if hasattr(NEST, 'model_validate'):
                # Pydantic v2 - criar sem metadata
                nest = NEST.model_validate(nest_dict_no_meta)
            else:
                # Pydantic v1
                nest = NEST(**nest_dict_no_meta)
        except Exception as e:
            # Se falhar, tentar com metadata vazio
            nest_dict_empty = nest_dict_no_meta.copy()
            nest_dict_empty['metadata'] = {}
            if hasattr(NEST, 'model_validate'):
                nest = NEST.model_validate(nest_dict_empty)
            else:
                nest = NEST(**nest_dict_empty)
        
        # AGORA adicionar metadata DEPOIS que o objeto foi criado
        # Isso evita que o Pydantic valide o metadata durante __init__
        if nest_metadata and isinstance(nest_metadata, dict):
            # Usar model_copy do Pydantic v2 ou setattr
            try:
                if hasattr(nest, 'model_copy'):
                    # Pydantic v2
                    nest = nest.model_copy(update={'metadata': nest_metadata})
                else:
                    # Pydantic v1 - usar setattr
                    object.__setattr__(nest, 'metadata', nest_metadata)
            except Exception:
                # Se falhar, deixar metadata vazio
                pass
        
        return nest
    
    async def list_all_nests(self) -> List[NEST]:
        """Retorna todos os NESTs do banco de dados"""
        nest_models = self.db.query(NESTModel).all()
        nests = []
        
        for nest_model in nest_models:
            # Buscar slices
            slice_models = self.db.query(NetworkSliceModel).filter(
                NetworkSliceModel.nest_id == nest_model.nest_id
            ).all()
            
            network_slices = []
            for slice_model in slice_models:
                # Garantir que metadata seja dict ou None
                # SQLAlchemy pode retornar MetaData object, converter para dict
                slice_metadata = slice_model.extra_metadata
                if slice_metadata is None:
                    slice_metadata = {}
                elif not isinstance(slice_metadata, dict):
                    # Tentar converter MetaData object para dict
                    if hasattr(slice_metadata, '__dict__'):
                        slice_metadata = dict(slice_metadata.__dict__)
                    else:
                        try:
                            import json
                            slice_metadata = json.loads(str(slice_metadata)) if slice_metadata else {}
                        except:
                            slice_metadata = {}
                
                # Garantir que resources seja dict
                slice_resources = slice_model.resources
                if not isinstance(slice_resources, dict):
                    slice_resources = {}
                
                network_slice = NetworkSlice(
                    slice_id=slice_model.slice_id,
                    slice_type=slice_model.slice_type,
                    resources=slice_resources,
                    status=NetworkSliceStatus(slice_model.status),
                    metadata=slice_metadata
                )
                network_slices.append(network_slice)
            
            # Garantir que metadata seja dict ou None
            # SQLAlchemy pode retornar MetaData object, converter para dict
            nest_metadata = nest_model.extra_metadata
            if nest_metadata is None:
                nest_metadata = {}
            elif not isinstance(nest_metadata, dict):
                # Tentar converter MetaData object para dict
                if hasattr(nest_metadata, '__dict__'):
                    nest_metadata = dict(nest_metadata.__dict__)
                else:
                    try:
                        import json
                        nest_metadata = json.loads(str(nest_metadata)) if nest_metadata else {}
                    except:
                        nest_metadata = {}
            
            # CORREÇÃO CIRÚRGICA: Criar NEST sem metadata primeiro, adicionar depois
            nest_dict_no_meta = {
                "nest_id": str(nest_model.nest_id),
                "intent_id": str(nest_model.intent_id),
                "status": NetworkSliceStatus(nest_model.status),
                "network_slices": network_slices,
                "gst_id": str(nest_model.gst_id) if nest_model.gst_id else None
            }
            
            # Criar NEST sem metadata primeiro
            try:
                if hasattr(NEST, 'model_validate'):
                    nest = NEST.model_validate(nest_dict_no_meta)
                else:
                    nest = NEST(**nest_dict_no_meta)
            except Exception:
                nest_dict_empty = nest_dict_no_meta.copy()
                nest_dict_empty['metadata'] = {}
                if hasattr(NEST, 'model_validate'):
                    nest = NEST.model_validate(nest_dict_empty)
                else:
                    nest = NEST(**nest_dict_empty)
            
            # Adicionar metadata DEPOIS
            if nest_metadata and isinstance(nest_metadata, dict):
                try:
                    if hasattr(nest, 'model_copy'):
                        nest = nest.model_copy(update={'metadata': nest_metadata})
                    else:
                        object.__setattr__(nest, 'metadata', nest_metadata)
                except Exception:
                    pass
            
            nests.append(nest)
        
        return nests
    
    # Método _get_timestamp herdado de NESTGeneratorBase

