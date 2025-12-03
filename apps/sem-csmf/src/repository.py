"""
Repository Pattern - SEM-CSMF
Camada de acesso a dados
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.db_models import IntentDB, NESTDB, NetworkSliceDB
from models.intent import Intent
from models.nest import NEST, NetworkSlice, NetworkSliceStatus


class IntentRepository:
    """Repository para Intents"""
    
    @staticmethod
    def create(db: Session, intent: Intent) -> IntentDB:
        """Cria um novo intent no banco"""
        db_intent = IntentDB(
            intent_id=intent.intent_id,
            tenant_id=intent.tenant_id,
            service_type=intent.service_type.value,
            sla_requirements=intent.sla_requirements.model_dump(),
            metadata=intent.metadata
        )
        db.add(db_intent)
        db.commit()
        db.refresh(db_intent)
        return db_intent
    
    @staticmethod
    def get_by_id(db: Session, intent_id: str) -> Optional[IntentDB]:
        """Busca intent por ID"""
        return db.query(IntentDB).filter(IntentDB.intent_id == intent_id).first()
    
    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[IntentDB]:
        """Lista todos os intents"""
        return db.query(IntentDB).offset(skip).limit(limit).all()


class NESTRepository:
    """Repository para NESTs"""
    
    @staticmethod
    def create(db: Session, nest: NEST) -> NESTDB:
        """Cria um novo NEST no banco"""
        db_nest = NESTDB(
            nest_id=nest.nest_id,
            intent_id=nest.intent_id,
            gst_id=nest.gst_id,
            status=nest.status.value if hasattr(nest.status, 'value') else str(nest.status),
            metadata=nest.metadata
        )
        db.add(db_nest)
        
        # Criar network slices associados
        for network_slice in nest.network_slices:
            db_slice = NetworkSliceDB(
                slice_id=network_slice.slice_id,
                nest_id=nest.nest_id,
                slice_type=network_slice.slice_type,
                resources=network_slice.resources,
                status=network_slice.status.value if hasattr(network_slice.status, 'value') else str(network_slice.status),
                metadata=network_slice.metadata
            )
            db.add(db_slice)
        
        db.commit()
        db.refresh(db_nest)
        return db_nest
    
    @staticmethod
    def get_by_id(db: Session, nest_id: str) -> Optional[NESTDB]:
        """Busca NEST por ID"""
        return db.query(NESTDB).filter(NESTDB.nest_id == nest_id).first()
    
    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[NESTDB]:
        """Lista todos os NESTs"""
        return db.query(NESTDB).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_intent_id(db: Session, intent_id: str) -> Optional[NESTDB]:
        """Busca NEST por intent_id"""
        return db.query(NESTDB).filter(NESTDB.intent_id == intent_id).first()
    
    @staticmethod
    def convert_to_pydantic(db_nest: NESTDB) -> NEST:
        """Converte NESTDB para modelo Pydantic NEST"""
        network_slices = []
        for db_slice in db_nest.network_slices:
            network_slice = NetworkSlice(
                slice_id=db_slice.slice_id,
                slice_type=db_slice.slice_type,
                resources=db_slice.resources,
                status=NetworkSliceStatus(db_slice.status),
                metadata=db_slice.metadata
            )
            network_slices.append(network_slice)
        
        return NEST(
            nest_id=db_nest.nest_id,
            intent_id=db_nest.intent_id,
            status=NetworkSliceStatus(db_nest.status),
            network_slices=network_slices,
            gst_id=db_nest.gst_id,
            metadata=db_nest.metadata
        )

