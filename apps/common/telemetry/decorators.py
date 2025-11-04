#!/usr/bin/env python3
"""
TriSLA Telemetry Decorators
Decorators para instrumentação automática de funções e métodos
"""

import functools
import time
import logging
from typing import Any, Callable, Optional, Dict
from opentelemetry import trace, metrics, logs
from opentelemetry.trace import Status, StatusCode

# Configurar logging
logger = logging.getLogger(__name__)

def trace_function(
    operation_name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True
):
    """
    Decorator para instrumentar função com traces
    
    Args:
        operation_name: Nome da operação (padrão: nome da função)
        attributes: Atributos adicionais para o span
        record_exception: Se deve registrar exceções
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                try:
                    # Adicionar atributos
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    # Adicionar atributos dos argumentos
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Executar função
                    result = await func(*args, **kwargs)
                    
                    # Adicionar atributos do resultado
                    if hasattr(result, '__dict__'):
                        span.set_attribute("result.type", type(result).__name__)
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                try:
                    # Adicionar atributos
                    if attributes:
                        for key, value in attributes.items():
                            span.set_attribute(key, value)
                    
                    # Adicionar atributos dos argumentos
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)
                    
                    # Executar função
                    result = func(*args, **kwargs)
                    
                    # Adicionar atributos do resultado
                    if hasattr(result, '__dict__'):
                        span.set_attribute("result.type", type(result).__name__)
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        # Retornar wrapper apropriado
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def measure_time(
    metric_name: str,
    description: str = "",
    unit: str = "s",
    labels: Optional[Dict[str, str]] = None
):
    """
    Decorator para medir tempo de execução com métricas
    
    Args:
        metric_name: Nome da métrica
        description: Descrição da métrica
        unit: Unidade da métrica
        labels: Labels adicionais
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            meter = metrics.get_meter(__name__)
            histogram = meter.create_histogram(
                name=metric_name,
                description=description or f"Tempo de execução de {func.__name__}",
                unit=unit
            )
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                histogram.record(duration, labels or {})
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            meter = metrics.get_meter(__name__)
            histogram = meter.create_histogram(
                name=metric_name,
                description=description or f"Tempo de execução de {func.__name__}",
                unit=unit
            )
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                histogram.record(duration, labels or {})
        
        # Retornar wrapper apropriado
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def log_execution(
    level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False
):
    """
    Decorator para registrar execução de função com logs
    
    Args:
        level: Nível de log
        include_args: Se deve incluir argumentos no log
        include_result: Se deve incluir resultado no log
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = logs.get_logger(__name__)
            
            # Log de início
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
                "event": "function_start"
            }
            
            if include_args:
                log_data["args"] = str(args)
                log_data["kwargs"] = str(kwargs)
            
            logger.log(level, f"Executando {func.__name__}", extra=log_data)
            
            try:
                result = await func(*args, **kwargs)
                
                # Log de sucesso
                log_data["event"] = "function_success"
                if include_result:
                    log_data["result"] = str(result)
                
                logger.log(level, f"Concluído {func.__name__}", extra=log_data)
                return result
                
            except Exception as e:
                # Log de erro
                log_data["event"] = "function_error"
                log_data["error"] = str(e)
                
                logger.log(logging.ERROR, f"Erro em {func.__name__}: {e}", extra=log_data)
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = logs.get_logger(__name__)
            
            # Log de início
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
                "event": "function_start"
            }
            
            if include_args:
                log_data["args"] = str(args)
                log_data["kwargs"] = str(kwargs)
            
            logger.log(level, f"Executando {func.__name__}", extra=log_data)
            
            try:
                result = func(*args, **kwargs)
                
                # Log de sucesso
                log_data["event"] = "function_success"
                if include_result:
                    log_data["result"] = str(result)
                
                logger.log(level, f"Concluído {func.__name__}", extra=log_data)
                return result
                
            except Exception as e:
                # Log de erro
                log_data["event"] = "function_error"
                log_data["error"] = str(e)
                
                logger.log(logging.ERROR, f"Erro em {func.__name__}: {e}", extra=log_data)
                raise
        
        # Retornar wrapper apropriado
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def instrument_class(
    class_name: Optional[str] = None,
    methods: Optional[list] = None
):
    """
    Decorator para instrumentar classe inteira
    
    Args:
        class_name: Nome da classe para traces
        methods: Lista de métodos para instrumentar (padrão: todos os métodos públicos)
    """
    def decorator(cls):
        if methods is None:
            # Instrumentar todos os métodos públicos
            methods_to_instrument = [
                name for name, method in cls.__dict__.items()
                if callable(method) and not name.startswith('_')
            ]
        else:
            methods_to_instrument = methods
        
        for method_name in methods_to_instrument:
            if hasattr(cls, method_name):
                original_method = getattr(cls, method_name)
                
                # Aplicar decorators
                instrumented_method = trace_function(
                    operation_name=f"{class_name or cls.__name__}.{method_name}"
                )(original_method)
                
                setattr(cls, method_name, instrumented_method)
        
        return cls
    
    return decorator

# Decorator combinado para instrumentação completa
def full_instrumentation(
    operation_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    log_level: int = logging.INFO,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Decorator combinado para instrumentação completa (traces + métricas + logs)
    
    Args:
        operation_name: Nome da operação
        metric_name: Nome da métrica de tempo
        log_level: Nível de log
        attributes: Atributos adicionais
    """
    def decorator(func: Callable) -> Callable:
        # Aplicar todos os decorators
        instrumented_func = func
        
        # Trace
        instrumented_func = trace_function(
            operation_name=operation_name,
            attributes=attributes
        )(instrumented_func)
        
        # Métricas de tempo
        if metric_name:
            instrumented_func = measure_time(
                metric_name=metric_name,
                description=f"Tempo de execução de {func.__name__}"
            )(instrumented_func)
        
        # Logs
        instrumented_func = log_execution(
            level=log_level,
            include_args=True,
            include_result=True
        )(instrumented_func)
        
        return instrumented_func
    
    return decorator




