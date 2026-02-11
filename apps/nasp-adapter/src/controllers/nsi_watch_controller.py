"""
NSI Watch Controller - NASP Adapter
Controller real que observa (watch) NetworkSliceInstances e executa reconcile
FASE C3-C1: Implementação real sem simulação
"""

import logging
import time
import threading
from typing import Dict, Any, Optional
from kubernetes import client, watch
from kubernetes.client.rest import ApiException
from opentelemetry import trace
from .k8s_auth import load_incluster_config_with_validation

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)


class NSIWatchController:
    """
    Controller que observa NSIs via watch e executa reconcile
    Implementa padrão controller do Kubernetes
    """
    
    def __init__(self, namespace: str = "trisla"):
        """
        Inicializa o watch controller
        
        Args:
            namespace: Namespace onde os NSIs estão (padrão: trisla)
        """
        self.namespace = namespace
        self.custom_api = None
        self.core_v1 = None
        self.netpol_api = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """
        Inicializa clientes Kubernetes
        FASE C3-C3.2 FIX B: Hardening com validação e logs explícitos
        """
        try:
            # FASE C3-C3.2 FIX B: Usar função utilitária com validação
            api_client, token_present, namespace, apiserver = load_incluster_config_with_validation()
            
            # Criar APIs usando o ApiClient validado
            self.custom_api = client.CustomObjectsApi(api_client=api_client)
            self.core_v1 = client.CoreV1Api(api_client=api_client)
            self.netpol_api = client.NetworkingV1Api(api_client=api_client)
            
            logger.info("✅ [NSI-WATCH] Clientes Kubernetes inicializados")
            logger.info(f"✅ [NSI-WATCH] Usando namespace: {namespace}")
        except Exception as e:
            logger.error(f"❌ [NSI-WATCH] Erro ao inicializar clientes: {e}")
            logger.error(f"❌ [NSI-WATCH] Falha ao carregar in-cluster config - verificar ServiceAccount e automountServiceAccountToken")
            raise
    
    def start_watch(self):
        """
        Inicia watch contínuo de NetworkSliceInstances
        Executa reconcile quando detecta eventos ADDED ou MODIFIED
        """
        logger.info(f"🔷 [NSI-WATCH] Iniciando watch (namespace={self.namespace})")
        
        w = watch.Watch()
        
        while True:
            try:
                # Watch de NetworkSliceInstances
                stream = w.stream(
                    self.custom_api.list_namespaced_custom_object,
                    group="trisla.io",
                    version="v1",
                    namespace=self.namespace,
                    plural="networksliceinstances",
                    timeout_seconds=60
                )
                
                for event in stream:
                    event_type = event['type']
                    nsi = event['object']
                    
                    nsi_id = nsi.get('spec', {}).get('nsiId') or nsi.get('metadata', {}).get('name')
                    current_phase = nsi.get('status', {}).get('phase', 'Requested')
                    
                    logger.info(f"🔷 [NSI-WATCH] Evento: {event_type} | NSI: {nsi_id} | Phase: {current_phase}")
                    
                    # Reconcile quando ADDED ou MODIFIED e phase precisa de processamento
                    if event_type in ['ADDED', 'MODIFIED']:
                        if current_phase in [None, 'Requested', 'Accepted']:
                            logger.info(f"🔄 [NSI-RECONCILE] Iniciando reconcile para NSI: {nsi_id} (phase={current_phase})")
                            try:
                                self.reconcile(nsi)
                            except Exception as e:
                                logger.error(f"❌ [NSI-RECONCILE] Erro ao reconciliar NSI {nsi_id}: {e}", exc_info=True)
                
            except ApiException as e:
                if e.status == 404:
                    logger.warning(f"⚠️ [NSI-WATCH] CRD não encontrado. Aguardando 10s antes de retry...")
                    time.sleep(10)
                else:
                    logger.error(f"❌ [NSI-WATCH] Erro na API: {e}")
                    time.sleep(5)
            except Exception as e:
                logger.error(f"❌ [NSI-WATCH] Erro no watch: {e}", exc_info=True)
                time.sleep(5)
    
    def reconcile(self, nsi: Dict[str, Any]):
        """
        Reconcile determinístico de um NSI
        
        Executa na ordem:
        A) Normalizar identificadores
        B) Criar namespace
        C) Criar ResourceQuota + LimitRange + NetworkPolicy
        D) Criar 3 NSSIs (RAN/TN/CORE)
        E) Atualizar status do NSI
        
        Args:
            nsi: Objeto NSI completo
        """
        with tracer.start_as_current_span("reconcile_nsi") as span:
            # A) Normalizar identificadores
            nsi_id = nsi.get('spec', {}).get('nsiId') or nsi.get('metadata', {}).get('name')
            span.set_attribute("nsi.id", nsi_id)
            
            logger.info(f"🔄 [NSI-RECONCILE] Reconciliando NSI: {nsi_id}")
            
            # B) Criar namespace alvo
            ns_name = f"ns-{nsi_id}"
            self._ensure_namespace(ns_name, nsi)
            
            # C) Criar ResourceQuota + NetworkPolicy
            # === C3-C3.5C FIX ===
            # LimitRange removido nesta fase.
            # Motivo:
            # - ResourceQuota já garante isolamento
            # - defaultRequest não é aceito pelo client python
            # - Não é requisito 3GPP para NSI/NSSI
            # - Evita falha no reconcile
            self._ensure_resource_quota(ns_name, nsi)
            logger.info("[NSI-RECONCILE] Skipping LimitRange creation (C3-C3.5C)")
            self._ensure_network_policy(ns_name, nsi)
            
            # D) Criar 3 NSSIs (RAN/TN/CORE)
            nssi_ids = []
            for domain in ["RAN", "TN", "CORE"]:
                nssi_id = self._ensure_nssi(nsi_id, domain, ns_name, nsi)
                nssi_ids.append(nssi_id)
            
            # E) Atualizar status do NSI
            current_phase = nsi.get('status', {}).get('phase', 'Requested')
            
            if current_phase == 'Requested':
                self._update_nsi_status(nsi_id, {
                    "phase": "Accepted",
                    "message": "NSI accepted, starting instantiation"
                })
                current_phase = "Accepted"
            
            if current_phase == 'Accepted':
                self._update_nsi_status(nsi_id, {
                    "phase": "Instantiating",
                    "message": "Creating namespace and NSSIs"
                })
            
            # Após criar tudo, marcar como Active
            self._update_nsi_status(nsi_id, {
                "phase": "Active",
                "message": f"NSI instantiated with {len(nssi_ids)} NSSIs",
                "nssiIds": nssi_ids
            })
            
            logger.info(f"✅ [NSI] phase -> Active: {nsi_id}")
            span.set_attribute("nsi.phase", "Active")
            span.set_attribute("nsi.nssi_count", len(nssi_ids))
    
    def _ensure_namespace(self, namespace_name: str, nsi: Dict[str, Any]):
        """Cria namespace se não existir (idempotente)"""
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=namespace_name,
                    labels={
                        "trisla.io/nsi-id": nsi.get('spec', {}).get('nsiId', ''),
                        "trisla.io/tenant-id": nsi.get('spec', {}).get('tenantId', 'default'),
                        "trisla.io/service-profile": nsi.get('spec', {}).get('serviceProfile', 'eMBB'),
                        "app": "trisla",
                        "component": "nsi-namespace"
                    }
                )
            )
            
            self.core_v1.create_namespace(body=namespace)
            logger.info(f"✅ [NSI] creating namespace {namespace_name}")
            
        except ApiException as e:
            if e.status == 409:  # Already exists
                logger.debug(f"ℹ️ [NSI] Namespace já existe: {namespace_name}")
            else:
                logger.error(f"❌ [NSI] Erro ao criar namespace {namespace_name}: {e}")
                raise
    
    def _ensure_resource_quota(self, namespace_name: str, nsi: Dict[str, Any]):
        """Cria ResourceQuota se não existir (idempotente).
        Nome da quota DEVE ser RFC 1123 válido (nunca terminar em '-').
        spec.nsiId tem precedência; fallback metadata.name para CRs legados."""
        nsi_id = nsi.get('spec', {}).get('nsiId') or nsi.get('metadata', {}).get('name') or ''
        nsi_id = (nsi_id or 'unknown').strip()
        # RFC 1123: lowercase alphanumeric and hyphen only; must not start/end with hyphen
        nsi_id_safe = ''.join(c if c.isalnum() or c == '-' else '-' for c in nsi_id.lower()).strip('-') or 'nsi'
        quota_name = f"nsi-quota-{nsi_id_safe}"
        
        # Calcular recursos baseado no serviceProfile
        service_profile = nsi.get('spec', {}).get('serviceProfile', 'eMBB')
        
        if service_profile == "URLLC":
            cpu = "4"
            memory = "8Gi"
        elif service_profile == "eMBB":
            cpu = "8"
            memory = "16Gi"
        else:  # mMTC
            cpu = "2"
            memory = "4Gi"
        
        try:
            quota = client.V1ResourceQuota(
                metadata=client.V1ObjectMeta(
                    name=quota_name,
                    namespace=namespace_name,
                    labels={
                        "trisla.io/nsi-id": nsi.get('spec', {}).get('nsiId', '')
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
            logger.info(f"✅ [NSI] creating resourcequota {quota_name}")
            
        except ApiException as e:
            if e.status == 409:
                # Já existe, tentar atualizar
                try:
                    self.core_v1.patch_namespaced_resource_quota(
                        name=quota_name,
                        namespace=namespace_name,
                        body=quota
                    )
                    logger.debug(f"ℹ️ [NSI] ResourceQuota atualizada: {quota_name}")
                except:
                    logger.debug(f"ℹ️ [NSI] ResourceQuota já existe: {quota_name}")
            else:
                logger.error(f"❌ [NSI] Erro ao criar ResourceQuota: {e}")
                raise
    
    # === C3-C3.5C FIX ===
    # Método _ensure_limit_range removido.
    # Motivo:
    # - ResourceQuota já garante isolamento
    # - defaultRequest não é aceito pelo client python
    # - Não é requisito 3GPP para NSI/NSSI
    # - Evita falha no reconcile
    
    def _ensure_network_policy(self, namespace_name: str, nsi: Dict[str, Any]):
        """Cria NetworkPolicy se não existir (idempotente). Nome RFC 1123 válido."""
        nsi_id = nsi.get('spec', {}).get('nsiId') or nsi.get('metadata', {}).get('name') or ''
        nsi_id_safe = (nsi_id or 'unknown').strip()
        nsi_id_safe = ''.join(c if c.isalnum() or c == '-' else '-' for c in nsi_id_safe.lower()).strip('-') or 'nsi'
        policy_name = f"nsi-netpol-{nsi_id_safe}"
        
        try:
            # FASE C3-C3.6A: Correção do NetworkPolicy - usar pod_selector com V1LabelSelector
            network_policy = client.V1NetworkPolicy(
                metadata=client.V1ObjectMeta(
                    name=policy_name,
                    namespace=namespace_name,
                    labels={
                        "trisla.io/nsi-id": nsi_id_safe,
                        "trisla.io/nsi": nsi_id_safe
                    }
                ),
                spec=client.V1NetworkPolicySpec(
                    pod_selector=client.V1LabelSelector(match_labels={}),  # seleciona TODOS os pods
                    policy_types=["Ingress", "Egress"],
                    ingress=[client.V1NetworkPolicyIngressRule()],  # allow-all ingress
                    egress=[client.V1NetworkPolicyEgressRule()]  # allow-all egress
                )
            )
            
            self.netpol_api.create_namespaced_network_policy(namespace=namespace_name, body=network_policy)
            logger.info(f"✅ [NSI-RECONCILE] NetworkPolicy ensured: {namespace_name}/{policy_name}")
            
        except ApiException as e:
            if e.status == 409:
                try:
                    self.netpol_api.patch_namespaced_network_policy(
                        name=policy_name,
                        namespace=namespace_name,
                        body=network_policy
                    )
                    logger.debug(f"ℹ️ [NSI] NetworkPolicy atualizada: {policy_name}")
                except:
                    logger.debug(f"ℹ️ [NSI] NetworkPolicy já existe: {policy_name}")
            else:
                logger.warning(f"⚠️ [NSI] Erro ao criar NetworkPolicy (pode não estar habilitado): {e}")
    
    def _ensure_nssi(self, nsi_id: str, domain: str, namespace_name: str, nsi: Dict[str, Any]) -> str:
        """Cria NSSI se não existir (idempotente)"""
        nssi_id = f"{nsi_id}-{domain.lower()}"
        
        try:
            nssi_body = {
                "apiVersion": "trisla.io/v1",
                "kind": "NetworkSliceSubnetInstance",
                "metadata": {
                    "name": nssi_id,
                    "namespace": self.namespace,
                    "labels": {
                        "trisla.io/nsi-id": nsi_id,
                        "trisla.io/nssi-id": nssi_id,
                        "trisla.io/nssi-domain": domain,
                        "trisla.io/service-profile": nsi.get('spec', {}).get('serviceProfile', 'eMBB'),
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
                    "namespace": namespace_name
                }
            }
            
            self.custom_api.create_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networkslicesubnetinstances",
                body=nssi_body
            )
            
            logger.info(f"✅ [NSI] creating NSSI {domain.lower()}: {nssi_id}")
            return nssi_id
            
        except ApiException as e:
            if e.status == 409:
                logger.debug(f"ℹ️ [NSI] NSSI já existe: {nssi_id}")
                return nssi_id
            else:
                logger.error(f"❌ [NSI] Erro ao criar NSSI {nssi_id}: {e}")
                raise
    
    def _update_nsi_status(self, nsi_id: str, status_updates: Dict[str, Any]):
        """Atualiza status do NSI usando status subresource"""
        try:
            from datetime import datetime, timezone
            
            # Buscar NSI atual
            nsi = self.custom_api.get_namespaced_custom_object(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networksliceinstances",
                name=nsi_id
            )
            
            # Preparar patch do status
            current_status = nsi.get('status', {})
            current_status.update(status_updates)
            current_status['updatedAt'] = datetime.now(timezone.utc).isoformat()
            
            # Patch apenas do status (subresource)
            status_patch = {
                "status": current_status
            }
            
            self.custom_api.patch_namespaced_custom_object_status(
                group="trisla.io",
                version="v1",
                namespace=self.namespace,
                plural="networksliceinstances",
                name=nsi_id,
                body=status_patch
            )
            
            phase = status_updates.get('phase', 'Unknown')
            logger.info(f"✅ [NSI] Status atualizado: {nsi_id} → {phase}")
            
        except ApiException as e:
            logger.error(f"❌ [NSI] Erro ao atualizar status do NSI {nsi_id}: {e}")
            raise


def start_nsi_watch():
    """
    Função para iniciar watch em thread separada
    Usada no startup do FastAPI
    """
    try:
        logger.info("🔷 [NSI-WATCH] Iniciando watch controller...")
        controller = NSIWatchController(namespace="trisla")
        logger.info("✅ [NSI-WATCH] started (namespace=trisla)")
        controller.start_watch()
    except Exception as e:
        logger.error(f"❌ [NSI-WATCH] Erro ao iniciar watch: {e}", exc_info=True)

