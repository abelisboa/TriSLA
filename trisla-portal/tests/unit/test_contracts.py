import pytest
from datetime import datetime
from src.schemas.contracts import (
    Contract,
    ContractCreate,
    Violation,
    Renegotiation,
    Penalty,
    ContractStatus,
    ViolationType,
    Severity,
)


@pytest.mark.unit
class TestContractSchemas:
    """Test contract Pydantic schemas"""
    
    def test_contract_create(self):
        """Test ContractCreate schema"""
        data = {
            "tenant_id": "tenant-001",
            "intent_id": "intent-001",
            "nest_id": "nest-001",
            "decision_id": "decision-001",
            "sla_requirements": {
                "latency": {"max": "10ms"},
                "reliability": 0.99999
            },
            "domains": ["RAN", "Transport"],
            "metadata": {"service_type": "URLLC"}
        }
        contract = ContractCreate(**data)
        assert contract.tenant_id == "tenant-001"
        assert contract.domains == ["RAN", "Transport"]
    
    def test_violation_schema(self):
        """Test Violation schema"""
        violation = Violation(
            id="violation-001",
            contract_id="contract-001",
            violation_type=ViolationType.LATENCY,
            metric_name="latency",
            expected_value="10ms",
            actual_value="15ms",
            severity=Severity.HIGH,
            detected_at=datetime.utcnow(),
            status="DETECTED"
        )
        assert violation.violation_type == ViolationType.LATENCY
        assert violation.severity == Severity.HIGH
    
    def test_renegotiation_schema(self):
        """Test Renegotiation schema"""
        renegotiation = Renegotiation(
            id="reneg-001",
            contract_id="contract-001",
            previous_version=1,
            new_version=2,
            reason="VIOLATION",
            changes={"sla_requirements": {}},
            status="PENDING",
            requested_at=datetime.utcnow(),
            requested_by="tenant"
        )
        assert renegotiation.previous_version == 1
        assert renegotiation.new_version == 2







