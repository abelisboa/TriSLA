#!/usr/bin/env python3
"""
Script definitivo para corrigir terminações de linha em scripts shell
Força conversão CRLF/CR para LF (Unix)
"""
import os
from pathlib import Path

def fix_file_line_endings(file_path):
    """Corrige terminações de linha de um arquivo"""
    try:
        # Ler em modo binário
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Substituir CRLF e CR por LF
        original_content = content
        content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
        
        # Escrever de volta
        if content != original_content:
            with open(file_path, 'wb') as f:
                f.write(content)
            # Garantir permissão de execução
            os.chmod(file_path, 0o755)
            return True
        else:
            # Garantir permissão mesmo se não mudou
            os.chmod(file_path, 0o755)
            return False
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    script_dir = Path(__file__).parent
    backend_dir = script_dir
    
    scripts_to_fix = [
        backend_dir / "scripts" / "rebuild_venv.sh",
        backend_dir / "scripts" / "validar_instalacao.sh",
        backend_dir / "scripts" / "fix_line_endings.sh",
        backend_dir / "scripts" / "fix_all_line_endings.py",
        backend_dir / "corrigir_scripts.py",
    ]
    
    print("=" * 60)
    print("  🔧 CORREÇÃO DE TERMINAÇÕES DE LINHA")
    print("=" * 60)
    print()
    
    fixed_count = 0
    for script_path in scripts_to_fix:
        if script_path.exists():
            if fix_file_line_endings(script_path):
                print(f"✅ {script_path.name} - Corrigido (CRLF → LF)")
                fixed_count += 1
            else:
                print(f"ℹ️  {script_path.name} - Já estava correto (LF)")
        else:
            print(f"⚠️  {script_path.name} - Não encontrado")
    
    print()
    print("=" * 60)
    if fixed_count > 0:
        print(f"✅ {fixed_count} arquivo(s) corrigido(s)")
    else:
        print("✅ Todos os arquivos já estavam corretos")
    print("=" * 60)

if __name__ == "__main__":
    main()

