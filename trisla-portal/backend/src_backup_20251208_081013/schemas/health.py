from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Pod(BaseModel):
    name: str
    status: str
    ready: bool
    restarts: int


class ModuleStatus(BaseModel):
    name: str
    status: str  # UP, DOWN, DEGRADED
    latency: Optional[float] = None
    error_rate: Optional[float] = None
    throughput: Optional[float] = None
    pods: Optional[List[Pod]] = None


class HealthResponse(BaseModel):
    status: str  # healthy, unhealthy
    modules: List[ModuleStatus]
    timestamp: datetime


