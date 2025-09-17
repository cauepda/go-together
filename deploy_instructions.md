# Deploy Instructions

## 1. Deploy Lambda API

### Arquivos necessários:
- `lambda_api.py` - API principal
- `requirements_lambda.txt` - Dependências

### Deploy via CDK:
```bash
# Usar o CDK já criado, substituindo o arquivo principal por lambda_api.py
```

### Endpoints da API:
- `GET /` - Status da API
- `POST /passengers` - Criar passageiro
- `GET /passengers` - Listar passageiros
- `POST /find-matches` - Buscar matches
- `DELETE /passengers` - Limpar todos
- `DELETE /passengers/{name}` - Remover específico

## 2. Deploy Streamlit

### Configurar URL da API:
1. Editar `.streamlit/secrets.toml`
2. Substituir `https://your-lambda-url.amazonaws.com` pela URL real do Lambda

### Deploy no Streamlit Cloud:
1. Usar arquivo `streamlit_lambda.py`
2. Configurar secrets no painel do Streamlit Cloud
3. Adicionar `LAMBDA_API_URL` com a URL do Lambda

### Teste local:
```bash
# Terminal 1 - API local (para testes)
uvicorn lambda_api:app --reload

# Terminal 2 - Streamlit
streamlit run streamlit_lambda.py
```

## 3. Arquivos criados:

- `lambda_api.py` - API FastAPI para Lambda
- `streamlit_lambda.py` - Interface que consome a API
- `requirements_lambda.txt` - Dependências do Lambda
- `.streamlit/secrets.toml` - Configuração da URL da API