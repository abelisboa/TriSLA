# ============================================
# Script para Testar Restore de Backup
# ============================================

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗"
Write-Host "║  TriSLA - Testar Restore de Backup                       ║"
Write-Host "╚════════════════════════════════════════════════════════════╝"
Write-Host ""

# Verificar se PostgreSQL está acessível
Write-Host "Verificando conexão com PostgreSQL..."
$useDocker = $false
try {
    # Tentar via Docker primeiro (mais comum)
    $testQuery = "SELECT 1" | & docker exec -i trisla-postgres psql -U trisla -d postgres -t 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL acessível via Docker"
        $useDocker = $true
    } else {
        throw "Falha na conexão Docker"
    }
} catch {
    # Tentar via psql local
    try {
        $env:PGPASSWORD = "trisla_password"
        $testQuery = "SELECT 1" | & psql -h localhost -p 5432 -U trisla -d postgres -t 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL acessível via psql local"
        } else {
            throw "Falha na conexão"
        }
    } catch {
        Write-Host "❌ Erro: Não foi possível conectar ao PostgreSQL"
        Write-Host "   Verifique se o container está rodando: docker compose ps postgres"
        exit 1
    } finally {
        Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
    }
}

# Verificar se há backups disponíveis
Write-Host ""
Write-Host "Procurando backups disponíveis..."
$backupDir = "backups\postgres"
if (-not (Test-Path $backupDir)) {
    Write-Host "⚠️  Diretório de backups não encontrado. Criando backup de teste..."
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Criar backup de teste
    Write-Host "Criando backup de teste..."
    .\scripts\backup-postgres.ps1
}

$backups = Get-ChildItem -Path $backupDir -Filter "trisla_backup_*.sql.gz" | Sort-Object LastWriteTime -Descending

if ($backups.Count -eq 0) {
    Write-Host "❌ Nenhum backup encontrado. Criando backup primeiro..."
    .\scripts\backup-postgres.ps1
    $backups = Get-ChildItem -Path $backupDir -Filter "trisla_backup_*.sql.gz" | Sort-Object LastWriteTime -Descending
}

Write-Host ""
Write-Host "Backups disponíveis:"
$i = 1
foreach ($backup in $backups) {
    $size = [math]::Round($backup.Length / 1MB, 2)
    Write-Host "  $i. $($backup.Name) ($size MB) - $($backup.LastWriteTime)"
    $i++
}

Write-Host ""
$choice = Read-Host "Selecione o backup para restaurar (número) ou 'n' para criar novo backup"

if ($choice -eq 'n' -or $choice -eq 'N') {
    Write-Host "Criando novo backup..."
    .\scripts\backup-postgres.ps1
    $backups = Get-ChildItem -Path $backupDir -Filter "trisla_backup_*.sql.gz" | Sort-Object LastWriteTime -Descending
    $selectedBackup = $backups[0]
} else {
    $index = [int]$choice - 1
    if ($index -lt 0 -or $index -ge $backups.Count) {
        Write-Host "❌ Escolha inválida"
        exit 1
    }
    $selectedBackup = $backups[$index]
}

Write-Host ""
Write-Host "Backup selecionado: $($selectedBackup.Name)"
Write-Host ""

# Confirmar
$confirm = Read-Host "⚠️  ATENÇÃO: Esta operação irá SOBRESCREVER o banco atual. Continuar? (sim/não)"
if ($confirm -ne "sim") {
    Write-Host "Operação cancelada."
    exit 0
}

# Executar restore
Write-Host ""
Write-Host "Executando restore..."
if ($useDocker) {
    .\scripts\restore-postgres.ps1 -BackupFile $selectedBackup.FullName -UseDocker
} else {
    .\scripts\restore-postgres.ps1 -BackupFile $selectedBackup.FullName
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Teste de restore concluído com sucesso!"
    Write-Host ""
    Write-Host "Verificando integridade dos dados..."
    
    # Verificar dados
    $env:PGPASSWORD = "trisla_password"
    try {
        $intentCount = "SELECT COUNT(*) FROM intents;" | 
            & psql -h localhost -p 5432 -U trisla -d trisla -t | 
            ForEach-Object { $_.Trim() }
        $nestCount = "SELECT COUNT(*) FROM nests;" | 
            & psql -h localhost -p 5432 -U trisla -d trisla -t | 
            ForEach-Object { $_.Trim() }
        
        Write-Host "  ✅ Intents: $intentCount"
        Write-Host "  ✅ NESTs: $nestCount"
    } catch {
        Write-Host "  ⚠️  Não foi possível verificar dados (tabelas podem não existir)"
    } finally {
        Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
    }
} else {
    Write-Host ""
    Write-Host "❌ Teste de restore falhou!"
    exit 1
}

