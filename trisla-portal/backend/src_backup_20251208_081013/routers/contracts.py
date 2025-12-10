from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.schemas.contracts import (
    Contract,
    ContractCreate,
    ContractUpdate,
    Violation,
    Renegotiation,
    Penalty,
)
from src.services.contracts import ContractService

router = APIRouter()
contract_service = ContractService()


@router.get("/", response_model=List[Contract])
async def list_contracts(
    status: Optional[str] = Query(None),
    tenant: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
):
    """Lista contratos"""
    try:
        contracts = await contract_service.list_contracts(status, tenant, type)
        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}", response_model=Contract)
async def get_contract(contract_id: str):
    """Retorna detalhes de um contrato"""
    try:
        contract = await contract_service.get_contract(contract_id)
        return contract
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=Contract)
async def create_contract(contract: ContractCreate):
    """Cria um novo contrato"""
    try:
        new_contract = await contract_service.create_contract(contract)
        return new_contract
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}/violations", response_model=List[Violation])
async def get_contract_violations(contract_id: str):
    """Retorna violações de um contrato"""
    try:
        violations = await contract_service.get_violations(contract_id)
        return violations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}/renegotiations", response_model=List[Renegotiation])
async def get_contract_renegotiations(contract_id: str):
    """Retorna renegociações de um contrato"""
    try:
        renegotiations = await contract_service.get_renegotiations(contract_id)
        return renegotiations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}/penalties", response_model=List[Penalty])
async def get_contract_penalties(contract_id: str):
    """Retorna penalidades de um contrato"""
    try:
        penalties = await contract_service.get_penalties(contract_id)
        return penalties
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contract_id}/versions")
async def get_contract_versions(contract_id: str):
    """Retorna versões de um contrato"""
    try:
        versions = await contract_service.get_versions(contract_id)
        return versions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare")
async def compare_contracts(ids: str = Query(..., description="Comma-separated contract IDs")):
    """Compara contratos"""
    try:
        contract_ids = ids.split(",")
        comparison = await contract_service.compare_contracts(contract_ids)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_contract_analytics():
    """Retorna analytics de contratos"""
    try:
        analytics = await contract_service.get_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






