# ============================================
# Script de Restore do PostgreSQL - TriSLA (PowerShell)
# ============================================

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile,
    
    [string]$PGHost = "localhost",
    [int]$PGPort = 5432,
    [string]$PGDatabase = "trisla",
    [string]$PGUser = "trisla",
    [string]$PGPassword = "trisla_password",
    [switch]$UseDocker = $false
)

$ErrorActionPreference = "Stop"

# Verificar se arquivo existe
if (-not (Test-Path $BackupFile)) {
    Write-Host "❌ Erro: Arquivo de backup não encontrado: $BackupFile"
    exit 1
}

Write-Host "=========================================="
Write-Host "TriSLA - Restore do PostgreSQL"
Write-Host "=========================================="
Write-Host "Data/Hora: $(Get-Date)"
Write-Host "Banco: $PGDatabase"
Write-Host "Host: ${PGHost}:${PGPort}"
Write-Host "Arquivo: $BackupFile"
Write-Host ""

# Confirmar ação
$confirm = Read-Host "⚠️  ATENÇÃO: Esta operação irá SOBRESCREVER o banco de dados atual. Continuar? (sim/não)"
if ($confirm -ne "sim") {
    Write-Host "Operação cancelada."
    exit 0
}

# Verificar se deve usar Docker
if ($UseDocker) {
    Write-Host "Usando Docker para restore..."
    $dockerPsql = "docker exec -i trisla-postgres psql"
    $dockerPgDump = "docker exec -i trisla-postgres pg_dump"
} else {
    # Verificar se pg_restore/psql está disponível
    $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
    if (-not $psqlPath) {
        Write-Host "⚠️  psql não encontrado localmente. Tentando usar Docker..."
        $UseDocker = $true
        $dockerPsql = "docker exec -i trisla-postgres psql"
        $dockerPgDump = "docker exec -i trisla-postgres pg_dump"
    } else {
        $dockerPsql = "psql"
        $dockerPgDump = "pg_dump"
    }
}

$env:PGPASSWORD = $PGPassword

# Verificar conexão
Write-Host "Verificando conexão com banco de dados..."
try {
    if ($UseDocker) {
        $testQuery = "SELECT 1" | & docker exec -i trisla-postgres psql -U $PGUser -d postgres -t 2>&1
    } else {
        $env:PGPASSWORD = $PGPassword
        $testQuery = "SELECT 1" | & psql -h $PGHost -p $PGPort -U $PGUser -d postgres -t 2>&1
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Falha na conexão"
    }
} catch {
    Write-Host "❌ Erro: Não foi possível conectar ao PostgreSQL"
    Write-Host "   Tente usar: -UseDocker"
    exit 1
}

# Fazer backup de segurança
$SafetyBackup = "backups\postgres\safety_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql.gz"
Write-Host ""
Write-Host "Criando backup de segurança do estado atual..."
New-Item -ItemType Directory -Path "backups\postgres" -Force | Out-Null

try {
    $tempFile = Join-Path $env:TEMP "safety_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    if ($UseDocker) {
        & docker exec -i trisla-postgres pg_dump -U $PGUser -d $PGDatabase --clean --if-exists --create | Out-File -FilePath $tempFile -Encoding UTF8
    } else {
        $env:PGPASSWORD = $PGPassword
        & pg_dump -h $PGHost -p $PGPort -U $PGUser -d $PGDatabase --clean --if-exists --create | Out-File -FilePath $tempFile -Encoding UTF8
    }
    
    # Comprimir
    $bytes = [System.IO.File]::ReadAllBytes($tempFile)
    $compressed = [System.IO.Compression.GZipStream]::new(
        [System.IO.File]::Create($SafetyBackup),
        [System.IO.Compression.CompressionLevel]::Optimal
    )
    $compressed.Write($bytes, 0, $bytes.Length)
    $compressed.Close()
    Remove-Item $tempFile -Force
    
    Write-Host "✅ Backup de segurança criado: $SafetyBackup"
} catch {
    Write-Host "⚠️  Aviso: Não foi possível criar backup de segurança: $_"
}

# Restaurar backup
Write-Host ""
Write-Host "Iniciando restore..."

try {
    if ($BackupFile.EndsWith(".gz")) {
        # Backup comprimido - descomprimir e restaurar
        $tempRestore = Join-Path $env:TEMP "restore_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
        
        # Descomprimir
        $compressed = [System.IO.Compression.GZipStream]::new(
            [System.IO.File]::OpenRead($BackupFile),
            [System.IO.Compression.CompressionMode]::Decompress
        )
        $decompressed = [System.IO.File]::Create($tempRestore)
        $compressed.CopyTo($decompressed)
        $compressed.Close()
        $decompressed.Close()
        
        # Restaurar
        if ($UseDocker) {
            Get-Content $tempRestore | & docker exec -i trisla-postgres psql -U $PGUser -d postgres
        } else {
            $env:PGPASSWORD = $PGPassword
            Get-Content $tempRestore | & psql -h $PGHost -p $PGPort -U $PGUser -d postgres
        }
        
        Remove-Item $tempRestore -Force
    } else {
        # Backup não comprimido
        if ($UseDocker) {
            Get-Content $BackupFile | & docker exec -i trisla-postgres psql -U $PGUser -d postgres
        } else {
            $env:PGPASSWORD = $PGPassword
            Get-Content $BackupFile | & psql -h $PGHost -p $PGPort -U $PGUser -d postgres
        }
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Restore concluído com sucesso!"
        Write-Host ""
        Write-Host "Verificando integridade do banco..."
        
        # Verificar tabelas
        $tableCount = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | 
            & psql -h $PGHost -p $PGPort -U $PGUser -d $PGDatabase -t | 
            ForEach-Object { $_.Trim() }
        
        Write-Host "   Tabelas encontradas: $tableCount"
        
        # Verificar dados
        try {
            $intentCount = "SELECT COUNT(*) FROM intents;" | 
                & psql -h $PGHost -p $PGPort -U $PGUser -d $PGDatabase -t | 
                ForEach-Object { $_.Trim() }
            Write-Host "   Intents: $intentCount"
        } catch {
            Write-Host "   Intents: 0 (tabela não encontrada)"
        }
        
        try {
            $nestCount = "SELECT COUNT(*) FROM nests;" | 
                & psql -h $PGHost -p $PGPort -U $PGUser -d $PGDatabase -t | 
                ForEach-Object { $_.Trim() }
            Write-Host "   NESTs: $nestCount"
        } catch {
            Write-Host "   NESTs: 0 (tabela não encontrada)"
        }
        
        Write-Host ""
        Write-Host "=========================================="
        Write-Host "Restore finalizado com sucesso!"
        Write-Host "=========================================="
    } else {
        throw "Falha no restore"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erro durante o restore: $_"
    Write-Host ""
    Write-Host "Para restaurar o backup de segurança:"
    Write-Host "  .\scripts\restore-postgres.ps1 -BackupFile `"$SafetyBackup`""
    exit 1
} finally {
    Remove-Item env:PGPASSWORD -ErrorAction SilentlyContinue
}

