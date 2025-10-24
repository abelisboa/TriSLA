#!/bin/bash
mkdir -p WU-004_fix/src/{semantic,ai,integration,monitoring,blockchain}

cat > WU-004_fix/README_WU-004_FIX.md <<'EOF'
# 🧩 WU-004_FIX — Atualização dos Dockerfiles TriSLA para python:3.11-slim

## ✅ Objetivo
Atualizar todos os módulos TriSLA para incluir `curl` e migrar a base de imagem para `python:3.11-slim`.

## 🚀 Passos
cd /mnt/c/Users/USER/Documents/trisla-deploy
unzip WU-004_fix_python3.11.zip -o
./build_all.sh
./push_all.sh

Depois no NASP:
kubectl delete pods --all -n trisla-nsp
kubectl get pods -n trisla-nsp -w
kubectl exec -it trisla-semantic-layer-xxxxx -n trisla-nsp -- which curl
✅ Esperado: /usr/bin/curl
EOF

for mod in semantic ai integration monitoring; do
cat > WU-004_fix/src/$mod/Dockerfile <<'EOF'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl && apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
EOF
done

cat > WU-004_fix/src/blockchain/Dockerfile <<'EOF'
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl && apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["/app/entrypoint.sh"]
EOF

zip -r WU-004_fix_python3.11.zip WU-004_fix
echo "✅ Pacote gerado: WU-004_fix_python3.11.zip"
