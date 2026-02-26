import re
from pathlib import Path

TARGET = Path("/app/src/capacity_accounting.py")

NEW_BLOCK = r'''
# === GLOBAL_CAPACITY_ACCOUNTING_BEGIN ===
import os
from kubernetes import client

def _parse_cpu_to_millicores(v: str) -> int:
    v = str(v).strip()
    if v.endswith("m"):
        return int(v[:-1])
    # cpu em cores (pode ser "2" ou "2.5")
    return int(float(v) * 1000)

def _parse_mem_to_bytes(v: str) -> int:
    v = str(v).strip()
    # K8s quantities: Ki, Mi, Gi, Ti, Pi, Ei e também K, M, G...
    units = {
        "Ki": 1024, "Mi": 1024**2, "Gi": 1024**3, "Ti": 1024**4,
        "Pi": 1024**5, "Ei": 1024**6,
        "K": 1000, "M": 1000**2, "G": 1000**3, "T": 1000**4,
        "P": 1000**5, "E": 1000**6,
    }
    m = re.match(r"^([0-9.]+)([a-zA-Z]+)?$", v)
    if not m:
        return int(float(v))
    num = float(m.group(1))
    unit = m.group(2) or ""
    if unit == "":
        return int(num)
    if unit not in units:
        return int(num)
    return int(num * units[unit])

def _bytes_to_gi(b: int) -> float:
    return b / (1024**3)

def _cluster_allocatable() -> dict:
    core = client.CoreV1Api()
    nodes = core.list_node().items
    cpu_m = 0
    mem_b = 0
    for n in nodes:
        a = n.status.allocatable or {}
        if "cpu" in a:
            cpu_m += _parse_cpu_to_millicores(a["cpu"])
        if "memory" in a:
            mem_b += _parse_mem_to_bytes(a["memory"])
    return {"cpu_m": cpu_m, "mem_b": mem_b, "nodes": len(nodes)}

def _sum_active_reserved(active: list) -> dict:
    cpu_m = 0
    mem_b = 0
    for r in (active or []):
        rr = r.get("spec", {}).get("resourcesReserved", {}) or r.get("resources_reserved", {}) or {}
        c = rr.get("cpu") or rr.get("requests.cpu") or rr.get("limits.cpu")
        m = rr.get("memory") or rr.get("requests.memory") or rr.get("limits.memory")
        if c:
            cpu_m += _parse_cpu_to_millicores(c)
        if m:
            mem_b += _parse_mem_to_bytes(m)
    return {"cpu_m": cpu_m, "mem_b": mem_b}

def ledger_check(multidomain: dict, active: list, slice_type: str, sla_req: dict) -> dict:
    """
    Accounting global forte:
      headroom = allocatable*(1-safety) - reserved_active
      requested = cost(slice_type, sla_req)
    Rejeita se requested > headroom.
    """
    safety = float(os.getenv("CAPACITY_SAFETY_FACTOR", "0.1"))
    alloc = _cluster_allocatable()
    reserved = _sum_active_reserved(active)

    # IMPORTANTE: cost() já existe no cost_model.py e é chamado pelo main.py.
    # Aqui apenas replicamos o consumo esperado já calculado no pipeline (por segurança, aceitamos cpu/memory).
    from cost_model import cost
    req = cost(slice_type, sla_req) or {}
    req_cpu = _parse_cpu_to_millicores(req.get("cpu", "0"))
    req_mem = _parse_mem_to_bytes(req.get("memory", "0"))

    cpu_budget = int(alloc["cpu_m"] * (1.0 - safety))
    mem_budget = int(alloc["mem_b"] * (1.0 - safety))

    cpu_headroom = cpu_budget - reserved["cpu_m"]
    mem_headroom = mem_budget - reserved["mem_b"]

    pass_cpu = req_cpu <= cpu_headroom
    pass_mem = req_mem <= mem_headroom

    reasons = []
    if not pass_cpu:
        reasons.append(f"cpu_insufficient:req={req_cpu}m headroom={cpu_headroom}m alloc={alloc['cpu_m']}m safety={safety}")
    if not pass_mem:
        reasons.append(f"mem_insufficient:req={_bytes_to_gi(req_mem):.2f}Gi headroom={_bytes_to_gi(mem_headroom):.2f}Gi alloc={_bytes_to_gi(alloc['mem_b']):.2f}Gi safety={safety}")

    return {
        "pass": (pass_cpu and pass_mem),
        "reasons": reasons or ["ok"],
        "allocatable": {"cpu_m": alloc["cpu_m"], "mem_gi": round(_bytes_to_gi(alloc["mem_b"]), 2), "nodes": alloc["nodes"]},
        "reserved_active": {"cpu_m": reserved["cpu_m"], "mem_gi": round(_bytes_to_gi(reserved["mem_b"]), 2)},
        "headroom": {"cpu_m": cpu_headroom, "mem_gi": round(_bytes_to_gi(mem_headroom), 2)},
        "requested": {"cpu_m": req_cpu, "mem_gi": round(_bytes_to_gi(req_mem), 2)},
    }
# === GLOBAL_CAPACITY_ACCOUNTING_END ===
'''

def main():
    txt = TARGET.read_text(encoding="utf-8")

    # Remove bloco anterior, se existir
    txt = re.sub(r"# === GLOBAL_CAPACITY_ACCOUNTING_BEGIN ===.*?# === GLOBAL_CAPACITY_ACCOUNTING_END ===\n?", "", txt, flags=re.S)

    # Anexa bloco no fim (mais seguro do que tentar “cirurgiar” funções antigas em runtime)
    txt = txt.rstrip() + "\n\n" + NEW_BLOCK.strip() + "\n"

    TARGET.write_text(txt, encoding="utf-8")
    print("OK: capacity_accounting.py patched (GLOBAL accounting).")

if __name__ == "__main__":
    main()
