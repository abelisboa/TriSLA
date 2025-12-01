#!/usr/bin/env python3
"""
Script de Validação e Testes Locais do TriSLA
Executa validações e testes que podem ser feitos na máquina local
"""

import sys
import os
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Cores para output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

BASE_DIR = Path(__file__).parent.parent


class TriSLAValidator:
    """Validador local do TriSLA"""
    
    # Portas dos módulos
    MODULES = {
        "SEM-CSMF": 8080,
        "ML-NSMF": 8081,
        "Decision Engine": 8082,
        "BC-NSSMF": 8083,
        "SLA-Agent Layer": 8084,
        "NASP Adapter": 8085,
    }
    
    # Serviços de monitoramento
    MONITORING = {
        "OTLP Collector (gRPC)": 4317,
        "OTLP Collector (HTTP)": 4318,
        "Prometheus": 9090,
        "Grafana": 3000,
    }
    
    def __init__(self):
        self.results = {
            "health_checks": {},
            "endpoints": {},
            "interfaces": {},
            "monitoring": {},
            "slo_reports": {}
        }
    
    def print_header(self, title: str):
        """Imprime cabeçalho de seção"""
        print(f"\n{'━' * 64}")
        print(f"{title}")
        print(f"{'━' * 64}\n")
    
    def check_service(self, name: str, port: int, timeout: int = 2) -> bool:
        """Verifica se um serviço está rodando na porta especificada"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def test_health_endpoint(self, module: str, port: int) -> Optional[Dict]:
        """Testa endpoint de health de um módulo"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def test_interface_i01(self) -> bool:
        """Testa Interface I-01: Intent Recepção"""
        try:
            intent_data = {
                "intent_id": "test-001",
                "service_type": "5G",
                "sla_requirements": {
                    "latency": "10ms",
                    "bandwidth": "100Mbps"
                }
            }
            response = requests.post(
                "http://localhost:8080/api/v1/intents",
                json=intent_data,
                timeout=5
            )
            return response.status_code in [200, 201]
        except:
            return False
    
    def test_interface_i02(self, nest_id: str = "test-nest-001") -> bool:
        """Testa Interface I-02: NEST Geração"""
        try:
            response = requests.get(
                f"http://localhost:8080/api/v1/nests/{nest_id}",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def test_interface_i03(self) -> bool:
        """Testa Interface I-03: Previsão ML (Kafka)"""
        # Requer Kafka rodando - apenas verifica se o módulo está disponível
        return self.check_service("ML-NSMF", 8081)
    
    def validate_health_modules(self):
        """1. Verificar Health dos Módulos"""
        self.print_header("1️⃣  Verificando Health dos Módulos")
        
        for module, port in self.MODULES.items():
            is_running = self.check_service(module, port)
            status = f"{GREEN}✅{NC}" if is_running else f"{YELLOW}⚠️{NC}"
            print(f"{status} {module} (porta {port})")
            self.results["health_checks"][module] = is_running
    
    def validate_health_endpoints(self):
        """2. Testar Endpoints de Health"""
        self.print_header("2️⃣  Testando Endpoints de Health")
        
        for module, port in self.MODULES.items():
            health_data = self.test_health_endpoint(module, port)
            if health_data:
                print(f"{GREEN}✅{NC} {module}: {json.dumps(health_data, indent=2)}")
                self.results["endpoints"][module] = health_data
            else:
                print(f"{YELLOW}⚠️{NC} {module} não está acessível")
                self.results["endpoints"][module] = None
    
    def validate_interfaces(self):
        """3. Testar Interfaces I-01 a I-07"""
        self.print_header("3️⃣  Testando Interfaces I-01 a I-07")
        
        # I-01: Intent Recepção
        i01_ok = self.test_interface_i01()
        status_i01 = f"{GREEN}✅{NC}" if i01_ok else f"{YELLOW}⚠️{NC}"
        print(f"{status_i01} I-01 (Intent Recepção): {'OK' if i01_ok else 'Falhou ou serviço não disponível'}")
        self.results["interfaces"]["I-01"] = i01_ok
        
        # I-02: NEST Geração
        i02_ok = self.test_interface_i02()
        status_i02 = f"{GREEN}✅{NC}" if i02_ok else f"{YELLOW}⚠️{NC}"
        print(f"{status_i02} I-02 (NEST Geração): {'OK' if i02_ok else 'Falhou ou serviço não disponível'}")
        self.results["interfaces"]["I-02"] = i02_ok
        
        # I-03: Previsão ML
        i03_ok = self.test_interface_i03()
        status_i03 = f"{GREEN}✅{NC}" if i03_ok else f"{YELLOW}⚠️{NC}"
        print(f"{status_i03} I-03 (Previsão ML): {'OK' if i03_ok else 'Serviço não disponível'}")
        self.results["interfaces"]["I-03"] = i03_ok
        
        # I-04, I-05, I-06, I-07 requerem Kafka e outros serviços
        print(f"{YELLOW}⚠️{NC} I-04, I-05, I-06, I-07: Requerem Kafka e serviços adicionais")
        print("   Execute testes de integração completos com: pytest tests/integration/")
    
    def validate_otlp_collector(self):
        """4. Verificar OTLP Collector"""
        self.print_header("4️⃣  Verificando OTLP Collector")
        
        # Verificar portas
        grpc_ok = self.check_service("OTLP Collector", 4317)
        http_ok = self.check_service("OTLP Collector", 4318)
        
        status_grpc = f"{GREEN}✅{NC}" if grpc_ok else f"{YELLOW}⚠️{NC}"
        status_http = f"{GREEN}✅{NC}" if http_ok else f"{YELLOW}⚠️{NC}"
        
        print(f"{status_grpc} OTLP Collector (gRPC) porta 4317")
        print(f"{status_http} OTLP Collector (HTTP) porta 4318")
        
        # Verificar configuração
        config_path = BASE_DIR / "monitoring" / "otel-collector" / "config.yaml"
        if config_path.exists():
            print(f"{GREEN}✅{NC} Configuração do OTLP Collector encontrada")
        else:
            print(f"{YELLOW}⚠️{NC} Configuração do OTLP Collector não encontrada")
        
        self.results["monitoring"]["otlp_collector"] = {
            "grpc": grpc_ok,
            "http": http_ok,
            "config_exists": config_path.exists()
        }
    
    def validate_metrics(self):
        """5. Verificar Métricas TriSLA"""
        self.print_header("5️⃣  Verificando Métricas TriSLA")
        
        prometheus_ok = self.check_service("Prometheus", 9090)
        status = f"{GREEN}✅{NC}" if prometheus_ok else f"{YELLOW}⚠️{NC}"
        print(f"{status} Prometheus (porta 9090)")
        
        # Verificar configuração
        prom_config = BASE_DIR / "monitoring" / "prometheus" / "prometheus.yml"
        slo_rules = BASE_DIR / "monitoring" / "prometheus" / "rules" / "slo-rules.yml"
        
        if prom_config.exists():
            print(f"{GREEN}✅{NC} Configuração do Prometheus encontrada")
        else:
            print(f"{YELLOW}⚠️{NC} Configuração do Prometheus não encontrada")
        
        if slo_rules.exists():
            print(f"{GREEN}✅{NC} Regras SLO do Prometheus encontradas")
        else:
            print(f"{YELLOW}⚠️{NC} Regras SLO do Prometheus não encontradas")
        
        self.results["monitoring"]["prometheus"] = {
            "running": prometheus_ok,
            "config_exists": prom_config.exists(),
            "slo_rules_exists": slo_rules.exists()
        }
    
    def validate_traces(self):
        """6. Verificar Traces"""
        self.print_header("6️⃣  Verificando Traces")
        
        otlp_ok = self.check_service("OTLP Collector", 4317)
        if otlp_ok:
            print(f"{GREEN}✅{NC} OTLP Collector está disponível para receber traces")
        else:
            print(f"{YELLOW}⚠️{NC} OTLP Collector não está disponível")
            print("   Inicie o OTLP Collector para coletar traces")
        
        self.results["monitoring"]["traces"] = {
            "otlp_available": otlp_ok
        }
    
    def validate_slo_reports(self):
        """7. Verificar SLO Reports"""
        self.print_header("7️⃣  Verificando SLO Reports")
        
        generator_path = BASE_DIR / "monitoring" / "slo-reports" / "generator.py"
        
        if generator_path.exists():
            print(f"{GREEN}✅{NC} Gerador de SLO Reports encontrado")
            
            # Verificar se pode importar
            try:
                result = subprocess.run(
                    ["python3", "-c", "import sys; sys.path.insert(0, 'monitoring/slo-reports'); import generator"],
                    cwd=BASE_DIR,
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"{GREEN}✅{NC} Gerador de SLO Reports está funcional")
                else:
                    print(f"{YELLOW}⚠️{NC} Gerador de SLO Reports tem dependências faltando")
            except:
                print(f"{YELLOW}⚠️{NC} Não foi possível testar o gerador")
        else:
            print(f"{YELLOW}⚠️{NC} Gerador de SLO Reports não encontrado")
        
        self.results["slo_reports"]["generator_exists"] = generator_path.exists()
    
    def validate_slo_reporter_logs(self):
        """8. Verificar Logs do SLO Reporter"""
        self.print_header("8️⃣  Verificando Logs do SLO Reporter")
        
        slo_dir = BASE_DIR / "monitoring" / "slo-reports"
        
        if slo_dir.exists():
            generator = slo_dir / "generator.py"
            if generator.exists():
                print(f"{GREEN}✅{NC} Script do SLO Reporter encontrado")
                print(f"\n{BLUE}ℹ️{NC}  Para ver logs do SLO Reporter, execute:")
                print(f"   python3 {generator}")
            else:
                print(f"{YELLOW}⚠️{NC} Script do SLO Reporter não encontrado")
        else:
            print(f"{YELLOW}⚠️{NC} Diretório de SLO Reports não encontrado")
    
    def print_summary(self):
        """Imprime resumo da validação"""
        self.print_header("📋 Resumo da Validação")
        
        print("Para executar testes completos, certifique-se de que:")
        print("  1. Todos os módulos estão rodando (ou use Docker Compose)")
        print("  2. OTLP Collector está configurado e rodando")
        print("  3. Prometheus está configurado e rodando")
        print("  4. Kafka está disponível (para testes de interfaces I-03, I-04, I-05)")
        print()
        print("Para iniciar todos os serviços localmente:")
        print("  docker-compose up -d")
        print()
        print("Para executar testes automatizados:")
        print("  pytest tests/ -v")
        print()
        
        # Salvar resultados em JSON
        results_file = BASE_DIR / "validation-results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"{BLUE}ℹ️{NC}  Resultados salvos em: {results_file}")
    
    def run_all(self):
        """Executa todas as validações"""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║     TriSLA - Validação e Testes Locais                   ║")
        print("╚════════════════════════════════════════════════════════════╝")
        
        self.validate_health_modules()
        self.validate_health_endpoints()
        self.validate_interfaces()
        self.validate_otlp_collector()
        self.validate_metrics()
        self.validate_traces()
        self.validate_slo_reports()
        self.validate_slo_reporter_logs()
        self.print_summary()


def main():
    """Função principal"""
    validator = TriSLAValidator()
    validator.run_all()


if __name__ == "__main__":
    main()

