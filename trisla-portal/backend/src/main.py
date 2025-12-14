from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio

from src.config import settings
from src.routers import sla
from src.services.nasp_health import check_all_nasp_modules, check_sem_csmf, check_bc_nssmf
from src.schemas.nasp_diagnostics import NASPDiagnosticsResponse, NASPModuleStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Telemetry disabled in local environment
logger.info("ℹ️  TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN - Telemetry disabled in local environment")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN Backend starting...")
    
    # Diagnóstico inicial leve: testar pelo menos SEM-CSMF e BC-NSSMF
    logger.info("🔍 Executando diagnóstico inicial de conectividade NASP...")
    try:
        sem_status, bc_status = await asyncio.gather(
            check_sem_csmf(),
            check_bc_nssmf(),
            return_exceptions=True
        )
        
        if isinstance(sem_status, Exception) or not sem_status.get("reachable", False):
            logger.warning(f"⚠️ SEM-CSMF não acessível no startup: {sem_status.get('detail', 'erro desconhecido') if not isinstance(sem_status, Exception) else str(sem_status)}")
        else:
            logger.info(f"✅ SEM-CSMF acessível (latência: {sem_status.get('latency_ms', 0):.2f}ms)")
        
        if isinstance(bc_status, Exception) or not bc_status.get("reachable", False):
            logger.warning(f"⚠️ BC-NSSMF não acessível no startup: {bc_status.get('detail', 'erro desconhecido') if not isinstance(bc_status, Exception) else str(bc_status)}")
        else:
            logger.info(f"✅ BC-NSSMF acessível (latência: {bc_status.get('latency_ms', 0):.2f}ms)")
    except Exception as e:
        logger.warning(f"⚠️ Erro ao executar diagnóstico inicial: {str(e)}")
    
    yield
    # Shutdown
    logger.info("🛑 TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN Backend shutting down...")


app = FastAPI(
    title="TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN",
    description="API para gerenciamento de SLA em redes 5G/O-RAN",
    version="3.7.21",
    lifespan=lifespan,
)

# CORS - Permitir todas as origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only essential SLA router
app.include_router(sla.router, prefix="/api/v1/sla", tags=["SLA"])


@app.get("/")
async def root():
    return {
        "name": "TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN",
        "version": "3.7.21",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check básico do Portal.
    Para diagnóstico detalhado do NASP, usar /nasp/diagnostics.
    """
    # Verificação leve: apenas indicar se o último diagnóstico foi bem-sucedido
    # Não fazer todos os testes aqui para não deixar o endpoint pesado
    return {
        "status": "healthy",
        "version": "3.7.21",
        "nasp_reachable": None,  # Será preenchido pelo diagnóstico se necessário
        "nasp_details_url": "/nasp/diagnostics"
    }


@app.get("/api/v1/health", tags=["health"])
async def health_v1():
    """
    Alias para /health - retrocompatibilidade com frontend que espera /api/v1/health
    """
    return await health_check()


@app.get("/nasp/diagnostics", response_model=NASPDiagnosticsResponse)
async def nasp_diagnostics():
    """
    Retorna o estado de conectividade entre o Portal e todos os módulos NASP.
    
    Verifica:
    - SEM-CSMF (localhost:8080)
    - ML-NSMF (localhost:8081)
    - Decision Engine (localhost:8082)
    - BC-NSSMF (localhost:8083)
    - SLA-Agent Layer (localhost:8084)
    
    Retorna latência, status de conexão e detalhes de erro (se houver).
    """
    diagnostics = await check_all_nasp_modules()
    
    return NASPDiagnosticsResponse(
        sem_csmf=NASPModuleStatus(**diagnostics["sem_csmf"]),
        ml_nsmf=NASPModuleStatus(**diagnostics["ml_nsmf"]),
        decision=NASPModuleStatus(**diagnostics["decision"]),
        bc_nssmf=NASPModuleStatus(**diagnostics["bc_nssmf"]),
        sla_agent=NASPModuleStatus(**diagnostics["sla_agent"])
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )

