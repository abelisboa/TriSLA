"""
Authentication & Authorization - SEM-CSMF
JWT-based authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Secret key (em produção, usar variável de ambiente)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "trisla-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera hash da senha"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica e decodifica token JWT"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency para autenticação (opcional - pode ser desabilitada em desenvolvimento)
def get_current_user_optional():
    """Dependency opcional para autenticação"""
    if is_auth_enabled():
        return Depends(verify_token)
    else:
        # Se autenticação desabilitada, retorna função que não requer token
        def no_auth_required():
            return None
        return Depends(no_auth_required)

def get_current_user(token: str = Depends(verify_token)):
    """Dependency para obter usuário autenticado"""
    return token


# Função para verificar se autenticação está habilitada
def is_auth_enabled() -> bool:
    """Verifica se autenticação está habilitada"""
    return os.getenv("ENABLE_AUTH", "false").lower() == "true"

