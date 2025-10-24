#!/usr/bin/env python3
# ================================================================
#  supervisor_check.py — Verificador de Estrutura TriSLA@NASP
#  Autor: Abel Lisboa | Projeto: TriSLA@NASP
#  Data: Outubro/2025
# ================================================================

import os
import json
from pathlib import Path

# --- Configurações ---
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIRS = ["STATE", "PROMPTS", "docs", "automation", "helm", "src"]
REPORT_FILE = ROOT / "structure_validation.json"

# --- Funções auxiliares ---
def check_directory_structure(root_path):
    """Verifica se todos os diretórios e arquivos obrigatórios existem."""
    results = {}

    for d in EXPECTED_DIRS:
        dir_path = root_path / d
        if dir_path.exists() and dir_path.is_dir():
            results[d] = {"status": "OK", "details": []}

            for file in dir_path.rglob("*"):
                if file.is_file():
                    results[d]["details"].append(str(file.relative_to(root_path)))
        else:
            results[d] = {"status": "MISSING", "details": []}
    return results


def print_colored(text, color):
    """Imprime texto colorido no terminal."""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "reset": "\033[0m",
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def main():
    print("\n🔍 Verificando estrutura TriSLA@NASP...\n")
    results = check_directory_structure(ROOT)

    ok_count = 0
    missing_count = 0

    for dir_name, info in results.items():
        if info["status"] == "OK":
            print_colored(f"[✔] Diretório {dir_name}: completo", "green")
            ok_count += 1
        else:
            print_colored(f"[✖] Diretório {dir_name}: ausente!", "red")
            missing_count += 1

    # --- Gerar relatório JSON ---
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print("\n--- Resumo ---")
    print_colored(f"Diretórios OK: {ok_count}", "green")
    print_colored(f"Diretórios ausentes: {missing_count}", "red" if missing_count > 0 else "green")

    if missing_count == 0:
        print_colored("\n✅ Estrutura TriSLA@NASP validada com sucesso!\n", "green")
    else:
        print_colored("\n⚠️  Estrutura incompleta. Verifique o arquivo structure_validation.json.\n", "yellow")


if __name__ == "__main__":
    main()
