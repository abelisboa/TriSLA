"""
Modelos de NEST (Network Slice Template)
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class NetworkSliceStatus(str, Enum):
    """Status do network slice"""
    PENDING = "pending"
    GENERATED = "generated"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


class NetworkSlice(BaseModel):
    """Network Slice individual"""
    slice_id: str
    slice_type: str
    resources: Dict[str, Any]
    status: NetworkSliceStatus
    metadata: Optional[Dict[str, Any]] = None


class NEST(BaseModel):
    """Network Slice Template"""
    nest_id: str = Field(..., description="ID único do NEST")
    intent_id: str = Field(..., description="ID do intent que gerou este NEST")
    status: NetworkSliceStatus = Field(default=NetworkSliceStatus.GENERATED)
    network_slices: List[NetworkSlice] = Field(..., description="Lista de network slices")
    gst_id: Optional[str] = Field(None, description="ID do GST que gerou este NEST")
    created_at: Optional[str] = Field(None, description="Timestamp de criação")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados do NEST")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nest_id": "nest-001",
                "intent_id": "intent-001",
                "status": "generated",
                "network_slices": [
                    {
                        "slice_id": "slice-001",
                        "slice_type": "eMBB",
                        "resources": {
                            "cpu": "2",
                            "memory": "4Gi",
                            "bandwidth": "100Mbps"
                        },
                        "status": "generated"
                    }
                ]
            }
        }

