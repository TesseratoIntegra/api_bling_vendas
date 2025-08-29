import logging

from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services.bling_oauth import BlingOAuthService
from .services.bling_api import BlingAPIService

logger = logging.getLogger(__name__)


# TESTE E UTILITÁRIOS
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def test_integration(request):
    """
    View simples para testar se a integração está funcionando
    """
    return Response({
        'status': 'ok',
        'message': 'Integração Bling funcionando!',
        'version': '1.0.0',
        'endpoints': {
            'authentication': {
                'auth_start': '/integrations/auth/start/',
                'auth_status': '/integrations/auth/status/',
                'auth_callback': '/integrations/auth/callback/',
                'auth_logout': '/integrations/auth/logout/',
            },
            'products': {
                'list': '/integrations/products/',
                'detail': '/integrations/products/{id}/',
                'variations': '/integrations/products/{id}/variations/',
                'search': '/integrations/products/?search=termo',
            },
            'orders': {
                'list': '/integrations/orders/',
                'detail': '/integrations/orders/{id}/',
                'by_date': '/integrations/orders/?data_inicial=YYYY-MM-DD&data_final=YYYY-MM-DD',
            },
            'others': {
                'categories': '/integrations/categories/',
                'contacts': '/integrations/contacts/',
                'dashboard': '/integrations/dashboard/',
            }
        }
    })


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def api_health_check(request):
    """
    Verifica o status geral da API e conexões
    """
    try:
        oauth_service = BlingOAuthService()
        is_authenticated = oauth_service.is_authenticated()

        return Response({
            'api_status': 'healthy',
            'authentication_status': 'authenticated' if is_authenticated else 'not_authenticated',
            'cache_status': 'working',
            'timestamp': request.build_absolute_uri(),
        })
    except Exception as e:
        return Response({
            'api_status': 'unhealthy',
            'error': str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# AUTENTICAÇÃO OAUTH
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def start_authentication(request):
    """
    Inicia o processo de autenticação OAuth com o Bling
    """
    try:
        oauth_service = BlingOAuthService()
        auth_url, state = oauth_service.generate_auth_url()

        # Se for uma requisição do browser, redireciona diretamente
        if request.headers.get('accept', '').startswith('text/html'):
            return redirect(auth_url)

        # Se for uma requisição API, retorna JSON
        return Response({
            'auth_url': auth_url,
            'state': state,
            'message': 'Acesse a URL para autorizar a aplicação no Bling',
            'instructions': 'Abra a auth_url em uma nova aba para autorizar o acesso'
        })

    except Exception as e:
        logger.error(f"Erro ao iniciar autenticação: {e}")
        return Response(
            {'error': 'Erro ao iniciar autenticação', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_http_methods(["GET"])
def oauth_callback(request):
    """
    Callback do OAuth - recebe o código de autorização
    """
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    if error:
        logger.error(f"Erro no OAuth callback: {error}")
        return JsonResponse({
            'success': False,
            'error': error,
            'message': 'Erro na autorização'
        }, status=400)

    if not code or not state:
        return JsonResponse({
            'success': False,
            'error': 'Código ou state não fornecidos'
        }, status=400)

    try:
        oauth_service = BlingOAuthService()
        tokens = oauth_service.exchange_code_for_tokens(code, state)

        logger.info("Autenticação realizada com sucesso")

        return JsonResponse({
            'success': True,
            'message': 'Autenticação realizada com sucesso!',
            'expires_in': tokens.get('expires_in'),
            'next_steps': 'Agora você pode usar os endpoints da API'
        })

    except Exception as e:
        logger.error(f"Erro no callback OAuth: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Erro ao processar callback',
            'details': str(e)
        }, status=500)


@api_view(['POST', 'GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def logout_bling(request):
    """
    Revoga os tokens e faz logout do Bling
    """
    try:
        oauth_service = BlingOAuthService()
        oauth_service.revoke_tokens()
        
        return Response({
            'success': True,
            'message': 'Logout realizado com sucesso',
            'next_steps': 'Use /auth/start/ para reautenticar'
        })

    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        return Response(
            {'error': 'Erro no logout', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def auth_status(request):
    """
    Verifica o status da autenticação
    """
    try:
        oauth_service = BlingOAuthService()
        is_authenticated = oauth_service.is_authenticated()
        
        return Response({
            'authenticated': is_authenticated,
            'message': 'Autenticado' if is_authenticated else 'Não autenticado',
            'action_needed': None if is_authenticated else 'Acesse /auth/start/ para autenticar'
        })

    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        return Response(
            {'error': 'Erro ao verificar status', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# PRODUTOS
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_products(request):
    """
    Lista produtos do Bling

    Parâmetros:
    - page: Número da página (padrão: 1)
    - limit: Itens por página (padrão: 100, máx: 100)
    - search: Termo de busca
    - categoria: Filtrar por categoria
    """
    try:
        api_service = BlingAPIService()

        # Parâmetros de consulta
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 100)), 100)  # Máximo 100
        search = request.GET.get('search')

        if search:
            products = api_service.search_products(search, page, limit)
        else:
            # Filtros opcionais
            filters = {}
            if request.GET.get('categoria'):
                filters['criterio'] = 5  # Por categoria
                filters['termo'] = request.GET.get('categoria')

            products = api_service.get_products(page, limit, filters or None)

        # Adiciona metadados úteis
        if products and isinstance(products, dict):
            products['_metadata'] = {
                'page': page,
                'limit': limit,
                'search': search,
                'total_items': len(products.get('data', [])),
                'has_more': len(products.get('data', [])) == limit
            }

        return Response(products)

    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}")
        return Response(
            {'error': 'Erro ao buscar produtos', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_product_detail(request, product_identifier):
    """
    Obtém detalhes de um produto específico por ID ou código

    Parâmetros:
    - product_identifier: ID numérico ou código do produto
    """
    try:
        api_service = BlingAPIService()

        # Tenta primeiro como ID numérico
        try:
            product_id = int(product_identifier)
            product = api_service.get_product(product_id)
        except ValueError:
            # Se não for numérico, busca por código
            products_response = api_service.search_products(product_identifier)
            if products_response and 'data' in products_response:
                # Procura produto com código exato
                for p in products_response['data']:
                    if p.get('codigo') == product_identifier:
                        product = {'data': p}
                        break
                else:
                    return Response(
                        {
                            'error': f'Produto com código "{product_identifier}" não encontrado',
                            'suggestion': 'Verifique se o código está correto ou use o ID numérico'
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {
                        'error': f'Produto "{product_identifier}" não encontrado',
                        'suggestion': 'Verifique se o código/ID está correto'
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(product)

    except Exception as e:
        logger.error(f"Erro ao buscar produto {product_identifier}: {e}")
        return Response(
            {'error': 'Erro ao buscar produto', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_product_variations(request, product_identifier):
    """
    Lista variações de um produto (por ID ou código)

    NOTA: O endpoint de variações pode não estar disponível na API v3 do Bling.
    Esta função tenta diferentes abordagens para encontrar variações.
    """
    try:
        api_service = BlingAPIService()

        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 100)), 100)

        # Primeiro, obtém o ID do produto se for passado código
        try:
            product_id = int(product_identifier)
        except ValueError:
            # Busca o produto por código para obter o ID
            products_response = api_service.search_products(product_identifier)
            if products_response and 'data' in products_response:
                for p in products_response['data']:
                    if p.get('codigo') == product_identifier:
                        product_id = p['id']
                        break
                else:
                    return Response(
                        {'error': f'Produto com código "{product_identifier}" não encontrado'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {'error': f'Produto "{product_identifier}" não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )

        # Tenta buscar variações
        try:
            variations = api_service.get_product_variations(product_id, page, limit)
            return Response(variations)
        except Exception as variation_error:
            # Se falhar, tenta abordagem alternativa
            logger.warning(f"Endpoint de variações falhou: {variation_error}")

            # Busca produtos que podem ser variações (baseado no código)
            try:
                # Obtém o produto pai para pegar o código
                product_response = api_service.get_product(product_id)
                if product_response and 'data' in product_response:
                    parent_code = product_response['data'].get('codigo', '')

                    # Busca possíveis variações
                    search_patterns = [
                        f"{parent_code}-",  # Produtos com hífen
                        f"{parent_code}_",  # Produtos com underscore
                        f"{parent_code} ",  # Produtos com espaço
                    ]

                    all_variations = []
                    for pattern in search_patterns:
                        try:
                            search_result = api_service.search_products(pattern)
                            if search_result and 'data' in search_result:
                                for item in search_result['data']:
                                    code = item.get('codigo', '')
                                    # Verifica se realmente é uma variação
                                    if (code.startswith(parent_code) and 
                                        code != parent_code and 
                                        item['id'] != product_id):
                                        all_variations.append(item)
                        except:
                            continue

                    return Response({
                        'data': all_variations,
                        '_metadata': {
                            'method': 'alternative_search',
                            'parent_product_id': product_id,
                            'parent_code': parent_code,
                            'total_found': len(all_variations),
                            'note': 'Variações encontradas através de busca por código'
                        }
                    })
                else:
                    return Response({
                        'error': 'Não foi possível encontrar variações para este produto',
                        'details': 'Produto pai não encontrado'
                    }, status=status.HTTP_404_NOT_FOUND)

            except Exception as alt_error:
                logger.error(f"Erro na busca alternativa de variações: {alt_error}")
                return Response({
                    'error': 'Erro ao buscar variações',
                    'details': f'Endpoint não disponível: {variation_error}',
                    'note': 'O endpoint de variações pode não estar implementado na API v3 do Bling'
                }, status=status.HTTP_501_NOT_IMPLEMENTED)

    except Exception as e:
        logger.error(f"Erro ao buscar variações do produto {product_identifier}: {e}")
        return Response(
            {'error': 'Erro ao buscar variações', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# PEDIDOS
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_orders(request):
    """
    Lista pedidos do Bling

    Parâmetros:
    - page: Número da página (padrão: 1)
    - limit: Itens por página (padrão: 100, máx: 100)
    - data_inicial: Data inicial (YYYY-MM-DD)
    - data_final: Data final (YYYY-MM-DD)
    - situacao: Situação do pedido
    - numero: Número do pedido
    """
    try:
        api_service = BlingAPIService()

        # Parâmetros de consulta
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 100)), 100)

        # Filtros opcionais
        filters = {}
        if request.GET.get('data_inicial'):
            filters['dataInicial'] = request.GET.get('data_inicial')
        if request.GET.get('data_final'):
            filters['dataFinal'] = request.GET.get('data_final')
        if request.GET.get('situacao'):
            filters['situacao'] = request.GET.get('situacao')
        if request.GET.get('numero'):
            filters['numero'] = request.GET.get('numero')

        orders = api_service.get_orders(page, limit, filters or None)

        # Adiciona metadados
        if orders and isinstance(orders, dict):
            orders['_metadata'] = {
                'page': page,
                'limit': limit,
                'filters': filters,
                'total_items': len(orders.get('data', [])),
            }

        return Response(orders)

    except Exception as e:
        logger.error(f"Erro ao buscar pedidos: {e}")
        return Response(
            {'error': 'Erro ao buscar pedidos', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_order_detail(request, order_id):
    """
    Obtém detalhes de um pedido específico
    """
    try:
        api_service = BlingAPIService()
        order = api_service.get_order(order_id)

        return Response(order)

    except Exception as e:
        logger.error(f"Erro ao buscar pedido {order_id}: {e}")
        return Response(
            {'error': 'Erro ao buscar pedido', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# CATEGORIAS
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_categories(request):
    """
    Lista categorias de produtos
    """
    try:
        api_service = BlingAPIService()

        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 100)), 100)

        categories = api_service.get_categories(page, limit)

        return Response(categories)

    except Exception as e:
        logger.error(f"Erro ao buscar categorias: {e}")
        return Response(
            {'error': 'Erro ao buscar categorias', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# CONTATOS
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_contacts(request):
    """
    Lista contatos (clientes/fornecedores)
    """
    try:
        api_service = BlingAPIService()

        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 100)), 100)
        search = request.GET.get('search')

        if search:
            contacts = api_service.search_contacts(search, page, limit)
        else:
            contacts = api_service.get_contacts(page, limit)

        return Response(contacts)

    except Exception as e:
        logger.error(f"Erro ao buscar contatos: {e}")
        return Response(
            {'error': 'Erro ao buscar contatos', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# RELATÓRIOS E RESUMOS
@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def get_dashboard_summary(request):
    """
    Obtém um resumo para dashboard com informações principais
    """
    try:
        api_service = BlingAPIService()

        # Coleta dados em paralelo (simulado)
        summary = {
            'timestamp': request.build_absolute_uri(),
            'products': {'recent': [], 'error': None},
            'orders': {'recent': [], 'error': None},
            'categories': {'list': [], 'error': None},
        }

        # Produtos recentes
        try:
            products_response = api_service.get_products(page=1, limit=5)
            if products_response and 'data' in products_response:
                summary['products']['recent'] = products_response['data']
                summary['products']['total_pages'] = products_response.get('meta', {}).get('totalPages', 0)
        except Exception as e:
            summary['products']['error'] = str(e)

        # Pedidos recentes
        try:
            orders_response = api_service.get_orders(page=1, limit=5)
            if orders_response and 'data' in orders_response:
                summary['orders']['recent'] = orders_response['data']
                summary['orders']['total_pages'] = orders_response.get('meta', {}).get('totalPages', 0)
        except Exception as e:
            summary['orders']['error'] = str(e)

        # Categorias
        try:
            categories_response = api_service.get_categories(page=1, limit=10)
            if categories_response and 'data' in categories_response:
                summary['categories']['list'] = categories_response['data']
                summary['categories']['total_pages'] = categories_response.get('meta', {}).get('totalPages', 0)
        except Exception as e:
            summary['categories']['error'] = str(e)

        return Response(summary)

    except Exception as e:
        logger.error(f"Erro ao buscar resumo: {e}")
        return Response(
            {'error': 'Erro ao buscar resumo', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ============================================================================
# VIEWS DE DEBUG (REMOVER EM PRODUÇÃO)
# ============================================================================

@api_view(['GET'])
@renderer_classes([JSONRenderer])
@permission_classes([AllowAny])
def debug_product_structure(request, product_id):
    """
    Debug: mostra toda estrutura de um produto específico
    """
    try:
        api_service = BlingAPIService()
        product_response = api_service.get_product(product_id)

        if product_response and 'data' in product_response:
            product_data = product_response['data']

            # Análise da estrutura
            analysis = {
                'product_id': product_id,
                'basic_info': {
                    'id': product_data.get('id'),
                    'nome': product_data.get('nome'),
                    'codigo': product_data.get('codigo'),
                    'tipo': product_data.get('tipo'),
                    'situacao': product_data.get('situacao')
                },
                'all_fields': list(product_data.keys()),
                'variations_related_fields': {},
                'full_product_data': product_data
            }

            # Procura por campos relacionados a variações
            variation_keywords = ['variacao', 'variacoes', 'variation', 'variations', 'lote', 'grade']
            for key, value in product_data.items():
                if any(keyword in key.lower() for keyword in variation_keywords):
                    analysis['variations_related_fields'][key] = value

            return Response(analysis)
        else:
            return Response(
                {'error': 'Produto não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    except Exception as e:
        logger.error(f"Erro no debug do produto {product_id}: {e}")
        return Response(
            {'error': 'Erro no debug', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
