#!/usr/bin/env bash
set -euo pipefail

# ===============================================
# TRISLA_GHCR_MIRROR — Espelhamento determinístico
# - Varre imagens em uso no namespace trisla
# - Impõe tag explícita (sem :latest, sem "sem tag")
# - Faz mirror para ghcr.io/abelisboa/mirror-*
# - Corrige:
#   (1) Repositório destino sem ":" (registry:port vira registry-port)
#   (2) Auth rootless (prioriza docker/podman; skopeo usa --authfile)
# ===============================================

TS="$(date -u +%Y%m%dT%H%M%SZ)"
NS="${NS:-trisla}"
GHCR_ORG="${GHCR_ORG:-ghcr.io/abelisboa}"
OUT_DIR="${OUT_DIR:-./evidencias_mirror_${TS}}"

mkdir -p "${OUT_DIR}"

echo "=================================================="
echo "TRISLA_GHCR_MIRROR — Espelhamento determinístico"
echo "Timestamp: ${TS}"
echo "Namespace: ${NS}"
echo "GHCR_ORG : ${GHCR_ORG}"
echo "Output   : ${OUT_DIR}"
echo "=================================================="
echo

# --- ferramentas ---
HAS_SKOPEO=0; command -v skopeo >/dev/null 2>&1 && HAS_SKOPEO=1
HAS_CRANE=0; command -v crane  >/dev/null 2>&1 && HAS_CRANE=1
HAS_DOCKER=0; command -v docker >/dev/null 2>&1 && HAS_DOCKER=1

if [[ $HAS_SKOPEO -eq 0 && $HAS_CRANE -eq 0 && $HAS_DOCKER -eq 0 ]]; then
  echo "ABORT: Nenhuma ferramenta encontrada (skopeo/crane/docker)."
  exit 2
fi

# --- localizar authfile legível para skopeo/crane (rootless) ---
AUTHFILE=""
if [[ -r "${HOME}/.docker/config.json" ]]; then
  AUTHFILE="${HOME}/.docker/config.json"
elif [[ -r "${HOME}/.config/containers/auth.json" ]]; then
  AUTHFILE="${HOME}/.config/containers/auth.json"
fi

# --- login GHCR (sem vazar token) ---
if [[ -n "${GHCR_TOKEN:-}" && -n "${GHCR_USER:-}" ]]; then
  if [[ $HAS_DOCKER -eq 1 ]]; then
    echo "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USER}" --password-stdin >/dev/null || true
    echo "OK: docker login ghcr.io realizado (ou já estava logado)."
  fi
  if [[ $HAS_CRANE -eq 1 ]]; then
    crane auth login ghcr.io -u "${GHCR_USER}" -p "${GHCR_TOKEN}" >/dev/null || true
    echo "OK: crane auth login ghcr.io realizado (ou já estava logado)."
  fi
else
  echo "INFO: GHCR_USER/GHCR_TOKEN não informados (push pode falhar se não houver login prévio)."
fi

if [[ -n "${AUTHFILE}" ]]; then
  echo "INFO: AUTHFILE detectado para skopeo/crane: ${AUTHFILE}"
else
  echo "INFO: Nenhum AUTHFILE legível detectado (~/.docker/config.json ou ~/.config/containers/auth.json)."
  echo "      Se skopeo/crane falhar auth, prefira docker/podman (docker login já cobre)."
fi
echo

# --- Coleta imagens (containers + initContainers) ---
echo "FASE 1 — Inventário de imagens (namespace=${NS})"
echo "------------------------------------------------"

kubectl get pods -n "${NS}" -o jsonpath='{range .items[*]}{range .spec.initContainers[*]}{.image}{"\n"}{end}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' \
  | sed '/^$/d' | sort -u > "${OUT_DIR}/images_unique.txt"

echo "OK: $(wc -l < "${OUT_DIR}/images_unique.txt") imagens únicas encontradas."
echo

# --- PIN determinístico (sem latest / sem tag) ---
declare -A PIN
PIN["hyperledger/besu"]="hyperledger/besu:24.2.0"
PIN["apache/kafka"]="apache/kafka:3.6.1"
PIN["curlimages/curl"]="curlimages/curl:8.6.0"
PIN["networkstatic/iperf3"]="networkstatic/iperf3:3.16"
PIN["alpine"]="alpine:3.19"
PIN["library/alpine"]="library/alpine:3.19"
PIN["192.168.10.16:5000/library/alpine"]="192.168.10.16:5000/library/alpine:3.19"

normalize_image() {
  local img="$1"

  # já é mirror (evita looping se o usuário rodar após rewire)
  if [[ "$img" == "${GHCR_ORG}/mirror-"* ]]; then
    echo "$img"
    return
  fi

  local last_part="${img##*/}"

  # Sem tag (observação: registry:port não está no last_part, então é seguro)
  if [[ "$last_part" != *":"* ]]; then
    if [[ -n "${PIN[$img]:-}" ]]; then
      echo "${PIN[$img]}"
      return
    fi
    echo "ABORT_NO_TAG::$img"
    return
  fi

  # :latest
  if [[ "$img" == *":latest" ]]; then
    local base="${img%:latest}"

    if [[ -n "${PIN[$base]:-}" ]]; then
      echo "${PIN[$base]}"
      return
    fi

    # fallback técnico (opinião): se for alpine e ninguém pinou, fixa 3.19
    if [[ "$base" == *"alpine" ]]; then
      echo "${base}:3.19"
      return
    fi

    echo "ABORT_LATEST::$img"
    return
  fi

  echo "$img"
}

