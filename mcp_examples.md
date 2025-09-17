# Exemplos MCP Protocol - AWS Pricing

## Formato de Request JSON

```json
{
  "tool": "generate_cost_report",
  "arguments": {
    "prompt": "Estime custos mensais do Lambda go-together-api-v2"
  }
}
```

## Formato de Response JSON

### Sucesso:
```json
{
  "result": "📊 RELATÓRIO DE CUSTOS AWS LAMBDA - GO TOGETHER API V2\n\n🔧 Configuração:\n• Invocações/mês: 1,000,000\n• Duração média: 200ms\n• Memória: 512MB\n• Região: us-east-1\n• Fonte de preços: Fallback\n\n💰 Custos Mensais:\n• Requests: $0.2000\n• Compute: $1.6667\n• TOTAL: $1.8667\n\n📅 Projeção Anual: $22.40\n\n📈 Custo por Grupo de Passageiros:\n• 1 passageiro(s): $0.00000187/pessoa\n• 2 passageiro(s): $0.00000094/pessoa\n• 3 passageiro(s): $0.00000062/pessoa\n• 4 passageiro(s): $0.00000047/pessoa\n\n📊 Custo por invocação: $0.00000187"
}
```

### Erro:
```json
{
  "error": "Unknown tool: invalid_tool"
}
```

## Como Testar

### 1. Via linha de comando:
```bash
echo '{"tool": "generate_cost_report", "arguments": {"prompt": "test"}}' | python3 mcp_aws_pricing.py
```

### 2. Via script Python:
```python
import subprocess
import json

request = {"tool": "generate_cost_report", "arguments": {"prompt": "test"}}
process = subprocess.Popen(
    ["python3", "mcp_aws_pricing.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

stdout, _ = process.communicate(json.dumps(request))
response = json.loads(stdout)
print(response["result"])
```

## Ferramentas Disponíveis

- **generate_cost_report**: Gera relatório de custos AWS Lambda
  - Argumentos: `prompt` (string, opcional)
  - Retorna: Relatório formatado em texto