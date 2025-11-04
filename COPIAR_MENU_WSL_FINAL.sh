#!/bin/bash
# Script para copiar o menu do Windows para WSL
# Execute no WSL

cd ~/trisla-dashboard-local/scripts-wsl

# Copiar do Windows
cp /mnt/c/Users/USER/Documents/trisla-deploy/trisla-dashboard-local/scripts-wsl/dashboard-menu.sh .

# Dar permissão
chmod +x dashboard-menu.sh

echo "✅ Menu copiado e pronto!"
echo "🚀 Execute: ./dashboard-menu.sh"





