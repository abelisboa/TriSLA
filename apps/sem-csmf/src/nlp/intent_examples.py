"""
Intent Examples Dataset - SEM-CSMF
Conjunto expandido de exemplos de intents para treinamento e validação do NLP parser
"""

# Exemplos de intents em linguagem natural para diferentes tipos de slice

URLLC_EXAMPLES = [
    "Preciso de uma rede com latência máxima de 5ms para cirurgia remota",
    "Criar slice URLLC com latência de 1ms e confiabilidade de 99.999%",
    "Slice para aplicação crítica com latência ultra-baixa de 10ms",
    "Rede para telemedicina com latência máxima de 3ms",
    "Slice URLLC para controle industrial com latência de 2ms",
    "Necessito de uma rede ultra confiável com latência abaixo de 5ms",
    "Criar network slice para aplicação de segurança pública com latência de 1ms",
    "Slice para veículos autônomos com latência máxima de 10ms e alta confiabilidade",
    "Rede para automação industrial com latência de 1ms e confiabilidade de 99.99%",
    "Slice URLLC para controle de drones com latência máxima de 5ms",
    "Network slice para aplicação de realidade aumentada industrial com latência de 2ms",
    "Criar slice para sistema de controle de tráfego com latência de 1ms",
    "Rede para monitoramento crítico com latência abaixo de 10ms e alta confiabilidade",
    "Slice URLLC para aplicação de segurança com latência de 3ms",
    "Network slice para sistema de emergência com latência máxima de 5ms",
    "Criar slice para aplicação de controle remoto com latência de 1ms",
]

EMBB_EXAMPLES = [
    "Criar slice eMBB com throughput mínimo de 1Gbps para streaming de vídeo",
    "Preciso de uma rede com largura de banda de 500Mbps para aplicações de realidade aumentada",
    "Slice para transmissão de vídeo 4K com throughput de 2Gbps",
    "Rede para aplicações de banda larga móvel com throughput mínimo de 1Gbps",
    "Criar slice eMBB com latência de 50ms e throughput de 1Gbps",
    "Slice para streaming de conteúdo com largura de banda de 500Mbps",
    "Rede para aplicações de vídeo com throughput mínimo de 1Gbps",
    "Slice eMBB para usuários móveis com alta taxa de transmissão de dados",
    "Network slice para transmissão de vídeo 8K com throughput de 4Gbps",
    "Criar slice eMBB para aplicações de realidade virtual com largura de banda de 1Gbps",
    "Slice para streaming de jogos em nuvem com throughput mínimo de 500Mbps",
    "Rede para aplicações de vídeo conferência com largura de banda de 100Mbps",
    "Slice eMBB para download de conteúdo com throughput de 2Gbps",
    "Network slice para aplicações de mídia social com throughput de 500Mbps",
    "Criar slice para transmissão de eventos ao vivo com largura de banda de 1Gbps",
    "Slice eMBB para aplicações de educação online com throughput de 100Mbps",
]

MMTC_EXAMPLES = [
    "Criar slice mMTC para IoT massivo com densidade de 1 milhão de dispositivos por km²",
    "Slice para sensores IoT com baixa taxa de dados de 0.1Mbps",
    "Rede para internet das coisas com densidade alta de dispositivos",
    "Slice mMTC para sensores industriais com throughput de 0.1Mbps",
    "Criar slice para aplicações IoT massivas com latência tolerável de 1000ms",
    "Slice para dispositivos IoT com baixa largura de banda e alta densidade",
    "Rede para sensores com throughput mínimo de 0.1Mbps",
    "Slice mMTC para monitoramento ambiental com muitos dispositivos",
    "Network slice para sensores de agricultura com densidade de 100 mil dispositivos por km²",
    "Criar slice mMTC para smart cities com milhões de sensores",
    "Slice para dispositivos wearables com throughput de 0.01Mbps",
    "Rede para sensores de saúde com baixa taxa de dados e alta densidade",
    "Slice mMTC para monitoramento de infraestrutura com muitos dispositivos",
    "Network slice para sensores de segurança com throughput de 0.1Mbps",
    "Criar slice para aplicações de logística IoT com latência de 1000ms",
    "Slice mMTC para sensores de energia com densidade alta de dispositivos",
]

MIXED_EXAMPLES = [
    "Preciso de uma rede com latência de 20ms e throughput de 500Mbps para realidade aumentada",
    "Criar slice com latência de 15ms, throughput de 200Mbps e confiabilidade de 99.9%",
    "Slice para aplicação mista com latência de 30ms e throughput de 300Mbps",
    "Rede com requisitos de latência de 25ms e largura de banda de 400Mbps",
]

# Padrões de extração para melhorar o parser
LATENCY_PATTERNS = [
    r'lat[êe]ncia\s*(?:m[áa]xima|max|maximum)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*ms',
    r'latency\s*(?:max|maximum)?\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*ms',
    r'(\d+(?:\.\d+)?)\s*ms\s*(?:de\s*)?lat[êe]ncia',
    r'(\d+(?:\.\d+)?)\s*ms\s*(?:of\s*)?latency',
    r'lat[êe]ncia\s*(?:abaixo|below|under)\s*de\s*(\d+(?:\.\d+)?)\s*ms',
    r'latency\s*(?:below|under)\s*(\d+(?:\.\d+)?)\s*ms',
    r'ultra\s*baixa\s*lat[êe]ncia\s*de\s*(\d+(?:\.\d+)?)\s*ms',
    r'ultra\s*low\s*latency\s*of\s*(\d+(?:\.\d+)?)\s*ms',
]

THROUGHPUT_PATTERNS = [
    r'throughput\s*(?:m[íi]nimo|min|minimum)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
    r'(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)\s*(?:de\s*)?throughput',
    r'largura\s*de\s*banda\s*(?:m[íi]nima|min)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
    r'bandwidth\s*(?:min|minimum)?\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
    r'taxa\s*(?:m[íi]nima|min)?\s*(?:de\s*)?transmiss[ãa]o\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
    r'data\s*rate\s*(?:min|minimum)?\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
]

RELIABILITY_PATTERNS = [
    r'confiabilidade\s*(?:de|of)?\s*(\d+(?:\.\d+)?)%',
    r'reliability\s*(?:of)?\s*(\d+(?:\.\d+)?)%',
    r'(\d+(?:\.\d+)?)%\s*(?:de\s*)?confiabilidade',
    r'(\d+(?:\.\d+)?)%\s*(?:of\s*)?reliability',
    r'alta\s*confiabilidade\s*de\s*(\d+(?:\.\d+)?)%',
    r'high\s*reliability\s*of\s*(\d+(?:\.\d+)?)%',
    r'ultra\s*confi[áa]vel\s*com\s*(\d+(?:\.\d+)?)%',
    r'ultra\s*reliable\s*with\s*(\d+(?:\.\d+)?)%',
]

# Palavras-chave para inferência de tipo de slice
URLLC_KEYWORDS = [
    "urllc", "ultra reliable", "low latency", "ultra confiável", "baixa latência",
    "surgery", "cirurgia", "crítica", "critical", "telemedicina", "telemedicine",
    "controle industrial", "industrial control", "segurança pública", "public safety",
    "veículos autônomos", "autonomous vehicles", "aplicação crítica", "critical application"
]

EMBB_KEYWORDS = [
    "embb", "enhanced mobile broadband", "broadband", "banda larga", "video", "streaming",
    "realidade aumentada", "augmented reality", "realidade virtual", "virtual reality",
    "4k", "8k", "high definition", "alta definição", "transmissão de vídeo", "video transmission",
    "bandwidth", "largura de banda", "throughput", "taxa de transmissão"
]

MMTC_KEYWORDS = [
    "mmtc", "massive", "iot", "internet das coisas", "sensores", "sensors",
    "dispositivos", "devices", "monitoramento", "monitoring", "ambiental", "environmental",
    "industrial", "densidade", "density", "muitos dispositivos", "many devices",
    "sensores industriais", "industrial sensors", "massive iot", "iot massivo"
]

# Função auxiliar para obter todos os exemplos
def get_all_examples():
    """Retorna todos os exemplos de intents"""
    return {
        "URLLC": URLLC_EXAMPLES,
        "eMBB": EMBB_EXAMPLES,
        "mMTC": MMTC_EXAMPLES,
        "MIXED": MIXED_EXAMPLES
    }

# Função auxiliar para obter padrões de extração
def get_extraction_patterns():
    """Retorna todos os padrões de extração"""
    return {
        "latency": LATENCY_PATTERNS,
        "throughput": THROUGHPUT_PATTERNS,
        "reliability": RELIABILITY_PATTERNS
    }

# Função auxiliar para obter palavras-chave
def get_keywords():
    """Retorna todas as palavras-chave por tipo de slice"""
    return {
        "URLLC": URLLC_KEYWORDS,
        "eMBB": EMBB_KEYWORDS,
        "mMTC": MMTC_KEYWORDS
    }

