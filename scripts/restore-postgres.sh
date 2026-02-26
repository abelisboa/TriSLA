#!/bin/bash
# ============================================
# Script de Restore do PostgreSQL - TriSLA
# ============================================

set -e

# Verificar argumentos
if [ $# -lt 1 ]; then
    echo "Uso: $0 <arquivo_backup>"
    echo "Exemplo: $0 backups/postgres/trisla_backup_20231119_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"

# Verificar se arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

# Variáveis de ambiente do PostgreSQL
PGHOST="${PGHOST:-postgres}"
PGPORT="${PGPORT:-5432}"
PGDATABASE="${PGDATABASE:-trisla}"
PGUSER="${PGUSER:-trisla}"
PGPASSWORD="${PGPASSWORD:-trisla_password}"

echo "=========================================="
echo "TriSLA - Restore do PostgreSQL"
echo "=========================================="
echo "Data/Hora: $(date)"
echo "Banco: ${PGDATABASE}"
echo "Host: ${PGHOST}:${PGPORT}"
echo "Arquivo: ${BACKUP_FILE}"
echo ""

# Confirmar ação
read -p "⚠️  ATENÇÃO: Esta operação irá SOBRESCREVER o banco de dados atual. Continuar? (sim/não): " confirm
if [ "$confirm" != "sim" ]; then
    echo "Operação cancelada."
    exit 0
fi

# Exportar senha
export PGPASSWORD

# Verificar se banco existe
echo "Verificando conexão com banco de dados..."
if ! psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ Erro: Não foi possível conectar ao PostgreSQL"
    exit 1
fi

# Fazer backup do estado atual (safety net)
SAFETY_BACKUP="backups/postgres/safety_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
echo ""
echo "Criando backup de segurança do estado atual..."
mkdir -p backups/postgres
pg_dump -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
    --clean --if-exists --create \
    | gzip > "${SAFETY_BACKUP}"
echo "✅ Backup de segurança criado: ${SAFETY_BACKUP}"

# Restaurar backup
echo ""
echo "Iniciando restore..."
if [[ "$BACKUP_FILE" == *.gz ]]; then
    # Backup comprimido
    gunzip -c "$BACKUP_FILE" | psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d postgres
else
    # Backup não comprimido
    psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d postgres < "$BACKUP_FILE"
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Restore concluído com sucesso!"
    echo ""
    echo "Verificando integridade do banco..."
    
    # Verificar tabelas
    TABLE_COUNT=$(psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
        -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    
    echo "   Tabelas encontradas: $TABLE_COUNT"
    
    # Verificar dados
    INTENT_COUNT=$(psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
        -t -c "SELECT COUNT(*) FROM intents;" 2>/dev/null || echo "0")
    NEST_COUNT=$(psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" \
        -t -c "SELECT COUNT(*) FROM nests;" 2>/dev/null || echo "0")
    
    echo "   Intents: $INTENT_COUNT"
    echo "   NESTs: $NEST_COUNT"
    
    echo ""
    echo "=========================================="
    echo "Restore finalizado com sucesso!"
    echo "=========================================="
else
    echo ""
    echo "❌ Erro durante o restore!"
    echo ""
    echo "Para restaurar o backup de segurança:"
    echo "  $0 ${SAFETY_BACKUP}"
    exit 1
fi

