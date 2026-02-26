"""
Testes de Integração - Fluxo de Persistência
Testa o fluxo completo de persistência de dados
"""

import pytest
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar paths dos módulos
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "sem-csmf" / "src"))

from database import SessionLocal, init_db, Base
from models.db_models import IntentModel, NESTModel, NetworkSliceModel
from nest_generator_db import NESTGeneratorDB
from models.nest import NetworkSliceStatus


@pytest.fixture
def db_session():
    """Cria sessão de banco de dados para testes"""
    # Usar banco de teste em memória
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.mark.asyncio
async def test_intent_persistence(db_session):
    """Testa persistência de Intent"""
    intent = IntentModel(
        intent_id="test-intent-persistence",
        tenant_id="tenant-1",
        service_type="eMBB",
        sla_requirements={"latency": "10ms"}
    )
    
    db_session.add(intent)
    db_session.commit()
    
    # Verificar se foi persistido
    saved_intent = db_session.query(IntentModel).filter(
        IntentModel.intent_id == "test-intent-persistence"
    ).first()
    
    assert saved_intent is not None, "Intent should be persisted"
    assert saved_intent.intent_id == "test-intent-persistence"
    assert saved_intent.service_type == "eMBB"


@pytest.mark.asyncio
async def test_nest_persistence(db_session):
    """Testa persistência de NEST"""
    nest_generator = NESTGeneratorDB(db_session)
    
    gst = {
        "gst_id": "gst-test-persistence",
        "intent_id": "test-intent-persistence",
        "service_type": "eMBB",
        "sla_requirements": {"latency": "10ms", "throughput": "100Mbps"},
        "template": {
            "slice_type": "eMBB",
            "sla": {"latency": "10ms"},
            "priority": "high_throughput"
        }
    }
    
    nest = await nest_generator.generate_nest(gst)
    
    # Verificar se foi persistido
    saved_nest = db_session.query(NESTModel).filter(
        NESTModel.nest_id == nest.nest_id
    ).first()
    
    assert saved_nest is not None, "NEST should be persisted"
    assert saved_nest.nest_id == nest.nest_id
    assert saved_nest.intent_id == gst["intent_id"]


@pytest.mark.asyncio
async def test_nest_retrieval(db_session):
    """Testa recuperação de NEST do banco"""
    nest_generator = NESTGeneratorDB(db_session)
    
    # Criar NEST
    gst = {
        "gst_id": "gst-test-retrieval",
        "intent_id": "test-intent-retrieval",
        "service_type": "eMBB",
        "sla_requirements": {"latency": "10ms"},
        "template": {"slice_type": "eMBB"}
    }
    
    nest = await nest_generator.generate_nest(gst)
    nest_id = nest.nest_id
    
    # Recuperar NEST
    retrieved_nest = await nest_generator.get_nest(nest_id)
    
    assert retrieved_nest is not None, "NEST should be retrievable"
    assert retrieved_nest.nest_id == nest_id
    assert retrieved_nest.intent_id == gst["intent_id"]
    assert isinstance(retrieved_nest.metadata, dict), "Metadata should be a dict"


@pytest.mark.asyncio
async def test_network_slice_persistence(db_session):
    """Testa persistência de Network Slices"""
    nest_generator = NESTGeneratorDB(db_session)
    
    gst = {
        "gst_id": "gst-test-slices",
        "intent_id": "test-intent-slices",
        "service_type": "eMBB",
        "sla_requirements": {"latency": "10ms"},
        "template": {"slice_type": "eMBB"}
    }
    
    nest = await nest_generator.generate_nest(gst)
    
    # Verificar se slices foram persistidos
    slices = db_session.query(NetworkSliceModel).filter(
        NetworkSliceModel.nest_id == nest.nest_id
    ).all()
    
    assert len(slices) > 0, "Network slices should be persisted"
    assert all(slice.nest_id == nest.nest_id for slice in slices), "All slices should belong to the NEST"


@pytest.mark.asyncio
async def test_full_persistence_flow(db_session):
    """Testa fluxo completo de persistência: Intent → NEST → Slices"""
    # 1. Criar Intent
    intent = IntentModel(
        intent_id="test-full-flow",
        tenant_id="tenant-1",
        service_type="eMBB",
        sla_requirements={"latency": "10ms"}
    )
    db_session.add(intent)
    db_session.commit()
    
    # 2. Gerar NEST
    nest_generator = NESTGeneratorDB(db_session)
    gst = {
        "gst_id": "gst-test-full-flow",
        "intent_id": intent.intent_id,
        "service_type": "eMBB",
        "sla_requirements": {"latency": "10ms"},
        "template": {"slice_type": "eMBB"}
    }
    
    nest = await nest_generator.generate_nest(gst)
    
    # 3. Verificar tudo foi persistido
    saved_intent = db_session.query(IntentModel).filter(
        IntentModel.intent_id == intent.intent_id
    ).first()
    
    saved_nest = db_session.query(NESTModel).filter(
        NESTModel.nest_id == nest.nest_id
    ).first()
    
    saved_slices = db_session.query(NetworkSliceModel).filter(
        NetworkSliceModel.nest_id == nest.nest_id
    ).all()
    
    assert saved_intent is not None, "Intent should be persisted"
    assert saved_nest is not None, "NEST should be persisted"
    assert len(saved_slices) > 0, "Slices should be persisted"
    assert saved_nest.intent_id == saved_intent.intent_id, "NEST should reference Intent"

