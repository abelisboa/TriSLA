from fastapi import APIRouter
from src.service import BCService
from src.models import SLARequest, SLAStatusUpdate

router = APIRouter(prefix="/bc")

svc = BCService()

@router.post("/register")
def register_sla(req: SLARequest):
    slos = [(s.name, s.value, s.threshold) for s in req.slos]
    receipt = svc.register_sla(req.customer, req.serviceName, req.slaHash, slos)
    return {"status": "ok", "tx": receipt.transactionHash.hex()}

@router.post("/update")
def update_status(req: SLAStatusUpdate):
    receipt = svc.update_status(req.slaId, req.newStatus)
    return {"status": "ok", "tx": receipt.transactionHash.hex()}

@router.get("/{sla_id}")
def get_sla(sla_id: int):
    return svc.get_sla(sla_id)
