# ============================================
# TriSLA - Verificar Estrutura do Projeto
# ============================================

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     TriSLA - Verificação de Estrutura do Projeto         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$rootPath = $PSScriptRoot + "\.."
Set-Location $rootPath

# ============================================
# Estrutura Esperada
# ============================================

$expectedStructure = @{
    "ansible" = @{
        "ansible.cfg" = $true
        "inventory.yaml" = $true
        "group_vars" = @{
            "all.yml" = $true
            "control_plane.yml" = $true
            "workers.yml" = $true
        }
        "playbooks" = @{
            "deploy-trisla-nasp.yml" = $true
            "pre-flight.yml" = $true
            "setup-namespace.yml" = $true
            "validate-cluster.yml" = $true
        }
        "README.md" = $true
    }
    "apps" = @{
        "sem-csmf" = @{
            "Dockerfile" = $true
            "requirements.txt" = $true
            "src" = @{
                "main.py" = $true
                "grpc_server.py" = $true
                "intent_processor.py" = $true
                "nest_generator.py" = $true
            }
        }
        "ml_nsmf" = @{  # Diretório real é ml_nsmf (underscore)
            "Dockerfile" = $true
            "requirements.txt" = $true
            "models" = @{
                "viability_model.pkl" = $true
                "scaler.pkl" = $true
                "model_metadata.json" = $true
            }
            "src" = @{
                "main.py" = $true
                "predictor.py" = $true
            }
        }
        "decision-engine" = @{
            "Dockerfile" = $true
            "requirements.txt" = $true
            "src" = @{
                "main.py" = $true
                "decision_maker.py" = $true
                "rule_engine.py" = $true
            }
        }
        "bc-nssmf" = @{
            "Dockerfile" = $true
            "requirements.txt" = $true
            "src" = @{
                "main.py" = $true
                "smart_contracts.py" = $true
            }
        }
        "sla-agent-layer" = @{
            "Dockerfile" = $true
            "requirements.txt" = $true
            "src" = @{
                "main.py" = $true
                "agent_core.py" = $true
            }
        }
        "nasp-adapter" = @{
            "Dockerfile" = $true
            "requirements.txt" = $true
            "src" = @{
                "main.py" = $true
                "nasp_client.py" = $true
            }
        }
        "ui-dashboard" = @{
            "Dockerfile" = $true
            "package.json" = $true
            "src" = @{
                "App.tsx" = $true
            }
        }
    }
    "helm" = @{
        "trisla" = @{
            "Chart.yaml" = $true
            "values.yaml" = $true
            "values-nasp.yaml" = $true
            "templates" = @{
                "deployment-sem-csmf.yaml" = $true
                "service-sem-csmf.yaml" = $true
                "configmap.yaml" = $true
                "ingress.yaml" = $true
            }
        }
    }
    "monitoring" = @{
        "prometheus" = @{
            "prometheus.yml" = $true
            "rules" = @{
                "slo-rules.yml" = $true
            }
        }
        "otel-collector" = @{
            "config.yaml" = $true
        }
        "grafana" = @{
            "dashboards" = @{
                "trisla-overview.json" = $true
            }
        }
        "slo-reports" = @{
            "generator.py" = $true
        }
    }
    "tests" = @{
        "unit" = @{
            "test_sem_csmf.py" = $true
            "test_ml_nsmf.py" = $true
            "test_decision_engine.py" = $true
        }
        "integration" = @{
            "test_interfaces.py" = $true
        }
        "e2e" = @{
            "test_full_workflow.py" = $true
        }
        "pytest.ini" = $true
        "requirements.txt" = $true
    }
    "scripts" = @{
        "start-local.ps1" = $true
        "start-local.sh" = $true
        "validate-local.ps1" = $true
        "validate-local.sh" = $true
        "run-local-tests.ps1" = $true
        "run-local-tests.sh" = $true
    }
    "docs" = @{
        "DESENVOLVIMENTO_LOCAL.md" = $true
        "TROUBLESHOOTING_DOCKER.md" = $true
        "VALIDACAO_WINDOWS.md" = $true
    }
    "docker-compose.yml" = $true
    "README.md" = $true
    ".gitignore" = $true
    "env.example" = $true
}

