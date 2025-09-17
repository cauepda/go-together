# Arquitetura do Sistema Go Together

## Diagrama de Arquitetura

```mermaid
graph TB
    subgraph "Cliente"
        UI[Streamlit App]
        CLI[CLI/Scripts]
    end
    
    subgraph "API Layer"
        API[FastAPI Server<br/>Port 8000]
    end
    
    subgraph "Core Services"
        PM[Passenger Matcher<br/>Haversine Algorithm]
        CC[Cost Calculator<br/>Per-km pricing]
        LD[Location Data<br/>Predefined locations]
    end
    
    subgraph "MCP Integration"
        MCP[MCP AWS Pricing Server<br/>stdio protocol]
        AWS_API[AWS Pricing API<br/>boto3]
    end
    
    subgraph "AWS Services"
        LAMBDA[AWS Lambda<br/>go-together-api-v2]
        PRICING[AWS Pricing Service]
    end
    
    subgraph "Data Storage"
        MEM[(In-Memory Storage<br/>Routes & Matches)]
    end
    
    UI --> API
    CLI --> API
    API --> PM
    API --> CC
    API --> LD
    API --> MEM
    
    PM --> CC
    CC --> MCP
    MCP --> AWS_API
    AWS_API --> PRICING
    
    API -.-> LAMBDA
    
    classDef client fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef core fill:#e8f5e8
    classDef mcp fill:#fff3e0
    classDef aws fill:#ffebee
    classDef storage fill:#f1f8e9
    
    class UI,CLI client
    class API api
    class PM,CC,LD core
    class MCP,AWS_API mcp
    class LAMBDA,PRICING aws
    class MEM storage
```

## Componentes

### 1. **Interface do Usuário**
- **Streamlit App**: Interface web para cadastro e visualização
- **CLI/Scripts**: Testes e automação

### 2. **API Layer**
- **FastAPI Server**: API REST com endpoints para matching
- **Endpoints**: `/routes`, `/find-matches`, `/routes` (GET)

### 3. **Core Services**
- **Passenger Matcher**: Algoritmo Haversine para matching geográfico
- **Cost Calculator**: Cálculo de divisão de custos por passageiro
- **Location Data**: Localizações pré-definidas de São Paulo

### 4. **MCP Integration**
- **MCP Server**: Protocolo stdio para integração com Amazon Q
- **AWS Pricing API**: Estimativas de custo em tempo real

### 5. **AWS Services**
- **Lambda**: Deploy da API (go-together-api-v2)
- **Pricing Service**: Dados de preços AWS

### 6. **Storage**
- **In-Memory**: Armazenamento temporário de rotas e matches

## Fluxo de Dados

1. **Cadastro de Rota**: UI → API → Storage
2. **Busca de Match**: UI → API → Matcher → Cost Calculator → Response
3. **Estimativa AWS**: API → MCP → AWS Pricing → Response
4. **Deploy**: Local API → AWS Lambda (via CDK)