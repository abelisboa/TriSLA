# TriSLA UERANSIM UE tools extension — minimal traffic utilities only.
# Base: frozen free5gc/ueransim digest from evidencias_ueransim_image_baseline_audit_20260605T194337Z
FROM docker.io/free5gc/ueransim@sha256:21fab7112edb449691545e27dd5781e7897e1dca2448726a27c22ac92c7ea059

USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    iperf3 \
    curl \
    wget \
    netcat-openbsd \
 && rm -rf /var/lib/apt/lists/* \
 && command -v iperf3 \
 && command -v curl \
 && command -v wget \
 && command -v nc
