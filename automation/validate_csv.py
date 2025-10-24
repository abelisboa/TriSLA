#!/usr/bin/env python3
# ==========================================
# 🔍 TriSLA CSV Validator
# ==========================================
# Objetivo:
# Validar e mostrar informações sobre o arquivo CSV de acompanhamento

import csv
import os
from datetime import datetime

CSV_PATH = "PROMPTS/automation/TRISLA_PIPELINE_TRACKER.csv"

def validate_csv():
    """Valida o arquivo CSV e mostra informações."""
    print("🔍 Validando arquivo CSV do TriSLA...")
    print("=" * 50)
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Arquivo não encontrado: {CSV_PATH}")
        return False
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        
        print(f"✅ Arquivo CSV carregado: {len(rows)} linhas")
        
        if not rows:
            print("⚠️ Arquivo CSV vazio")
            return False
        
        # Mostrar campos disponíveis
        print(f"\n📋 Campos disponíveis ({len(rows[0].keys())}):")
        for field in rows[0].keys():
            print(f"  - {field}")
        
        # Analisar status
        status_count = {}
        pending_items = []
        
        for row in rows:
            status = row.get('Status Atual', '').strip()
            item = row.get('Item', 'Unknown')
            cmd = row.get('Comando Principal', '').strip()
            
            # Contar status
            if status in status_count:
                status_count[status] += 1
            else:
                status_count[status] = 1
            
            # Identificar pendentes
            if status in ['❌', '⚙️'] and cmd:
                pending_items.append({
                    'item': item,
                    'status': status,
                    'command': cmd
                })
        
        # Mostrar estatísticas
        print(f"\n📊 Estatísticas de Status:")
        for status, count in status_count.items():
            print(f"  {status}: {count}")
        
        print(f"\n🔄 Itens pendentes: {len(pending_items)}")
        
        if pending_items:
            print("\n📋 Itens pendentes:")
            for i, item in enumerate(pending_items, 1):
                print(f"  {i}. {item['item']} ({item['status']})")
                cmd_preview = item['command'][:60] + "..." if len(item['command']) > 60 else item['command']
                print(f"     Comando: {cmd_preview}")
        
        # Verificar última atualização
        print(f"\n🕒 Últimas atualizações:")
        recent_updates = []
        for row in rows:
            update_date = row.get('Data Última Atualização', '').strip()
            if update_date:
                recent_updates.append((row.get('Item', 'Unknown'), update_date))
        
        if recent_updates:
            # Ordenar por data (assumindo formato YYYY-MM-DD HH:MM)
            recent_updates.sort(key=lambda x: x[1], reverse=True)
            for item, date in recent_updates[:5]:  # Mostrar apenas os 5 mais recentes
                print(f"  - {item}: {date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar CSV: {e}")
        return False

def show_sample_commands():
    """Mostra comandos de exemplo para diferentes tipos de itens."""
    print(f"\n💡 Comandos de Exemplo:")
    print("=" * 50)
    
    examples = [
        ("Docker Build", "docker build -t ghcr.io/user/image:latest ./path"),
        ("Docker Push", "docker push ghcr.io/user/image:latest"),
        ("Helm Deploy", "helm upgrade --install app ./helm/chart -n namespace"),
        ("Kubectl Check", "kubectl get pods -n namespace"),
        ("Git Commit", "git add . && git commit -m 'message'"),
        ("Git Push", "git push origin main"),
        ("Test API", "curl -I http://localhost:8000/health"),
        ("Check Logs", "kubectl logs -n namespace -l app=name --tail=50")
    ]
    
    for desc, cmd in examples:
        print(f"  {desc}:")
        print(f"    {cmd}")
        print()

if __name__ == "__main__":
    success = validate_csv()
    
    if success:
        show_sample_commands()
        print("✅ Validação concluída com sucesso!")
    else:
        print("❌ Validação falhou!")
    
    print(f"\n📄 Arquivo: {CSV_PATH}")
    print(f"🕒 Validado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
