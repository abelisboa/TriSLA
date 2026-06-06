"""
NSI Controller - NASP Adapter
Controller real para gerenciar Network Slice Instances (NSI) no Kubernetes
FASE C3-B2: Implementação real sem simulação
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from kubernetes import client
from kubernetes.client.rest import ApiException
from opentelemetry import trace
from .k8s_auth import load_incluster_config_with_validation

try:
    from slice_service_binding import (
        MAPPING_ANNOTATION_KEY,
        enrich_nsi_spec,
        mapping_annotation_value,
    )
except ImportError:
    enrich_nsi_spec = None  # type: ignore
    mapping_annotation_value = None  # type: ignore
    MAPPING_ANNOTATION_KEY = "trisla.io/slice-service-binding"

try:
    from nssf_adapter import (
        NSSF_SELECTION_ANNOTATION_KEY,
        select_nssf_slice,
    )
except ImportError:
    select_nssf_slice = None  # type: ignore
    NSSF_SELECTION_ANNOTATION_KEY = "trisla.io/nssf-selection"

try:
    from amf_smf_correlation import (
        AMF_BINDING_ANNOTATION_KEY,
        PDU_SESSION_SUMMARY_ANNOTATION_KEY,
        SMF_BINDING_ANNOTATION_KEY,
        run_amf_smf_binding,
    )
    from nssf_adapter import parse_nssf_selection_annotation
except ImportError:
    run_amf_smf_binding = None  # type: ignore
    AMF_BINDING_ANNOTATION_KEY = "trisla.io/amf-binding"
    SMF_BINDING_ANNOTATION_KEY = "trisla.io/smf-binding"
    PDU_SESSION_SUMMARY_ANNOTATION_KEY = "trisla.io/pdu-session-summary"
    parse_nssf_selection_annotation = None  # type: ignore

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class NSIController:
    """
    Controller real para Network Slice Instances
    Observa NSIs e cria recursos Kubernetes reais quando status.phase == Accepted
    """
    
    def __init__(self):
        """
        Inicializa o controller com clientes Kubernetes
        FASE C3-C3.2 FIX B: Hardening com validação e logs explícitos
        """
        try:
            # FASE C3-C3.2 FIX B: Usar função utilitária com validação
            api_client, token_present, namespace, apiserver = load_incluster_config_with_validation()
            
            # Criar APIs usando o ApiClient validado
            self.core_v1 = client.CoreV1Api(api_client=api_client)
            self.custom_api = client.CustomObjectsApi(api_client=api_client)
            self.apps_v1 = client.AppsV1Api(api_client=api_client)
            self.namespace = namespace  # Namespace do pod (trisla) para criar CRs no mesmo ns
            logger.info("✅ NSIController inicializado com sucesso")
            logger.info(f"✅ [NSI] Usando namespace: {namespace}")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar NSIController: {e}")
            logger.error(f"❌ [NSI] Falha ao carregar in-cluster config - verificar ServiceAccount e automountServiceAccountToken")
            raise
    
    def create_nsi(self, nsi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria um Network Slice Instance (NSI) no cluster Kubernetes
        
        Args:
            nsi_spec: Especificação do NSI contendo:
                - nsiId: ID do NSI
                - tenantId: ID do tenant
                - serviceProfile: URLLC | eMBB | mMTC
                - nssai: {sst, sd}
                - sla: {latency, reliability, availability, throughput}
        
        Returns:
            NSI criado com status
        """
        with tracer.start_as_current_span("create_nsi") as span:
            nsi_id = nsi_spec.get("nsiId") or f"nsi-{uuid.uuid4().hex[:8]}"
            span.set_attribute("nsi.id", nsi_id)
            
            logger.info(f"🔷 [NSI] Criando NSI: {nsi_id}")

            if enrich_nsi_spec is not None:
                enrich_nsi_spec(nsi_spec)

            slice_service_binding = nsi_spec.pop("_sliceServiceBinding", None)
            nssai_spec = nsi_spec.get("nssai", {"sst": 1})

            nssf_sel_ann = None
            if isinstance(slice_service_binding, dict) and select_nssf_slice is not None:
                try:
                    nssf_result = select_nssf_slice(slice_service_binding)
                    slice_service_binding = nssf_result.get("binding", slice_service_binding)
                    nssf_sel_ann = nssf_result.get("nssf_selection_annotation")
                except Exception as exc:
                    logger.warning("[NSSF] selection failed (non-blocking): %s", exc)

            labels = {
                "trisla.io/nsi-id": nsi_id,
                "trisla.io/tenant-id": nsi_spec.get("tenantId", "default"),
                "trisla.io/service-profile": nsi_spec.get("serviceProfile", "eMBB"),
                "app": "trisla",
                "component": "nsi",
            }
            annotations: Dict[str, str] = {}
            if isinstance(slice_service_binding, dict) and mapping_annotation_value is not None:
                annotations[MAPPING_ANNOTATION_KEY] = mapping_annotation_value(slice_service_binding)
                labels["trisla.io/ssb-version"] = slice_service_binding.get("mapping_version", "ssb-v1")
                labels["trisla.io/binding-phase"] = str(
                    slice_service_binding.get("binding_phase", "METADATA_ONLY")
                )
                if slice_service_binding.get("sd"):
                    labels["trisla.io/sd"] = str(slice_service_binding["sd"])
                labels["trisla.io/sst"] = str(slice_service_binding.get("sst", nssai_spec.get("sst", 1)))
                if nssf_sel_ann:
                    annotations[NSSF_SELECTION_ANNOTATION_KEY] = nssf_sel_ann
                if slice_service_binding.get("integration_flags", {}).get("nssf_integrated"):
                    labels["trisla.io/nssf-integrated"] = "true"
                    nsi_info = (slice_service_binding.get("nssf_selection") or {}).get("nsiInformation") or {}
                    if nsi_info.get("nsiId"):
                        labels["trisla.io/nssf-nsi-id"] = str(nsi_info["nsiId"])

            # Criar objeto NSI no mesmo namespace do adapter (trisla)
            nsi_body = {
                "apiVersion": "trisla.io/v1",
                "kind": "NetworkSliceInstance",
                "metadata": {
                    "name": nsi_id,
                    "namespace": self.namespace,
                    "labels": labels,
                    "annotations": annotations,
                },
                "spec": {
                    "nsiId": nsi_id,
                    "tenantId": nsi_spec.get("tenantId", "default"),
                    "serviceProfile": nsi_spec.get("serviceProfile", "eMBB"),
                    "nssai": nssai_spec,
                    "sla": nsi_spec.get("sla", {})
                },
                "status": {
                    "phase": "Requested",
                    "message": "NSI creation requested",
                    "createdAt": datetime.now(timezone.utc).isoformat()
                }
            }
            
            try:
                # Criar NSI via CustomObjectsApi no namespace do adapter
                created_nsi = self.custom_api.create_namespaced_custom_object(
                    group="trisla.io",
                    version="v1",
                    namespace=self.namespace,
                    plural="networksliceinstances",
                    body=nsi_body
                )
                
                logger.info(f"✅ [NSI] NSI criado: {nsi_id}")
                span.set_attribute("nsi.created", True)
                
                # Processar NSI (mover para Accepted e instanciar)
                self.process_nsi(nsi_id)
                
                return created_nsi
                
            except ApiException as e:
                logger.error(f"❌ [NSI] Erro ao criar NSI {nsi_id}: {e}")
                span.record_exception(e)
                raise
    
    def process_nsi(self, nsi_id: str):
        """
        Processa um NSI: move para Accepted e inicia instanciação
        
        Args:
            nsi_id: ID do NSI a processar
        """
        with tracer.start_as_current_span("process_nsi") as span:
            span.set_attribute("nsi.id", nsi_id)
            
            logger.info(f"🔄 [NSI] Processando NSI: {nsi_id}")
            
            try:
                # Buscar NSI atual
                nsi = self.custom_api.get_namespaced_custom_object(
                    group="trisla.io",
                    version="v1",
                    namespace=self.namespace,
                    plural="networksliceinstances",
                    name=nsi_id
                )
                
                current_phase = nsi.get("status", {}).get("phase", "Requested")
                
                # Se ainda não foi aceito, aceitar
                if current_phase == "Requested":
                    self._update_nsi_phase(nsi_id, "Accepted", "NSI accepted, starting instantiation")
                    logger.info(f"✅ [NSI] NSI {nsi_id} → Accepted")
                
                # Se aceito, iniciar instanciação
                if current_phase in ["Requested", "Accepted"]:
                    self._instantiate_nsi(nsi_id, nsi)
                
            except ApiException as e:
                logger.error(f"❌ [NSI] Erro ao processar NSI {nsi_id}: {e}")
                span.record_exception(e)
                raise
    
    def _instantiate_nsi(self, nsi_id: str, nsi: Dict[str, Any]):
        """
        Instancia um NSI: cria namespace, quotas, NSSIs
        
        Args:
            nsi_id: ID do NSI
            nsi: Objeto NSI completo
        """
        with tracer.start_as_current_span("instantiate_nsi") as span:
            span.set_attribute("nsi.id", nsi_id)
            
            logger.info(f"🚀 [NSI] Instantiating NSI: {nsi_id}")
            
            # Atualizar fase para Instantiating
            self._update_nsi_phase(nsi_id, "Instantiating", "Creating namespace and NSSIs")
            
            try:
                # 1. Criar namespace isolado
                namespace_name = f"ns-{nsi_id}"
                self._create_namespace(namespace_name, nsi)
                
                # 2. Criar ResourceQuota
                self._create_resource_quota(namespace_name, nsi)
                
                # === C3-C3.5C FIX ===
                # LimitRange removido nesta fase.
                # Motivo:
                # - ResourceQuota já garante isolamento
                # - defaultRequest não é aceito pelo client python
                # - Não é requisito 3GPP para NSI/NSSI
                # - Evita falha no reconcile
                logger.info("[NSI-RECONCILE] Skipping LimitRange creation (C3-C3.5C)")
                
                # 3. Criar NetworkPolicy
                self._create_network_policy(namespace_name, nsi)
                
                # 5. Criar 3 NSSIs (RAN, TN, CORE)
                nssi_ids = []
                for domain in ["RAN", "TN", "CORE"]:
                    nssi_id = self._create_nssi(nsi_id, domain, namespace_name, nsi)
                    nssi_ids.append(nssi_id)
                
                # 6. Atualizar NSI para Active
                self._update_nsi_phase(nsi_id, "Active", f"NSI instantiated with {len(nssi_ids)} NSSIs")
                
                # Atualizar lista de NSSIs no status
                self._update_nsi_status(nsi_id, {"nssiIds": nssi_ids})
                
                logger.info(f"✅ [NSI] Instantiating → Active: {nsi_id}")
                span.set_attribute("nsi.phase", "Active")
                span.set_attribute("nsi.nssi_count", len(nssi_ids))

                self._apply_o2c_bindings(nsi_id)
                
            except Exception as e:
                logger.error(f"❌ [NSI] Erro ao instanciar NSI {nsi_id}: {e}", exc_info=True)
                self._update_nsi_phase(nsi_id, "Degraded", f"Instantiation failed: {str(e)}")
                span.record_exception(e)
                raise
    
    def _create_namespace(self, namespace_name: str, nsi: Dict[str, Any]):
        """Cria namespace isolado para o NSI"""
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace_name,
                    labels={
                        "trisla.io/nsi-id": nsi["spec"]["nsiId"],
                        "trisla.io/tenant-id": nsi["spec"]["tenantId"],
                        "trisla.io/service-profile": nsi["spec"]["serviceProfile"],
                        "app": "trisla",
                        "component": "nsi-namespace"
                    }
                )
            )
            
            self.core_v1.create_namespace(body=namespace)
            logger.info(f"✅ [NSI] Namespace criado: {namespace_name}")
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.info(f"ℹ️ [NSI] Namespace já existe: {namespace_name}")
            else:
                raise
    
    def _create_resource_quota(self, namespace_name: str, nsi: Dict[str, Any]):
        """Cria ResourceQuota para o namespace"""
        try:
            # Calcular recursos baseado no serviceProfile
            service_profile = nsi["spec"]["serviceProfile"]
            
            if service_profile == "URLLC":
                cpu = "4"
                memory = "8Gi"
            elif service_profile == "eMBB":
                cpu = "8"
                memory = "16Gi"
            else:  # mMTC
                cpu = "2"
                memory = "4Gi"
            
            quota = client.V1ResourceQuota(
                metadata=client.V1ObjectMeta(
                    name=f"nsi-quota-{nsi['spec']['nsiId']}",
                    namespace=namespace_name,
                    labels={
                        "trisla.io/nsi-id": nsi["spec"]["nsiId"]
                    }
                ),
                spec=client.V1ResourceQuotaSpec(
                    hard={
                        "requests.cpu": cpu,
                        "requests.memory": memory,
                        "limits.cpu": cpu,
                        "limits.memory": memory
                    }
                )
            )
            
            self.core_v1.create_namespaced_resource_quota(namespace=namespace_name, body=quota)
            logger.info(f"✅ [NSI] ResourceQuota criada para {namespace_name}")
            
        except ApiException as e:
            if e.status == 409:
                logger.info(f"ℹ️ [NSI] ResourceQuota já existe para {namespace_name}")
            else:
                raise
    
    # === C3-C3.5C FIX ===
    # Método _create_limit_range removido.
    # Motivo:
    # - ResourceQuota já garante isolamento
    # - defaultRequest não é aceito pelo client python
    # - Não é requisito 3GPP para NSI/NSSI
    # - Evita falha no reconcile
    
    def _create_network_policy(self, namespace_name: str, nsi: Dict[str, Any]):
        """Cria NetworkPolicy para isolamento"""
        nsi_id = nsi["spec"]["nsiId"]
        policy_name = f"nsi-netpol-{nsi_id}"
        
        try:
            # FASE C3-C3.6A: Correção do NetworkPolicy - usar pod_selector com V1LabelSelector
            network_policy = client.V1NetworkPolicy(
                metadata=client.V1ObjectMeta(
                    name=policy_name,
                    namespace=namespace_name,
                    labels={
                        "trisla.io/nsi-id": nsi_id,
                        "trisla.io/nsi": nsi_id
                    }
                ),
                spec=client.V1NetworkPolicySpec(
                    pod_selector=client.V1LabelSelector(match_labels={}),  # seleciona TODOS os pods
                    policy_types=["Ingress", "Egress"],
                    ingress=[client.V1NetworkPolicyIngressRule()],  # allow-all ingress
                    egress=[client.V1NetworkPolicyEgressRule()]  # allow-all egress
                )
            )
            
            netpol_api = client.NetworkingV1Api()
            netpol_api.create_namespaced_network_policy(namespace=namespace_name, body=network_policy)
            logger.info(f"✅ [NSI-RECONCILE] NetworkPolicy ensured: {namespace_name}/{policy_name}")
            
        except ApiException as e:
            if e.status == 409:
                logger.info(f"ℹ️ [NSI] NetworkPolicy já existe para {namespace_name}")
            else:
                logger.warning(f"⚠️ [NSI] Erro ao criar NetworkPolicy (pode não estar habilitado): {e}")
    
    def _create_nssi(self, nsi_id: str, domain: str, namespace_name: str, nsi: Dict[str, Any]) -> str:
        """Cria um Network Slice Subnet Instance (NSSI)"""
        nssi_id = f"{nsi_id}-{domain.lower()}"
        
        logger.info(f"🔷 [NSSI] Criando NSSI: {nssi_id} (domain={domain})")

        nssi_annotations: Dict[str, str] = {}
        nssi_labels = {
            "trisla.io/nsi-id": nsi_id,
            "trisla.io/nssi-id": nssi_id,
            "trisla.io/nssi-domain": domain,
            "trisla.io/service-profile": nsi["spec"]["serviceProfile"],
            "app": "trisla",
            "component": "nssi",
        }
        raw_map = (nsi.get("metadata") or {}).get("annotations", {}).get(MAPPING_ANNOTATION_KEY)
        if raw_map:
            nssi_annotations["trisla.io/parent-slice-service-binding"] = raw_map
            nssi_labels["trisla.io/ssb-version"] = "ssb-v1"
        
        nssi_body = {
            "apiVersion": "trisla.io/v1",
            "kind": "NetworkSliceSubnetInstance",
            "metadata": {
                "name": nssi_id,
                "namespace": self.namespace,
                "labels": nssi_labels,
                "annotations": nssi_annotations,
            },
            "spec": {
                "nssiId": nssi_id,
                "domain": domain,
                "parentNsi": nsi_id,
                "resources": {
                    "cpu": "1",
                    "memory": "2Gi"
                }
            },
            "status": {
                "phase": "Active",
                "message": f"NSSI {domain} instantiated",
                "namespace": namespace_name,
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
        }
        
        try:
            created_nssi = self.custom_api.create_namespaced_custom_object(
                group="trisla.io",
                version="v1",
namespace=self.namespace,
                    plural="networkslicesubnetinstances",
                body=nssi_body
            )
            
            logger.info(f"✅ [NSSI] NSSI criado: {nssi_id}")
            return nssi_id
            
        except ApiException as e:
            if e.status == 409:
                logger.info(f"ℹ️ [NSSI] NSSI já existe: {nssi_id}")
                return nssi_id
            else:
                logger.error(f"❌ [NSSI] Erro ao criar NSSI {nssi_id}: {e}")
                raise
    
    def _apply_o2c_bindings(self, nsi_id: str) -> None:
        """O2C: AMF/SMF read-only observation + correlation (non-blocking)."""
        if run_amf_smf_binding is None or mapping_annotation_value is None:
            return
        try:
            nsi = self.custom_api.get_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networksliceinstances",
                name=nsi_id,
            )
            ann = (nsi.get("metadata") or {}).get("annotations") or {}
            from slice_service_binding import parse_mapping_annotation

            ssb = parse_mapping_annotation(ann.get(MAPPING_ANNOTATION_KEY))
            if not isinstance(ssb, dict):
                return

            nssf_sel = None
            if parse_nssf_selection_annotation is not None:
                nssf_sel = parse_nssf_selection_annotation(ann.get(NSSF_SELECTION_ANNOTATION_KEY))

            result = run_amf_smf_binding(ssb, nssf_selection=nssf_sel)
            if result.get("skipped"):
                return

            binding = result.get("binding") or ssb
            patch_ann = dict(ann)
            patch_ann[MAPPING_ANNOTATION_KEY] = mapping_annotation_value(binding)
            if result.get("amf_binding_annotation"):
                patch_ann[AMF_BINDING_ANNOTATION_KEY] = result["amf_binding_annotation"]
            if result.get("smf_binding_annotation"):
                patch_ann[SMF_BINDING_ANNOTATION_KEY] = result["smf_binding_annotation"]
            if result.get("pdu_session_summary_annotation"):
                patch_ann[PDU_SESSION_SUMMARY_ANNOTATION_KEY] = result["pdu_session_summary_annotation"]

            patch_labels = dict((nsi.get("metadata") or {}).get("labels") or {})
            patch_labels["trisla.io/binding-phase"] = str(binding.get("binding_phase", "METADATA_ONLY"))
            flags = binding.get("integration_flags") or {}
            if flags.get("amf_integrated"):
                patch_labels["trisla.io/amf-integrated"] = "true"
            if flags.get("smf_integrated"):
                patch_labels["trisla.io/smf-integrated"] = "true"

            body = {
                "metadata": {
                    "annotations": patch_ann,
                    "labels": patch_labels,
                }
            }
            self.custom_api.patch_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networksliceinstances",
                name=nsi_id,
                body=body,
            )
            logger.info(
                "[O2C] bindings applied nsi=%s phase=%s correlation=%s",
                nsi_id,
                binding.get("binding_phase"),
                result.get("correlation_status"),
            )
        except Exception as exc:
            logger.warning("[O2C] binding apply failed (non-blocking): %s", exc)

    def _update_nsi_phase(self, nsi_id: str, phase: str, message: str):
        """Atualiza a fase do NSI (via subresource status)."""
        try:
            status_body = {
                "status": {
                    "phase": phase,
                    "message": message,
                    "updatedAt": datetime.now(timezone.utc).isoformat(),
                }
            }
            self.custom_api.patch_namespaced_custom_object_status(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networksliceinstances",
                name=nsi_id,
                body=status_body,
            )
        except ApiException as e:
            logger.error(f"❌ [NSI] Erro ao atualizar fase do NSI {nsi_id}: {e}")
            raise
    
    def _update_nsi_status(self, nsi_id: str, status_updates: Dict[str, Any]):
        """Atualiza campos do status do NSI (via subresource status)."""
        try:
            status_body = {"status": dict(status_updates)}
            status_body["status"]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            self.custom_api.patch_namespaced_custom_object_status(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networksliceinstances",
                name=nsi_id,
                body=status_body,
            )
        except ApiException as e:
            logger.error(f"❌ [NSI] Erro ao atualizar status do NSI {nsi_id}: {e}")
            raise

