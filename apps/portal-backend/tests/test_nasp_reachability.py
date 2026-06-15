from src.services.nasp_reachability import aggregate_nasp_reachability


def test_aggregate_all_operational():
    diagnostics = {
        "sem_csmf": {"reachable": True, "status_code": 200},
        "ml_nsmf": {"reachable": True, "status_code": 200},
        "decision": {"reachable": True, "status_code": 200},
        "bc_nssmf": {"reachable": True, "status_code": 200},
        "sla_agent": {"reachable": True, "status_code": 200},
    }
    result = aggregate_nasp_reachability(diagnostics)
    assert result == {
        "reachable_modules": 5,
        "total_modules": 5,
        "reachability_percent": 100,
    }


def test_aggregate_partial_via_status_code():
    diagnostics = {
        "sem_csmf": {"reachable": False, "status_code": 503},
        "ml_nsmf": {"reachable": True, "status_code": 200},
        "decision": {"status_code": 200},
        "bc_nssmf": {"reachable": True},
        "sla_agent": {"reachable": False},
    }
    result = aggregate_nasp_reachability(diagnostics)
    assert result["reachable_modules"] == 3
    assert result["total_modules"] == 5
    assert result["reachability_percent"] == 60
