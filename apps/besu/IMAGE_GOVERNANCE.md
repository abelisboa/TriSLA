# Governança da Imagem Besu - TriSLA

## Imagem Oficial
- **Registry:** `ghcr.io/abelisboa/trisla-besu`
- **Tag:** `v3.7.16`
- **Base Image:** `hyperledger/besu:23.10.1`
- **Digest (último push):** `sha256:896b2f330fd1dc83cc18ba962bf697de30341e7da6f7706b1e2a01ed79e4cb92`

## Política de Acesso
- **Visibilidade:** Pública
- **Secret necessário:** Não
- **Compatibilidade NASP:** Sim

## Validação
- ✅ `docker pull ghcr.io/abelisboa/trisla-besu:v3.7.16` funciona localmente
- ✅ Helm Chart referencia: `ghcr.io/abelisboa/trisla-besu:v3.7.16`
- ✅ Resolve ImagePullBackOff em deployments NASP

## Sprint de Governança
- **Sprint:** S3.5.14_LOCAL
- **Data:** 2025-12-19
- **Objetivo:** Resolver definitivamente a governança da imagem Besu para compatibilidade NASP

## Build e Push
```bash
docker build -t ghcr.io/abelisboa/trisla-besu:v3.7.16 -f apps/besu/Dockerfile apps/besu
docker push ghcr.io/abelisboa/trisla-besu:v3.7.16
```

## Notas
- Imagem é um wrapper simples do `hyperledger/besu:23.10.1`
- Nenhuma modificação funcional é feita na imagem base
- A configuração do Besu (flags, probes) é feita via Helm Chart

