"""
Semantic Cache - SEM-CSMF
Sistema de cache para resultados de reasoning semântico
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


class SemanticCache:
    """Cache para resultados de reasoning semântico"""
    
    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000, enable_lru: bool = True):
        """
        Inicializa cache semântico
        
        Args:
            ttl_seconds: Time-to-live em segundos (padrão: 1 hora)
            max_size: Tamanho máximo do cache (padrão: 1000 entradas)
            enable_lru: Se True, usa estratégia LRU para eviction (padrão: True)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.enable_lru = enable_lru
        self.hits = 0
        self.misses = 0
        self.access_order: List[str] = []  # Para LRU
    
    def _generate_key(self, operation: str, params: Dict[str, Any]) -> str:
        """
        Gera chave única para operação e parâmetros
        
        Args:
            operation: Nome da operação (ex: "infer_slice_type", "validate_sla")
            params: Parâmetros da operação
            
        Returns:
            Chave hash MD5
        """
        # Normalizar parâmetros para garantir consistência
        normalized = {
            "op": operation,
            "params": json.dumps(params, sort_keys=True)
        }
        key_str = json.dumps(normalized, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, operation: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        Obtém resultado do cache
        
        Args:
            operation: Nome da operação
            params: Parâmetros da operação
            
        Returns:
            Resultado em cache ou None se não encontrado/expirado
        """
        with tracer.start_as_current_span("cache_get") as span:
            key = self._generate_key(operation, params)
            span.set_attribute("cache.key", key)
            span.set_attribute("cache.operation", operation)
            
            if key not in self.cache:
                self.misses += 1
                span.set_attribute("cache.hit", False)
                return None
            
            entry = self.cache[key]
            
            # Verificar se expirou
            if datetime.now() > entry["expires_at"]:
                del self.cache[key]
                self.misses += 1
                span.set_attribute("cache.hit", False)
                span.set_attribute("cache.expired", True)
                return None
            
            # Cache hit
            self.hits += 1
            span.set_attribute("cache.hit", True)
            span.set_attribute("cache.hits_total", self.hits)
            span.set_attribute("cache.misses_total", self.misses)
            
            # Atualizar ordem de acesso para LRU
            if self.enable_lru and key in self.access_order:
                self.access_order.remove(key)
                self.access_order.append(key)
            
            return entry["value"]
    
    def set(self, operation: str, params: Dict[str, Any], value: Any, ttl_override: Optional[int] = None):
        """
        Armazena resultado no cache
        
        Args:
            operation: Nome da operação
            params: Parâmetros da operação
            value: Valor a ser armazenado
            ttl_override: TTL customizado (opcional)
        """
        with tracer.start_as_current_span("cache_set") as span:
            key = self._generate_key(operation, params)
            span.set_attribute("cache.key", key)
            span.set_attribute("cache.operation", operation)
            
            # Limpar cache se exceder tamanho máximo
            if len(self.cache) >= self.max_size:
                if self.enable_lru:
                    self._evict_lru()
                else:
                    self._evict_oldest()
            
            ttl = ttl_override if ttl_override is not None else self.ttl_seconds
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self.cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.now(),
                "operation": operation
            }
            
            # Atualizar ordem de acesso para LRU
            if self.enable_lru:
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
            
            span.set_attribute("cache.size", len(self.cache))
    
    def _evict_oldest(self):
        """Remove entrada mais antiga do cache (FIFO)"""
        if not self.cache:
            return
        
        # Encontrar entrada mais antiga
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]["created_at"]
        )
        del self.cache[oldest_key]
        
        # Remover da ordem de acesso se LRU estiver habilitado
        if self.enable_lru and oldest_key in self.access_order:
            self.access_order.remove(oldest_key)
    
    def _evict_lru(self):
        """Remove entrada menos recentemente usada (LRU)"""
        if not self.cache or not self.access_order:
            # Fallback para FIFO se LRU não estiver disponível
            self._evict_oldest()
            return
        
        # Remover a entrada menos recentemente usada (primeira da lista)
        lru_key = self.access_order.pop(0)
        if lru_key in self.cache:
            del self.cache[lru_key]
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        self.access_order.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "ttl_seconds": self.ttl_seconds
        }
    
    def invalidate(self, operation: Optional[str] = None):
        """
        Invalida entradas do cache
        
        Args:
            operation: Operação específica para invalidar (None = todas)
        """
        if operation is None:
            self.clear()
        else:
            # Remover todas as entradas da operação
            keys_to_remove = [
                key for key, entry in self.cache.items()
                if entry["operation"] == operation
            ]
            for key in keys_to_remove:
                del self.cache[key]
                if self.enable_lru and key in self.access_order:
                    self.access_order.remove(key)

