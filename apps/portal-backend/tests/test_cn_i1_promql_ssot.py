"""CN-I1 PromQL defaults — Sprint 5A real core alignment."""

from src.telemetry.promql_ssot import (
    CN_I1_CPU_DEFAULT,
    CN_I1_MEMORY_DEFAULT,
    CORE_CPU_SCOPED_FREE5GC_STACK,
    CORE_MEMORY_SCOPED_FREE5GC_STACK,
)


def test_cn_i1_defaults_use_scoped_free5gc_container_metrics():
    assert CN_I1_CPU_DEFAULT == CORE_CPU_SCOPED_FREE5GC_STACK
    assert CN_I1_MEMORY_DEFAULT == CORE_MEMORY_SCOPED_FREE5GC_STACK
    assert "container_cpu_usage_seconds_total" in CN_I1_CPU_DEFAULT
    assert "ns-1274485" in CN_I1_CPU_DEFAULT
    assert "container_memory_working_set_bytes" in CN_I1_MEMORY_DEFAULT
    assert "ns-1274485" in CN_I1_MEMORY_DEFAULT


def test_cn_i1_defaults_do_not_use_phantom_trisla_core_series():
    assert "trisla_core_cpu_utilization" not in CN_I1_CPU_DEFAULT
    assert "trisla_core_memory_utilization" not in CN_I1_MEMORY_DEFAULT
