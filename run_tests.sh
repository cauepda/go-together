#!/bin/bash

# Script para executar todos os testes do projeto Go Together

echo "🧪 EXECUTANDO TESTES DO GO TOGETHER"
echo "=================================="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8+"
    exit 1
fi

# Verificar se dependências estão instaladas
echo "📦 Verificando dependências..."
python3 -c "import boto3, fastapi, streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Instalando dependências..."
    pip install -r requirements.txt
fi

# Executar testes MCP
echo ""
echo "🔧 Testando integração MCP AWS Pricing..."
python3 test_mcp_integration_enhanced.py

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Todos os testes passaram!"
    echo ""
    echo "📋 PRÓXIMOS PASSOS:"
    echo "1. Configure AWS credentials: aws configure"
    echo "2. Use @generate_cost_report no Amazon Q"
    echo "3. Execute /tools para verificar MCP"
    echo ""
    echo "🔗 LINKS ÚTEIS:"
    echo "• Boto3 Pricing: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html"
    echo "• AWS Lambda Pricing: https://aws.amazon.com/lambda/pricing/"
    echo "• MCP Protocol: https://modelcontextprotocol.io/"
else
    echo ""
    echo "❌ Alguns testes falharam. Verifique a configuração."
    exit 1
fi