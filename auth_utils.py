import os
import base64
import json
from flask import Blueprint, redirect, request, jsonify
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

auth_bp = Blueprint('auth', __name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

AUTHORIZATION_URL = 'https://www.bling.com.br/Api/v3/oauth/authorize'
TOKEN_URL = 'https://bling.com.br/Api/v3/oauth/token'

# --- Configuração do banco SQLite com SQLAlchemy ---
Base = declarative_base()
engine = create_engine('sqlite:///tokens.db', echo=False)
SessionLocal = sessionmaker(bind=engine)

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)

Base.metadata.create_all(engine)  # Cria a tabela caso não exista


def _get_basic_auth_header(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    """Cria header Authorization Basic para OAuth."""
    token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    return {'Authorization': f"Basic {token}"}


def carregar_tokens():
    """Carrega tokens do banco de dados."""
    session = SessionLocal()
    token = session.query(Token).first()
    session.close()
    if token:
        return {
            'access_token': token.access_token,
            'refresh_token': token.refresh_token
        }
    return {}


def salvar_tokens(tokens):
    """Salva tokens no banco de dados."""
    session = SessionLocal()
    token = session.query(Token).first()
    if token:
        token.access_token = tokens.get('access_token')
        token.refresh_token = tokens.get('refresh_token')
    else:
        token = Token(
            access_token=tokens.get('access_token'),
            refresh_token=tokens.get('refresh_token')
        )
        session.add(token)
    session.commit()
    session.close()


def obter_token_por_codigo(code):
    """Troca código de autorização pelo token de acesso e refresh token."""
    headers = _get_basic_auth_header()
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    return response


def refresh_access_token():
    """Renova o access token usando o refresh token salvo."""
    tokens = carregar_tokens()
    refresh_token = tokens.get('refresh_token')
    if not refresh_token:
        print("Nenhum refresh_token encontrado.")
        return False

    headers = _get_basic_auth_header()
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        token_data = response.json()
        salvar_tokens({
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token')
        })
        print("Access token renovado com sucesso.")
        return True
    else:
        print("Erro ao renovar token:", response.text)
        return False


@auth_bp.route('/', methods=['GET'])
def auth_bling():
    """Inicia o fluxo de OAuth redirecionando para o Bling."""
    state = os.urandom(16).hex()
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'state': state,
        'redirect_uri': REDIRECT_URI
    }
    redirect_url = f'{AUTHORIZATION_URL}?{urlencode(params)}'
    return redirect(redirect_url)


@auth_bp.route('/oauth/bling', methods=['GET'])
def oauth_callback():
    """Callback do OAuth que recebe o código e obtém tokens."""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Código de autorização não fornecido."}), 400

    response = obter_token_por_codigo(code)
    if response.status_code != 200:
        return jsonify({"error": "Erro ao obter token", "detalhes": response.text}), 400

    token_data = response.json()
    if 'access_token' not in token_data:
        return jsonify({"error": "Access token não encontrado na resposta."}), 400

    salvar_tokens({
        'access_token': token_data.get('access_token'),
        'refresh_token': token_data.get('refresh_token')
    })

    return jsonify({"message": "Token de acesso obtido com sucesso."}), 200
