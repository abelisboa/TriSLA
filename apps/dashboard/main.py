#!/usr/bin/env python3
"""
TriSLA Dashboard - Interface Web Moderna
Dashboard completo para gerenciamento e monitoramento do TriSLA
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uvicorn

app = FastAPI(title="TriSLA Dashboard", version="1.0.0")

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurações
TRISLA_SERVICES = {
    "nwdaf": "http://nwdaf:8080",
    "decision_engine": "http://decision-engine:8080",
    "ml_nsmf": "http://ml-nsmf:8080",
    "sla_agents": "http://sla-agents:8080",
    "sem_nsmf": "http://sem-nsmf:8080",
    "bc_nssmf": "http://bc-nssmf:8080",
    "prometheus": "http://prometheus:9090",
    "grafana": "http://grafana:3000"
}

# Cache de dados
data_cache = {}
cache_ttl = 30  # segundos

class TrislaDashboard:
    """Classe principal do dashboard TriSLA"""
    
    def __init__(self):
        self.services = TRISLA_SERVICES
        self.cache = {}
        self.last_update = {}
    
    async def get_service_data(self, service_name: str, endpoint: str = "/api/v1/status") -> Dict[str, Any]:
        """Obter dados de um serviço específico"""
        try:
            service_url = self.services.get(service_name)
            if not service_url:
                return {"error": f"Serviço {service_name} não configurado"}
            
            # Verificar cache
            cache_key = f"{service_name}_{endpoint}"
            if cache_key in self.cache:
                last_update = self.last_update.get(cache_key, datetime.min)
                if datetime.now() - last_update < timedelta(seconds=cache_ttl):
                    return self.cache[cache_key]
            
            # Fazer requisição
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    self.cache[cache_key] = data
                    self.last_update[cache_key] = datetime.now()
                    return data
                else:
                    return {"error": f"Erro HTTP {response.status_code}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    async def get_all_services_status(self) -> Dict[str, Any]:
        """Obter status de todos os serviços"""
        status = {}
        tasks = []
        
        for service_name in self.services.keys():
            task = self.get_service_data(service_name)
            tasks.append((service_name, task))
        
        # Executar todas as requisições em paralelo
        for service_name, task in tasks:
            try:
                result = await task
                status[service_name] = result
            except Exception as e:
                status[service_name] = {"error": str(e)}
        
        return status
    
    async def get_nwdaf_analytics(self) -> Dict[str, Any]:
        """Obter análises do NWDAF"""
        return await self.get_service_data("nwdaf", "/api/v1/analytics")
    
    async def get_nwdaf_predictions(self) -> Dict[str, Any]:
        """Obter predições do NWDAF"""
        return await self.get_service_data("nwdaf", "/api/v1/predictions")
    
    async def get_nwdaf_anomalies(self) -> Dict[str, Any]:
        """Obter anomalias do NWDAF"""
        return await self.get_service_data("nwdaf", "/api/v1/anomalies")
    
    async def get_network_slices(self) -> Dict[str, Any]:
        """Obter slices de rede"""
        return await self.get_service_data("decision_engine", "/api/v1/slices")
    
    async def create_network_slice(self, slice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Criar novo slice de rede"""
        try:
            service_url = self.services["decision_engine"]
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{service_url}/api/v1/slices",
                    json=slice_data
                )
                if response.status_code == 201:
                    return response.json()
                else:
                    return {"error": f"Erro HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_prometheus_metrics(self, query: str) -> Dict[str, Any]:
        """Obter métricas do Prometheus"""
        try:
            service_url = self.services["prometheus"]
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{service_url}/api/v1/query",
                    params={"query": query}
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Erro HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

# Instância global do dashboard
dashboard = TrislaDashboard()

# Rotas da API
@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Página principal do dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "TriSLA Dashboard",
        "services": list(TRISLA_SERVICES.keys())
    })

@app.get("/api/status")
async def get_status():
    """API para obter status de todos os serviços"""
    status = await dashboard.get_all_services_status()
    return JSONResponse(content=status)

@app.get("/api/nwdaf/analytics")
async def get_nwdaf_analytics():
    """API para obter análises do NWDAF"""
    analytics = await dashboard.get_nwdaf_analytics()
    return JSONResponse(content=analytics)

@app.get("/api/nwdaf/predictions")
async def get_nwdaf_predictions():
    """API para obter predições do NWDAF"""
    predictions = await dashboard.get_nwdaf_predictions()
    return JSONResponse(content=predictions)

@app.get("/api/nwdaf/anomalies")
async def get_nwdaf_anomalies():
    """API para obter anomalias do NWDAF"""
    anomalies = await dashboard.get_nwdaf_anomalies()
    return JSONResponse(content=anomalies)

@app.get("/api/slices")
async def get_slices():
    """API para obter slices de rede"""
    slices = await dashboard.get_network_slices()
    return JSONResponse(content=slices)

@app.post("/api/slices")
async def create_slice(slice_data: Dict[str, Any]):
    """API para criar novo slice de rede"""
    result = await dashboard.create_network_slice(slice_data)
    return JSONResponse(content=result)

@app.get("/api/metrics")
async def get_metrics(query: str):
    """API para obter métricas do Prometheus"""
    metrics = await dashboard.get_prometheus_metrics(query)
    return JSONResponse(content=metrics)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Painel administrativo"""
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "title": "TriSLA Admin Panel"
    })

@app.get("/monitoring", response_class=HTMLResponse)
async def monitoring_panel(request: Request):
    """Painel de monitoramento"""
    return templates.TemplateResponse("monitoring.html", {
        "request": request,
        "title": "TriSLA Monitoring"
    })

@app.get("/slices", response_class=HTMLResponse)
async def slices_panel(request: Request):
    """Painel de gerenciamento de slices"""
    return templates.TemplateResponse("slices.html", {
        "request": request,
        "title": "TriSLA Slices Management"
    })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)




