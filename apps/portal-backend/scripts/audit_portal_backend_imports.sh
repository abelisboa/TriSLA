#!/usr/bin/env bash
set -euo pipefail

BASE=~/gtp5g/trisla/apps/portal-backend

echo "=================================================="
echo "TriSLA Portal Backend Import Audit"
echo "=================================================="

cd "$BASE"

echo
echo "[1] Estrutura src:"
find src -type f | sort

echo
echo "[2] Utils:"
find src -type f | grep utils || true

echo
echo "[3] Imports src.utils:"
grep -R "src.utils" src || true

echo
echo "[4] Imports src.services:"
grep -R "src.services" src || true

echo
echo "[5] Imports src.config:"
grep -R "src.config" src || true

echo
echo "[6] Imports quebráveis:"
python3 - <<'PY'
import os,re

base='src'

mods=[]

for root,_,files in os.walk(base):
    for f in files:
        if f.endswith('.py'):
            p=os.path.join(root,f)
            with open(p) as fh:
                txt=fh.read()
            for m in re.findall(r'from (src\.[\w\.]+) import',txt):
                mods.append((p,m))

for file,mod in mods:
    rel=mod.replace('.','/')+'.py'
    if not os.path.exists(rel):
        pkg=mod.replace('.','/')
        if not os.path.exists(pkg):
            print(f'BROKEN: {file} -> {mod}')
PY

echo
echo "=================================================="
echo "Audit complete"
echo "=================================================="
