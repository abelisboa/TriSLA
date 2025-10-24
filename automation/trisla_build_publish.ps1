# ==========================================
# 🚀 TriSLA Build & Publish Automation (PowerShell)
# ==========================================
# Objetivo:
# Automatizar o build e publicação de todos os módulos TriSLA pendentes,
# lendo o arquivo CSV de acompanhamento e atualizando o status automaticamente.

param(
    [switch]$DryRun,
    [switch]$Verbose
)

# Configuração do arquivo CSV
$CSV_PATH = "PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Invoke-Command {
    param(
        [string]$Command,
        [switch]$DryRun
    )
    
    Write-ColorOutput "`n🧩 Executando: $Command" "Cyan"
    
    if ($DryRun) {
        Write-ColorOutput "⚠️ DRY RUN - Comando não executado" "Yellow"
        return $true
    }
    
    try {
        $result = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Sucesso: $Command" "Green"
            if ($result) {
                Write-ColorOutput "📤 Output: $result" "Gray"
            }
            return $true
        } else {
            Write-ColorOutput "❌ Falha: $Command" "Red"
            if ($result) {
                Write-ColorOutput "🚨 Erro: $result" "Red"
            }
            return $false
        }
    } catch {
        Write-ColorOutput "💥 Exceção ao executar '$Command': $($_.Exception.Message)" "Red"
        return $false
    }
}

function Update-CSV {
    param(
        [array]$Rows
    )
    
    try {
        $Rows | Export-Csv -Path $CSV_PATH -NoTypeInformation -Encoding UTF8
        Write-ColorOutput "📄 CSV atualizado: $CSV_PATH" "Green"
        return $true
    } catch {
        Write-ColorOutput "💥 Erro ao atualizar CSV: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-CSVStructure {
    param([array]$Rows)
    
    if ($Rows.Count -eq 0) {
        Write-ColorOutput "⚠️ CSV vazio ou inválido" "Yellow"
        return $false
    }
    
    $requiredFields = @("Item", "Comando Principal", "Status Atual")
    $firstRow = $Rows[0]
    
    foreach ($field in $requiredFields) {
        if (-not $firstRow.PSObject.Properties.Name -contains $field) {
            Write-ColorOutput "⚠️ Campo obrigatório '$field' não encontrado no CSV" "Yellow"
            return $false
        }
    }
    
    return $true
}

function Get-CurrentTimestamp {
    return Get-Date -Format "yyyy-MM-dd HH:mm"
}

function Main {
    Write-ColorOutput "`n🚀 Iniciando automação TriSLA Build & Publish..." "Green"
    Write-ColorOutput ("=" * 60) "Cyan"
    
    if ($DryRun) {
        Write-ColorOutput "⚠️ MODO DRY RUN ATIVADO - Nenhum comando será executado" "Yellow"
    }
    
    # Verificar se o arquivo CSV existe
    if (-not (Test-Path $CSV_PATH)) {
        Write-ColorOutput "❌ Arquivo CSV não encontrado: $CSV_PATH" "Red"
        return
    }
    
    # Ler o CSV
    try {
        $rows = Import-Csv -Path $CSV_PATH -Encoding UTF8
    } catch {
        Write-ColorOutput "💥 Erro ao ler CSV: $($_.Exception.Message)" "Red"
        return
    }
    
    # Validar estrutura do CSV
    if (-not (Test-CSVStructure $rows)) {
        Write-ColorOutput "❌ Estrutura do CSV inválida" "Red"
        return
    }
    
    Write-ColorOutput "📊 Total de itens no pipeline: $($rows.Count)" "White"
    
    # Filtrar itens pendentes
    $pendingItems = @()
    foreach ($row in $rows) {
        $status = $row."Status Atual".Trim()
        $cmd = $row."Comando Principal".Trim()
        
        if ($status -in @("❌", "⚙️") -and $cmd) {
            $pendingItems += $row
        }
    }
    
    Write-ColorOutput "🔄 Itens pendentes para execução: $($pendingItems.Count)" "White"
    
    if ($pendingItems.Count -eq 0) {
        Write-ColorOutput "✅ Nenhum item pendente encontrado!" "Green"
        return
    }
    
    # Executar itens pendentes
    $updatedRows = @()
    $successCount = 0
    $failureCount = 0
    
    foreach ($row in $rows) {
        $status = $row."Status Atual".Trim()
        $cmd = $row."Comando Principal".Trim()
        $item = $row."Item"
        
        # Só executa itens com status ❌ ou ⚙️ e que tenham comando válido
        if ($status -in @("❌", "⚙️") -and $cmd) {
            Write-ColorOutput ("`n" + "=" * 60) "Cyan"
            Write-ColorOutput "🎯 Processando: $item" "Yellow"
            Write-ColorOutput "📋 Comando: $cmd" "White"
            Write-ColorOutput "📊 Status atual: $status" "White"
            
            $success = Invoke-Command -Command $cmd -DryRun:$DryRun
            
            if ($success) {
                $row."Status Atual" = "✅"
                $row."Data Última Atualização" = Get-CurrentTimestamp
                Write-ColorOutput "✅ Concluído: $item" "Green"
                $successCount++
            } else {
                $row."Status Atual" = "❌"
                $row."Data Última Atualização" = Get-CurrentTimestamp
                Write-ColorOutput "❌ Falha ao executar: $item" "Red"
                $failureCount++
            }
        }
        
        $updatedRows += $row
    }
    
    # Atualizar CSV
    if (Update-CSV $updatedRows) {
        Write-ColorOutput ("`n" + "=" * 60) "Cyan"
        Write-ColorOutput "📊 RESUMO DA EXECUÇÃO:" "White"
        Write-ColorOutput "✅ Sucessos: $successCount" "Green"
        Write-ColorOutput "❌ Falhas: $failureCount" "Red"
        Write-ColorOutput "📄 Arquivo atualizado: $CSV_PATH" "White"
        Write-ColorOutput "✅ Pipeline TriSLA atualizado com sucesso!" "Green"
    } else {
        Write-ColorOutput "❌ Falha ao atualizar CSV" "Red"
        return
    }
}

# Executar função principal
Main
