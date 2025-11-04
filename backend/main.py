"""
TriSLA Dashboard Backend v3.2.4
FastAPI application with Prometheus metrics endpoint
"""
from fastapi import FastAPI
from prometheus_client import make_asgi_app, Counter, Gauge, Histogram
import time

app = FastAPI(
    title="TriSLA Dashboard API",
    description="Backend API for TriSLA Dashboard monitoring",
    version="3.2.4"
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Custom metrics
request_count = Counter('trisla_requests_total', 'Total number of requests')
request_duration = Histogram('trisla_request_duration_seconds', 'Request duration in seconds')
active_connections = Gauge('trisla_active_connections', 'Number of active connections')

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TriSLA Dashboard Backend",
        "version": "3.2.4",
        "status": "running"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    request_count.inc()
    return {"status": "healthy", "service": "trisla-dashboard-backend"}

@app.get("/status")
async def status():
    """Status endpoint with metrics"""
    request_count.inc()
    return {
        "status": "operational",
        "version": "3.2.4",
        "metrics_endpoint": "/metrics"
    }

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Middleware to track request duration"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    request_duration.observe(process_time)
    response.headers["X-Process-Time"] = str(process_time)
    return response
