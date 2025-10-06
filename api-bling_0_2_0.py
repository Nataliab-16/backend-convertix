from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import time
import requests
from dotenv import load_dotenv
from auth_utils import (
    auth_bp,
    carregar_tokens,
    salvar_tokens,
    refresh_access_token
)
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Configuração inicial ===
load_dotenv()
app = Flask(__name__)
CORS(app, origins="*")
app.register_blueprint(auth_bp)

# === Constantes e variáveis de ambiente ===
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
API_BASE_URL = 'https://www.bling.com.br/Api/v3'
RATE_LIMIT = 3  # máx 3 requisições por segundo
SLEEP_SECONDS = 1.2  # leve folga para segurança

# === Funções auxiliares ===

def obter_headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

def buscar_lista_vendas(headers, data_inicial=None, data_final=None):
    """Busca todas as páginas de vendas da API Bling"""
    url = f'{API_BASE_URL}/pedidos/vendas'
    pagina = 1
    limite = 100
    todas_vendas = []

    while True:
        params = {
            "pagina": pagina,
            "limite": limite
        }
        if data_inicial:
            params["dataInicial"] = data_inicial
        if data_final:
            params["dataFinal"] = data_final

        print(f"📄 Buscando página {pagina} com params: {params}")
        resp = requests.get(url, headers=headers, params=params)

        if resp.status_code != 200:
            raise RuntimeError(f'Erro ao buscar pedidos: {resp.text}')

        vendas = resp.json().get('data', [])
        if not vendas:
            break

        todas_vendas.extend(vendas)
        pagina += 1
        time.sleep(SLEEP_SECONDS)

    return todas_vendas

def buscar_detalhes_venda(venda_id, headers):
    """Busca os detalhes de uma venda específica"""
    url = f'{API_BASE_URL}/pedidos/vendas/{venda_id}'
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f'Erro ao buscar detalhes da venda {venda_id}: {resp.text}')
    return resp.json().get('data', {})

def buscar_nome_vendedora(vendedora_id, headers, cache):
    """Retorna o nome da vendedora a partir do ID, usando cache local"""
    if not vendedora_id:
        return None
    if vendedora_id in cache:
        return cache[vendedora_id]

    time.sleep(SLEEP_SECONDS)  # respeita rate limit
    url = f'{API_BASE_URL}/vendedores/{vendedora_id}'
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        nome = resp.json().get('data', {}).get('contato', {}).get('nome')
        cache[vendedora_id] = nome
        return nome

    print(f"❌ Erro ao buscar vendedora {vendedora_id}: {resp.text}")
    return None

def processar_venda(venda, headers, cache_vendedoras):
    """Processa uma única venda: busca detalhes e nome da vendedora"""
    venda_id = venda.get('id')
    if not venda_id:
        return None

    try:
        time.sleep(SLEEP_SECONDS)  # respeita rate limit
        dados_venda = buscar_detalhes_venda(venda_id, headers)
        id_vendedora = dados_venda.get('vendedor', {}).get('id')
        nome_vendedora = buscar_nome_vendedora(id_vendedora, headers, cache_vendedoras)

        return {
            'id_venda': dados_venda.get('id'),
            'numero_venda': dados_venda.get('numero'),
            'id_vendedora': id_vendedora,
            'nome_vendedora': nome_vendedora,
            'data_venda': dados_venda.get('data'),
            'valor_total': dados_venda.get('totalProdutos')
        }

    except Exception as e:
        print(f"Erro ao processar venda {venda_id}: {e}")
        return None

# === Rota principal ===

@app.route('/pedidos/vendas', methods=['GET'])
def get_detalhes_vendas():
    try:
        # Verifica e atualiza token de acesso
        refresh_access_token()
        tokens = carregar_tokens()
        access_token = tokens.get('access_token')

        if not access_token:
            return jsonify({"error": "Token de acesso não encontrado. Faça login via /"}), 401

        headers = obter_headers(access_token)

        # Captura filtros de data
        data_inicial = request.args.get("dataInicial")
        data_final = request.args.get("dataFinal")

        # Busca lista de vendas
        lista_vendas = buscar_lista_vendas(headers, data_inicial, data_final)
        cache_vendedoras = {}

        resultados = []
        with ThreadPoolExecutor(max_workers=RATE_LIMIT) as executor:
            futuros = [
                executor.submit(processar_venda, venda, headers, cache_vendedoras)
                for venda in lista_vendas
            ]

            for futuro in as_completed(futuros):
                resultado = futuro.result()
                if resultado:
                    resultados.append(resultado)

        return jsonify({"vendas": resultados}), 200

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500
    

@app.route('/vendedora/<int:vendedora_id>', methods=['GET'])
def get_nome_vendedora(vendedora_id):
    try:
        # Atualiza token de acesso
        refresh_access_token()
        tokens = carregar_tokens()
        access_token = tokens.get('access_token')

        if not access_token:
            return jsonify({"error": "Token de acesso não encontrado. Faça login via /"}), 401

        headers = obter_headers(access_token)
        cache_vendedoras = {}

        # Chama a função que busca o nome da vendedora
        nome_vendedora = buscar_nome_vendedora(vendedora_id, headers, cache_vendedoras)

        if nome_vendedora:
            return jsonify({
                "id_vendedora": vendedora_id,
                "nome_vendedora": nome_vendedora
            }), 200
        else:
            return jsonify({
                "error": f"Não foi possível encontrar a vendedora com ID {vendedora_id}"
            }), 404

    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

# === Execução ===
