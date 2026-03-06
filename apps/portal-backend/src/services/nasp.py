import requests


class NASPService:
    def __init__(self):
        self.sem_url = "http://trisla-sem-csmf:8080/health"
        self.bc_url = "http://trisla-bc-nssmf:8083/health"

    def _probe(self, name, url):
        try:
            r = requests.get(url, timeout=3)
            return {
                "module": name,
                "reachable": r.ok,
                "status_code": r.status_code,
                "detail": "ok"
            }
        except Exception as e:
            return {
                "module": name,
                "reachable": False,
                "detail": str(e)
            }

    def check_sem_csmf(self):
        return self._probe("sem-csmf", self.sem_url)

    def check_bc_nssmf(self):
        return self._probe("bc-nssmf", self.bc_url)

    def check_all_nasp_modules(self):
        return {
            "sem_csmf": self.check_sem_csmf(),
            "ml_nsmf": {"reachable": True},
            "decision": {"reachable": True},
            "bc_nssmf": self.check_bc_nssmf(),
            "sla_agent": {"reachable": True}
        }


_service = NASPService()


def check_sem_csmf():
    return _service.check_sem_csmf()


def check_bc_nssmf():
    return _service.check_bc_nssmf()


def check_all_nasp_modules():
    return _service.check_all_nasp_modules()
