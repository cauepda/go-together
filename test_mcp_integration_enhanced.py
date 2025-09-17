#!/usr/bin/env python3
"""
Teste da integração MCP AWS Pricing com boto3
"""
import sys
import os
from mcp_aws_pricing import generate_cost_report, AWSPricingMCP
from passenger_matcher import PassengerMatcher, Passenger, Location

def test_aws_pricing_api():
    """Testa conexão com AWS Pricing API"""
    print("=== TESTE 1: AWS Pricing API ===")
    
    pricing = AWSPricingMCP()
    
    # Testar obtenção de preços
    pricing_data = pricing.get_lambda_pricing_from_aws()
    print(f"Request price: ${pricing_data['request_price']:.10f}")
    print(f"GB-second price: ${pricing_data['gb_second_price']:.10f}")
    
    # Testar estimativa de custos
    costs = pricing.estimate_lambda_costs()
    print(f"Pricing source: {costs['pricing_source']}")
    print(f"Monthly cost: ${costs['total_monthly_cost_usd']:.4f}")
    
    return costs['pricing_source'] == "AWS API"

def test_cost_report_generation():
    """Testa geração de relatório de custos"""
    print("\n=== TESTE 2: Geração de Relatório ===")
    
    report = generate_cost_report("Estime custos mensais do Lambda go-together-api-v2")
    print(report)
    
    # Verificar se relatório contém informações essenciais
    required_items = ["1,000,000", "200ms", "512MB", "TOTAL"]
    missing_items = [item for item in required_items if item not in report]
    
    if missing_items:
        print(f"❌ Itens faltando no relatório: {missing_items}")
        return False
    
    print("✅ Relatório gerado com sucesso")
    return True

def test_passenger_matching_with_costs():
    """Testa matching de passageiros com custos AWS"""
    print("\n=== TESTE 3: Matching com Custos AWS ===")
    
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
    
    if not groups:
        print("❌ Nenhum grupo encontrado")
        return False
    
    # Verificar se custos AWS estão incluídos
    for i, group in enumerate(groups, 1):
        print(f"\nGrupo {i}:")
        print(f"  Passageiros: {[p.name for p in group['passengers']]}")
        print(f"  Custo por pessoa: R$ {group['cost_per_person']}")
        
        if 'aws_cost_per_passenger_usd' not in group:
            print("❌ Custos AWS não encontrados no grupo")
            return False
            
        print(f"  Custo AWS por pessoa: ${group['aws_cost_per_passenger_usd']:.8f}")
        print(f"  Custo AWS total do match: ${group['aws_cost_per_match_usd']:.8f}")
    
    print("✅ Matching com custos AWS funcionando")
    return True

def test_error_handling():
    """Testa tratamento de erros"""
    print("\n=== TESTE 4: Tratamento de Erros ===")
    
    # Testar com credenciais inválidas (simulado)
    try:
        pricing = AWSPricingMCP()
        costs = pricing.estimate_lambda_costs()
        
        # Deve funcionar mesmo sem credenciais (fallback)
        if costs['total_monthly_cost_usd'] > 0:
            print("✅ Fallback pricing funcionando")
            return True
        else:
            print("❌ Fallback pricing falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🧪 INICIANDO TESTES MCP AWS PRICING INTEGRATION\n")
    
    tests = [
        ("AWS Pricing API", test_aws_pricing_api),
        ("Cost Report Generation", test_cost_report_generation),
        ("Passenger Matching with Costs", test_passenger_matching_with_costs),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "="*50)
    print("📋 RESUMO DOS TESTES:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(tests)} testes passaram")
    
    if passed == len(tests):
        print("🎉 Todos os testes passaram! Integração MCP funcionando.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique a configuração.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)