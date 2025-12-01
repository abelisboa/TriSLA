from pydantic import BaseModel
from typing import List

class SLO(BaseModel):
    name: str
    value: int
    threshold: int

class SLARequest(BaseModel):
    customer: str
    serviceName: str
    slaHash: str
    slos: List[SLO]

class SLAStatusUpdate(BaseModel):
    slaId: int
    newStatus: int
