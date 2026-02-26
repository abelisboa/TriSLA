from typing import List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from src.models.database import SessionLocal
from src.models.contract import (
    ContractModel,
    ViolationModel,
    RenegotiationModel,
    PenaltyModel,
)
from src.schemas.contracts import (
    Contract,
    ContractCreate,
    ContractUpdate,
    Violation,
    Renegotiation,
    Penalty,
)


class ContractService:
    def __init__(self):
        self.db: Session = SessionLocal()

    async def list_contracts(
        self, status: Optional[str] = None, tenant: Optional[str] = None, type: Optional[str] = None
    ) -> List[Contract]:
        """Lista contratos com filtros"""
        query = self.db.query(ContractModel)
        if status:
            query = query.filter(ContractModel.status == status)
        if tenant:
            query = query.filter(ContractModel.tenant_id == tenant)
        if type:
            query = query.filter(ContractModel.contract_metadata["service_type"].astext == type)

        contracts = query.all()
        return [Contract.model_validate(c) for c in contracts]

    async def get_contract(self, contract_id: str) -> Contract:
        """Retorna um contrato"""
        contract = self.db.query(ContractModel).filter(ContractModel.id == contract_id).first()
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        return Contract.model_validate(contract)

    async def create_contract(self, contract: ContractCreate) -> Contract:
        """Cria um novo contrato"""
        db_contract = ContractModel(**contract.model_dump())
        self.db.add(db_contract)
        self.db.commit()
        self.db.refresh(db_contract)
        return Contract.model_validate(db_contract)

    async def get_violations(self, contract_id: str) -> List[Violation]:
        """Retorna violações de um contrato"""
        violations = (
            self.db.query(ViolationModel)
            .filter(ViolationModel.contract_id == contract_id)
            .all()
        )
        return [Violation.model_validate(v) for v in violations]

    async def get_renegotiations(self, contract_id: str) -> List[Renegotiation]:
        """Retorna renegociações de um contrato"""
        renegotiations = (
            self.db.query(RenegotiationModel)
            .filter(RenegotiationModel.contract_id == contract_id)
            .all()
        )
        return [Renegotiation.model_validate(r) for r in renegotiations]

    async def get_penalties(self, contract_id: str) -> List[Penalty]:
        """Retorna penalidades de um contrato"""
        penalties = (
            self.db.query(PenaltyModel)
            .filter(PenaltyModel.contract_id == contract_id)
            .all()
        )
        return [Penalty.model_validate(p) for p in penalties]

    async def get_versions(self, contract_id: str) -> List[Contract]:
        """Retorna versões de um contrato"""
        contract = await self.get_contract(contract_id)
        # Buscar todas as versões do mesmo contrato base
        contracts = (
            self.db.query(ContractModel)
            .filter(ContractModel.intent_id == contract.intent_id)
            .order_by(ContractModel.version)
            .all()
        )
        return [Contract.model_validate(c) for c in contracts]

    async def compare_contracts(self, contract_ids: List[str]) -> Any:
        """Compara contratos"""
        contracts = []
        for contract_id in contract_ids:
            contract = await self.get_contract(contract_id)
            contracts.append(contract)
        # Implementar lógica de comparação
        return {"contracts": contracts, "diff": {}}

    async def get_analytics(self) -> Any:
        """Retorna analytics de contratos"""
        total = self.db.query(ContractModel).count()
        active = self.db.query(ContractModel).filter(ContractModel.status == "ACTIVE").count()
        violated = self.db.query(ContractModel).filter(ContractModel.status == "VIOLATED").count()
        return {
            "total": total,
            "active": active,
            "violated": violated,
            "violation_rate": violated / total if total > 0 else 0,
        }


