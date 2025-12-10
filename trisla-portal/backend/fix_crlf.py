#!/usr/bin/env python3
"""
Script para corrigir line endings (CRLF → LF) em arquivos Python e Shell
Garante formato UNIX para WSL2
"""
import os
import sys

def fix_line_endings(filepath):
    """Converte CRLF para LF em um arquivo"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Verificar se tem CRLF
        if b'\r\n' in content:
            # Converter CRLF para LF
            content = content.replace(b'\r\n', b'\n')
            
            # Salvar arquivo
            with open(filepath, 'wb') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Erro ao processar {filepath}: {e}", file=sys.stderr)
        return False

def main():
    """Processa todos os arquivos .py e .sh"""
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    fixed_count = 0
    
    # Processar arquivos .py
    for root, dirs, files in os.walk(os.path.join(base_dir, 'src')):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_line_endings(filepath):
                    print(f"✅ Corrigido: {filepath}")
                    fixed_count += 1
    
    # Processar arquivos .sh
    for file in os.listdir(base_dir):
        if file.endswith('.sh'):
            filepath = os.path.join(base_dir, file)
            if os.path.isfile(filepath):
                if fix_line_endings(filepath):
                    print(f"✅ Corrigido: {filepath}")
                    fixed_count += 1
    
    if fixed_count > 0:
        print(f"\n✅ {fixed_count} arquivo(s) corrigido(s)")
    else:
        print("\n✅ Nenhum arquivo precisou correção (já está em LF)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
