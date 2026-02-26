import os
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException


class WorkloadProvisioner:
    """
    Provisiona workload REAL dentro do namespace do NSI.
    Objetivo: forçar o scheduler Kubernetes a validar capacidade fisicamente.
    Se faltar CPU/MEM → Pending com FailedScheduling (Insufficient*) → falha auditável.
    """

    def __init__(self):
        config.load_incluster_config()
        self.core = client.CoreV1Api()
        self.apps = client.AppsV1Api()

        # Defaults intencionais:
        # - habilitado por padrão para você já ver efeito (pode desligar por env)
        self.enabled = os.getenv("WORKLOAD_PROVISIONING_ENABLED", "true").lower() == "true"
        self.timeout = int(os.getenv("WORKLOAD_TIMEOUT_SECONDS", "120"))

    def provision(self, namespace: str, nsi_id: str, service_profile: str):
        if not self.enabled:
            return {"ok": True, "reason": "disabled"}

        deployment_name = f"nsi-load-{nsi_id}"
        cpu_req, mem_req = self._profile_resources(service_profile)

        deployment = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=deployment_name,
                namespace=namespace,
                labels={"trisla.io/nsi-id": nsi_id, "component": "nsi-load"},
            ),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels={"app": deployment_name}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": deployment_name}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name="load",
                                image=os.getenv("WORKLOAD_IMAGE", "polinux/stress"),
                                args=os.getenv(
                                    "WORKLOAD_ARGS",
                                    "--cpu 2 --vm 1 --vm-bytes 256M"
                                ).split(),
                                resources=client.V1ResourceRequirements(
                                    requests={"cpu": cpu_req, "memory": mem_req},
                                    limits={"cpu": cpu_req, "memory": mem_req},
                                ),
                            )
                        ]
                    ),
                ),
            ),
        )

        try:
            self.apps.create_namespaced_deployment(namespace, deployment)
        except ApiException as e:
            if e.status != 409:
                raise

        return self._wait_for_schedule(namespace, deployment_name)

    def _wait_for_schedule(self, namespace: str, deployment_name: str):
        deadline = time.time() + self.timeout

        while time.time() < deadline:
            pods = self.core.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment_name}",
            ).items

            if not pods:
                time.sleep(2)
                continue

            pod = pods[0]
            phase = pod.status.phase or ""

            if phase == "Running":
                return {"ok": True, "reason": "scheduled_running"}

            if phase == "Pending":
                # Captura evidência do scheduler via Events
                events = self.core.list_namespaced_event(namespace).items
                for ev in events:
                    msg = (ev.message or "")
                    if "FailedScheduling" in msg or "Insufficient" in msg:
                        return {"ok": False, "reason": "insufficient_resources", "details": msg}

            time.sleep(2)

        return {"ok": False, "reason": "timeout_waiting_schedule"}

    def _profile_resources(self, profile: str):
        # Defaults conservadores (não estouram cluster), mas geram consumo real.
        if profile == "URLLC":
            return os.getenv("URLLC_CPU", "500m"), os.getenv("URLLC_MEM", "512Mi")
        if profile == "eMBB":
            return os.getenv("EMBB_CPU", "2000m"), os.getenv("EMBB_MEM", "2Gi")
        return os.getenv("MMTC_CPU", "200m"), os.getenv("MMTC_MEM", "256Mi")
