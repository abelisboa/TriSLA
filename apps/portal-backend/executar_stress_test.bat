@echo off
REM Script para executar o stress test completo no Windows
echo ========================================
echo STRESS TEST COMPLETO - TRI SLA
echo Capítulo 6 - Considerações Preliminares
echo ========================================
echo.

cd /d %~dp0

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

echo.
echo Executando orquestrador...
python tools\stress_test_orchestrator.py

echo.
echo ========================================
echo Execucao concluida!
echo ========================================
echo.
echo Verifique os arquivos gerados:
echo - backend\STRESS_TEST_REPORT.md
echo - backend\stress_test_report.json
echo - backend\figures\*.png
echo - backend\stress_test_orchestrator.log
echo.
pause




