# Go Together - Sistema de Matching de Caronas

API FastAPI para matching inteligente de caronas com cálculo automático de divisão de custos.

## Funcionalidades

- **Matching por coordenadas**: Algoritmo baseado em fórmula de Haversine
- **Divisão de custos**: Cálculo automático de custos por passageiro
- **API REST**: Endpoints para criar rotas e buscar matches
- **Economia estimada**: Calcula economia vs. viagem individual

## Instalação

```bash
pip install -r requirements.txt
```

## Executar API

```bash
python3 api.py
```

A API estará disponível em `http://localhost:8000`

## Endpoints

### POST /routes
Cria nova rota de motorista
```json
{
  "driver_id": "motorista1",
  "start": {"lat": -23.5505, "lon": -46.6333, "name": "Centro SP"},
  "end": {"lat": -23.5629, "lon": -46.6544, "name": "Vila Madalena"},
  "max_detour_km": 5.0,
  "cost_per_km": 1.5
}
```

### POST /find-matches
Busca matches para passageiro
```json
{
  "passenger_id": "passageiro1",
  "pickup": {"lat": -23.5475, "lon": -46.6361, "name": "República"},
  "dropoff": {"lat": -23.5558, "lon": -46.6396, "name": "Consolação"}
}
```

### GET /routes
Lista todas as rotas disponíveis

## Testar

```bash
python3 test_api.py
```

## Documentação

Acesse `http://localhost:8000/docs` para documentação interativa da API.

## Prompts utilizados:

1. Gere um script Python para matching de caronas baseado em coordenadas e crie testes unitários para função de matching de rotas
2. Crie uma API Python que receba dados de usuários e retorne matches de carona com divisão de custos, aqui vamos utilizar FastAPI
3. Gere um app Streamlit para cadastro de caronas e exibição de matches, pense que haverá um usuário preenchendo qual será a origem, o destino será um lugar fixo para todos os usuários.
4. Reformule nossa aplicação pensando no seguinte cenário: Não haverá motorista, somente passageiros, que posteriormente devem ser conectados, pode ser via celular (o passageiro deve informar no cadastro);
5. Vamos improvisar a questão da localização de origem, no momento está difícil de colocar o local específico, melhore isso de alguma forma, sendo oferecendo possibilidades de local como é feito no google maps ou até mesmo mostrando um mapa para o usuário colocar onde ele irá sair, veja o que fica melhor e faça.
6. Gere código AWS CDK para deploy de uma API FastAPI em Lambda, irei fazer o deploy justamente dessa que estamos utilizando
