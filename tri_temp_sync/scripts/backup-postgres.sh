#!/bin/bash
# ============================================
# Script de Backup do PostgreSQL - TriSLA
# ============================================

set -e

# Configurações
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/trisla_backup_${TIMESTAMP}.sql.gz"

# Variáveis de ambiente do PostgreSQL
PGHOST="${PGHOST:-postgres}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-trisla}"
PGUSER="${PGUSER:-trisla}"
PGPASSWORD="${PGPASSWORD:-trisla_password}"

# Criar diretório de backup se não existir
mkdir -p "${BACKUP_DIR}"

echo "=========================================="
echo "TriSLA - Backup do PostgreSQL"
echo "=========================================="
echo "Data/Hora: $(date)"
echo "Banco: ${PGDATABASE}"
echo "Host: ${PGHOST}:${PGPORT}"
echo "Arquivo: ${BACKUP_FILE}"
echo ""

# Exportar senha para evitar prompt
export PGPASSWORD

# Fazer backup
echo "Iniciando backup..."
pg_dump -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
    --clean --if-exists --create \
    | gzip > "${BACKUP_FILE}"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ Backup concluído com sucesso!"
    echo "   Tamanho: ${BACKUP_SIZE}"
    echo "   Arquivo: ${BACKUP_FILE}"
else
    echo "❌ Erro ao fazer backup!"
    exit 1
fi

# Limpar backups antigos
echo ""
echo "Limpando backups antigos (retention: ${RETENTION_DAYS} dias)..."
find "${BACKUP_DIR}" -name "trisla_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
echo "✅ Limpeza concluída"

echo ""
echo "=========================================="
echo "Backup finalizado"
echo "=========================================="

