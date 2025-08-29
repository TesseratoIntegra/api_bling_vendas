const API_BASE = 'http://localhost:8000/integrations';

// Helper para requisições
export const apiRequest = async (endpoint, options = {}) => {
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
};

// Autenticação
export const authAPI = {
  checkStatus: () => apiRequest('/auth/status/'),
  startAuth: () => apiRequest('/auth/start/'),
  logout: () => apiRequest('/auth/logout/', { method: 'POST' })
};

// Dashboard
export const dashboardAPI = {
  getSummary: () => apiRequest('/dashboard/'),
  getHealthCheck: () => apiRequest('/health/')
};

// Produtos
export const productsAPI = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/products/?${queryString}`);
  },
  getById: (id) => apiRequest(`/products/${id}/`),
  search: (term, page = 1) => apiRequest(`/products/?search=${term}&page=${page}`)
};

// Pedidos
export const ordersAPI = {
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/orders/?${queryString}`);
  },
  getById: (id) => apiRequest(`/orders/${id}/`),
  getByDateRange: (startDate, endDate, page = 1) => {
    return apiRequest(`/orders/?data_inicial=${startDate}&data_final=${endDate}&page=${page}`);
  }
};

// Categorias
export const categoriesAPI = {
  getAll: (page = 1) => apiRequest(`/categories/?page=${page}`)
};

// Contatos
export const contactsAPI = {
  getAll: (page = 1) => apiRequest(`/contacts/?page=${page}`),
  search: (term, page = 1) => apiRequest(`/contacts/?search=${term}&page=${page}`)
};