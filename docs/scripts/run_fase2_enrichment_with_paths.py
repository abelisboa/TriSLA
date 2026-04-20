#!/usr/bin/env python3
"""Executa enriquecimento Fase 2 (preferindo docs/scripts/fase2_transport_enrichment_v2.py)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    for rel in ("docs/scripts/fase2_transport_enrichment_v2.py", "scripts/fase2_transport_enrichment_v2.py"):
        target = root / rel
        if target.is_file():
            spec = importlib.util.spec_from_file_location("_f2enrich", target)
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return int(mod.main())
    print(f"[FAIL] Nenhum fase2_transport_enrichment_v2.py em {root}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
