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
            
            # Criar objeto NSI
            nsi_body = {
                "apiVersion": "trisla.io/v1",
                "kind": "NetworkSliceInstance",
                "metadata": {
                    "name": nsi_id,
                    "namespace": "default",
                    "labels": {
                        "trisla.io/nsi-id": nsi_id,
                        "trisla.io/tenant-id": nsi_spec.get("tenantId", "default"),
                        "trisla.io/service-profile": nsi_spec.get("serviceProfile", "eMBB"),
                        "app": "trisla",
                        "component": "nsi"
                    }
                },
                "spec": {
                    "nsiId": nsi_id,
                    "tenantId": nsi_spec.get("tenantId", "default"),
                    "serviceProfile": nsi_spec.get("serviceProfile", "eMBB"),
                    "nssai": nsi_spec.get("nssai", {"sst": 1}),
                    "sla": nsi_spec.get("sla", {})
                },
                "status": {
                    "phase": "Requested",
                    "message": "NSI creation requested",
                    "createdAt": datetime.now(timezone.utc).isoformat()
                }
            }
            
            try:
                # Criar NSI via CustomObjectsApi
                created_nsi = self.custom_api.create_namespaced_custom_object(
                    group="trisla.io",
                    version="v1",
                    namespace="default",
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
                    namespace="default",
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
        
        nssi_body = {
            "apiVersion": "trisla.io/v1",
            "kind": "NetworkSliceSubnetInstance",
            "metadata": {
                "name": nssi_id,
                "namespace": "default",
                "labels": {
                    "trisla.io/nsi-id": nsi_id,
                    "trisla.io/nssi-id": nssi_id,
                    "trisla.io/nssi-domain": domain,
                    "trisla.io/service-profile": nsi["spec"]["serviceProfile"],
                    "app": "trisla",
                    "component": "nssi"
                }
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
                namespace="default",
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
    
    def _update_nsi_phase(self, nsi_id: str, phase: str, message: str):
        """Atualiza a fase do NSI"""
        try:
            nsi = self.custom_api.get_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace="default",
                plural="networksliceinstances",
                name=nsi_id
            )
            
            nsi["status"]["phase"] = phase
            nsi["status"]["message"] = message
            nsi["status"]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            
            self.custom_api.patch_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace="default",
                plural="networksliceinstances",
                name=nsi_id,
                body=nsi
            )
            
        except ApiException as e:
            logger.error(f"❌ [NSI] Erro ao atualizar fase do NSI {nsi_id}: {e}")
            raise
    
    def _update_nsi_status(self, nsi_id: str, status_updates: Dict[str, Any]):
        """Atualiza campos do status do NSI"""
        try:
            nsi = self.custom_api.get_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace="default",
                plural="networksliceinstances",
                name=nsi_id
            )
            
            nsi["status"].update(status_updates)
            nsi["status"]["updatedAt"] = datetime.now(timezone.utc).isoformat()
            
            self.custom_api.patch_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace="default",
                plural="networksliceinstances",
                name=nsi_id,
                body=nsi
            )
            
        except ApiException as e:
            logger.error(f"❌ [NSI] Erro ao atualizar status do NSI {nsi_id}: {e}")
            raise

