@echo off
REM Script para build e push da imagem frontend v3.7.32
REM Execute este script no PowerShell ou CMD do Windows

echo Building frontend image v3.7.32...

cd /d "C:\Users\USER\Documents\TriSLA-clean\trisla-portal\frontend"

if not exist "Dockerfile" (
    echo Erro: Dockerfile nao encontrado!
    exit /b 1
)

REM Build da imagem
docker build -t ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32 --build-arg NEXT_PUBLIC_TRISLA_API_BASE_URL=http://localhost:8001/api/v1 .

if %ERRORLEVEL% NEQ 0 (
    echo Erro no build!
    exit /b 1
)

echo Build concluido com sucesso!
echo.
echo Fazendo push da imagem...

REM Push da imagem
docker push ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32

if %ERRORLEVEL% NEQ 0 (
    echo Erro no push!
    exit /b 1
)

echo Push concluido com sucesso!
echo.
echo Verificando imagem...
docker images | findstr trisla-portal-frontend | findstr v3.7.32

echo.
echo Imagem ghcr.io/abelisboa/trisla-portal-frontend:v3.7.32 pronta!
echo.
echo Proximos passos:
echo    1. Conectar ao NASP: ssh porvir5g@ppgca.unisinos.br
echo    2. SSH para node006: ssh node006
echo    3. Deploy: helm upgrade --install trisla-portal ./helm/trisla-portal -n trisla --create-namespace --wait

