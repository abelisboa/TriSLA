# Load Tests - TriSLA Observability Portal

Testes de carga usando k6.

## Instalação

```bash
# Instalar k6
# Windows (via Chocolatey)
choco install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# macOS
brew install k6
```

## Executar Testes

```bash
# Teste básico
k6 run k6_script.js

# Com URL customizada
k6 run --env BASE_URL=http://localhost:8000 k6_script.js

# Com mais usuários
k6 run --vus 100 --duration 5m k6_script.js
```

## Cenários de Teste

1. **Ramp Up**: Aumento gradual de carga
2. **Sustained Load**: Carga constante
3. **Spike Test**: Picos de tráfego
4. **Stress Test**: Teste de limites

## Métricas

- **http_req_duration**: Latência das requisições
- **http_req_failed**: Taxa de erro
- **iterations**: Número de iterações
- **vus**: Virtual users ativos







