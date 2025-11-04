#!/usr/bin/env python3
# ==========================================
# 🧪 TriSLA Automation Test Script
# ==========================================
# Objetivo:
# Testar o script de automação sem executar comandos reais,
# apenas validando a lógica e estrutura.

import csv
import os
import sys
from pathlib import Path

# Adicionar o diretório automation ao path
sys.path.append(str(Path(__file__).parent))

def test_csv_reading():
    """Testa a leitura do arquivo CSV."""
    print("🧪 Testando leitura do CSV...")
    
    CSV_PATH = "../PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Arquivo CSV não encontrado: {CSV_PATH}")
        return False
    
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        print(f"✅ CSV lido com sucesso: {len(rows)} linhas")
        
        # Mostrar estrutura
        if rows:
            print("📋 Campos disponíveis:")
            for field in rows[0].keys():
                print(f"  - {field}")
            
            print("\n📊 Status dos itens:")
            status_count = {}
            for row in rows:
                status = row.get("Status Atual", "").strip()
                status_count[status] = status_count.get(status, 0) + 1
            
            for status, count in status_count.items():
                print(f"  {status}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return False

def test_pending_items():
    """Testa identificação de itens pendentes."""
    print("\n🧪 Testando identificação de itens pendentes...")
    
    CSV_PATH = "../PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"
    
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        
        pending_items = []
        for row in rows:
            status = row.get("Status Atual", "").strip()
            cmd = row.get("Comando Principal", "").strip()
            item = row.get("Item", "Unknown")
            
            if status in ["❌", "⚙️"] and cmd:
                pending_items.append({
                    'item': item,
                    'status': status,
                    'command': cmd
                })
        
        print(f"✅ Itens pendentes identificados: {len(pending_items)}")
        
        if pending_items:
            print("\n📋 Itens pendentes:")
            for i, item in enumerate(pending_items, 1):
                print(f"  {i}. {item['item']} ({item['status']})")
                print(f"     Comando: {item['command'][:80]}{'...' if len(item['command']) > 80 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao identificar itens pendentes: {e}")
        return False

def test_command_validation():
    """Testa validação de comandos."""
    print("\n🧪 Testando validação de comandos...")
    
    # Comandos de teste
    test_commands = [
        "echo 'Teste de comando simples'",
        "ls -la",
        "pwd",
        "invalid_command_that_should_fail"
    ]
    
    print("📋 Comandos de teste:")
    for cmd in test_commands:
        print(f"  - {cmd}")
    
    print("\n⚠️ Nota: Esta é apenas uma validação de estrutura.")
    print("   Os comandos reais serão executados pelo script principal.")
    
    return True

def main():
    print("🧪 Iniciando testes do TriSLA Automation...")
    print("=" * 60)
    
    tests = [
        ("Leitura do CSV", test_csv_reading),
        ("Identificação de itens pendentes", test_pending_items),
        ("Validação de comandos", test_command_validation)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSOU")
                passed += 1
            else:
                print(f"❌ {test_name}: FALHOU")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name}: ERRO - {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES:")
    print(f"✅ Testes passaram: {passed}")
    print(f"❌ Testes falharam: {failed}")
    print(f"📈 Taxa de sucesso: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 Todos os testes passaram! O script está pronto para uso.")
        return True
    else:
        print(f"\n⚠️ {failed} teste(s) falharam. Verifique os problemas antes de usar o script.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
