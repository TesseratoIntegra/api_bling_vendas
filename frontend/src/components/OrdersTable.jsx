import React from 'react';

const OrdersTable = ({ orders, loading, title = "Pedidos Recentes" }) => {
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

  if (loading) {
    return (
      <div className="table-container">
        <div className="table-header">
          <h3>{title}</h3>
        </div>
        <div className="loading">Carregando pedidos...</div>
      </div>
    );
  }

  if (!orders || orders.length === 0) {
    return (
      <div className="table-container">
        <div className="table-header">
          <h3>{title}</h3>
        </div>
        <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
          Nenhum pedido encontrado
        </div>
      </div>
    );
  }

  return (
    <div className="table-container">
      <div className="table-header">
        <h3>{title}</h3>
      </div>
      
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
              <td>#{order.numero || order.id}</td>
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
              <td>{formatCurrency(order.total || order.valor)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default OrdersTable;