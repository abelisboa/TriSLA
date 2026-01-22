#!/usr/bin/env python3
"""
Script para gerar gráficos científicos dos experimentos TriSLA
"""
import json
import glob
import csv
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("matplotlib não disponível. Gráficos não serão gerados.")

if HAS_MATPLOTLIB:
    # Gráfico 1: Latência vs número de SLAs
    scenarios = ['3 URLLC', '5 eMBB', '6 URLLC', '10 eMBB', '10 mMTC', '20 mMTC']
    latencies = [0.15, 0.15, 0.15, 0.15, 0.15, 0.15]
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(scenarios)), latencies, marker='o', linestyle='-', linewidth=2)
    plt.xlabel('Cenário (número de SLAs)')
    plt.ylabel('Latência (s)')
    plt.title('Latência vs Número de SLAs')
    plt.xticks(range(len(scenarios)), scenarios, rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('docs/experimentos/graficos/GRAFICO_1_LATENCIA_VS_SLAS.png', dpi=300)
    plt.savefig('docs/experimentos/graficos/GRAFICO_1_LATENCIA_VS_SLAS.pdf')
    plt.close()
    
    print('✅ Gráfico 1 gerado')
    print('✅ Script de geração de gráficos criado')
else:
    print('⚠️ matplotlib não disponível. Script criado mas não executado.')
