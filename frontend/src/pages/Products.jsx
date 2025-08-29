import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { productsAPI } from '../services/api';

const Products = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  
  const { data: productsData, loading, refetch } = useApi(
    () => productsAPI.getAll({ 
      page, 
      limit: 20,
      ...(searchTerm && { search: searchTerm })
    }),
    [page, searchTerm]
  );

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    refetch();
  };

  const formatCurrency = (value) => {
    if (!value) return 'R$ 0,00';
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'A': return 'Ativo';
      case 'I': return 'Inativo';
      default: return status || 'N/A';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'A':
        return { color: '#10b981', backgroundColor: '#dcfce7' };
      case 'I':
        return { color: '#ef4444', backgroundColor: '#fee2e2' };
      default:
        return { color: '#64748b', backgroundColor: '#f1f5f9' };
    }
  };

  const products = productsData?.data || [];
  const hasMore = productsData?._metadata?.has_more || false;

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Produtos</h2>
        
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder="Buscar produtos..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              padding: '10px',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              minWidth: '200px'
            }}
          />
          <button type="submit" className="btn btn-primary">
            Buscar
          </button>
        </form>
      </div>

      {loading ? (
        <div className="loading">Carregando produtos...</div>
      ) : (
        <div className="table-container">
          <div className="table-header">
            <h3>Lista de Produtos ({products.length} itens)</h3>
          </div>
          
          {products.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              {searchTerm ? 'Nenhum produto encontrado para a busca.' : 'Nenhum produto encontrado.'}
            </div>
          ) : (
            <>
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Código</th>
                    <th>Nome</th>
                    <th>Preço</th>
                    <th>Tipo</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((product) => (
                    <tr key={product.id}>
                      <td>{product.id}</td>
                      <td style={{ fontWeight: '500' }}>{product.codigo}</td>
                      <td>{product.nome}</td>
                      <td>{formatCurrency(product.preco)}</td>
                      <td>{product.tipo === 'P' ? 'Produto' : product.tipo}</td>
                      <td>
                        <span 
                          style={{
                            ...getStatusColor(product.situacao),
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '500'
                          }}
                        >
                          {getStatusText(product.situacao)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Paginação Simples */}
              <div className="pagination">
                <button 
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="btn"
                >
                  Anterior
                </button>
                
                <span style={{ margin: '0 15px', color: 'var(--text-secondary)' }}>
                  Página {page}
                </span>
                
                <button 
                  onClick={() => setPage(page + 1)}
                  disabled={!hasMore}
                  className="btn"
                >
                  Próxima
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Products;