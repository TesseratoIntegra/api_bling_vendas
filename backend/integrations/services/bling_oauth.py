import requests
import secrets

from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
import logging


logger = logging.getLogger(__name__)


class BlingOAuthService:
    """
    Serviço para gerenciar autenticação OAuth 2.0 com o Bling ERP
    """

    def __init__(self):
        self.api_url = settings.BLING_API_URL
        self.client_id = settings.BLING_CLIENT_ID
        self.client_secret = settings.BLING_CLIENT_SECRET
        self.redirect_uri = settings.BLING_REDIRECT_URI

    def generate_auth_url(self):
        """
        Gera URL de autorização para iniciar o fluxo OAuth
        """
        # Gera state para segurança
        state = secrets.token_urlsafe(32)

        # Salva o state no cache por 10 minutos
        cache.set(f'oauth_state_{state}', True, 600)

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'read write'  # Ajuste os escopos conforme necessário
        }

        auth_url = f"https://www.bling.com.br/Api/v3/oauth/authorize?{urlencode(params)}"
        return auth_url, state

    def validate_state(self, state):
        """
        Valida o state retornado pelo OAuth
        """
        cache_key = f'oauth_state_{state}'
        if cache.get(cache_key):
            cache.delete(cache_key)
            return True
        return False

    def exchange_code_for_tokens(self, code, state):
        """
        Troca o código de autorização pelos tokens de acesso
        """
        if not self.validate_state(state):
            raise ValueError("State inválido ou expirado")

        token_url = "https://www.bling.com.br/Api/v3/oauth/token"

        # Credenciais no formato Basic Auth (Base64)
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()

        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {credentials_b64}',  # Credenciais no header
            'User-Agent': 'Bling-Integration/1.0'
        }

        try:
            response = requests.post(token_url, data=data, headers=headers, timeout=30)

            # Log da requisição para debug (sem mostrar credenciais completas)
            logger.info(f"Token request URL: {token_url}")
            logger.info(f"Token request data: {data}")
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")

            response.raise_for_status()

            tokens = response.json()

            # Salva os tokens no cache (ajuste o tempo conforme o expires_in)
            expires_in = tokens.get('expires_in', 3600)
            cache.set('bling_access_token', tokens['access_token'], expires_in - 60)

            if 'refresh_token' in tokens:
                # Refresh token geralmente tem vida útil maior
                cache.set('bling_refresh_token', tokens['refresh_token'], expires_in * 24)

            logger.info("Tokens OAuth obtidos com sucesso")
            return tokens

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao obter tokens: {e}")
            logger.error(f"Response status: {response.status_code}")
            logger.error(f"Response content: {response.text}")

            # Retorna detalhes do erro para debug (sem credenciais)
            error_details = {
                'status_code': response.status_code,
                'response_text': response.text,
                'request_url': token_url
            }
            raise Exception(f"Erro na autenticação Bling: {e}. Detalhes: {error_details}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição: {e}")
            raise Exception(f"Erro de conexão: {e}")

    def refresh_access_token(self):
        """
        Renova o access token usando o refresh token
        """
        refresh_token = cache.get('bling_refresh_token')
        if not refresh_token:
            raise ValueError("Refresh token não encontrado. Necessário reautenticar.")

        token_url = "https://www.bling.com.br/Api/v3/oauth/token"

        # Credenciais no formato Basic Auth (Base64)
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {credentials_b64}',  # Credenciais no header
            'User-Agent': 'Bling-Integration/1.0'
        }

        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()

            tokens = response.json()

            # Atualiza os tokens no cache
            expires_in = tokens.get('expires_in', 3600)
            cache.set('bling_access_token', tokens['access_token'], expires_in - 60)

            if 'refresh_token' in tokens:
                cache.set('bling_refresh_token', tokens['refresh_token'], expires_in * 24)

            logger.info("Access token renovado com sucesso")
            return tokens

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao renovar token: {e}")
            raise Exception(f"Erro ao renovar token: {e}")

    def get_valid_access_token(self):
        """
        Retorna um access token válido, renovando se necessário
        """
        access_token = cache.get('bling_access_token')
        
        if access_token:
            return access_token

        # Tenta renovar o token
        try:
            tokens = self.refresh_access_token()
            return tokens['access_token']
        except:
            # Se não conseguir renovar, precisa reautenticar
            raise ValueError("Token expirado. Necessário reautenticar.")

    def revoke_tokens(self):
        """
        Revoga os tokens (logout)
        """
        access_token = cache.get('bling_access_token')

        if access_token:
            revoke_url = f"{self.api_url}/oauth/revoke"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }

            try:
                response = requests.post(revoke_url, headers=headers)
                response.raise_for_status()
                logger.info("Tokens revogados com sucesso")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Erro ao revogar tokens: {e}")

        # Remove do cache
        cache.delete('bling_access_token')
        cache.delete('bling_refresh_token')

    def is_authenticated(self):
        """
        Verifica se há tokens válidos
        """
        try:
            self.get_valid_access_token()
            return True
        except:
            return False
