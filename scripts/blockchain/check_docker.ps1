# Verifica e tenta iniciar Docker Desktop no Windows

Write-Host "[TriSLA] Verificando Docker..." -ForegroundColor Cyan

if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
        docker ps | Out-Null
        Write-Host "[TriSLA] ✅ Docker está rodando." -ForegroundColor Green
        exit 0
    } catch {
        Write-Host "[TriSLA] ⚠️  Docker instalado mas não está rodando." -ForegroundColor Yellow
        
        # Tentar iniciar Docker Desktop
        $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        if (Test-Path $dockerPath) {
            Write-Host "[TriSLA] Tentando iniciar Docker Desktop..." -ForegroundColor Cyan
            Start-Process $dockerPath
            
            Write-Host "[TriSLA] Aguardando Docker Desktop iniciar (30s)..." -ForegroundColor Cyan
            Start-Sleep -Seconds 30
            
            # Verificar novamente
            for ($i = 1; $i -le 10; $i++) {
                try {
                    docker ps | Out-Null
                    Write-Host "[TriSLA] ✅ Docker iniciado com sucesso!" -ForegroundColor Green
                    exit 0
                } catch {
                    Write-Host "[TriSLA] Esperando Docker... Tentativa $i/10" -ForegroundColor Yellow
                    Start-Sleep -Seconds 3
                }
            }
        }
        
        Write-Host "❌ ERRO: Docker não está rodando." -ForegroundColor Red
        Write-Host "   Por favor, inicie o Docker Desktop manualmente e tente novamente." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "❌ ERRO: Docker não está instalado." -ForegroundColor Red
    exit 1
}

