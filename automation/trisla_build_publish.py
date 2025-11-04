#!/usr/bin/env python3
# ==========================================
# 🚀 TriSLA Build & Publish Automation
# ==========================================
# Objetivo:
# Automatizar o build e publicação de todos os módulos TriSLA pendentes,
# lendo o arquivo CSV de acompanhamento e atualizando o status automaticamente.

import csv
import subprocess
import datetime
import os
import sys
from pathlib import Path

# Configuração do arquivo CSV
CSV_PATH = "../PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"

def run_command(cmd):
    """Executa um comando shell e retorna sucesso/falha."""
    print(f"\n🧩 Executando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Sucesso: {cmd}")
            if result.stdout.strip():
                print(f"📤 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Falha: {cmd}")
            if result.stderr.strip():
                print(f"🚨 Erro: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"💥 Exceção ao executar '{cmd}': {e}")
        return False

def update_csv(rows):
    """Atualiza o CSV com o novo status."""
    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        print(f"📄 CSV atualizado: {CSV_PATH}")
        return True
    except Exception as e:
        print(f"💥 Erro ao atualizar CSV: {e}")
        return False

def validate_csv_structure(rows):
    """Valida se o CSV tem a estrutura esperada."""
    if not rows:
        print("⚠️ CSV vazio ou inválido")
        return False
    
    required_fields = ["Item", "Comando Principal", "Status Atual"]
    first_row = rows[0]
    
    for field in required_fields:
        if field not in first_row:
            print(f"⚠️ Campo obrigatório '{field}' não encontrado no CSV")
            return False
    
    return True

def get_current_timestamp():
    """Retorna timestamp atual formatado."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

def main():
    print("\n🚀 Iniciando automação TriSLA Build & Publish...")
    print("=" * 60)
    
    # Verificar se o arquivo CSV existe
    if not os.path.exists(CSV_PATH):
        print(f"❌ Arquivo CSV não encontrado: {CSV_PATH}")
        sys.exit(1)
    
    # Ler o CSV
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"💥 Erro ao ler CSV: {e}")
        sys.exit(1)
    
    # Validar estrutura do CSV
    if not validate_csv_structure(rows):
        print("❌ Estrutura do CSV inválida")
        sys.exit(1)
    
    print(f"📊 Total de itens no pipeline: {len(rows)}")
    
    # Filtrar itens pendentes
    pending_items = []
    for row in rows:
        status = row.get("Status Atual", "").strip()
        cmd = row.get("Comando Principal", "").strip()
        
        if status in ["❌", "⚙️"] and cmd:
            pending_items.append(row)
    
    print(f"🔄 Itens pendentes para execução: {len(pending_items)}")
    
    if not pending_items:
        print("✅ Nenhum item pendente encontrado!")
        return
    
    # Executar itens pendentes
    updated_rows = []
    success_count = 0
    failure_count = 0
    
    for row in rows:
        status = row.get("Status Atual", "").strip()
        cmd = row.get("Comando Principal", "").strip()
        item = row.get("Item", "Unknown")
        
        # Só executa itens com status ❌ ou ⚙️ e que tenham comando válido
        if status in ["❌", "⚙️"] and cmd:
            print(f"\n{'='*60}")
            print(f"🎯 Processando: {item}")
            print(f"📋 Comando: {cmd}")
            print(f"📊 Status atual: {status}")
            
            success = run_command(cmd)
            
            if success:
                row["Status Atual"] = "✅"
                row["Data Última Atualização"] = get_current_timestamp()
                print(f"✅ Concluído: {item}")
                success_count += 1
            else:
                row["Status Atual"] = "❌"
                row["Data Última Atualização"] = get_current_timestamp()
                print(f"❌ Falha ao executar: {item}")
                failure_count += 1
        
        updated_rows.append(row)
    
    # Atualizar CSV
    if update_csv(updated_rows):
        print(f"\n{'='*60}")
        print("📊 RESUMO DA EXECUÇÃO:")
        print(f"✅ Sucessos: {success_count}")
        print(f"❌ Falhas: {failure_count}")
        print(f"📄 Arquivo atualizado: {CSV_PATH}")
        print("✅ Pipeline TriSLA atualizado com sucesso!")
    else:
        print("❌ Falha ao atualizar CSV")
        sys.exit(1)

if __name__ == "__main__":
    main()
