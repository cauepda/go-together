# Setup MCP AWS Pricing Integration

## 1. Instalar dependências MCP
```bash
npm install -g @aws/aws-pricing-mcp-server
```

## 2. Configurar AWS credentials
```bash
aws configure
# ou definir variáveis de ambiente:
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

## 3. Verificar configuração MCP
```bash
cat ~/.aws/amazonq/agents/default.json
```

## 4. Testar integração
```bash
cd go-together
python3 test_mcp_integration.py
```

## 5. Usar prompt salvo
No Amazon Q chat:
```
@generate_cost_report Estime custos mensais do Lambda
```

## 6. Verificar ferramentas disponíveis
No Amazon Q chat:
```
/tools
```

## Exemplo de uso:

1. **Gerar relatório**: `@generate_cost_report`
2. **Calcular custos por grupo**: Automático no matching
3. **Verificar configuração**: `/tools` para listar ferramentas MCP

## Arquivos criados:
- `~/.aws/amazonq/agents/default.json` - Configuração MCP
- `mcp_aws_pricing.py` - Módulo de integração
- `~/.aws/amazonq/prompts/generate_cost_report.md` - Prompt salvo
- `test_mcp_integration.py` - Testes
- `passenger_matcher.py` - Atualizado com custos AWS