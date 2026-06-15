"""
NASP Client - Conexão com serviços reais do NASP
Sprint 8G: endpoints alinhados ao Free5GC ns-1274485 + health check real no startup.
"""

import httpx
from typing import Any, Dict, Optional

from opentelemetry import trace

from nasp_connectivity import (
    DEFAULT_ENDPOINTS,
    probe_http_reachable,
    resolve_endpoint,
)

tracer = trace.get_tracer(__name__)


class NASPClient:
    """Cliente para serviços reais do NASP"""

    def __init__(self):
        import os

        nasp_mode = os.getenv("NASP_MODE", "real")
        self._mode = nasp_mode

        if nasp_mode == "mock":
            mock = os.getenv("NASP_CORE_ENDPOINT", "http://mock-nasp-core:80")
            self.ran_endpoint = os.getenv("NASP_RAN_ENDPOINT", mock)
            self.ran_metrics_endpoint = os.getenv("NASP_RAN_METRICS_ENDPOINT", mock)
            self.transport_endpoint = os.getenv("NASP_TRANSPORT_ENDPOINT", mock)
            self.core_endpoint = mock
            self.core_upf_endpoint = mock
            self.core_upf_metrics_endpoint = mock
            self.core_amf_endpoint = mock
            self.core_smf_endpoint = mock
            self.core_nrf_endpoint = mock
        else:
            self.ran_endpoint = resolve_endpoint("NASP_RAN_ENDPOINT")
            self.ran_metrics_endpoint = resolve_endpoint("NASP_RAN_METRICS_ENDPOINT")
            self.core_amf_endpoint = resolve_endpoint("NASP_CORE_AMF_ENDPOINT")
            self.core_smf_endpoint = resolve_endpoint("NASP_CORE_SMF_ENDPOINT")
            self.core_nrf_endpoint = resolve_endpoint("NASP_CORE_NRF_ENDPOINT")
            self.transport_endpoint = resolve_endpoint("NASP_TRANSPORT_ENDPOINT")
            self.core_endpoint = resolve_endpoint("NASP_CORE_ENDPOINT")
            # Legacy fields kept for metadata; UPF has no HTTP SBI metrics in lab.
            from nasp_connectivity import FREE5GC_NAMESPACE

            self.core_upf_endpoint = os.getenv(
                "NASP_CORE_UPF_ENDPOINT",
                f"http://upf-service.{FREE5GC_NAMESPACE}.svc.cluster.local:8805",
            )
            self.core_upf_metrics_endpoint = self.core_amf_endpoint

        self.client = httpx.AsyncClient(timeout=30.0)
        self._connected = False
        self._connectivity_detail: Dict[str, Any] = {}

    async def connect(self) -> bool:
        """Valida conectividade Core (AMF + SMF SBI) no ns-1274485."""
        with tracer.start_as_current_span("connect_nasp") as span:
            detail: Dict[str, Any] = {
                "mode": self._mode,
                "core_namespace": "ns-1274485",
                "probes": {},
            }
            if self._mode == "mock":
                self._connected = True
                detail["probes"]["mock"] = {"reachable": True}
                self._connectivity_detail = detail
                span.set_attribute("nasp.connected", True)
                return True

            amf_ok, amf_status = await probe_http_reachable(
                self.client, self.core_amf_endpoint
            )
            smf_ok, smf_status = await probe_http_reachable(
                self.client, self.core_smf_endpoint
            )
            nrf_ok, nrf_status = await probe_http_reachable(
                self.client, self.core_nrf_endpoint
            )

            detail["probes"]["amf"] = {
                "endpoint": self.core_amf_endpoint,
                "reachable": amf_ok,
                "http_status": amf_status,
            }
            detail["probes"]["smf"] = {
                "endpoint": self.core_smf_endpoint,
                "reachable": smf_ok,
                "http_status": smf_status,
            }
            detail["probes"]["nrf"] = {
                "endpoint": self.core_nrf_endpoint,
                "reachable": nrf_ok,
                "http_status": nrf_status,
            }

            # Core connectivity SSOT: AMF and SMF SBI must respond.
            self._connected = bool(amf_ok and smf_ok)
            detail["nasp_connected"] = self._connected
            self._connectivity_detail = detail

            span.set_attribute("nasp.connected", self._connected)
            span.set_attribute("nasp.amf.reachable", amf_ok)
            span.set_attribute("nasp.smf.reachable", smf_ok)
            return self._connected

    def is_connected(self) -> bool:
        return self._connected

    def get_connectivity_detail(self) -> Dict[str, Any]:
        return dict(self._connectivity_detail)

    async def get_ran_metrics(self) -> Dict[str, Any]:
        with tracer.start_as_current_span("get_ran_metrics") as span:
            try:
                response = await self.client.get(
                    f"{self.ran_metrics_endpoint}/metrics", timeout=10.0
                )
                response.raise_for_status()
                metrics = (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else {"raw": response.text}
                )
                span.set_attribute("metrics.source", "nasp_ran_real")
                span.set_attribute("metrics.endpoint", self.ran_metrics_endpoint)
                return metrics
            except Exception as e:
                span.record_exception(e)
                raise

    async def execute_ran_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        with tracer.start_as_current_span("execute_ran_action") as span:
            try:
                response = await self.client.post(
                    f"{self.ran_endpoint}/api/v1/actions",
                    json=action,
                )
                response.raise_for_status()
                result = response.json()
                span.set_attribute("action.executed", True)
                span.set_attribute("action.domain", "RAN")
                return result
            except Exception as e:
                span.record_exception(e)
                raise

    async def get_transport_metrics(self) -> Dict[str, Any]:
        with tracer.start_as_current_span("get_transport_metrics") as span:
            ok, status = await probe_http_reachable(
                self.client, self.transport_endpoint
            )
            span.set_attribute("metrics.source", "nasp_transport_sbi_probe")
            return {
                "reachable": ok,
                "http_status": status,
                "endpoint": self.transport_endpoint,
                "source": "nasp_transport_sbi_connectivity",
            }

    async def get_core_metrics(self) -> Dict[str, Any]:
        with tracer.start_as_current_span("get_core_metrics") as span:
            amf_ok, amf_status = await probe_http_reachable(
                self.client, self.core_amf_endpoint
            )
            smf_ok, smf_status = await probe_http_reachable(
                self.client, self.core_smf_endpoint
            )
            span.set_attribute("metrics.source", "nasp_core_sbi_probe")
            return {
                "amf": {
                    "reachable": amf_ok,
                    "http_status": amf_status,
                    "endpoint": self.core_amf_endpoint,
                },
                "smf": {
                    "reachable": smf_ok,
                    "http_status": smf_status,
                    "endpoint": self.core_smf_endpoint,
                },
                "source": "nasp_core_sbi_connectivity",
            }
