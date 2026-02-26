#!/bin/bash

set -e

NS="${1:-trisla}"
CRD="networksliceinstances.trisla.io"
BASE_DIR="/home/porvir5g/gtp5g/trisla"
OUT_DIR="${BASE_DIR}/evidencias_crd_schema/nsi_schema_$(date -u +%Y%m%dT%H%M%SZ)"

echo "============================================"
echo "TriSLA CRD SCHEMA EXTRACTION"
echo "Namespace : ${NS}"
echo "CRD       : ${CRD}"
echo "Output    : ${OUT_DIR}"
echo "============================================"

mkdir -p "${OUT_DIR}"

echo "1️⃣ Extraindo CRD completo..."
kubectl get crd ${CRD} -o yaml > "${OUT_DIR}/01_crd_full.yaml"

echo "2️⃣ Extraindo bloco openAPIV3Schema..."
awk '
/openAPIV3Schema:/,EOF
' "${OUT_DIR}/01_crd_full.yaml" > "${OUT_DIR}/02_openapi_schema.yaml"

echo "3️⃣ Extraindo bloco spec schema..."
awk '
/spec:/, /status:/ 
' "${OUT_DIR}/02_openapi_schema.yaml" > "${OUT_DIR}/03_spec_schema_block.yaml" || true

echo "4️⃣ Procurando campo SLA dentro do schema..."
grep -n "sla" "${OUT_DIR}/02_openapi_schema.yaml" > "${OUT_DIR}/04_sla_field_search.txt" || true

echo "5️⃣ Extraindo possível definição de spec.sla..."
awk '
/sla:/, /type:/ 
' "${OUT_DIR}/02_openapi_schema.yaml" > "${OUT_DIR}/05_sla_definition_block.yaml" || true

echo "6️⃣ Verificando se CRD possui subresource status..."
kubectl get crd ${CRD} -o yaml | grep -n "subresources" > "${OUT_DIR}/06_subresources_check.txt" || true

echo "============================================"
echo "CRD SCHEMA EXTRACTION COMPLETED"
echo "Evidence directory:"
echo "${OUT_DIR}"
echo "============================================"
