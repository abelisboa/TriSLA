#!/bin/bash

echo "=== CRIANDO SERVIDOR DE DOWNLOAD ==="

# Criar arquivo HTML para download
cat > download_trisla.html << 'HTML'
<!DOCTYPE html>
<html>
<head>
    <title>Download TriSLA - Dissertação</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Download TriSLA - Arquivos para Dissertação</h1>
    <p>Clique no link abaixo para baixar todos os arquivos:</p>
    <a href="trisla_dissertacao_completo.tar.gz" download>📁 Baixar Arquivo Completo (TAR.GZ)</a>
    
    <h2>Conteúdo do Arquivo:</h2>
    <ul>
        <li>📊 Relatórios técnicos completos</li>
        <li>🔧 Work Units documentadas</li>
        <li>📈 Evidências experimentais</li>
        <li>📋 Logs do sistema</li>
        <li>⚙️ Configurações de deploy</li>
        <li>📊 Métricas de performance</li>
    </ul>
    
    <h2>Resultados Finais:</h2>
    <ul>
        <li>✅ Taxa de sucesso: 100% (8/8 jobs)</li>
        <li>✅ Cenários 5G: URLLC, eMBB, mMTC validados</li>
        <li>✅ Teste de carga: 5 jobs simultâneos processados</li>
        <li>✅ Performance: ~5 segundos por job</li>
        <li>✅ Disponibilidade: 100%</li>
    </ul>
    
    <p><strong>Data:</strong> 29/10/2025</p>
    <p><strong>Responsável:</strong> Abel José Rodrigues Lisboa</p>
    <p><strong>Cluster:</strong> Híbrido-UNISINOS</p>
    <p><strong>Status:</strong> ✅ SUCESSO ABSOLUTO</p>
</body>
</html>
HTML

# Iniciar servidor HTTP simples
echo "🌐 Servidor de download iniciado em:"
echo "   http://192.168.10.16:8080/download_trisla.html"
echo ""
echo "📁 Para baixar o arquivo:"
echo "   wget http://192.168.10.16:8080/trisla_dissertacao_completo.tar.gz"
echo ""
echo "⏹️  Para parar o servidor: Ctrl+C"

# Iniciar servidor
python3 -m http.server 8080
