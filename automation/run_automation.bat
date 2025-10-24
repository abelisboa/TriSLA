@echo off
REM ==========================================
REM TriSLA Build & Publish Automation Launcher
REM ==========================================
REM Este arquivo facilita a execução do script PowerShell no Windows

echo.
echo 🚀 TriSLA Build & Publish Automation
echo =====================================
echo.

REM Verificar se PowerShell está disponível
powershell -Command "Get-Host" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PowerShell não encontrado
    pause
    exit /b 1
)

REM Verificar se o arquivo CSV existe
if not exist "PROMPTS\automation\TRISLA_PIPELINE_TRACKER.csv" (
    echo ❌ Arquivo CSV não encontrado: PROMPTS\automation\TRISLA_PIPELINE_TRACKER.csv
    pause
    exit /b 1
)

echo 📋 Opções disponíveis:
echo 1. Testar automação (sem executar comandos)
echo 2. Executar automação completa
echo 3. Executar em modo dry-run
echo 4. Sair
echo.

set /p choice="Escolha uma opção (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🧪 Executando testes...
    powershell -ExecutionPolicy Bypass -File "automation\test_automation.ps1"
) else if "%choice%"=="2" (
    echo.
    echo 🚀 Executando automação completa...
    powershell -ExecutionPolicy Bypass -File "automation\trisla_build_publish.ps1"
) else if "%choice%"=="3" (
    echo.
    echo ⚠️ Executando em modo dry-run...
    powershell -ExecutionPolicy Bypass -File "automation\trisla_build_publish.ps1" -DryRun
) else if "%choice%"=="4" (
    echo.
    echo 👋 Saindo...
    exit /b 0
) else (
    echo.
    echo ❌ Opção inválida
    pause
    exit /b 1
)

echo.
echo ✅ Execução concluída
pause
