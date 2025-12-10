from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from src.config import settings
from src.routers import sla

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
    yield
    # Shutdown
    logger.info("🛑 TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN Backend shutting down...")


app = FastAPI(
    title="TRISLA - GARANTIA DE SLA EM REDES 5G/O-RAN",
    description="API para gerenciamento de SLA em redes 5G/O-RAN",
    version="1.0.0",
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
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )

