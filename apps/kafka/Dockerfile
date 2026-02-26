# ============================================
# TriSLA Kafka Image
# Version: v3.11.2
# Baseline: apache/kafka official
# ============================================

FROM apache/kafka:3.7.0

LABEL org.opencontainers.image.title="TriSLA Kafka"
LABEL org.opencontainers.image.description="Kafka broker for TriSLA NASP"
LABEL org.opencontainers.image.version="v3.11.2"
LABEL org.opencontainers.image.vendor="TriSLA Project"
LABEL org.opencontainers.image.source="NASP"

# Garantir timezone consistente
ENV TZ=UTC

# NÃO alteramos:
# - ENTRYPOINT
# - CMD
# - PORTS
# - CONFIG
# - VOLUMES
# - USER

# Apenas encapsulamos a imagem sob controle do projeto.
