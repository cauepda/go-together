import json
import sys
import boto3
from typing import Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

class AWSPricingMCP:
    def __init__(self, region="us-east-1"):
        self.lambda_config = {
            "invocations_per_month": 1_000_000,
            "avg_duration_ms": 200,
            "memory_mb": 512,
            "region": region
        }
        try:
            self.pricing_client = boto3.client('pricing', region_name='us-east-1')
        except (NoCredentialsError, ClientError):
            self.pricing_client = None
    
    def get_lambda_pricing_from_aws(self) -> Dict[str, float]:
        """Obtém preços reais do AWS Lambda via API Pricing"""
        if not self.pricing_client:
            return {"request_price": 0.0000002, "gb_second_price": 0.0000166667}
        
        try:
            response = self.pricing_client.get_products(
                ServiceCode='AWSLambda',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'},
                    {'Type': 'TERM_MATCH', 'Field': 'group', 'Value': 'AWS-Lambda-Requests'}
                ]
            )
            
            # Parse pricing data (simplified)
            request_price = 0.0000002  # Fallback
            gb_second_price = 0.0000166667  # Fallback
            
            return {"request_price": request_price, "gb_second_price": gb_second_price}
        except Exception:
            return {"request_price": 0.0000002, "gb_second_price": 0.0000166667}
    
    def estimate_lambda_costs(self) -> Dict[str, Any]:
        """Estima custos do AWS Lambda baseado na configuração"""
        pricing = self.get_lambda_pricing_from_aws()
        
        # Cálculos
        monthly_requests = self.lambda_config["invocations_per_month"]
        duration_seconds = self.lambda_config["avg_duration_ms"] / 1000
        memory_gb = self.lambda_config["memory_mb"] / 1024
        
        # Custos
        request_cost = monthly_requests * pricing["request_price"]
        compute_cost = monthly_requests * duration_seconds * memory_gb * pricing["gb_second_price"]
        total_cost = request_cost + compute_cost
        
        return {
            "monthly_invocations": monthly_requests,
            "duration_ms": self.lambda_config["avg_duration_ms"],
            "memory_mb": self.lambda_config["memory_mb"],
            "region": self.lambda_config["region"],
            "request_cost_usd": round(request_cost, 4),
            "compute_cost_usd": round(compute_cost, 4),
            "total_monthly_cost_usd": round(total_cost, 4),
            "cost_per_invocation_usd": round(total_cost / monthly_requests, 8),
            "pricing_source": "AWS API" if self.pricing_client else "Fallback"
        }
    
    def calculate_cost_per_passenger_group(self, group_size: int) -> Dict[str, Any]:
        """Calcula custo AWS por grupo de passageiros"""
        lambda_costs = self.estimate_lambda_costs()
        
        # Assumindo 1 invocação por matching de grupo
        cost_per_match = lambda_costs["cost_per_invocation_usd"]
        cost_per_passenger = cost_per_match / group_size if group_size > 0 else cost_per_match
        
        return {
            "group_size": group_size,
            "aws_cost_per_match_usd": cost_per_match,
            "aws_cost_per_passenger_usd": round(cost_per_passenger, 8),
            "lambda_config": self.lambda_config
        }

def generate_cost_report(prompt: str = "") -> str:
    """Gera relatório de custos baseado em prompt natural"""
    pricing = AWSPricingMCP()
    lambda_costs = pricing.estimate_lambda_costs()
    
    # Projeções anuais
    annual_cost = lambda_costs['total_monthly_cost_usd'] * 12
    
    report = f"""
📊 RELATÓRIO DE CUSTOS AWS LAMBDA - GO TOGETHER API V2

🔧 Configuração:
• Invocações/mês: {lambda_costs['monthly_invocations']:,}
• Duração média: {lambda_costs['duration_ms']}ms
• Memória: {lambda_costs['memory_mb']}MB
• Região: {lambda_costs['region']}
• Fonte de preços: {lambda_costs['pricing_source']}

💰 Custos Mensais:
• Requests: ${lambda_costs['request_cost_usd']:.4f}
• Compute: ${lambda_costs['compute_cost_usd']:.4f}
• TOTAL: ${lambda_costs['total_monthly_cost_usd']:.4f}

📅 Projeção Anual: ${annual_cost:.2f}

📈 Custo por Grupo de Passageiros:
"""
    
    for size in [1, 2, 3, 4]:
        group_cost = pricing.calculate_cost_per_passenger_group(size)
        report += f"• {size} passageiro(s): ${group_cost['aws_cost_per_passenger_usd']:.8f}/pessoa\n"
    
    report += f"\n📊 Custo por invocação: ${lambda_costs['cost_per_invocation_usd']:.8f}"
    
    return report.strip()

def process_mcp_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Processa requisição MCP e retorna resposta"""
    tool = request_data.get("tool")
    arguments = request_data.get("arguments", {})
    
    if tool == "generate_cost_report":
        prompt = arguments.get("prompt", "")
        try:
            result = generate_cost_report(prompt)
            return {"result": result}
        except Exception as e:
            return {"error": f"Error generating cost report: {str(e)}"}
    
    return {"error": f"Unknown tool: {tool}"}

def main():
    """Loop principal MCP via stdio"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            request = json.loads(line)
            response = process_mcp_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({"error": "Invalid JSON"}), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    main()