"""
Utilitários para processamento de texto e correção de erros ortográficos
Conforme Capítulo 5 - SEM-CSMF (PNL)
"""
import re
from typing import Dict, Any


# Dicionário de correções comuns
CORRECOES_ORTOGRAFICAS: Dict[str, str] = {
    'cirugia': 'cirurgia',
    'vidiu': 'vídeo',
    '4k': '4K',
    'urllc': 'URLLC',
    'embb': 'eMBB',
    'mmtc': 'mMTC',
    'latencia': 'latência',
    'confiabilidade': 'confiabilidade',
    'disponibilidade': 'disponibilidade',
    'throughput': 'throughput',
    'jitter': 'jitter',
    'packet loss': 'packet loss',
}


def corrigir_erros_ortograficos(texto: str) -> str:
    """
    Corrige erros leves de ortografia no texto de intenção
    
    Exemplos:
    - "cirugia remota" → "cirurgia remota"
    - "vidiu 4k" → "vídeo 4K"
    
    Args:
        texto: Texto original com possíveis erros
        
    Returns:
        Texto corrigido
    """
    texto_corrigido = texto
    
    # Aplicar correções do dicionário (case-insensitive)
    for erro, correcao in CORRECOES_ORTOGRAFICAS.items():
        # Usar regex para substituir palavra inteira (case-insensitive)
        pattern = re.compile(r'\b' + re.escape(erro) + r'\b', re.IGNORECASE)
        texto_corrigido = pattern.sub(correcao, texto_corrigido)
    
    return texto_corrigido.strip()


def infer_service_type_from_intent(intent: str) -> str:
    """
    Inferência semântica determinística ANTES do SEM-CSMF
    Conforme Capítulo 5 - SEM-CSMF (inferência semântica inicial)
    
    Esta função é determinística e rastreável, não é IA inventada.
    É inferência semântica baseada em palavras-chave, como descrito na dissertação.
    
    Exemplos:
    - "cirurgia remota" → URLLC
    - "streaming 4K em estádio lotado" → eMBB
    - "milhares de sensores IoT" → mMTC
    
    Args:
        intent: Texto da intenção em linguagem natural
        
    Returns:
        Tipo de slice inferido: "URLLC", "eMBB" ou "mMTC"
        
    Raises:
        ValueError: Se não foi possível inferir o tipo de slice
    """
    intent_lower = intent.lower()
    
    # Palavras-chave para URLLC (prioridade alta)
    urllc_keywords = [
        'cirurgia', 'remota', 'cirurgia remota', 'surgery', 'remote surgery',
        'baixa latência', 'low latency', 'ultra confiável', 'ultra-reliable',
        'urllc', 'crítico', 'tempo real', 'real-time', 'critical',
        'latência', 'latency', 'confiabilidade', 'reliability'
    ]
    
    # Palavras-chave para eMBB
    embb_keywords = [
        'streaming', '4k', 'vídeo', 'video', 'estádio', 'stadium', 'lota', 'crowd',
        'banda larga', 'broadband', 'embb', 'enhanced mobile', 'alta velocidade',
        'high speed', 'download', 'upload', 'throughput'
    ]
    
    # Palavras-chave para mMTC
    mmtc_keywords = [
        'sensores', 'sensors', 'iot', 'internet das coisas', 'milhares', 'thousands',
        'dispositivos', 'devices', 'densidade', 'density', 'mmtc', 'massive machine',
        'machine type', 'máquinas', 'machines', 'sensor network'
    ]
    
    # Contar ocorrências
    urllc_count = sum(1 for kw in urllc_keywords if kw in intent_lower)
    embb_count = sum(1 for kw in embb_keywords if kw in intent_lower)
    mmtc_count = sum(1 for kw in mmtc_keywords if kw in intent_lower)
    
    # Retornar tipo com maior score (determinístico)
    if urllc_count > embb_count and urllc_count > mmtc_count:
        return "URLLC"
    elif embb_count > mmtc_count:
        return "eMBB"
    elif mmtc_count > 0:
        return "mMTC"
    else:
        # Se não conseguiu inferir, levantar erro (não retornar "AUTO")
        raise ValueError(f"Não foi possível inferir o tipo de slice a partir do intent: '{intent[:50]}...'")


def inferir_tipo_slice(texto: str) -> str:
    """
    Alias para infer_service_type_from_intent (compatibilidade)
    Retorna "AUTO" se não conseguir inferir (comportamento legado)
    """
    try:
        return infer_service_type_from_intent(texto)
    except ValueError:
        return "AUTO"


def extrair_parametros_tecnicos(texto: str) -> Dict[str, Any]:
    """
    Extrai parâmetros técnicos do texto de intenção
    Usa regex para encontrar valores numéricos com unidades
    
    Args:
        texto: Texto da intenção
        
    Returns:
        Dicionário com parâmetros extraídos
    """
    parametros: Dict[str, Any] = {}
    
    # Extrair latência (ex: "5ms", "10 ms", "latência de 5")
    latency_match = re.search(r'lat[êe]ncia.*?(\d+(?:\.\d+)?)\s*ms?', texto, re.IGNORECASE)
    if latency_match:
        parametros['latency'] = float(latency_match.group(1))
    
    # Extrair confiabilidade (ex: "99.999%", "99,999%")
    reliability_match = re.search(r'confiabilidade.*?(\d+(?:[.,]\d+)?)\s*%', texto, re.IGNORECASE)
    if reliability_match:
        valor = reliability_match.group(1).replace(',', '.')
        parametros['reliability'] = float(valor)
    
    # Extrair disponibilidade
    availability_match = re.search(r'disponibilidade.*?(\d+(?:[.,]\d+)?)\s*%', texto, re.IGNORECASE)
    if availability_match:
        valor = availability_match.group(1).replace(',', '.')
        parametros['availability'] = float(valor)
    
    # Extrair throughput
    throughput_match = re.search(r'throughput.*?(\d+(?:\.\d+)?)\s*(?:mbps|mb/s)', texto, re.IGNORECASE)
    if throughput_match:
        parametros['throughput'] = float(throughput_match.group(1))
    
    return parametros

