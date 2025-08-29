# Integração Bling ERP - API REST

Integração completa com a API v3 do Bling ERP usando Django REST Framework. Permite consumo de dados de produtos, pedidos, categorias e contatos através de uma API REST padronizada.

## Funcionalidades

- ✅ **Autenticação OAuth 2.0** com renovação automática de tokens
- ✅ **Gestão completa de produtos** (listagem, busca, detalhes)
- ✅ **Variações de produto** com busca alternativa inteligente
- ✅ **Pedidos de venda** com filtros por data e status
- ✅ **Categorias e contatos** com paginação
- ✅ **Dashboard com resumos** para visualização rápida
- ✅ **Cache inteligente** para performance
- ✅ **Logs detalhados** para debugging
- ✅ **Tratamento robusto de erros**

## Instalação Rápida

### 1. Dependências

```bash
pip install requests python-decouple django-cors-headers
```

### 2. Configurar .env

```env
API_URL=https://www.bling.com.br/Api/v3
CLIENT_ID=seu_client_id_aqui
CLIENT_SECRET=seu_client_secret_aqui
REDIRECT_URI=http://localhost:8000/integrations/auth/callback/
```

### 3. Configurar settings.py

```python
# Cache (usar locmem para desenvolvimento)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'bling-cache',
        'TIMEOUT': 3600,
    }
}

# DRF
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

# CORS (se necessário)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 4. URLs principais

```python
# urls.py do projeto
urlpatterns = [
    path('integrations/', include('integrations.urls')),
]
```

### 5. Iniciar

```bash
python manage.py runserver
```

Acesse: `http://localhost:8000/integrations/`

---

## API Endpoints

### Base URL
```
http://localhost:8000/integrations/
```

### Autenticação OAuth

#### Iniciar Autenticação
```http
GET /auth/start/
```

**Resposta:**
```json
{
    "auth_url": "https://www.bling.com.br/Api/v3/oauth/authorize?...",
    "state": "abc123...",
    "message": "Acesse a URL para autorizar a aplicação no Bling",
    "instructions": "Abra a auth_url em uma nova aba para autorizar o acesso"
}
```

#### Status da Autenticação
```http
GET /auth/status/
```

**Resposta:**
```json
{
    "authenticated": true,
    "message": "Autenticado",
    "action_needed": null
}
```

#### Logout
```http
POST /auth/logout/
```

**Resposta:**
```json
{
    "success": true,
    "message": "Logout realizado com sucesso",
    "next_steps": "Use /auth/start/ para reautenticar"
}
```

---

### Produtos

#### Listar Produtos
```http
GET /products/
GET /products/?page=1&limit=50
GET /products/?search=notebook
```

**Parâmetros Query:**
- `page` (int): Número da página (padrão: 1)
- `limit` (int): Itens por página (padrão: 100, máx: 100)  
- `search` (string): Termo de busca
- `categoria` (string): Filtrar por categoria

**Resposta:**
```json
{
    "data": [
        {
            "id": 16458663084,
            "nome": "Aparelho",
            "codigo": "99",
            "preco": 0,
            "situacao": "A",
            "tipo": "P"
        }
    ],
    "_metadata": {
        "page": 1,
        "limit": 100,
        "search": null,
        "total_items": 1,
        "has_more": false
    }
}
```

#### Obter Produto
```http
GET /products/{id}/
GET /products/16458663084/
GET /products/99/  <!-- Por código -->
```

**Resposta:**
```json
{
    "data": {
        "id": 16458663084,
        "nome": "Aparelho",
        "codigo": "99",
        "preco": 0,
        "situacao": "A"
        // ... outros campos
    }
}
```

#### Variações do Produto
```http
GET /products/{id}/variations/
GET /products/16458663084/variations/
```

**Resposta (se não encontrar variações via API oficial):**
```json
{
    "data": [],
    "_metadata": {
        "method": "alternative_search",
        "parent_product_id": 16458663084,
        "parent_code": "99",
        "total_found": 0,
        "note": "Variações encontradas através de busca por código"
    }
}
```

---

### Pedidos

#### Listar Pedidos
```http
GET /orders/
GET /orders/?page=1&limit=50
GET /orders/?data_inicial=2024-01-01&data_final=2024-12-31
GET /orders/?situacao=aprovado
```

**Parâmetros Query:**
- `page` (int): Número da página
- `limit` (int): Itens por página (máx: 100)
- `data_inicial` (string): Data inicial (YYYY-MM-DD)
- `data_final` (string): Data final (YYYY-MM-DD)  
- `situacao` (string): Status do pedido
- `numero` (string): Número do pedido

**Resposta:**
```json
{
    "data": [
        {
            "id": 12345,
            "numero": "123",
            "dataEmissao": "2024-08-28",
            "contato": {
                "nome": "Cliente Teste"
            },
            "total": 1500.00
        }
    ],
    "_metadata": {
        "page": 1,
        "limit": 100,
        "filters": {
            "dataInicial": "2024-01-01"
        },
        "total_items": 1
    }
}
```

#### Obter Pedido
```http
GET /orders/{id}/
```

---

### Outros Endpoints

#### Categorias
```http
GET /categories/
```

#### Contatos
```http
GET /contacts/
GET /contacts/?search=cliente
```

#### Dashboard
```http
GET /dashboard/
```

