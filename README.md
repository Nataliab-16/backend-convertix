# 📦 Bling OAuth2 + API Flask

Este projeto demonstra como autenticar com a API do Bling usando OAuth2, salvar os tokens em um banco de dados SQLite com SQLAlchemy e usar esses tokens para consumir os endpoints da API do Bling.

---

## 🔐 `auth_utils.py`: Módulo de Autenticação

### Objetivo

Gerenciar todo o fluxo de autenticação com o Bling (OAuth 2.0), incluindo:
- Redirecionamento para autenticação
- Troca do código de autorização por tokens
- Armazenamento local de `access_token` e `refresh_token`
- Renovação automática do `access_token`

### Componentes principais

#### 🔹 Banco de Dados (SQLite)
Utiliza SQLAlchemy para armazenar os tokens em um arquivo `tokens.db`:
```python
class Token(Base):
    id = Column(Integer, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
```

#### 🔹 Funções
- `carregar_tokens()`: Lê o `access_token` e `refresh_token` salvos no banco.
- `salvar_tokens(tokens)`: Salva ou atualiza os tokens.
- `obter_token_por_codigo(code)`: Troca o `code` da URL pelo par de tokens.
- `refresh_access_token()`: Usa o `refresh_token` salvo para obter um novo `access_token`.
- `_get_basic_auth_header()`: Cria o header `Authorization: Basic` com `client_id:client_secret`.

#### 🔹 Rotas (`Blueprint`)
- `GET /`: Inicia o fluxo de login, redirecionando para o Bling.
- `GET /oauth/bling`: Callback que recebe o `code` e salva os tokens.

---

## 🚀 `api-bling.py`: API com Flask

Este arquivo define uma API REST que utiliza os tokens de autenticação para consultar a API do Bling.

### Funcionalidades

- Busca a lista de pedidos de vendas (`/pedidos/vendas`)
- Para cada venda, busca:
  - Detalhes da venda
  - Nome da vendedora associada

### Como funciona o fluxo?

1. A primeira rota acessada deve ser `/` para iniciar o login no Bling.
2. O Bling redireciona para `/oauth/bling` com um `code` de autorização.
3. Esse `code` é trocado por tokens e salvos no banco.
4. As rotas de dados (ex: `/pedidos/vendas`) usam o `access_token` para consultar dados protegidos na API.
5. Se o `access_token` estiver expirado, ele é renovado automaticamente via `refresh_token`.

### Rota principal da API
#### `GET /pedidos/vendas`
Parâmetros opcionais:
- `dataInicial=YYYY-MM-DD`
- `dataFinal=YYYY-MM-DD`

Retorna uma lista detalhada de vendas com nome da vendedora e valor total.

---

## 🧪 Exemplos de uso

1. **Iniciar login:**
   Acesse: `http://localhost:8080/`
   Isso abrirá o login do Bling e, ao finalizar, salvará os tokens localmente.

2. **Listar pedidos:**
   Faça uma requisição GET:
   ```
   http://localhost:8080/pedidos/vendas?dataInicial=2025-07-01&dataFinal=2025-07-03
   ```

---

## ⚙️ Variáveis de Ambiente (`.env`)

Certifique-se de ter um arquivo `.env` com os seguintes valores:

```
CLIENT_ID=seu_client_id_bling
CLIENT_SECRET=seu_client_secret_bling
REDIRECT_URI=http://localhost:8080/oauth/bling
```

---

## 📦 Requisitos

- Python 3.8+
- Flask
- SQLAlchemy
- python-dotenv
- requests
- flask-cors

Crie um ambiente virtual com:

```bash
python -m venv venv
venv\Scripts\activate
``` 
Para Windows ou:

```bash
python3 -m venv venv
source venv/bin/activate
```
Para Linux/MacOS


Instale as dependências com:
```bash
pip install -r requirements.txt
```

---

## ✅ Conclusão

Este projeto demonstra como implementar autenticação OAuth2 com Bling em Python + Flask, de forma modular e segura, permitindo consultas autenticadas na API de pedidos de vendas.