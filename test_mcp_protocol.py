#!/usr/bin/env python3
"""
Teste do protocolo MCP via stdio
"""
import subprocess
import json

def test_mcp_protocol():
    """Testa comunicação MCP via stdio"""
    print("🧪 TESTANDO PROTOCOLO MCP VIA STDIO\n")
    
    # Teste 1: Comando válido
    print("=== TESTE 1: Comando Válido ===")
    request = {
        "tool": "generate_cost_report",
        "arguments": {"prompt": "Estime custos mensais do Lambda"}
    }
    
    try:
        process = subprocess.Popen(
            ["python3", "mcp_aws_pricing.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(json.dumps(request))
        
        if stderr:
            print(f"⚠️  Stderr: {stderr}")
        
        response = json.loads(stdout.strip())
        
        if "result" in response:
            print("✅ Resposta recebida com sucesso")
            print(f"📊 Tamanho do relatório: {len(response['result'])} caracteres")
        else:
            print(f"❌ Erro na resposta: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    
    # Teste 2: Comando inválido
    print("\n=== TESTE 2: Comando Inválido ===")
    request = {"tool": "invalid_tool", "arguments": {}}
    
    try:
        process = subprocess.Popen(
            ["python3", "mcp_aws_pricing.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
        stdout, _ = process.communicate(json.dumps(request))
        response = json.loads(stdout.strip())
        
        if "error" in response and "Unknown tool" in response["error"]:
            print("✅ Erro tratado corretamente")
        else:
            print(f"❌ Resposta inesperada: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    
    # Teste 3: JSON inválido
    print("\n=== TESTE 3: JSON Inválido ===")
    
    try:
        process = subprocess.Popen(
            ["python3", "mcp_aws_pricing.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
        stdout, _ = process.communicate("invalid json")
        response = json.loads(stdout.strip())
        
        if "error" in response and "Invalid JSON" in response["error"]:
            print("✅ JSON inválido tratado corretamente")
        else:
            print(f"❌ Resposta inesperada: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
    
    print("\n🎉 Todos os testes do protocolo MCP passaram!")
    return True

if __name__ == "__main__":
    success = test_mcp_protocol()
    exit(0 if success else 1)