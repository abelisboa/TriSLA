import re
from pathlib import Path

TARGET = Path("/app/src/controllers/nsi_controller.py")

BEGIN = "# === WORKLOAD_ENFORCEMENT_BEGIN ==="
END   = "# === WORKLOAD_ENFORCEMENT_END ==="

BLOCK = r'''
# === WORKLOAD_ENFORCEMENT_BEGIN ===
try:
    from workload_provisioner import ensure_workload
except Exception:
    ensure_workload = None

# Após garantir namespace/quota/netpol e antes de marcar Active,
# cria workload real que consome CPU/memória (evidência de enforcement).
if ensure_workload is not None:
    try:
        sp = nsi.get("spec", {}).get("serviceProfile", "eMBB")
        ensure_workload(namespace_name, nsi_id, sp)
        logger.info("[WORKLOAD] provisioned (best-effort) for %s in %s", nsi_id, namespace_name)
    except Exception as we:
        logger.warning("[WORKLOAD] provisioning failed (non-fatal by default): %s", we)
# === WORKLOAD_ENFORCEMENT_END ===
'''

def main():
    txt = TARGET.read_text(encoding="utf-8")

    # remove bloco antigo se existir
    txt = re.sub(rf"{re.escape(BEGIN)}.*?{re.escape(END)}\n?", "", txt, flags=re.S)

    # ponto de inserção: após NetworkPolicy (logo depois da chamada _create_network_policy)
    # Insere após a linha: self._create_network_policy(namespace_name, nsi)
    pattern = r"(self\._create_network_policy\(namespace_name,\s*nsi\)\s*\n)"
    m = re.search(pattern, txt)
    if not m:
        raise SystemExit("ERRO: não encontrei ponto de inserção após _create_network_policy().")

    insert_at = m.end(1)
    txt = txt[:insert_at] + "\n" + BLOCK.strip() + "\n\n" + txt[insert_at:]

    TARGET.write_text(txt, encoding="utf-8")
    print("OK: nsi_controller.py patched (WORKLOAD provisioning hook).")

if __name__ == "__main__":
    main()
