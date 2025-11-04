#!/usr/bin/env python3
import os, re, json
out = []
for root, _, files in os.walk("./apps"):
    for f in files:
        if f.endswith((".py", ".sol")):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            refs = re.findall(r'I-\d{2}', content)
            for r in set(refs):
                out.append({"interface": r, "file": path})
open("./docs/MATRIZ_RASTREABILIDADE.md","w", encoding='utf-8').write(
    "| Interface | Arquivo Fonte |\n|------------|----------------|\n" +
    "\n".join([f"| {i['interface']} | {i['file']} |" for i in sorted(out, key=lambda x:x['interface'])])
)
print(f"✅ Matriz de rastreabilidade gerada com {len(out)} vínculos.")

