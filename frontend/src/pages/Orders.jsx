import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { ordersAPI } from '../services/api';

const Orders = () => {
  const [filters, setFilters] = useState({
    data_inicial: '',
    data_final: '',
    situacao: '',
    page: 1
  });

  const { data: ordersData, loading, refetch } = useApi(
    () => ordersAPI.getAll({
      ...filters,
      limit: 20
    }),
    [filters]
  );

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
      page: 1 // Reset page when filtering
    }));
  };

  const handlePageChange = (newPage) => {
    setFilters(prev => ({
      ...prev,
      page: newPage
    }));
  };

  const clearFilters = () => {
    setFilters({
      data_inicial: '',
      data_final: '',
      situacao: '',
      page: 1
    });
  };

  const formatCurrency = (value) => {
    if (!value) return 'R$ 0,00';
    return value.toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'aprovado':
        return { color: '#10b981', backgroundColor: '#dcfce7' };
      case 'pendente':
        return { color: '#f59e0b', backgroundColor: '#fef3c7' };
      case 'cancelado':
        return { color: '#ef4444', backgroundColor: '#fee2e2' };
      default:
        return { color: '#64748b', backgroundColor: '#f1f5f9' };
    }
  };

  const orders = ordersData?.data || [];
  const totalItems = ordersData?._metadata?.total_items || 0;

  // Calcula total de vendas dos pedidos filtrados
  const totalSales = orders.reduce((sum, order) => sum + (order.total || 0), 0);

  return (
    <div className="container">
      <div style={{ marginBottom: '20px' }}>
        <h2>Pedidos</h2>
        
        {/* Filtros */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '15px', 
          marginTop: '20px',
          padding: '20px',
          backgroundColor: 'var(--card-background)',
          borderRadius: '8px',
          border: '1px solid var(--border-color)'
        }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>
              Data Inicial:
            </label>
            <input
              type="date"
              value={filters.data_inicial}
              onChange={(e) => handleFilterChange('data_inicial', e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid var(--border-color)',
                borderRadius: '4px'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>
              Data Final:
            </label>
            <input
              type="date"
              value={filters.data_final}
              onChange={(e) => handleFilterChange('data_final', e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid var(--border-color)',
                borderRadius: '4px'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', fontWeight: '500' }}>
              Status:
            </label>
            <select
              value={filters.situacao}
              onChange={(e) => handleFilterChange('situacao', e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid var(--border-color)',
                borderRadius: '4px'
              }}
            >
              <option value="">Todos</option>
              <option value="aprovado">Aprovado</option>
              <option value="pendente">Pendente</option>
              <option value="cancelado">Cancelado</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'end', gap: '10px' }}>
            <button onClick={clearFilters} className="btn" style={{ backgroundColor: '#64748b', color: 'white' }}>
              Limpar
            </button>
          </div>
        </div>

        {/* Resumo */}
        {orders.length > 0 && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '15px', 
            margin: '20px 0'
          }}>
            <div style={{ 
              padding: '15px', 
              backgroundColor: 'var(--card-background)', 
              borderRadius: '6px',
              border: '1px solid var(--border-color)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--primary-color)' }}>
                {orders.length}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Pedidos Encontrados
              </div>
            </div>
            
            <div style={{ 
              padding: '15px', 
              backgroundColor: 'var(--card-background)', 
              borderRadius: '6px',
              border: '1px solid var(--border-color)',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--success-color)' }}>
                {formatCurrency(totalSales)}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                Total em Vendas
              </div>
            </div>
          </div>
        )}
      </div>

      {loading ? (
        <div className="loading">Carregando pedidos...</div>
      ) : (
        <div className="table-container">
          <div className="table-header">
            <h3>Lista de Pedidos</h3>
          </div>
          
          {orders.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Nenhum pedido encontrado com os filtros aplicados.
            </div>
          ) : (
            <>
              <table className="table">
                <thead>
                  <tr>
                    <th>Número</th>
                    <th>Data</th>
                    <th>Cliente</th>
                    <th>Status</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <td style={{ fontWeight: '500' }}>#{order.numero || order.id}</td>
                      <td>{formatDate(order.dataEmissao || order.data)}</td>
                      <td>{order.contato?.nome || order.cliente || 'Cliente não informado'}</td>
                      <td>
                        <span 
                          style={{
                            ...getStatusColor(order.situacao || order.status),
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '500'
                          }}
                        >
                          {order.situacao || order.status || 'Indefinido'}
                        </span>
                      </td>
                      <td style={{ fontWeight: '600' }}>{formatCurrency(order.total || order.valor)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Paginação */}
              <div className="pagination">
                <button 
                  onClick={() => handlePageChange(Math.max(1, filters.page - 1))}
                  disabled={filters.page === 1}
                  className="btn"
                >
                  Anterior
                </button>
                
                <span style={{ margin: '0 15px', color: 'var(--text-secondary)' }}>
                  Página {filters.page}
                </span>
                
                <button 
                  onClick={() => handlePageChange(filters.page + 1)}
                  disabled={orders.length < 20}
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

export default Orders;