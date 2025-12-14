from typing import Optional, Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    reason: str
    detail: Any
    phase: Optional[str] = None
    upstream_status: Optional[int] = None

