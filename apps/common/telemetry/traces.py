#!/usr/bin/env python3
"""
TriSLA Trace Context
Gerenciamento de contexto de traces para correlação entre módulos
"""

import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from opentelemetry import trace
from opentelemetry.trace import Span, Status, StatusCode
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# Configurar logging
import logging
logger = logging.getLogger(__name__)

@dataclass
class SpanContext:
    """Contexto de span para correlação"""
    trace_id: str
    span_id: str
    trace_flags: int = 1
    trace_state: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Converter para dicionário"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "trace_flags": str(self.trace_flags),
            "trace_state": self.trace_state or ""
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'SpanContext':
        """Criar a partir de dicionário"""
        return cls(
            trace_id=data["trace_id"],
            span_id=data["span_id"],
            trace_flags=int(data.get("trace_flags", 1)),
            trace_state=data.get("trace_state")
        )

@dataclass
class TraceContext:
    """Contexto de trace para correlação entre módulos"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    module_name: str = ""
    attributes: Dict[str, Any] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.start_time is None:
            self.start_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "module_name": self.module_name,
            "attributes": self.attributes,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TraceContext':
        """Criar a partir de dicionário"""
        return cls(
            trace_id=data["trace_id"],
            span_id=data["span_id"],
            parent_span_id=data.get("parent_span_id"),
            operation_name=data.get("operation_name", ""),
            module_name=data.get("module_name", ""),
            attributes=data.get("attributes", {}),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None,
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            status=data.get("status", "pending"),
            error_message=data.get("error_message")
        )

class TraceManager:
    """Gerenciador de traces para correlação entre módulos"""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.tracer = trace.get_tracer(module_name)
        self.active_spans: Dict[str, Span] = {}
        self.trace_contexts: Dict[str, TraceContext] = {}
    
    def start_span(
        self,
        operation_name: str,
        parent_context: Optional[TraceContext] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> TraceContext:
        """Iniciar novo span"""
        try:
            # Gerar IDs únicos
            trace_id = str(uuid.uuid4())
            span_id = str(uuid.uuid4())
            
            # Criar contexto de trace
            trace_context = TraceContext(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_context.span_id if parent_context else None,
                operation_name=operation_name,
                module_name=self.module_name,
                attributes=attributes or {}
            )
            
            # Iniciar span OpenTelemetry
            span = self.tracer.start_span(
                operation_name,
                context=parent_context.to_span_context() if parent_context else None
            )
            
            # Adicionar atributos
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            # Armazenar span ativo
            self.active_spans[span_id] = span
            self.trace_contexts[span_id] = trace_context
            
            logger.debug(f"Span iniciado: {operation_name} ({span_id})")
            return trace_context
            
        except Exception as e:
            logger.error(f"Erro ao iniciar span: {str(e)}")
            raise
    
    def end_span(
        self,
        trace_context: TraceContext,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> None:
        """Finalizar span"""
        try:
            span_id = trace_context.span_id
            
            if span_id in self.active_spans:
                span = self.active_spans[span_id]
                
                # Definir status
                if status == "success":
                    span.set_status(Status(StatusCode.OK))
                else:
                    span.set_status(Status(StatusCode.ERROR, error_message or "Unknown error"))
                
                # Finalizar span
                span.end()
                
                # Atualizar contexto
                trace_context.end_time = datetime.now()
                trace_context.status = status
                trace_context.error_message = error_message
                
                # Remover span ativo
                del self.active_spans[span_id]
                
                logger.debug(f"Span finalizado: {trace_context.operation_name} ({span_id})")
            else:
                logger.warning(f"Span não encontrado: {span_id}")
                
        except Exception as e:
            logger.error(f"Erro ao finalizar span: {str(e)}")
            raise
    
    def add_event(
        self,
        trace_context: TraceContext,
        event_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Adicionar evento ao span"""
        try:
            span_id = trace_context.span_id
            
            if span_id in self.active_spans:
                span = self.active_spans[span_id]
                span.add_event(event_name, attributes or {})
                logger.debug(f"Evento adicionado: {event_name} ao span {span_id}")
            else:
                logger.warning(f"Span não encontrado para evento: {span_id}")
                
        except Exception as e:
            logger.error(f"Erro ao adicionar evento: {str(e)}")
    
    def add_attribute(
        self,
        trace_context: TraceContext,
        key: str,
        value: Any
    ) -> None:
        """Adicionar atributo ao span"""
        try:
            span_id = trace_context.span_id
            
            if span_id in self.active_spans:
                span = self.active_spans[span_id]
                span.set_attribute(key, value)
                trace_context.attributes[key] = value
                logger.debug(f"Atributo adicionado: {key}={value} ao span {span_id}")
            else:
                logger.warning(f"Span não encontrado para atributo: {span_id}")
                
        except Exception as e:
            logger.error(f"Erro ao adicionar atributo: {str(e)}")
    
    def get_active_spans(self) -> List[TraceContext]:
        """Obter spans ativos"""
        return list(self.trace_contexts.values())
    
    def get_span_by_id(self, span_id: str) -> Optional[TraceContext]:
        """Obter span por ID"""
        return self.trace_contexts.get(span_id)
    
    def clear_completed_spans(self) -> None:
        """Limpar spans completados"""
        completed_span_ids = [
            span_id for span_id, context in self.trace_contexts.items()
            if context.status in ["success", "error"] and span_id not in self.active_spans
        ]
        
        for span_id in completed_span_ids:
            del self.trace_contexts[span_id]
        
        logger.debug(f"Limpos {len(completed_span_ids)} spans completados")

class TracePropagator:
    """Propagador de contexto de trace entre módulos"""
    
    def __init__(self):
        self.propagator = TraceContextTextMapPropagator()
    
    def inject_context(self, trace_context: TraceContext, carrier: Dict[str, str]) -> None:
        """Injetar contexto de trace em carrier"""
        try:
            # Criar contexto OpenTelemetry
            span_context = trace.set_span_in_context(
                trace.get_current_span()
            )
            
            # Injetar contexto
            self.propagator.inject(carrier, context=span_context)
            
            logger.debug(f"Contexto injetado: {trace_context.trace_id}")
            
        except Exception as e:
            logger.error(f"Erro ao injetar contexto: {str(e)}")
            raise
    
    def extract_context(self, carrier: Dict[str, str]) -> Optional[TraceContext]:
        """Extrair contexto de trace de carrier"""
        try:
            # Extrair contexto
            context = self.propagator.extract(carrier)
            
            # Obter span atual
            span = trace.get_current_span(context)
            
            if span and span.is_recording():
                # Criar contexto de trace
                trace_context = TraceContext(
                    trace_id=format(span.get_span_context().trace_id, '032x'),
                    span_id=format(span.get_span_context().span_id, '016x'),
                    operation_name=span.name,
                    module_name=self.module_name
                )
                
                logger.debug(f"Contexto extraído: {trace_context.trace_id}")
                return trace_context
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair contexto: {str(e)}")
            return None

# Função para criar trace manager
def create_trace_manager(module_name: str) -> TraceManager:
    """Criar gerenciador de traces para módulo"""
    return TraceManager(module_name)

# Função para criar propagador
def create_trace_propagator() -> TracePropagator:
    """Criar propagador de contexto de trace"""
    return TracePropagator()
