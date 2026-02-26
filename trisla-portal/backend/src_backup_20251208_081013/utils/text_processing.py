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


def inferir_tipo_slice(texto: str) -> str:
    """
    Infere tipo de slice a partir do texto de intenção
    Conforme Capítulo 5 - SEM-CSMF
    
    Exemplos:
    - "cirurgia remota" → URLLC
    - "streaming 4K em estádio lotado" → eMBB
    - "milhares de sensores IoT" → mMTC
    
    Args:
        texto: Texto da intenção
        
    Returns:
        Tipo de slice inferido: "URLLC", "eMBB", "mMTC" ou "AUTO"
    """
    texto_lower = texto.lower()
    
    # Palavras-chave para URLLC
    urllc_keywords = ['cirurgia', 'remota', 'cirurgia remota', 'baixa latência', 'ultra confiável', 
                      'urllc', 'ultra-reliable', 'low latency', 'crítico', 'tempo real']
    
    # Palavras-chave para eMBB
    embb_keywords = ['streaming', '4k', 'vídeo', 'estádio', 'lota', 'banda larga', 
                     'embb', 'enhanced mobile', 'broadband', 'alta velocidade']
    
    # Palavras-chave para mMTC
    mmtc_keywords = ['sensores', 'iot', 'milhares', 'dispositivos', 'densidade', 
                     'mmtc', 'massive machine', 'machine type', 'máquinas']
    
    # Contar ocorrências
    urllc_count = sum(1 for kw in urllc_keywords if kw in texto_lower)
    embb_count = sum(1 for kw in embb_keywords if kw in texto_lower)
    mmtc_count = sum(1 for kw in mmtc_keywords if kw in texto_lower)
    
    # Retornar tipo com maior score
    if urllc_count > embb_count and urllc_count > mmtc_count:
        return "URLLC"
    elif embb_count > mmtc_count:
        return "eMBB"
    elif mmtc_count > 0:
        return "mMTC"
    else:
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
