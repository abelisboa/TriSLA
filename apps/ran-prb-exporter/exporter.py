import os
import re
import time
from typing import Optional, Tuple

from flask import Flask, Response
from kubernetes import client, config

app = Flask(__name__)

NAMESPACE = os.environ.get("SRS_NAMESPACE", "srsran")
LABEL_SELECTOR = os.environ.get("SRS_LABEL_SELECTOR", "app=srsenb")
TAIL_LINES = int(os.environ.get("SRS_LOG_TAIL", "500"))


def _load_k8s() -> client.CoreV1Api:
    config.load_incluster_config()
    return client.CoreV1Api()


def _extract_prb(log_text: str) -> Tuple[Optional[float], str]:
    patterns = [
        re.compile(r"(?i)prb\s*(?:usage|util(?:ization)?)?\s*[:=]\s*(\d+(?:\.\d+)?)\s*%"),
        re.compile(r"(?i)rb\s*allocated\s*[:=]\s*(\d+)\s*/\s*(\d+)"),
        re.compile(r"(?i)prb\s*[:=]\s*(\d+(?:\.\d+)?)\s*%"),
    ]
    for line in reversed(log_text.splitlines()):
        for idx, pat in enumerate(patterns):
            m = pat.search(line)
            if not m:
                continue
            if idx == 1:
                used = float(m.group(1))
                total = float(m.group(2))
                if total > 0:
                    return (used / total) * 100.0, line.strip()
            else:
                return float(m.group(1)), line.strip()
    return None, ""


def _latest_srs_pod(v1: client.CoreV1Api) -> Optional[str]:
    pods = v1.list_namespaced_pod(NAMESPACE, label_selector=LABEL_SELECTOR).items
    if not pods:
        return None
    pods.sort(key=lambda p: p.metadata.creation_timestamp or 0, reverse=True)
    return pods[0].metadata.name


def read_real_prb() -> Tuple[Optional[float], str, str]:
    v1 = _load_k8s()
    pod_name = _latest_srs_pod(v1)
    if not pod_name:
        return None, "no_srsenb_pod_found", ""
    logs = v1.read_namespaced_pod_log(
        name=pod_name,
        namespace=NAMESPACE,
        tail_lines=TAIL_LINES,
        _preload_content=True,
    )
    prb, evidence = _extract_prb(logs or "")
    if prb is None:
        return None, "no_prb_pattern_found_in_logs", ""
    return prb, "ok", evidence


@app.route("/metrics")
def metrics() -> Response:
    now = int(time.time())
    prb, status, evidence = read_real_prb()
    lines = [
        "# HELP ran_prb_utilization RAN PRB utilization percentage extracted from real srsenb logs.",
        "# TYPE ran_prb_utilization gauge",
        "# HELP ran_prb_exporter_status Exporter status (1=parsed PRB from logs, 0=no valid PRB line found).",
        "# TYPE ran_prb_exporter_status gauge",
        f'ran_prb_exporter_status{{status="{status}"}} {1 if status == "ok" else 0}',
        "# HELP ran_prb_exporter_last_scrape_unixtime Last successful exporter scrape timestamp.",
        "# TYPE ran_prb_exporter_last_scrape_unixtime gauge",
        f"ran_prb_exporter_last_scrape_unixtime {now}",
    ]
    if prb is not None:
        lines.append(f"ran_prb_utilization {prb:.6f}")
    if evidence:
        safe = evidence.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'ran_prb_exporter_evidence{{line="{safe}"}} 1')
    body = "\n".join(lines) + "\n"
    return Response(body, mimetype="text/plain; version=0.0.4")


@app.route("/healthz")
def healthz() -> Response:
    return Response("ok\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9100)
