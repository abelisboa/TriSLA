# Sprint S3.5.17 — Governança final do Helm

## Objetivo
Eliminar definitivamente o Besu duplicado (trisla-trisla-besu) que causava ImagePullBackOff e poluição do cluster.

## Resultado
- ✅ Apenas 1 Deployment do Besu renderizado
- ✅ Nenhuma referência a `trisla-trisla-besu`
- ✅ Render validado via `helm template`
- ✅ SHA256 garante imutabilidade científica

## Correções Aplicadas
- Removido bloco `trisla-besu` de `values.yaml` (já estava comentado em `values-nasp.yaml`)
- Garantido que apenas o template `deployment-besu.yaml` pode gerar o Deployment do Besu
- Verificado que não há dependências Helm relacionadas a Besu

## Validações
- ✅ `helm lint` passa
- ✅ Render contém 1 e somente 1 Deployment Besu
- ✅ Nenhuma referência a `trisla-trisla-besu`
- ✅ Nenhuma dependência Helm fantasma

## Artefatos
- `render_besu_bc.yaml` - Render completo do Helm Chart (Besu + BC-NSSMF)
- `render_besu_bc.sha256` - Hash criptográfico SHA256 do render

## Próximo Deploy NASP
Após este sprint:
- ❌ Nunca mais será criado `trisla-trisla-besu`
- ✅ Deploy NASP terá Besu único
- ✅ Ambiente limpo e estável
- ✅ Encerramento definitivo da fase técnica

