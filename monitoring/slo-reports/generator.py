"""
SLO Reports Generator
Gera relatórios de SLO automaticamente
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
from prometheus_client import PrometheusConnect

class SLOReportGenerator:
    """Gera relatórios de SLO"""
    
    def __init__(self, prometheus_url: str = "http://prometheus:9090"):
        self.prom = PrometheusConnect(url=prometheus_url)
    
    def generate_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Gera relatório de SLO para período"""
        report = {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "slos": []
        }
        
        # Calcular SLOs
        slos = [
            self._calculate_latency_slo(start_time, end_time),
            self._calculate_throughput_slo(start_time, end_time),
            self._calculate_reliability_slo(start_time, end_time)
        ]
        
        report["slos"] = slos
        report["overall_compliance"] = self._calculate_overall_compliance(slos)
        
        return report
    
    def _calculate_latency_slo(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Calcula SLO de latência"""
        query = f"""
        histogram_quantile(0.99,
          rate(http_request_duration_seconds_bucket[{int((end - start).total_seconds())}s])
        )
        """
        
        result = self.prom.custom_query(query)
        p99_latency = float(result[0]['value'][1]) if result else 0.0
        
        target = 0.1  # 100ms
        compliance = (target - p99_latency) / target * 100 if p99_latency < target else 0
        
        return {
            "name": "Latency SLO",
            "target": f"{target * 1000}ms",
            "actual": f"{p99_latency * 1000}ms",
            "compliance": max(0, compliance),
            "status": "compliant" if p99_latency < target else "violated"
        }
    
    def _calculate_throughput_slo(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Calcula SLO de throughput"""
        query = f"""
        rate(http_requests_total[{int((end - start).total_seconds())}s])
        """
        
        result = self.prom.custom_query(query)
        throughput = float(result[0]['value'][1]) if result else 0.0
        
        target = 100.0  # req/s
        compliance = (throughput / target) * 100 if throughput < target else 100
        
        return {
            "name": "Throughput SLO",
            "target": f"{target} req/s",
            "actual": f"{throughput:.2f} req/s",
            "compliance": min(100, compliance),
            "status": "compliant" if throughput >= target else "violated"
        }
    
    def _calculate_reliability_slo(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Calcula SLO de confiabilidade"""
        query = f"""
        (rate(http_requests_total{{status=~"5.."}}[{int((end - start).total_seconds())}s]) /
         rate(http_requests_total[{int((end - start).total_seconds())}s])) * 100
        """
        
        result = self.prom.custom_query(query)
        error_rate = float(result[0]['value'][1]) if result else 0.0
        
        target = 1.0  # 1% max error rate
        compliance = max(0, (target - error_rate) / target * 100) if error_rate < target else 0
        
        return {
            "name": "Reliability SLO",
            "target": f"{target}% max error rate",
            "actual": f"{error_rate:.2f}%",
            "compliance": max(0, compliance),
            "status": "compliant" if error_rate < target else "violated"
        }
    
    def _calculate_overall_compliance(self, slos: List[Dict[str, Any]]) -> float:
        """Calcula compliance geral"""
        if not slos:
            return 0.0
        
        total_compliance = sum(slo.get("compliance", 0) for slo in slos)
        return total_compliance / len(slos)
    
    def export_report(self, report: Dict[str, Any], format: str = "json") -> str:
        """Exporta relatório"""
        if format == "json":
            return json.dumps(report, indent=2)
        elif format == "html":
            return self._generate_html(report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html(self, report: Dict[str, Any]) -> str:
        """Gera HTML do relatório"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SLO Report - {report['period']['start']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                .compliant {{ color: green; }}
                .violated {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>SLO Report</h1>
            <p>Period: {report['period']['start']} to {report['period']['end']}</p>
            <p>Overall Compliance: {report['overall_compliance']:.2f}%</p>
            <table>
                <tr>
                    <th>SLO</th>
                    <th>Target</th>
                    <th>Actual</th>
                    <th>Compliance</th>
                    <th>Status</th>
                </tr>
        """
        
        for slo in report['slos']:
            status_class = 'compliant' if slo['status'] == 'compliant' else 'violated'
            html += f"""
                <tr>
                    <td>{slo['name']}</td>
                    <td>{slo['target']}</td>
                    <td>{slo['actual']}</td>
                    <td>{slo['compliance']:.2f}%</td>
                    <td class="{status_class}">{slo['status']}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html

