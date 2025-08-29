from django.urls import path
from . import views


urlpatterns = [
    # Teste
    path('', views.test_integration, name='bling-test'),

    # Autenticação OAuth
    path('auth/start/', views.start_authentication, name='bling-auth-start'),
    path('auth/callback/', views.oauth_callback, name='bling-auth-callback'),
    path('auth/logout/', views.logout_bling, name='bling-auth-logout'),
    path('auth/status/', views.auth_status, name='bling-auth-status'),

    # Produtos
    path('products/', views.get_products, name='bling-products'),
    path('products/<str:product_identifier>/', views.get_product_detail, name='bling-product-detail'),
    path('products/<str:product_identifier>/variations/', views.get_product_variations, name='bling-product-variations'),

    # Pedidos
    path('orders/', views.get_orders, name='bling-orders'),
    path('orders/<int:order_id>/', views.get_order_detail, name='bling-order-detail'),

    # Categorias
    path('categories/', views.get_categories, name='bling-categories'),

    # Contatos
    path('contacts/', views.get_contacts, name='bling-contacts'),

    # Dashboard/Resumos
    path('dashboard/', views.get_dashboard_summary, name='bling-dashboard'),

    path('health/', views.api_health_check, name='bling-health'),
    path('debug/products/<str:product_id>/structure/', views.debug_product_structure, name='debug-structure'),
]
