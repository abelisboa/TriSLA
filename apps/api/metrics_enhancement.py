from prometheus_client import Histogram, Counter

trisla_req_duration = Histogram(
    "trisla_req_duration_seconds",
    "Tempo de resposta por interface",
    ["interface", "domain"]
)
trisla_req_errors = Counter(
    "trisla_req_error_total",
    "Total de erros por interface",
    ["interface", "domain"]
)

def observe_request(interface, domain, duration, is_error=False):
    trisla_req_duration.labels(interface=interface, domain=domain).observe(duration)
    if is_error:
        trisla_req_errors.labels(interface=interface, domain=domain).inc()

