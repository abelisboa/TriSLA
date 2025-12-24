"
CRD Executor - Cria NSI/NSSI via CRDs do Kubernetes
Modo CRD-first: quando não há endpoint HTTP externo, cria CRDs diretamente
"

import os
import uuid
from typing import Dict, Any, Optional
from opentelemetry import trace
from kubernetes import client, config
from kubernetes.client.rest import ApiException

tracer = trace.get_tracer(__name__)

# API Group e Version dos CRDs
API_GROUP = "trisla.io"
API_VERSION = "v1"
NSI_PLURAL = "networksliceinstances"
NSSI_PLURAL = "networkslicesubnetinstances"


class CRDExecutor:
    "Executor que cria CRDs NSI/NSSI diretamente no Kubernetes"
    
    def __init__(self, namespace: str = "trisla"):
        self.namespace = namespace
        
        # Carregar configuração do Kubernetes (dentro do cluster)
        try:
            config.load_incluster_config()
        except Exception:
            # Fallback para desenvolvimento local
            try:
                config.load_kube_config()
            except Exception as e:
                print(f"⚠️ Não foi possível carregar config do Kubernetes: {e}")
        
        self.api = client.CustomObjectsApi()
    
    def _generate_nsi_id(self) -> str:
        "Gera ID único para NSI"
        return f"nsi-{uuid.uuid4().hex[:8]}"
    
    def _generate_nssi_id(self) -> str:
        "Gera ID único para NSSI"
        return f"nssi-{uuid.uuid4().hex[:8]}"
    
    def _map_domain_to_subnet_type(self, domain: str) -> str:
        "Mapeia domain para SubnetType do CRD"
        domain_lower = domain.lower()
        if domain_lower == "ran":
            return "RAN"
        elif domain_lower == "transport" or domain_lower == "tn":
            return "TN"
        elif domain_lower == "core":
            return "CORE"
        else:
            return "RAN"  # default
    
    async def create_nsi(self, action: Dict[str, Any], sla_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        "Cria NetworkSliceInstance (NSI) via CRD"
        with tracer.start_as_current_span("create_nsi_crd") as span:
            try:
                nsi_id = self._generate_nsi_id()
                action_type = action.get("type", "instantiate")
                domain = action.get("domain", "ran")
                
                # Extrair SLA se disponível
                sla = sla_data or {}
                availability = sla.get("availability", 0.99)
                latency = sla.get("latency", "50ms")
                reliability = sla.get("reliability", 0.999)
                
                # Criar spec do NSI conforme schema do CRD
                nsi_body = {
                    "apiVersion": f"{API_GROUP}/{API_VERSION}",
                    "kind": "NetworkSliceInstance",
                    "metadata": {
                        "name": nsi_id,
                        "namespace": self.namespace,
                        "labels": {
                            "app": "trisla",
                            "domain": domain,
                            "action_type": action_type
                        }
                    },
                    "spec": {
                        "NsiId": nsi_id,
                        "TenantId": os.getenv("TRISLA_TENANT_ID", "default-tenant"),
                        "ServiceProfile": f"profile-{domain}",
                        "Nssai": {
                            "Sst": 1,  # Slice/Service Type padrão
                            "Sd": f"{domain}-{nsi_id[:6]}"  # Slice Differentiator
                        },
                        "Sla": {
                            "Availability": float(availability),
                            "Latency": str(latency),
                            "Reliability": float(reliability)
                        }
                    }
                }
                
                # Criar NSI via API do Kubernetes
                created = self.api.create_namespaced_custom_object(
                    group=API_GROUP,
                    version=API_VERSION,
                    namespace=self.namespace,
                    plural=NSI_PLURAL,
                    body=nsi_body
                )
                
                span.set_attribute("nsi.created", True)
                span.set_attribute("nsi.id", nsi_id)
                span.set_attribute("nsi.domain", domain)
                
                print(f"✅ CRD-FIRST: created NSI {nsi_id} in namespace {self.namespace}")
                
                return {
                    "nsi_id": nsi_id,
                    "status": "created",
                    "domain": domain,
                    "action_type": action_type,
                    "method": "crd",
                    "resource": created
                }
                
            except ApiException as e:
                span.record_exception(e)
                error_msg = f"Erro ao criar NSI via CRD: {e.reason} - {e.body}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg) from e
            except Exception as e:
                span.record_exception(e)
                error_msg = f"Erro inesperado ao criar NSI: {str(e)}"
                print(f"❌ {error_msg}")
                raise
    
    async def create_nssi(self, nsi_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        "Cria NetworkSliceSubnetInstance (NSSI) via CRD"
        with tracer.start_as_current_span("create_nssi_crd") as span:
            try:
                nssi_id = self._generate_nssi_id()
                domain = action.get("domain", "ran")
                subnet_type = self._map_domain_to_subnet_type(domain)
                
                # Criar spec do NSSI conforme schema do CRD
                nssi_body = {
                    "apiVersion": f"{API_GROUP}/{API_VERSION}",
                    "kind": "NetworkSliceSubnetInstance",
                    "metadata": {
                        "name": nssi_id,
                        "namespace": self.namespace,
                        "labels": {
                            "app": "trisla",
                            "nsi_id": nsi_id,
                            "domain": domain,
                            "subnet_type": subnet_type
                        }
                    },
                    "spec": {
                        "NsiId": nsi_id,
                        "NssiId": nssi_id,
                        "SubnetType": subnet_type,
                        "SubnetConfig": {
                            "domain": domain,
                            "action_type": action.get("type", "instantiate")
                        }
                    }
                }
                
                # Criar NSSI via API do Kubernetes
                created = self.api.create_namespaced_custom_object(
                    group=API_GROUP,
                    version=API_VERSION,
                    namespace=self.namespace,
                    plural=NSSI_PLURAL,
                    body=nssi_body
                )
                
                span.set_attribute("nssi.created", True)
                span.set_attribute("nssi.id", nssi_id)
                span.set_attribute("nssi.subnet_type", subnet_type)
                
                print(f"✅ CRD-FIRST: created NSSI {nssi_id} (type={subnet_type}) for NSI {nsi_id}")
                
                return {
                    "nssi_id": nssi_id,
                    "nsi_id": nsi_id,
                    "status": "created",
                    "subnet_type": subnet_type,
                    "method": "crd",
                    "resource": created
                }
                
            except ApiException as e:
                span.record_exception(e)
                error_msg = f"Erro ao criar NSSI via CRD: {e.reason} - {e.body}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg) from e
            except Exception as e:
                span.record_exception(e)
                error_msg = f"Erro inesperado ao criar NSSI: {str(e)}"
                print(f"❌ {error_msg}")
                raise
    
    async def execute_action(self, action: Dict[str, Any], sla_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        "Executa ação criando NSI e NSSI via CRDs"
        with tracer.start_as_current_span("execute_action_crd") as span:
            try:
                print(f"🔧 CRD-FIRST: creating NSI/NSSI for action {action}")
                
                # Criar NSI primeiro
                nsi_result = await self.create_nsi(action, sla_data)
                nsi_id = nsi_result["nsi_id"]
                
                # Criar NSSI associado
                nssi_result = await self.create_nssi(nsi_id, action)
                
                span.set_attribute("action.executed", True)
                span.set_attribute("action.method", "crd")
                
                return {
                    "status": "success",
                    "method": "crd",
                    "nsi": nsi_result,
                    "nssi": nssi_result,
                    "action": action
                }
                
            except Exception as e:
                span.record_exception(e)
                raise
