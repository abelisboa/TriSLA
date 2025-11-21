"""
Database Configuration - SEM-CSMF
SQLAlchemy setup com suporte a SQLite (dev) e PostgreSQL (prod)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./trisla_sem_csmf.db"  # SQLite para desenvolvimento
)

# Para PostgreSQL em produção:
# DATABASE_URL = "postgresql://user:password@localhost/trisla_sem_csmf"

# Criar engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # SQLite específico
        echo=False  # Set True para debug SQL
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexão antes de usar
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class para modelos
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa o banco de dados (cria tabelas)"""
    Base.metadata.create_all(bind=engine)
