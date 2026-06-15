"""Prometheus metrics for O8C actuation pipeline (Wave 1 + W2A scaffold)."""
from prometheus_client import Counter, Gauge

TRISLA_ACTUATION_REQUESTS_TOTAL = Counter(
    "trisla_actuation_requests_total",
    "Total actuation requests submitted (audit pipeline)",
    ["action_type", "action_domain", "risk_level"],
)

TRISLA_ACTUATION_AUTHORIZED_TOTAL = Counter(
    "trisla_actuation_authorized_total",
    "Actuation requests reaching authorized states",
    ["authorization_state", "action_domain"],
)

TRISLA_ACTUATION_DENIED_TOTAL = Counter(
    "trisla_actuation_denied_total",
    "Actuation requests denied",
    ["action_type", "action_domain"],
)

TRISLA_ACTUATION_PENDING_TOTAL = Gauge(
    "trisla_actuation_pending_total",
    "Actuation requests currently pending authorization",
)

TRISLA_ACTUATION_EXPIRED_TOTAL = Counter(
    "trisla_actuation_expired_total",
    "Actuation requests expired (auth or execution TTL)",
    ["action_domain", "expire_reason"],
)

TRISLA_ACTUATION_BY_DOMAIN = Counter(
    "trisla_actuation_by_domain",
    "Actuation audit events by domain",
    ["action_domain", "authorization_state"],
)

TRISLA_ACTUATION_EXECUTING_TOTAL = Counter(
    "trisla_actuation_executing_total",
    "Actuation scaffold executions started",
    ["action_type", "action_domain"],
)

TRISLA_ACTUATION_SUCCEEDED_TOTAL = Counter(
    "trisla_actuation_succeeded_total",
    "Actuation scaffold executions succeeded",
    ["action_type", "action_domain"],
)

TRISLA_ACTUATION_FAILED_TOTAL = Counter(
    "trisla_actuation_failed_total",
    "Actuation scaffold executions failed",
    ["action_type", "action_domain"],
)

TRISLA_ACTUATION_ROLLBACK_TOTAL = Counter(
    "trisla_actuation_rollback_total",
    "Actuation scaffold rollbacks recorded",
    ["action_domain"],
)

TRISLA_ACTUATION_VERIFY_TOTAL = Counter(
    "trisla_actuation_verify_total",
    "Actuation verify hook invocations (ACT-ASSUR-002 register)",
    ["verify_state", "action_domain"],
)

TRISLA_ACTUATION_EXECUTING_GAUGE = Gauge(
    "trisla_actuation_executing_gauge",
    "Actuation requests currently in EXECUTING state",
)

TRISLA_TRANSPORT_DRYRUN_TOTAL = Counter(
    "trisla_transport_dryrun_total",
    "ACT-TN-002 ONOS intent dry-run attempts (no POST)",
    ["action_type"],
)

TRISLA_TRANSPORT_DRYRUN_SUCCESS_TOTAL = Counter(
    "trisla_transport_dryrun_success_total",
    "ACT-TN-002 dry-run payload validated successfully",
    ["action_type"],
)

TRISLA_TRANSPORT_DRYRUN_VERIFY_TOTAL = Counter(
    "trisla_transport_dryrun_verify_total",
    "ACT-TN-002 dry-run verify hook invocations",
    ["verify_state"],
)

TRISLA_ADMISSION_THROTTLE_STATE = Gauge(
    "trisla_admission_throttle_state",
    "Admission throttle active (1=THROTTLED, 0=NORMAL/RESTORED)",
)

TRISLA_ADMISSION_THROTTLE_TOTAL = Counter(
    "trisla_admission_throttle_total",
    "ACT-ORCH-005 throttle activations",
    ["action_type"],
)

TRISLA_ADMISSION_RESTORE_TOTAL = Counter(
    "trisla_admission_restore_total",
    "ACT-ORCH-005 throttle restore (rollback) events",
    ["action_type"],
)

TRISLA_ADMISSION_THROTTLE_VERIFY_TOTAL = Counter(
    "trisla_admission_throttle_verify_total",
    "ACT-ORCH-005 verify hook invocations",
    ["verify_state"],
)

TRISLA_TRANSPORT_LIVE_TOTAL = Counter(
    "trisla_transport_live_total",
    "ACT-TN-002 LIVE ONOS intent POST attempts",
    ["action_type"],
)

TRISLA_TRANSPORT_LIVE_ROLLBACK_TOTAL = Counter(
    "trisla_transport_live_rollback_total",
    "ACT-TN-002 LIVE ONOS intent DELETE rollback events",
    ["action_type"],
)

TRISLA_TRANSPORT_LIVE_TOPOLOGY_DENIED_TOTAL = Counter(
    "trisla_transport_live_topology_denied_total",
    "ACT-TN-002 LIVE executions denied by topology gate",
)
