#!/usr/bin/env python3
"""
Script para corrigir terminações de linha em todos os scripts shell
Converte CRLF (Windows) para LF (Unix)
"""
import os
from pathlib import Path

def fix_line_endings(file_path):
    """Corrige terminações de linha de um arquivo"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Substitui CRLF e CR por LF
        original_content = content
        content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
        
        if content != original_content:
            with open(file_path, 'wb') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    
    scripts_to_fix = [
        backend_dir / "scripts" / "rebuild_venv.sh",
        backend_dir / "scripts" / "validar_instalacao.sh",
        backend_dir / "scripts" / "fix_line_endings.sh",
        backend_dir / "scripts" / "fix_all_line_endings.py",
    ]
    
    print("Corrigindo terminações de linha em scripts shell...")
    print()
    
    fixed_count = 0
    for script_path in scripts_to_fix:
        if script_path.exists():
            if fix_line_endings(script_path):
                print(f"✅ {script_path.name} - Corrigido")
                fixed_count += 1
            else:
                print(f"ℹ️  {script_path.name} - Já estava correto")
            # Garantir permissão de execução
            os.chmod(script_path, 0o755)
        else:
            print(f"⚠️  {script_path.name} - Não encontrado")
    
    print()
    print(f"✅ Correção concluída! {fixed_count} arquivo(s) corrigido(s).")

if __name__ == "__main__":
    main()

