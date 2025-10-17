# 🧭 Guia de Gestão GitHub — TriSLA@NASP
## Estratégia de Governança, Autoria e Execução entre Laptop, GitHub e NASP

---

## 🎯 Objetivo
Definir as melhores práticas de gestão do repositório GitHub para o projeto TriSLA@NASP, garantindo propriedade intelectual, continuidade científica e automação segura, mesmo após o desligamento da infraestrutura institucional (NASP — UNISINOS).

---

## ⚙️ Estrutura Recomendada
```
Laptop Abel  ←→  GitHub (abel-lisboa/trisla-nasp)
      ↓
   SSH remoto
      ↓
NASP (execução e coleta de métricas)
```

### Funções
- 💻 **Laptop pessoal:** ambiente principal de versionamento e commits.  
- ☁️ **GitHub:** repositório oficial e auditável.  
- 🖥️ **NASP:** executor remoto de experimentos e helm deploys.

---

## ⚖️ Comparativo de Estratégias
| Critério | Git no NASP | Git no Laptop |
|-----------|--------------|---------------|
| Autonomia | Baixa | Alta |
| Propriedade | Institucional | Pessoal |
| Acesso pós-defesa | Pode ser revogado | Permanente |
| Segurança | Depende da política do servidor | Total controle |
| Backup | Limitado | Permanente |

✅ **Conclusão:** Git vinculado ao **laptop pessoal**, NASP apenas executor remoto.

---

## 🧩 Configuração do Modelo Híbrido

### No Laptop
```bash
git clone https://github.com/abel-lisboa/trisla-nasp.git
cd trisla-nasp
git add .
git commit -m "WU-005: Atualização dos resultados experimentais"
git push origin main
```

### No NASP
```bash
ssh porvir5g@ppgca.unisinos.br
ssh node006
cd ~/trisla-nasp/
git pull origin main
bash run_trisla.sh
```

---

## 🔑 Habilitar CI/CD com Deploy Key NASP

No NASP:
```bash
ssh-keygen -t rsa -b 4096 -C "nasptrisla@unisinos"
cat ~/.ssh/id_rsa.pub
```

No GitHub:
- Settings → Deploy Keys → Add Key  
- Nome: `NASP-Deploy-Key`  
- Cole a chave pública e marque ✅ "Allow write access"

Teste a conexão:
```bash
ssh -T git@github.com
```

---

## 🧠 Workflow GitOps Recomendado

| Etapa | Ação | Responsável |
|-------|------|--------------|
| Desenvolvimento | Commits e versionamento | Laptop |
| Versionamento WUs | GitHub | GitOps |
| Execução | Helm / kubectl | NASP |
| Backups e métricas | Evidências / GitHub | Automático |

---

## 📘 Encerramento Pós-Defesa

1. NASP será desligado, mas o repositório GitHub permanece ativo.  
2. Gere uma tag de encerramento:
```bash
git tag -a v1.0-defense -m "Versão final TriSLA - Dissertação UNISINOS"
git push origin v1.0-defense
```
3. Opcional: tornar público após publicação do artigo.

---

## 🧩 Boas Práticas
- Cada WU = um commit (`WU-003: Integração NASP Core`)  
- Atualizar `docs/evidencias/` a cada execução  
- Evitar arquivos >50MB  
- Fazer backups regulares (`git push`)  
- Manter CI/CD ativo via deploy key NASP

---

📅 Última atualização: 16/10/2025  
👤 Autor: Abel José Rodrigues Lisboa  
🏛️ Projeto: TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
