"""
Security Middleware - SEM-CSMF
Rate limiting e outras medidas de segurança
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict
from typing import Dict, Tuple
import os

# Rate limiting configuration
RATE_LIMIT_ENABLED = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Rate limit storage (em produção, usar Redis)
rate_limit_storage: Dict[str, list] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting"""
    
    async def dispatch(self, request: Request, call_next):
        if not RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Obter IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Verificar rate limit
        current_time = time.time()
        window_start = current_time - RATE_LIMIT_WINDOW
        
        # Limpar requisições antigas
        rate_limit_storage[client_ip] = [
            req_time for req_time in rate_limit_storage[client_ip]
            if req_time > window_start
        ]
        
        # Verificar se excedeu o limite
        if len(rate_limit_storage[client_ip]) >= RATE_LIMIT_REQUESTS:
            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(RATE_LIMIT_REQUESTS),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(window_start + RATE_LIMIT_WINDOW))
                }
            )
        
        # Adicionar requisição atual
        rate_limit_storage[client_ip].append(current_time)
        
        # Continuar com a requisição
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        remaining = RATE_LIMIT_REQUESTS - len(rate_limit_storage[client_ip])
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(window_start + RATE_LIMIT_WINDOW))
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

