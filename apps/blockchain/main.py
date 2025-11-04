from fastapi import FastAPI
from pydantic import BaseModel
from hfc.fabric import Client as FabricClient
import datetime, logging

app = FastAPI(title="TriSLA – BC-NSSMF (Fabric)")
logging.basicConfig(level=logging.INFO)

cli = FabricClient(net_profile="./fabric-network/config/connection-profile.yaml")
org_admin = cli.get_user('Org1MSP', 'Admin')
cli.new_channel('trisla-channel')

class Contract(BaseModel):
    sla_id: str
    slice_type: str
    decision: str
    compliance: str

@app.post("/contracts/register")
def register(c: Contract):
    ts = datetime.datetime.utcnow().isoformat()
    args = [c.sla_id, c.slice_type, c.decision, ts, c.compliance]
    try:
        res = cli.chaincode_invoke(
            requestor=org_admin,
            channel_name='trisla-channel',
            peers=['peer0.org1.example.com'],
            args=args,
            cc_name='sla_chaincode',
            fcn='RegisterSLA',
            wait_for_event=True)
        return {"status": "success", "tx_id": res}
    except Exception as e:
        return {"status": "error", "details": str(e)}