echo "FASE 2 — Normalização determinística"
echo "------------------------------------"
BAD=0
> "${OUT_DIR}/images_normalized.txt"
> "${OUT_DIR}/images_abort.txt"

while read -r img; do
  n="$(normalize_image "$img")"
  if [[ "$n" == ABORT_* ]]; then
    echo "$n" | tee -a "${OUT_DIR}/images_abort.txt"
    BAD=1
  else
    echo "$n" >> "${OUT_DIR}/images_normalized.txt"
  fi
done < "${OUT_DIR}/images_unique.txt"

sort -u "${OUT_DIR}/images_normalized.txt" -o "${OUT_DIR}/images_normalized.txt"

if [[ $BAD -eq 1 ]]; then
  echo
  echo "ABORT: Existem imagens sem tag ou com latest sem PIN."
  echo "Ajuste PIN[] e rode novamente. Arquivo: ${OUT_DIR}/images_abort.txt"
  exit 10
fi

echo "OK: Normalização concluída (total: $(wc -l < "${OUT_DIR}/images_normalized.txt"))."
echo

# --- Mapeamento (origem -> destino GHCR) ---
echo "FASE 3 — Gerando mapeamento"
echo "---------------------------"

map_to_ghcr() {
  local src="$1"
  local tag="${src##*:}"
  local repo="${src%:*}"

  # remove prefixos comuns (mantém registry:port quando existir)
  repo="${repo#docker.io/}"
  repo="${repo#library/}"

  # sanitização forte:
  # - GHCR repo NÃO pode conter ":" (ex.: registry:5000)
  # - substitui / . : por -
  # - lowercase para garantir compatibilidade
  local safe_repo
  safe_repo="$(echo "$repo" | tr '[:upper:]' '[:lower:]' | sed 's/[\/\.\:]/-/g')"

  echo "${GHCR_ORG}/mirror-${safe_repo}:${tag}"
}

> "${OUT_DIR}/mirror_map.tsv"

while read -r src; do
  dst="$(map_to_ghcr "$src")"
  printf "%s\t%s\n" "$src" "$dst" >> "${OUT_DIR}/mirror_map.tsv"
done < "${OUT_DIR}/images_normalized.txt"

echo "OK: mirror_map.tsv gerado em: ${OUT_DIR}/mirror_map.tsv"
echo

# --- Mirror efetivo (prioridade: docker/podman > crane > skopeo) ---
echo "FASE 4 — Executando mirror (pull -> push)"
echo "----------------------------------------"

mirror_one() {
  local src="$1"
  local dst="$2"

  # 1) docker/podman (mais estável com login já realizado)
  if [[ $HAS_DOCKER -eq 1 ]]; then
    docker pull "${src}" >/dev/null
    docker tag "${src}" "${dst}"
    docker push "${dst}" >/dev/null
    return 0
  fi

  # 2) crane
  if [[ $HAS_CRANE -eq 1 ]]; then
    if [[ -n "${AUTHFILE}" ]]; then
      crane --authfile "${AUTHFILE}" copy "${src}" "${dst}" >/dev/null
    else
      crane copy "${src}" "${dst}" >/dev/null
    fi
    return 0
  fi

  # 3) skopeo (exige authfile legível em rootless)
  if [[ $HAS_SKOPEO -eq 1 ]]; then
    if [[ -n "${AUTHFILE}" ]]; then
      skopeo copy --all --authfile "${AUTHFILE}" "docker://${src}" "docker://${dst}" >/dev/null
    else
      # ainda tenta, mas pode falhar (permissão)
      skopeo copy --all "docker://${src}" "docker://${dst}" >/dev/null
    fi
    return 0
  fi

  return 1
}

COUNT=0
FAIL=0

> "${OUT_DIR}/mirror_failures.txt"

while IFS=$'\t' read -r src dst; do
  echo "MIRROR: ${src} -> ${dst}"
  if mirror_one "${src}" "${dst}"; then
    COUNT=$((COUNT+1))
  else
    echo "FAIL: ${src}" | tee -a "${OUT_DIR}/mirror_failures.txt"
    FAIL=$((FAIL+1))
  fi
done < "${OUT_DIR}/mirror_map.tsv"

echo
echo "FASE 5 — Relatório final"
echo "------------------------"
echo "OK   : ${COUNT}"
echo "FAIL : ${FAIL}"
echo "DIR  : ${OUT_DIR}"
echo

if [[ $FAIL -ne 0 ]]; then
  echo "ABORT: falhas detectadas."
  echo "Verifique: ${OUT_DIR}/mirror_failures.txt"
  exit 20
fi

echo "DONE: Mirror concluído com sucesso."
