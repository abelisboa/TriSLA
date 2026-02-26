import os
import time
import logging
from kubernetes import client
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name, str(default)).strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except Exception:
        return default

def _choose_resources(service_profile: str) -> dict:
    """
    Recursos do workload (requests/limits) por perfil.
    Pode ser sobrescrito por env:
      URLLC_CPU, URLLC_MEM, EMBB_CPU, EMBB_MEM, MMTC_CPU, MMTC_MEM
    """
    sp = (service_profile or "eMBB").strip()
    sp_norm = sp.upper()

    if sp_norm == "URLLC":
        cpu = os.getenv("URLLC_CPU", "2")
        mem = os.getenv("URLLC_MEM", "2Gi")
    elif sp_norm == "EMBB" or sp_norm == "EMBB":
        cpu = os.getenv("EMBB_CPU", "6")
        mem = os.getenv("EMBB_MEM", "8Gi")
    else:  # mMTC
        cpu = os.getenv("MMTC_CPU", "1")
        mem = os.getenv("MMTC_MEM", "1Gi")

    return {"cpu": cpu, "memory": mem}

def ensure_workload(namespace: str, nsi_id: str, service_profile: str) -> None:
    """
    Cria (idempotente) um Deployment 'nsi-load' no namespace do NSI para consumir CPU/memória.
    - WORKLOAD_PROVISIONING_ENABLED=true habilita.
    - WORKLOAD_IMAGE define imagem (default: polinux/stress).
    - WORKLOAD_TIMEOUT_SECONDS controla janela de estabilização.
    """
    if not _env_bool("WORKLOAD_PROVISIONING_ENABLED", False):
        logger.info("[WORKLOAD] provisioning disabled (WORKLOAD_PROVISIONING_ENABLED=false).")
        return

    apps = client.AppsV1Api()
    core = client.CoreV1Api()

    # sanity: namespace deve existir
    try:
        core.read_namespace(namespace)
    except Exception as e:
        logger.warning("[WORKLOAD] namespace %s not found/readable: %s", namespace, e)
        return

    name = "nsi-load"
    labels = {"app": "trisla", "component": "nsi-load", "trisla.io/nsi-id": nsi_id}

    image = os.getenv("WORKLOAD_IMAGE", "polinux/stress:latest")
    timeout = _env_int("WORKLOAD_TIMEOUT_SECONDS", 90)

    res = _choose_resources(service_profile)
    cpu = res["cpu"]
    mem = res["memory"]

    # Stress real: CPU + alocação de memória (se o container suportar)
    # polinux/stress suporta: --cpu N --vm N --vm-bytes X
    # Usamos 1 vm worker com vm-bytes ~80% do limit (aproximação simples via env WORKLOAD_VM_BYTES)
    vm_bytes = os.getenv("WORKLOAD_VM_BYTES", "80%")
    cmd = [
        "/bin/sh", "-lc",
        "echo '[WORKLOAD] starting stress...'; "
        "stress --cpu 2 --vm 1 --vm-bytes ${VM_BYTES} --timeout 3600s; "
        "echo '[WORKLOAD] stress finished'; sleep 3600"
    ]

    env = [client.V1EnvVar(name="VM_BYTES", value=vm_bytes)]

    container = client.V1Container(
        name="nsi-load",
        image=image,
        image_pull_policy=os.getenv("WORKLOAD_IMAGE_PULL_POLICY", "IfNotPresent"),
        command=cmd,
        env=env,
        resources=client.V1ResourceRequirements(
            requests={"cpu": cpu, "memory": mem},
            limits={"cpu": cpu, "memory": mem},
        ),
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels=labels),
        spec=client.V1PodSpec(
            containers=[container],
            restart_policy="Always",
        ),
    )

    spec = client.V1DeploymentSpec(
        replicas=1,
        selector=client.V1LabelSelector(match_labels={"component": "nsi-load", "trisla.io/nsi-id": nsi_id}),
        template=template,
    )

    body = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name, namespace=namespace, labels=labels),
        spec=spec,
    )

    try:
        apps.create_namespaced_deployment(namespace=namespace, body=body)
        logger.info("[WORKLOAD] Deployment created: %s/%s cpu=%s mem=%s image=%s", namespace, name, cpu, mem, image)
    except ApiException as e:
        if e.status == 409:
            # já existe: patch para manter idempotência
            try:
                apps.patch_namespaced_deployment(name=name, namespace=namespace, body=body)
                logger.info("[WORKLOAD] Deployment patched: %s/%s cpu=%s mem=%s", namespace, name, cpu, mem)
            except Exception as pe:
                logger.warning("[WORKLOAD] Deployment exists but patch failed: %s", pe)
        else:
            logger.error("[WORKLOAD] create failed: %s", e)
            raise

    # Aguarda pod Running/Ready (melhor esforço). Se ficar Pending por falta de recursos, isso é evidência de saturação.
    end = time.time() + timeout
    while time.time() < end:
        try:
            pods = core.list_namespaced_pod(namespace=namespace, label_selector=f"component=nsi-load,trisla.io/nsi-id={nsi_id}")
            if pods.items:
                p = pods.items[0]
                phase = p.status.phase
                ready = False
                if p.status.container_statuses:
                    ready = all(cs.ready for cs in p.status.container_statuses)
                logger.info("[WORKLOAD] pod=%s phase=%s ready=%s", p.metadata.name, phase, ready)
                if phase == "Running" and ready:
                    return
        except Exception:
            pass
        time.sleep(3)

    logger.warning("[WORKLOAD] timeout waiting readiness (this can be expected under saturation).")
