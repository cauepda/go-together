#!/usr/bin/env python3
from mcp_aws_pricing import generate_cost_report, AWSPricingMCP
from passenger_matcher import PassengerMatcher, Passenger, Location

def test_mcp_integration():
    """Testa integração MCP com sistema de matching"""
    
    # Teste 1: Relatório de custos
    print("=== TESTE 1: Relatório de Custos ===")
    report = generate_cost_report("Estime custos mensais do Lambda")
    print(report)
    
    # Teste 2: Matching com custos AWS
    print("\n=== TESTE 2: Matching com Custos AWS ===")
    
    # Criar passageiros de teste
    passengers = [
        Passenger("João", "+5511999999999", 
                 Location(-23.5505, -46.6333, "Centro SP"),
                 Location(-23.5629, -46.6544, "Vila Madalena")),
        Passenger("Maria", "+5511888888888",
                 Location(-23.5475, -46.6361, "República"), 
                 Location(-23.5629, -46.6544, "Vila Madalena")),
        Passenger("Pedro", "+5511777777777",
                 Location(-23.5558, -46.6396, "Consolação"),
                 Location(-23.5629, -46.6544, "Vila Madalena"))
    ]
    
    # Encontrar grupos
    groups = PassengerMatcher.find_passenger_groups(passengers)
    
    # Exibir resultados com custos AWS
    for i, group in enumerate(groups, 1):
        print(f"\nGrupo {i}:")
        print(f"  Passageiros: {[p.name for p in group['passengers']]}")
        print(f"  Custo por pessoa: R$ {group['cost_per_person']}")
        print(f"  Custo AWS por pessoa: ${group['aws_cost_per_passenger_usd']:.8f}")
        print(f"  Custo AWS total do match: ${group['aws_cost_per_match_usd']:.8f}")

if __name__ == "__main__":
    test_mcp_integration()