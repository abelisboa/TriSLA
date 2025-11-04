# 🎮 Menu Interativo TriSLA Dashboard

## 📋 Script Único com Menu

**Arquivo:** `scripts-wsl/dashboard-menu.sh`

Script interativo completo para gerenciar todos os serviços do dashboard com um menu numerado.

---

## 🚀 Como Usar

### 1. Dar Permissão de Execução (primeira vez)

```bash
cd ~/trisla-dashboard-local
chmod +x scripts-wsl/dashboard-menu.sh
```

### 2. Executar o Menu

```bash
./scripts-wsl/dashboard-menu.sh
```

---

## 📋 Opções do Menu

### 🌐 **ABRIR NO NAVEGADOR**

| Número | Nome | URL | Descrição |
|--------|------|-----|-----------|
| **1** | Frontend Dashboard | http://localhost:5173 | Interface principal do dashboard React |
| **2** | Backend API | http://localhost:5000 | API FastAPI principal |
| **3** | Swagger Docs | http://localhost:5000/docs | Documentação interativa da API |
| **4** | Health Check | http://localhost:5000/health | Status de saúde da API |

---

### 🚀 **INICIAR SERVIÇOS**

| Número | Nome | Ação |
|--------|------|------|
| **5** | Iniciar Backend | Inicia o servidor FastAPI na porta 5000 |
| **6** | Iniciar Frontend | Inicia o servidor Vite na porta 5173 |
| **7** | Iniciar Tudo | Inicia Backend + Frontend simultaneamente |

---

### 🛑 **PARAR SERVIÇOS**

| Número | Nome | Ação |
|--------|------|------|
| **8** | Parar Backend | Para o servidor FastAPI |
| **9** | Parar Frontend | Para o servidor Vite |
| **10** | Parar Tudo | Para todos os serviços |

---

### 🔄 **REINICIAR**

| Número | Nome | Ação |
|--------|------|------|
| **11** | Reiniciar Backend | Para e inicia o backend novamente |
| **12** | Reiniciar Frontend | Para e inicia o frontend novamente |
| **13** | Reiniciar Tudo | Reinicia todos os serviços |

---

### 📋 **INFORMAÇÕES**

| Número | Nome | Ação |
|--------|------|------|
| **14** | Ver Logs do Backend | Mostra últimas 50 linhas do log do backend |
| **15** | Ver Logs do Frontend | Mostra últimas 50 linhas do log do frontend |
| **16** | Status Detalhado | Mostra status completo com PIDs |

---

### 👋 **SAIR**

| Número | Nome | Ação |
|--------|------|------|
| **0** | Sair | Encerra o menu |

---

## 🎯 Exemplo de Uso

```bash
# 1. Iniciar o menu
./scripts-wsl/dashboard-menu.sh

# 2. Escolher opção 7 (Iniciar Tudo)
# 3. Aguardar serviços iniciarem
# 4. Escolher opção 1 (Abrir Frontend)
# 5. Trabalhar normalmente
# 6. Quando terminar, opção 10 (Parar Tudo)
# 7. Opção 0 (Sair)
```

---

## 🔧 Funcionalidades

### ✅ Status Automático

O menu mostra sempre o status atual:
- ✅ Verde = Serviço rodando
- ❌ Vermelho = Serviço parado

### ✅ Verificação de Porta

Antes de iniciar, verifica se a porta já está em uso.

### ✅ Detecção de Processos

Identifica processos rodando pelos PIDs.

### ✅ Logs em Tempo Real

Armazena logs em `backend.log` e `frontend.log`.

### ✅ Abrir Navegador Automático

Tenta abrir automaticamente usando:
- `wslview` (recomendado no WSL)
- `cmd.exe /c start` (fallback)
- `xdg-open` (fallback Linux puro)

---

## 🐛 Troubleshooting

### Script não executa

```bash
chmod +x scripts-wsl/dashboard-menu.sh
```

### Porta já em uso

O menu detecta automaticamente e oferece opção de parar o serviço antigo.

### Navegador não abre

Abra manualmente as URLs mostradas no menu.

### Logs não aparecem

Verifique se os arquivos `backend.log` e `frontend.log` existem na raiz do projeto.

---

## 📝 Arquivos Criados pelo Script

- `backend.pid` - PID do processo backend
- `frontend.pid` - PID do processo frontend
- `backend.log` - Logs do backend
- `frontend.log` - Logs do frontend

---

## 🎨 Interface

O menu é atualizado dinamicamente e mostra:
- Status de cada serviço
- PIDs dos processos
- URLs disponíveis
- Feedback colorido (verde/vermelho/amarelo)

---

**Agora você tem controle total do dashboard com um único script interativo!** 🎉





