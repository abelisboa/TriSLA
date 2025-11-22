#!/usr/bin/env python3
"""
Auditoria de imagens TriSLA no GHCR (versão baseada em Docker)
Verifica existência de imagens usando docker manifest inspect
"""

import subprocess
import datetime
import os
from pathlib import Path
from textwrap import dedent

# ------------------------------------------------------------
# Configuração
# ------------------------------------------------------------

MODULES = [
    ("SEM-CSMF", "trisla-sem-csmf", "ontologia trisla.owl"),
    ("ML-NSMF", "trisla-ml-nsmf", "modelo ML (viability_model.pkl), scaler"),
    ("Decision Engine", "trisla-decision-engine", "consumidor I-03, produtor I-04/I-05"),
    ("BC-NSSMF", "trisla-bc-nssmf", "integração com Besu"),
    ("SLA-Agent Layer", "trisla-sla-agent-layer", "agentes RAN/Transporte/Core"),
    ("NASP Adapter", "trisla-nasp-adapter", "interface com NASP real"),
    ("UI Dashboard", "trisla-ui-dashboard", "interface de observação TriSLA"),
]

DEFAULT_USER = "abelisboa"
GHCR_USER = os.environ.get("GHCR_USER", DEFAULT_USER)
REGISTRY = f"ghcr.io/{GHCR_USER}"

DOCS_PATH = Path(__file__).parent.parent / "docs" / "IMAGES_GHCR_MATRIX.md"


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    """Executa comando e retorna resultado"""
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def check_docker_available() -> None:
    """Verifica se Docker está disponível"""
    result = run_cmd(["docker", "version", "--format", "{{.Server.Version}}"])
    if result.returncode != 0:
        print("❌ Docker não encontrado ou não está em execução.")
        print("   Detalhes:", result.stderr.strip())
        raise SystemExit(1)


def image_exists(image_ref: str) -> bool:
    """
    Verifica se a imagem existe no registry usando:
        docker manifest inspect <image-ref>
    Se retornar código 0, consideramos que a imagem existe.
    """
    result = run_cmd(["docker", "manifest", "inspect", image_ref])
    return result.returncode == 0


def main() -> None:
    """Função principal"""
    print("🔍 Auditando imagens GHCR (via docker manifest inspect)...\n")

    check_docker_available()

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    rows = []
    ok_count = 0
    missing_count = 0

    for module_name, image_name, note in MODULES:
        image_ref = f"{REGISTRY}/{image_name}:latest"
        print(f"Verificando {module_name} ({image_name})... ", end="", flush=True)

        if image_exists(image_ref):
            status = "✅ OK"
            tag_status = "✅"
            obs = note
            ok_count += 1
            print("✅")
        else:
            status = "❌ FALTANDO"
            tag_status = "❌"
            obs = note
            missing_count += 1
            print("❌")

        rows.append(
            (
                module_name,
                f"`{image_ref}`",
                tag_status,
                status,
                obs,
            )
        )

    # Garantir que diretório docs existe
    DOCS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Gerar Markdown
    header = dedent(
        f"""
        # Matriz de Imagens GHCR — TriSLA

        **Data:** {now}
        **Gerado por:** scripts/audit_ghcr_images.py
        **GHCR User:** {GHCR_USER}

        ---

        ## Introdução Conceitual

        Todas as imagens Docker do TriSLA são publicadas no **GitHub Container Registry (GHCR)**.
        Esta matriz é baseada em verificações reais via:

        ```bash
        docker manifest inspect ghcr.io/{GHCR_USER}/trisla-<module-name>:latest
        ```

        Uma imagem é considerada **OK** se o comando acima retornar código de saída 0.

        ### Estrutura de Nomenclatura

        - **Registry base:** `ghcr.io/{GHCR_USER}/`
        - **Formato:** `ghcr.io/{GHCR_USER}/trisla-<module-name>`
        - **Tag padrão avaliada:** `latest`

        ---

        ## Tabela Principal de Imagens

        | Módulo | Imagem GHCR (com tag) | Tag Padrão | Status de Auditoria | Observação |
        |--------|-----------------------|------------|---------------------|------------|
        """
    ).strip("\n")

    table_lines = []
    for module_name, image_ref, tag_status, status, note in rows:
        table_lines.append(
            f"| {module_name} | {image_ref} | {tag_status} | {status} | {note} |"
        )

    footer = dedent(
        f"""

        ---

        ## Status de Auditoria

        **Última auditoria:** {now}

        **Resumo:**
        - ✅ Imagens OK: {ok_count}
        - ❌ Imagens faltando: {missing_count}

        ---

        ## Como interpretar este relatório

        - **✅ OK** : a imagem foi localizada com sucesso no GHCR via `docker manifest inspect`.
        - **❌ FALTANDO** : o comando retornou erro. Verifique se:
          - a imagem realmente foi publicada com a tag `latest`; ou
          - existe algum problema de autenticação ou de rede com o registry.

        ---

        ## Como Publicar Imagens Faltantes

        Se uma imagem estiver marcada como **FALTANDO**, siga estes passos:

        ### Método Automático (Recomendado)

        **Bash (Linux/macOS/WSL):**
        ```bash
        export GHCR_TOKEN="ghp_xxxxxxxxxxxx"
        ./scripts/publish_all_images_ghcr.sh
        ```

        **PowerShell (Windows):**
        ```powershell
        $env:GHCR_TOKEN = "ghp_xxxxxxxxxxxx"
        .\scripts\publish_all_images_ghcr.ps1
        ```

        ### Método Manual

        1. **Login no GHCR:**
           ```bash
           echo $GHCR_TOKEN | docker login ghcr.io -u abelisboa --password-stdin
           ```

        2. **Build e push da imagem:**
           ```bash
           docker buildx build \\
             -t ghcr.io/abelisboa/trisla-<module-name>:latest \\
             -f apps/<module-name>/Dockerfile \\
             --platform linux/amd64 \\
             --push \\
             ./apps/<module-name>
           ```

        3. **Reexecutar auditoria:**
           ```bash
           python3 scripts/audit_ghcr_images.py
           ```

        **Guia completo:** `docs/GHCR_PUBLISH_GUIDE.md`

        ---

        **Versão:** 2.0
        **ENGINE MASTER:** Sistema de Auditoria GHCR TriSLA (docker-based)
        """
    ).rstrip() + "\n"

    DOCS_PATH.write_text(header + "\n" + "\n".join(table_lines) + footer, encoding="utf-8")

    print("\n✅ Relatório salvo em:", DOCS_PATH.resolve())
    print("\n📊 Resumo:")
    print(f"   ✅ Imagens OK: {ok_count}")
    print(f"   ❌ Imagens faltando: {missing_count}")

    if missing_count > 0:
        print("\n⚠️ Ação necessária: Publicar imagens faltantes no GHCR")
        print("   Execute: ./scripts/publish_all_images_ghcr.sh")
        return 1
    else:
        print("\n✅ Todas as imagens estão disponíveis no GHCR")
        return 0


if __name__ == "__main__":
    exit(main())
