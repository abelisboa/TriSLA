# Comandos Git para Refatoração

Execute estes comandos para commitar a refatoração do repositório:

## PowerShell (Windows)

```powershell
# 1. Adicionar todas as mudanças
git add .

# 2. Verificar status
git status

# 3. Criar commit
git commit -m "refactor: reorganize repository structure for open-source

- Move all REPORT*, INSTALL*, TROUBLESHOOTING* files to docs/reports/
- Organize GHCR documentation in docs/ghcr/
- Organize NASP documentation in docs/nasp/
- Move security documentation to docs/security/
- Move deployment guides to docs/deployment/
- Remove private content from Git (TriSLA_PROMPTS/, *.patch, *.db, etc.)
- Update .gitignore to exclude private artifacts
- Clean root directory to contain only essential files"

# 4. Push para o repositório
git push origin main
```

## Bash (Linux/macOS/WSL)

```bash
# 1. Adicionar todas as mudanças
git add .

# 2. Verificar status
git status

# 3. Criar commit
git commit -m "refactor: reorganize repository structure for open-source

- Move all REPORT*, INSTALL*, TROUBLESHOOTING* files to docs/reports/
- Organize GHCR documentation in docs/ghcr/
- Organize NASP documentation in docs/nasp/
- Move security documentation to docs/security/
- Move deployment guides to docs/deployment/
- Remove private content from Git (TriSLA_PROMPTS/, *.patch, *.db, etc.)
- Update .gitignore to exclude private artifacts
- Clean root directory to contain only essential files"

# 4. Push para o repositório
git push origin main
```

---

**Nota:** Revise o status do Git antes de fazer o commit para garantir que todas as mudanças estão corretas.

