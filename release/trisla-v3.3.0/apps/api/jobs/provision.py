import time

def provision_subnet(data):
    for step in range(1, 6):
        time.sleep(1)
    return {"result": f"Subnet provisioned for {data.get('descricao', 'unknown')}"}
