"""
ReservationStore - Ledger de reservas (PROMPT_SMDCE_V2_CAPACITY_ACCOUNTING)
Backend: CRD TriSLAReservation (K8s CustomObjectsApi).
Operações: create_pending, activate, release, expire_pending, list_active, mark_orphaned.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from kubernetes import client
from kubernetes.client.rest import ApiException
from opentelemetry import trace

from controllers.k8s_auth import load_incluster_config_with_validation

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

GROUP = "trisla.io"
VERSION = "v1"
PLURAL = "trislareservations"


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ReservationStore:
    """Ledger de reservas via CRD TriSLAReservation."""

    def __init__(self):
        try:
            api_client, _, namespace, _ = load_incluster_config_with_validation()
            self.custom_api = client.CustomObjectsApi(api_client=api_client)
            self.namespace = namespace
            logger.info("✅ ReservationStore inicializado (namespace=%s)", self.namespace)
        except Exception as e:
            logger.error("❌ ReservationStore init failed: %s", e)
            raise

    def create_pending(
        self,
        intent_id: str,
        slice_type: str = "eMBB",
        resources_reserved: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Cria reserva em estado PENDING. Retorna o objeto criado (com spec.reservationId)."""
        with tracer.start_as_current_span("reservation_create_pending") as span:
            rid = f"res-{uuid.uuid4().hex[:12]}"
            span.set_attribute("reservation.id", rid)
            now = _iso_now()
            expires_at = None
            if ttl_seconds and ttl_seconds > 0:
                from datetime import timedelta
                exp = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
                expires_at = exp.isoformat().replace("+00:00", "Z")

            body = {
                "apiVersion": f"{GROUP}/{VERSION}",
                "kind": "TriSLAReservation",
                "metadata": {
                    "name": rid,
                    "namespace": self.namespace,
                    "labels": {
                        "trisla.io/reservation-id": rid,
                        "trisla.io/status": "PENDING",
                        "trisla.io/intent-id": intent_id,
                        "app": "trisla",
                    },
                },
                "spec": {
                    "reservationId": rid,
                    "intentId": intent_id,
                    "nsiId": "",
                    "sliceType": slice_type,
                    "status": "PENDING",
                    "resourcesReserved": resources_reserved or {},
                    "createdAt": now,
                    "expiresAt": expires_at or "",
                    "reason": "",
                },
            }
            try:
                created = self.custom_api.create_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, body=body,
                )
                logger.info("✅ [RESERVATION] create_pending: %s intent=%s", rid, intent_id)
                return created
            except ApiException as e:
                logger.error("❌ [RESERVATION] create_pending failed: %s", e)
                span.record_exception(e)
                raise

    def activate(self, reservation_id: str, nsi_id: str) -> Optional[Dict[str, Any]]:
        """Transiciona PENDING → ACTIVE e associa nsi_id."""
        with tracer.start_as_current_span("reservation_activate") as span:
            span.set_attribute("reservation.id", reservation_id)
            span.set_attribute("nsi.id", nsi_id)
            try:
                obj = self.custom_api.get_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, name=reservation_id,
                )
            except ApiException as e:
                if e.status == 404:
                    logger.warning("[RESERVATION] activate: reservation %s not found", reservation_id)
                    return None
                raise
            spec = obj.get("spec", {})
            if spec.get("status") != "PENDING":
                logger.warning("[RESERVATION] activate: %s not PENDING (current=%s)", reservation_id, spec.get("status"))
                return None
            spec["status"] = "ACTIVE"
            spec["nsiId"] = nsi_id
            spec["reason"] = "activated"
            obj["spec"] = spec
            try:
                updated = self.custom_api.patch_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, name=reservation_id, body=obj,
                )
                logger.info("✅ [RESERVATION] activate: %s → nsi=%s", reservation_id, nsi_id)
                return updated
            except ApiException as e:
                logger.error("❌ [RESERVATION] activate failed: %s", e)
                raise

    def release(self, reservation_id: str, reason: str = "release") -> Optional[Dict[str, Any]]:
        """Transiciona para RELEASED (rollback ou cancelamento)."""
        with tracer.start_as_current_span("reservation_release") as span:
            span.set_attribute("reservation.id", reservation_id)
            try:
                obj = self.custom_api.get_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, name=reservation_id,
                )
            except ApiException as e:
                if e.status == 404:
                    logger.warning("[RESERVATION] release: %s not found", reservation_id)
                    return None
                raise
            spec = obj.get("spec", {})
            if spec.get("status") in ("RELEASED", "EXPIRED", "ORPHANED"):
                return obj
            spec["status"] = "RELEASED"
            spec["reason"] = reason
            obj["spec"] = spec
            try:
                updated = self.custom_api.patch_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, name=reservation_id, body=obj,
                )
                logger.info("✅ [RESERVATION] release: %s reason=%s", reservation_id, reason)
                return updated
            except ApiException as e:
                logger.error("❌ [RESERVATION] release failed: %s", e)
                raise

    def list_active(self) -> List[Dict[str, Any]]:
        """Lista reservas com status ACTIVE (contam no ledger)."""
        with tracer.start_as_current_span("reservation_list_active"):
            try:
                resp = self.custom_api.list_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace, plural=PLURAL,
                )
                items = resp.get("items", [])
                active = [i for i in items if (i.get("spec") or {}).get("status") == "ACTIVE"]
                return active
            except ApiException as e:
                logger.error("❌ [RESERVATION] list_active failed: %s", e)
                return []

    def list_pending(self) -> List[Dict[str, Any]]:
        """Lista reservas PENDING (para reconciler TTL)."""
        try:
            resp = self.custom_api.list_namespaced_custom_object(
                group=GROUP, version=VERSION, namespace=self.namespace, plural=PLURAL,
            )
            items = resp.get("items", [])
            return [i for i in items if (i.get("spec") or {}).get("status") == "PENDING"]
        except ApiException as e:
            logger.error("❌ [RESERVATION] list_pending failed: %s", e)
            return []

    def expire_pending(self, ttl_seconds: int) -> int:
        """Expira reservas PENDING cujo createdAt + ttl_seconds já passou. Retorna quantidade expiradas."""
        now = datetime.now(timezone.utc)
        count = 0
        for item in self.list_pending():
            spec = item.get("spec", {})
            rid = spec.get("reservationId") or item.get("metadata", {}).get("name")
            created_str = spec.get("createdAt") or ""
            if not created_str:
                continue
            try:
                created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except Exception:
                continue
            if (now - created).total_seconds() >= ttl_seconds:
                try:
                    spec["status"] = "EXPIRED"
                    spec["reason"] = "ttl_expired"
                    item["spec"] = spec
                    self.custom_api.patch_namespaced_custom_object(
                        group=GROUP, version=VERSION, namespace=self.namespace,
                        plural=PLURAL, name=rid, body=item,
                    )
                    count += 1
                    logger.info("✅ [RESERVATION] expire_pending: %s", rid)
                except ApiException as e:
                    logger.warning("[RESERVATION] expire_pending patch failed for %s: %s", rid, e)
        return count

    def mark_orphaned(self, reservation_id: str, reason: str = "orphaned") -> Optional[Dict[str, Any]]:
        """Marca reserva ACTIVE como ORPHANED (drift: NSI não existe mais)."""
        with tracer.start_as_current_span("reservation_mark_orphaned") as span:
            span.set_attribute("reservation.id", reservation_id)
            try:
                obj = self.custom_api.get_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, name=reservation_id,
                )
            except ApiException as e:
                if e.status == 404:
                    return None
                raise
            spec = obj.get("spec", {})
            if spec.get("status") != "ACTIVE":
                return obj
            spec["status"] = "ORPHANED"
            spec["reason"] = reason
            obj["spec"] = spec
            try:
                updated = self.custom_api.patch_namespaced_custom_object(
                    group=GROUP, version=VERSION, namespace=self.namespace,
                    plural=PLURAL, name=reservation_id, body=obj,
                )
                logger.info("✅ [RESERVATION] mark_orphaned: %s reason=%s", reservation_id, reason)
                return updated
            except ApiException as e:
                logger.error("❌ [RESERVATION] mark_orphaned failed: %s", e)
                raise
