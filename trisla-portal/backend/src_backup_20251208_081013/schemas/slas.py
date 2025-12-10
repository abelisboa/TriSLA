from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class SLACreatePLN(BaseModel):
    intent_text: str
    tenant_id: str


class SLACreateTemplate(BaseModel):
    template_id: str
    form_values: Dict[str, Any]
    tenant_id: str


class SLATemplate(BaseModel):
    template_id: str
    name: str
    description: str
    service_type: str
    nest_template: Dict[str, Any]
    form_fields: Optional[List[Dict[str, Any]]] = None


class BatchStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BatchResult(BaseModel):
    sla_index: int
    tenant_id: str
    status: str  # success, error
    intent_id: Optional[str] = None
    nest_id: Optional[str] = None
    error: Optional[str] = None


class BatchJob(BaseModel):
    batch_id: str
    tenant_id: str
    total_slas: int
    processed_slas: int
    successful_slas: int
    failed_slas: int
    status: BatchStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: List[BatchResult]


class SLACreateBatch(BaseModel):
    tenant_id: str
    # File will be handled separately in the endpoint






