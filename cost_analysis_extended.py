from mcp_aws_pricing import AWSPricingMCP

def extended_cost_analysis():
    """Análise estendida de custos para go-together-api-v2"""
    pricing = AWSPricingMCP()
    costs = pricing.estimate_lambda_costs()
    
    # Projeções anuais
    annual_cost = costs["total_monthly_cost_usd"] * 12
    
    # Cenários de crescimento
    scenarios = [
        {"name": "Atual", "multiplier": 1},
        {"name": "2x Crescimento", "multiplier": 2},
        {"name": "5x Crescimento", "multiplier": 5},
        {"name": "10x Crescimento", "multiplier": 10}
    ]
    
    print("📊 ANÁLISE ESTENDIDA - GO-TOGETHER-API-V2\n")
    print(f"💰 Custo Base Mensal: ${costs['total_monthly_cost_usd']:.4f}")
    print(f"💰 Custo Base Anual: ${annual_cost:.2f}\n")
    
    print("📈 CENÁRIOS DE CRESCIMENTO:")
    for scenario in scenarios:
        monthly = costs["total_monthly_cost_usd"] * scenario["multiplier"]
        yearly = monthly * 12
        invocations = costs["monthly_invocations"] * scenario["multiplier"]
        print(f"• {scenario['name']}: ${monthly:.2f}/mês | ${yearly:.2f}/ano | {invocations:,} invocações")
    
    print("\n🎯 OTIMIZAÇÕES POSSÍVEIS:")
    print("• Reduzir memória para 256MB: ~50% economia no compute")
    print("• Otimizar duração para 100ms: ~50% economia no compute")
    print("• Usar ARM Graviton2: ~20% economia adicional")

if __name__ == "__main__":
    extended_cost_analysis()