# ============================================
# Função para verificar estrutura
# ============================================

function Verify-Structure {
    param(
        [string]$Path,
        [hashtable]$Expected,
        [string]$Indent = ""
    )
    
    $missing = @()
    $extra = @()
    $found = @()
    
    foreach ($key in $Expected.Keys) {
        $expectedItem = $Expected[$key]
        $itemPath = Join-Path $Path $key
        
        if ($expectedItem -is [hashtable]) {
            # É um diretório
            if (Test-Path $itemPath -PathType Container) {
                Write-Host "${Indent}✅ $key/" -ForegroundColor Green
                $subResult = Verify-Structure -Path $itemPath -Expected $expectedItem -Indent "$Indent  "
                $missing += $subResult.Missing
                $extra += $subResult.Extra
                $found += $subResult.Found
            } else {
                Write-Host "${Indent}❌ $key/ (FALTANDO)" -ForegroundColor Red
                $missing += $itemPath
            }
        } else {
            # É um arquivo
            if (Test-Path $itemPath -PathType Leaf) {
                Write-Host "${Indent}✅ $key" -ForegroundColor Green
                $found += $itemPath
            } else {
                Write-Host "${Indent}❌ $key (FALTANDO)" -ForegroundColor Red
                $missing += $itemPath
            }
        }
    }
    
    return @{
        Missing = $missing
        Extra = $extra
        Found = $found
    }
}

# ============================================
# Verificar arquivos temporários na raiz
# ============================================

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📁 Verificando Estrutura de Pastas e Arquivos" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$result = Verify-Structure -Path $rootPath -Expected $expectedStructure

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📋 Verificando Arquivos Temporários na Raiz" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

$tempFiles = @(
    "COMANDO_*.md",
    "COMANDOS_*.md",
    "CORRECAO_*.md",
    "CORRECOES_*.md",
    "RESUMO_*.md",
    "PROXIMOS_PASSOS_*.md",
    "PROXIMO_PASSO_*.md",
    "PROGRESSO_*.md",
    "GUIA_*.md",
    "LIMPEZA_*.md",
    "SOLUCAO_*.md",
    "REMOVER_*.md",
    "INSTRUCOES_*.md",
    "PLANO_*.md",
    "EXECUTAR_*.md",
    "FINAL_*.md"
)

$foundTempFiles = @()
foreach ($pattern in $tempFiles) {
    $files = Get-ChildItem -Path $rootPath -Filter $pattern -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $foundTempFiles += $file.Name
        Write-Host "⚠️  $($file.Name) (arquivo temporário)" -ForegroundColor Yellow
    }
}

# ============================================
# Resumo
# ============================================

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Resumo da Verificação" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Arquivos/Pastas encontrados: $($result.Found.Count)" -ForegroundColor Green
Write-Host "❌ Arquivos/Pastas faltando: $($result.Missing.Count)" -ForegroundColor $(if ($result.Missing.Count -eq 0) { "Green" } else { "Red" })
Write-Host "⚠️  Arquivos temporários na raiz: $($foundTempFiles.Count)" -ForegroundColor $(if ($foundTempFiles.Count -eq 0) { "Green" } else { "Yellow" })

if ($result.Missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Arquivos/Pastas faltando:" -ForegroundColor Red
    foreach ($item in $result.Missing) {
        Write-Host "  - $item" -ForegroundColor Red
    }
}

if ($foundTempFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  Arquivos temporários encontrados (devem ser removidos):" -ForegroundColor Yellow
    foreach ($file in $foundTempFiles) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "💡 Para remover arquivos temporários:" -ForegroundColor Cyan
    Write-Host "   git rm COMANDO_*.md CORRECAO_*.md RESUMO_*.md PROXIMOS_PASSOS_*.md LIMPEZA_*.md SOLUCAO_*.md REMOVER_*.md INSTRUCOES_*.md PLANO_*.md EXECUTAR_*.md FINAL_*.md" -ForegroundColor White
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Verificação concluída!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

