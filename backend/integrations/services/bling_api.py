import requests
import logging

from .bling_oauth import BlingOAuthService


logger = logging.getLogger(__name__)


class BlingAPIService:
    """
    Serviço para consumir a API do Bling ERP
    """

    def __init__(self):
        # URL correta da API do Bling
        self.api_url = "https://www.bling.com.br/Api/v3"
        self.oauth_service = BlingOAuthService()

    def _make_request(self, method, endpoint, params=None, data=None):
        """
        Faz requisições autenticadas para a API do Bling
        """
        try:
            access_token = self.oauth_service.get_valid_access_token()
        except ValueError as e:
            raise Exception(f"Erro de autenticação: {e}")

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        url = f"{self.api_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            else:
                raise ValueError(f"Método HTTP {method} não suportado")

            response.raise_for_status()

            # Se a resposta for 204 (No Content), retorna None
            if response.status_code == 204:
                return None

            return response.json()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP na API do Bling: {e}")
            logger.error(f"Resposta: {response.text}")
            raise Exception(f"Erro na API do Bling: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição: {e}")
            raise Exception(f"Erro de conexão: {e}")

    # PRODUTOS
    def get_products(self, page=1, limit=100, filters=None):
        """
        Lista produtos
        
        Args:
            page (int): Número da página
            limit (int): Itens por página (max 100)
            filters (dict): Filtros adicionais
        """
        params = {
            'pagina': page,
            'limite': limit
        }

        if filters:
            params.update(filters)

        return self._make_request('GET', '/produtos', params=params)

    def get_product(self, product_id):
        """
        Obtém um produto específico pelo ID
        """
        return self._make_request('GET', f'/produtos/{product_id}')

    def search_products(self, query, page=1, limit=100):
        """
        Busca produtos por termo
        """
        params = {
            'pagina': page,
            'limite': limit,
            'criterio': 1,  # Busca por código ou nome
            'termo': query
        }

        return self._make_request('GET', '/produtos', params=params)

    # VARIAÇÕES DE PRODUTO
    def get_product_variations(self, product_id, page=1, limit=100):
        """
        Lista variações de um produto
        """
        params = {
            'pagina': page,
            'limite': limit
        }

        return self._make_request('GET', f'/produtos/{product_id}/variacoes', params=params)

    def get_product_variation(self, product_id, variation_id):
        """
        Obtém uma variação específica de um produto
        """
        return self._make_request('GET', f'/produtos/{product_id}/variacoes/{variation_id}')

    # PEDIDOS
    def get_orders(self, page=1, limit=100, filters=None):
        """
        Lista pedidos

        Args:
            page (int): Número da página
            limit (int): Itens por página (max 100)
            filters (dict): Filtros como data_inicial, data_final, situacao, etc.
        """
        params = {
            'pagina': page,
            'limite': limit
        }

        if filters:
            params.update(filters)

        return self._make_request('GET', '/pedidos/vendas', params=params)

    def get_order(self, order_id):
        """
        Obtém um pedido específico pelo ID
        """
        return self._make_request('GET', f'/pedidos/vendas/{order_id}')

    def search_orders_by_number(self, order_number):
        """
        Busca pedido por número
        """
        params = {
            'numero': order_number
        }

        return self._make_request('GET', '/pedidos/vendas', params=params)

    def get_orders_by_date_range(self, start_date, end_date, page=1, limit=100):
        """
        Lista pedidos por período

        Args:
            start_date (str): Data inicial (formato: YYYY-MM-DD)
            end_date (str): Data final (formato: YYYY-MM-DD)
        """
        filters = {
            'dataInicial': start_date,
            'dataFinal': end_date
        }

        return self.get_orders(page=page, limit=limit, filters=filters)

    def get_orders_by_status(self, status, page=1, limit=100):
        """
        Lista pedidos por situação
        
        Args:
            status (str): Situação do pedido
        """
        filters = {
            'situacao': status
        }

        return self.get_orders(page=page, limit=limit, filters=filters)

    # CATEGORIAS DE PRODUTOS
    def get_categories(self, page=1, limit=100):
        """
        Lista categorias de produtos
        """
        params = {
            'pagina': page,
            'limite': limit
        }

        return self._make_request('GET', '/categorias/produtos', params=params)

    def get_category(self, category_id):
        """
        Obtém uma categoria específica pelo ID
        """
        return self._make_request('GET', f'/categorias/produtos/{category_id}')

    # CONTATOS (CLIENTES/FORNECEDORES)
    def get_contacts(self, page=1, limit=100, filters=None):
        """
        Lista contatos
        """
        params = {
            'pagina': page,
            'limite': limit
        }

        if filters:
            params.update(filters)

        return self._make_request('GET', '/contatos', params=params)

    def get_contact(self, contact_id):
        """
        Obtém um contato específico pelo ID
        """
        return self._make_request('GET', f'/contatos/{contact_id}')

    def search_contacts(self, query, page=1, limit=100):
        """
        Busca contatos por termo
        """
        params = {
            'pagina': page,
            'limite': limit,
            'criterio': 1,  # Busca por nome ou documento
            'termo': query
        }

        return self._make_request('GET', '/contatos', params=params)

    # MÉTODOS AUXILIARES PARA PAGINAÇÃO
    def get_all_products(self, filters=None, max_pages=None):
        """
        Obtém todos os produtos (com paginação automática)
        """
        all_products = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break

            response = self.get_products(page=page, filters=filters)

            if not response or 'data' not in response:
                break

            products = response['data']
            if not products:
                break

            all_products.extend(products)

            # Verifica se há mais páginas
            if len(products) < 100:  # Se retornou menos que o limite, é a última página
                break

            page += 1

        return all_products

    def get_all_orders(self, filters=None, max_pages=None):
        """
        Obtém todos os pedidos (com paginação automática)
        """
        all_orders = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break
 
            response = self.get_orders(page=page, filters=filters)

            if not response or 'data' not in response:
                break

            orders = response['data']
            if not orders:
                break

            all_orders.extend(orders)

            # Verifica se há mais páginas
            if len(orders) < 100:  # Se retornou menos que o limite, é a última página
                break

            page += 1

        return all_orders
