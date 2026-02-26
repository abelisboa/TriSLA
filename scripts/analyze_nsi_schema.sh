#!/bin/bash

set -e

BASE_DIR="/home/porvir5g/gtp5g/trisla"
LATEST_DIR=$(ls -dt ${BASE_DIR}/evidencias_crd_schema/nsi_schema_* | head -n 1)
OUT_DIR="${LATEST_DIR}/analysis"

echo "============================================"
echo "TriSLA NSI CRD SCHEMA ANALYSIS"
echo "Source : ${LATEST_DIR}"
echo "Output : ${OUT_DIR}"
echo "============================================"

mkdir -p "${OUT_DIR}"

echo "1️⃣ Verificando se 'status' é permitido no create..."
grep -n "subresources" ${LATEST_DIR}/01_crd_full.yaml > ${OUT_DIR}/01_subresources.txt || true

echo "2️⃣ Verificando definição de spec..."
grep -n "properties:" -n ${LATEST_DIR}/02_openapi_schema.yaml > ${OUT_DIR}/02_properties_locations.txt || true

echo "3️⃣ Extraindo propriedades de spec..."
awk '
/properties:/,/required:/
' ${LATEST_DIR}/02_openapi_schema.yaml > ${OUT_DIR}/03_spec_properties_block.txt || true

echo "4️⃣ Verificando campo SLA definido no CRD..."
grep -n "sla:" ${LATEST_DIR}/02_openapi_schema.yaml > ${OUT_DIR}/04_sla_occurrences.txt || true

echo "5️⃣ Verificando se SLA possui preserve-unknown-fields..."
grep -n "preserve" ${LATEST_DIR}/02_openapi_schema.yaml > ${OUT_DIR}/05_preserve_flags.txt || true

echo "6️⃣ Detectando required fields..."
grep -n "required:" ${LATEST_DIR}/02_openapi_schema.yaml > ${OUT_DIR}/06_required_fields.txt || true

echo "============================================"
echo "ANALYSIS COMPLETED"
echo "Evidence directory:"
echo "${OUT_DIR}"
echo "============================================"
