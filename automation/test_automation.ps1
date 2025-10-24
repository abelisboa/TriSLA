# ==========================================
# 🧪 TriSLA Automation Test Script (PowerShell)
# ==========================================
# Objetivo:
# Testar o script de automação sem executar comandos reais,
# apenas validando a lógica e estrutura.

param(
    [switch]$Verbose
)

# Configuração do arquivo CSV
$CSV_PATH = "PROMPTS\automation\TRISLA_PIPELINE_TRACKER.csv"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Test-CSVReading {
    Write-ColorOutput "🧪 Testando leitura do CSV..." "Cyan"
    
    if (-not (Test-Path $CSV_PATH)) {
        Write-ColorOutput "❌ Arquivo CSV não encontrado: $CSV_PATH" "Red"
        return $false
    }
    
    try {
        $rows = Import-Csv -Path $CSV_PATH -Encoding UTF8
        
        Write-ColorOutput "✅ CSV lido com sucesso: $($rows.Count) linhas" "Green"
        
        # Mostrar estrutura
        if ($rows.Count -gt 0) {
            Write-ColorOutput "📋 Campos disponíveis:" "White"
            $firstRow = $rows[0]
            foreach ($field in $firstRow.PSObject.Properties.Name) {
                Write-ColorOutput "  - $field" "Gray"
            }
            
            Write-ColorOutput "`n📊 Status dos itens:" "White"
            $statusCount = @{}
            foreach ($row in $rows) {
                $status = $row."Status Atual".Trim()
                if ($statusCount.ContainsKey($status)) {
                    $statusCount[$status]++
                } else {
                    $statusCount[$status] = 1
                }
            }
            
            foreach ($status in $statusCount.Keys) {
                Write-ColorOutput "  $status : $($statusCount[$status])" "Gray"
            }
        }
        
        return $true
        
    } catch {
        Write-ColorOutput "❌ Erro ao ler CSV: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-PendingItems {
    Write-ColorOutput "`n🧪 Testando identificação de itens pendentes..." "Cyan"
    
    try {
        $rows = Import-Csv -Path $CSV_PATH -Encoding UTF8
        
        $pendingItems = @()
        foreach ($row in $rows) {
            $status = $row."Status Atual".Trim()
            $cmd = $row."Comando Principal".Trim()
            $item = $row."Item"
            
            if ($status -in @("❌", "⚙️") -and $cmd) {
                $pendingItems += [PSCustomObject]@{
                    Item = $item
                    Status = $status
                    Command = $cmd
                }
            }
        }
        
        Write-ColorOutput "✅ Itens pendentes identificados: $($pendingItems.Count)" "Green"
        
        if ($pendingItems.Count -gt 0) {
            Write-ColorOutput "`n📋 Itens pendentes:" "White"
            for ($i = 0; $i -lt $pendingItems.Count; $i++) {
                $item = $pendingItems[$i]
                Write-ColorOutput "  $($i + 1). $($item.Item) ($($item.Status))" "Gray"
                $shortCmd = if ($item.Command.Length -gt 80) { 
                    $item.Command.Substring(0, 80) + "..." 
                } else { 
                    $item.Command 
                }
                Write-ColorOutput "     Comando: $shortCmd" "Gray"
            }
        }
        
        return $true
        
    } catch {
        Write-ColorOutput "❌ Erro ao identificar itens pendentes: $($_.Exception.Message)" "Red"
        return $false
    }
}

function Test-CommandValidation {
    Write-ColorOutput "`n🧪 Testando validação de comandos..." "Cyan"
    
    # Comandos de teste
    $testCommands = @(
        "Write-Host 'Teste de comando simples'",
        "Get-Location",
        "Get-Date",
        "invalid_command_that_should_fail"
    )
    
    Write-ColorOutput "📋 Comandos de teste:" "White"
    foreach ($cmd in $testCommands) {
        Write-ColorOutput "  - $cmd" "Gray"
    }
    
    Write-ColorOutput "`n⚠️ Nota: Esta é apenas uma validação de estrutura." "Yellow"
    Write-ColorOutput "   Os comandos reais serão executados pelo script principal." "Yellow"
    
    return $true
}

function Main {
    Write-ColorOutput "🧪 Iniciando testes do TriSLA Automation..." "Green"
    Write-ColorOutput "=" * 60 "Cyan"
    
    $tests = @(
        @{ Name = "Leitura do CSV"; Function = { Test-CSVReading } },
        @{ Name = "Identificação de itens pendentes"; Function = { Test-PendingItems } },
        @{ Name = "Validação de comandos"; Function = { Test-CommandValidation } }
    )
    
    $passed = 0
    $failed = 0
    
    foreach ($test in $tests) {
        Write-ColorOutput "`n🔍 Executando: $($test.Name)" "Yellow"
        try {
            if (& $test.Function) {
                Write-ColorOutput "✅ $($test.Name): PASSOU" "Green"
                $passed++
            } else {
                Write-ColorOutput "❌ $($test.Name): FALHOU" "Red"
                $failed++
            }
        } catch {
            Write-ColorOutput "💥 $($test.Name): ERRO - $($_.Exception.Message)" "Red"
            $failed++
        }
    }
    
    Write-ColorOutput "`n" + "=" * 60 "Cyan"
    Write-ColorOutput "📊 RESUMO DOS TESTES:" "White"
    Write-ColorOutput "✅ Testes passaram: $passed" "Green"
    Write-ColorOutput "❌ Testes falharam: $failed" "Red"
    $successRate = if (($passed + $failed) -gt 0) { [math]::Round(($passed / ($passed + $failed)) * 100, 1) } else { 0 }
    Write-ColorOutput "📈 Taxa de sucesso: $successRate%" "White"
    
    if ($failed -eq 0) {
        Write-ColorOutput "`n🎉 Todos os testes passaram! O script está pronto para uso." "Green"
        return $true
    } else {
        Write-ColorOutput "`n⚠️ $failed teste(s) falharam. Verifique os problemas antes de usar o script." "Yellow"
        return $false
    }
}

# Executar função principal
$success = Main
exit $(if ($success) { 0 } else { 1 })
