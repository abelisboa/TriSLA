# TriSLA Source (FastAPI edition)

## Modules
- `src/semantic` — SEM-NSMF (FastAPI)
- `src/ai` — ML-NSMF (FastAPI)
- `src/blockchain` — BC-NSSMF (simulated entrypoint)
- `src/integration` — Integration Gateway (FastAPI)
- `src/monitoring` — Prometheus config

## Build & Push (GHCR)
1) Login
```bash
echo "YOUR_TOKEN" | docker login ghcr.io -u abelisboa --password-stdin
```

2) Build all
```bash
./build_all.sh
```

3) Push all
```bash
./push_all.sh
```

## Local test (example)
```bash
docker run -p 8080:8080 ghcr.io/abelisboa/trisla-semantic:latest
curl http://localhost:8080/health
```
