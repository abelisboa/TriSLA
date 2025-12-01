# ============================================
# Script de Backup do PostgreSQL - TriSLA (PowerShell)
# ============================================

param(
    [string]$BackupDir = ".\backups\postgres",
    [int]$RetentionDays = 7,
    [string]$PGHost = "localhost",
    [int]$PGPort = 5432,
    [string]$PGDatabase = "trisla",
    [string]$PGUser = "trisla",
    [string]$PGPassword = "trisla_password"
)

$ErrorActionPreference = "Stop"

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path $BackupDir "trisla_backup_$Timestamp.sql.gz"

# Criar diretório de backup se não existir
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "=========================================="
Write-Host "TriSLA - Backup do PostgreSQL"
Write-Host "=========================================="
Write-Host "Data/Hora: $(Get-Date)"
Write-Host "Banco: $PGDatabase"
Write-Host "Host: ${PGHost}:${PGPort}"
Write-Host "Arquivo: $BackupFile"
Write-Host ""

# Verificar se pg_dump está disponível
$pgDumpPath = Get-Command pg_dump -ErrorAction SilentlyContinue
if (-not $pgDumpPath) {
    Write-Host "❌ Erro: pg_dump não encontrado. Instale PostgreSQL client tools."
    exit 1
}

# Fazer backup
Write-Host "Iniciando backup..."
$env:PGPASSWORD = $PGPassword

try {
    # Usar pg_dump e comprimir
    $tempFile = Join-Path $env:TEMP "trisla_backup_$Timestamp.sql"
    & pg_dump -h $PGHost -p $PGPort -U $PGUser -d $PGDatabase --clean --if-exists --create | Out-File -FilePath $tempFile -Encoding UTF8
    
    # Comprimir usando .NET
    $bytes = [System.IO.File]::ReadAllBytes($tempFile)
    $compressed = [System.IO.Compression.GZipStream]::new(
        [System.IO.File]::Create($BackupFile),
        [System.IO.Compression.CompressionLevel]::Optimal
    )
    $compressed.Write($bytes, 0, $bytes.Length)
    $compressed.Close()
    
    Remove-Item $tempFile -Force
    
    $BackupSize = (Get-Item $BackupFile).Length / 1MB
    Write-Host "✅ Backup concluído com sucesso!"
    Write-Host "   Tamanho: $([math]::Round($BackupSize, 2)) MB"
    Write-Host "   Arquivo: $BackupFile"
} catch {
    Write-Host "❌ Erro ao fazer backup: $_"
    exit 1
} finally {
    Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
}

# Limpar backups antigos
Write-Host ""
Write-Host "Limpando backups antigos (retention: $RetentionDays dias)..."
$cutoffDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $BackupDir -Filter "trisla_backup_*.sql.gz" | 
    Where-Object { $_.LastWriteTime -lt $cutoffDate } | 
    Remove-Item -Force
Write-Host "✅ Limpeza concluída"

Write-Host ""
Write-Host "=========================================="
Write-Host "Backup finalizado"
Write-Host "=========================================="

