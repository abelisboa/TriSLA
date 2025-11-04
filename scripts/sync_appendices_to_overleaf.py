#!/usr/bin/env python3
"""
Script de sincronização dos Apêndices TriSLA (Markdown → LaTeX)
Converte arquivos .md em .tex e os copia para o diretório Overleaf.
"""
import os
import re
from pathlib import Path

SRC = Path("./docs/apendices")
DEST = Path("/mnt/c/Users/USER/Documents/Dissertacao_TriSLA/Overleaf/apendices")

# Alternativa para Windows direto (se não usar WSL)
DEST_WIN = Path("C:/Users/USER/Documents/Dissertacao_TriSLA/Overleaf/apendices")

def markdown_to_latex(md_content: str) -> str:
    """Converte conteúdo Markdown básico para LaTeX."""
    # Substitui título principal por chapter
    tex = re.sub(r'^# 📘 (.+)$', r'\\chapter{\1}', md_content, flags=re.MULTILINE)
    
    # Substitui subtítulos
    tex = re.sub(r'^## (.+)$', r'\\section{\1}', tex, flags=re.MULTILINE)
    tex = re.sub(r'^### (.+)$', r'\\subsection{\1}', tex, flags=re.MULTILINE)
    
    # Substitui listas
    tex = re.sub(r'^- (.+)$', r'\\item \1', tex, flags=re.MULTILINE)
    
    # Substitui blocos de código
    tex = re.sub(r'```(\w+)?\n(.*?)```', r'\\begin{lstlisting}\n\2\n\\end{lstlisting}', tex, flags=re.DOTALL)
    
    # Substitui código inline
    tex = re.sub(r'`([^`]+)`', r'\\texttt{\1}', tex)
    
    # Substitui links
    tex = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'\\href{\2}{\1}', tex)
    
    return tex

def sync_appendices():
    """Sincroniza todos os apêndices Markdown para LaTeX."""
    # Tenta usar o caminho WSL primeiro, depois Windows direto
    dest_path = DEST if DEST.exists() or Path("/mnt/c").exists() else DEST_WIN
    
    os.makedirs(dest_path, exist_ok=True)
    
    if not SRC.exists():
        print(f"❌ Diretório fonte não encontrado: {SRC}")
        return
    
    synced_count = 0
    
    for file in SRC.glob("*.md"):
        if not file.is_file():
            continue
        
        print(f"📄 Processando: {file.name}")
        
        # Lê conteúdo Markdown
        with open(file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Converte para LaTeX
        tex_content = markdown_to_latex(md_content)
        
        # Gera nome do arquivo .tex
        tex_name = file.stem + ".tex"
        tex_path = dest_path / tex_name
        
        # Salva arquivo LaTeX
        with open(tex_path, 'w', encoding='utf-8') as out:
            out.write(tex_content)
        
        synced_count += 1
        print(f"  ✅ {tex_name}")
    
    print(f"\n✅ {synced_count} apêndice(s) sincronizado(s) com Overleaf.")
    print(f"📁 Destino: {dest_path}")

if __name__ == "__main__":
    sync_appendices()

