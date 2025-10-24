# WU-004_FIX_v4 — TriSLA AI e Semantic Layers (Build Final com curl ativo)

### Correções aplicadas
- Ajuste dos Dockerfiles para **preservar o `curl`** dentro das imagens.
- Remoção do `apt-get purge -y` genérico (que estava removendo o `curl`).
- Confirmação de compatibilidade com Python 3.11-slim.
- Adição de `requirements.txt` completos para reprodutibilidade total.

### Pastas
- **src/ai/** → Módulo TriSLA-AI (FastAPI + ML)
- **src/semantic/** → Módulo TriSLA-Semantic (FastAPI + Ontologia)

### Procedimento de build e push
```bash
docker build --no-cache -t ghcr.io/abelisboa/trisla-semantic:latest ./WU-004_fix_v4/src/semantic
docker build --no-cache -t ghcr.io/abelisboa/trisla-ai:latest ./WU-004_fix_v4/src/ai
docker push ghcr.io/abelisboa/trisla-semantic:latest
docker push ghcr.io/abelisboa/trisla-ai:latest
```

### Atualização no cluster NASP
```bash
sudo crictl rmi --prune
sudo crictl pull ghcr.io/abelisboa/trisla-ai:latest
sudo crictl pull ghcr.io/abelisboa/trisla-semantic:latest
kubectl rollout restart deployment trisla-ai-layer -n trisla-nsp
kubectl rollout restart deployment trisla-semantic-layer -n trisla-nsp
kubectl exec -it $(kubectl get pod -n trisla-nsp -l app=trisla-ai-layer -o name) -n trisla-nsp -- which curl
kubectl exec -it $(kubectl get pod -n trisla-nsp -l app=trisla-semantic-layer -o name) -n trisla-nsp -- which curl
```

✅ Esperado: `/usr/bin/curl`