**Resposta:**
```json
{
    "timestamp": "http://localhost:8000/integrations/dashboard/",
    "products": {
        "recent": [...],
        "error": null
    },
    "orders": {
        "recent": [...], 
        "error": null
    },
    "categories": {
        "list": [...],
        "error": null
    }
}
```

#### Health Check
```http
GET /health/
```

---

## Frontend - Guia de Consumo

### JavaScript Vanilla

#### 1. Setup Base

```javascript
const API_BASE = 'http://localhost:8000/integrations';

// Helper para requisições
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro na requisição');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Erro na API:', error);
        throw error;
    }
}
```

#### 2. Autenticação

```javascript
// Verificar status
async function checkAuthStatus() {
    const status = await apiRequest('/auth/status/');
    return status.authenticated;
}

// Iniciar autenticação  
async function startAuth() {
    const auth = await apiRequest('/auth/start/');
    // Abrir em nova janela
    window.open(auth.auth_url, '_blank');
    return auth;
}

// Logout
async function logout() {
    return await apiRequest('/auth/logout/', { method: 'POST' });
}
```

#### 3. Produtos

```javascript
// Listar produtos
async function getProducts(page = 1, limit = 50, search = '') {
    const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
        ...(search && { search })
    });
    
    return await apiRequest(`/products/?${params}`);
}

// Produto específico
async function getProduct(identifier) {
    return await apiRequest(`/products/${identifier}/`);
}

// Variações
async function getProductVariations(identifier) {
    return await apiRequest(`/products/${identifier}/variations/`);
}
```

#### 4. Pedidos

```javascript
// Listar pedidos
async function getOrders(filters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
    });
    
    return await apiRequest(`/orders/?${params}`);
}

// Pedidos por período
async function getOrdersByDate(startDate, endDate) {
    return await getOrders({
        data_inicial: startDate,
        data_final: endDate
    });
}
```

#### 5. Dashboard

```javascript
async function getDashboard() {
    return await apiRequest('/dashboard/');
}
```

### React Hooks

```jsx
import { useState, useEffect } from 'react';

// Hook para status de autenticação
function useAuth() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        checkAuthStatus()
            .then(setIsAuthenticated)
            .finally(() => setLoading(false));
    }, []);
    
    const startAuth = async () => {
        const auth = await apiRequest('/auth/start/');
        window.open(auth.auth_url, '_blank');
    };
    
    return { isAuthenticated, loading, startAuth };
}

// Hook para produtos
function useProducts(page = 1, search = '') {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        setLoading(true);
        getProducts(page, 50, search)
            .then(response => setProducts(response.data || []))
            .catch(setError)
            .finally(() => setLoading(false));
    }, [page, search]);
    
    return { products, loading, error };
}

// Componente exemplo
function ProductsList() {
    const { products, loading, error } = useProducts();
    
    if (loading) return <div>Carregando...</div>;
    if (error) return <div>Erro: {error.message}</div>;
    
    return (
        <div>
            {products.map(product => (
                <div key={product.id}>
                    <h3>{product.nome}</h3>
                    <p>Código: {product.codigo}</p>
                    <p>Preço: R$ {product.preco}</p>
                </div>
            ))}
        </div>
    );
}
```

### Vue.js Composition API

```javascript
import { ref, onMounted } from 'vue';

// Composable para produtos
export function useProducts() {
    const products = ref([]);
    const loading = ref(false);
    const error = ref(null);
    
    const fetchProducts = async (page = 1, search = '') => {
        loading.value = true;
        error.value = null;
        
        try {
            const response = await getProducts(page, 50, search);
            products.value = response.data || [];
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
    };
    
    onMounted(() => fetchProducts());
    
    return {
        products,
        loading, 
        error,
        fetchProducts
    };
}
```

---

## Tratamento de Erros

### Códigos de Status HTTP

- `200` - Sucesso
- `400` - Erro de validação (dados incorretos)
- `401` - Não autenticado (token expirado/inválido)
- `404` - Recurso não encontrado
- `500` - Erro interno do servidor
- `501` - Funcionalidade não implementada (ex: endpoint de variações)

### Estrutura de Erro

```json
{
    "error": "Descrição do erro",
    "details": "Detalhes técnicos",
    "suggestion": "Sugestão para resolver"
}
```

### Tratamento no Frontend

```javascript
async function handleApiCall(apiFunction) {
    try {
        return await apiFunction();
    } catch (error) {
        if (error.message.includes('401')) {
            // Token expirado - reautenticar
            console.log('Token expirado, reautenticar necessário');
            window.location.href = '/login';
        } else if (error.message.includes('404')) {
            // Recurso não encontrado
            console.log('Recurso não encontrado');
        } else {
            // Outros erros
            console.error('Erro na API:', error.message);
        }
        throw error;
    }
}
```

---

## Notas Importantes

### Variações de Produto
A API v3 do Bling ainda não implementou completamente o endpoint de variações. O sistema usa busca alternativa baseada em códigos de produto.

### Autenticação
Os tokens OAuth são gerenciados automaticamente. Se expirarem, será necessário reautenticar via `/auth/start/`.

### Limites
- Máximo 100 itens por página
- Cache padrão de 1 hora
- Renovação automática de tokens

### Produção
Para produção:
- Configure Redis para cache
- Use HTTPS nas URLs de callback
- Remova endpoints de debug
- Configure logs adequados

---

## Suporte

Para dúvidas sobre a API do Bling: [Documentação Oficial](https://developer.bling.com.br/)

Para issues desta integração: Verifique os logs da aplicação Django.
