import sys
from pathlib import Path

TARGET = Path("/app/src/controllers/nsi_controller.py")

INSERT_AFTER = "self._create_network_policy(namespace_name, nsi)"
MARKER_BEGIN = "# === WORKLOAD_ENFORCEMENT_BEGIN ==="
MARKER_END = "# === WORKLOAD_ENFORCEMENT_END ==="

BLOCK = f"""
{MARKER_BEGIN}
                # 2.5 Workload real (Capacity Enforcement Físico)
                # - Força scheduler a validar capacidade de CPU/MEM em tempo real
                # - Se falhar (Insufficient/FailedScheduling), rejeita e interrompe reconcile
                from workload_provisioner import WorkloadProvisioner

                service_profile = nsi.get("spec", {{}}).get("serviceProfile", "eMBB")
                provisioner = WorkloadProvisioner()
                wr = provisioner.provision(namespace_name, nsi_id, service_profile)

                if not wr.get("ok"):
                    self._update_nsi_phase(
                        nsi_id,
                        "Rejected",
                        f"Capacity enforcement failed: {{wr.get('reason')}}"
                    )
                    raise Exception(f"Capacity enforcement failed: {{wr}}")
{MARKER_END}
"""

def main():
    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}", file=sys.stderr)
        sys.exit(2)

    text = TARGET.read_text(encoding="utf-8")

    # Idempotência
    if MARKER_BEGIN in text and MARKER_END in text:
        print("OK: patch already applied (marker found).")
        sys.exit(0)

    if INSERT_AFTER not in text:
        print("ERROR: insertion anchor not found.", file=sys.stderr)
        sys.exit(3)

    parts = text.split(INSERT_AFTER)
    if len(parts) != 2:
        print("ERROR: anchor appears multiple times; refusing to patch.", file=sys.stderr)
        sys.exit(4)

    new_text = parts[0] + INSERT_AFTER + BLOCK + parts[1]
    TARGET.write_text(new_text, encoding="utf-8")
    print("OK: patch applied.")

if __name__ == "__main__":
    main()
