import React from 'react';
import { useApi } from '../hooks/useApi';
import { dashboardAPI, ordersAPI } from '../services/api';
import MetricsCard from '../components/MetricsCard';
import SalesChart from '../components/SalesChart';
import OrdersTable from '../components/OrdersTable';

const Dashboard = () => {
  const { data: dashboardData, loading: dashboardLoading, error: dashboardError } = useApi(() => dashboardAPI.getSummary());
  const { data: ordersData, loading: ordersLoading, error: ordersError } = useApi(() => ordersAPI.getAll({ limit: 5 }));

  // Calcula métricas dos dados
  const calculateMetrics = () => {
    // Usa dados mock se houver erro na API
    if (ordersError || !ordersData) {
      return {
        totalOrders: 0,
        totalSales: 0,
        productsCount: dashboardData?.products?.recent?.length || 0,
        avgOrderValue: 0
      };
    }

    const orders = ordersData.data || [];
    const totalOrders = orders.length;
    const totalSales = orders.reduce((sum, order) => sum + (order.total || 0), 0);
    const productsCount = dashboardData?.products?.recent?.length || 0;

    return {
      totalOrders,
      totalSales,
      productsCount,
      avgOrderValue: totalOrders > 0 ? totalSales / totalOrders : 0
    };
  };

  const metrics = calculateMetrics();

  // Gera dados do gráfico baseado nos pedidos ou dados mock
  const generateChartData = () => {
    if (ordersError || !ordersData?.data) {
      // Retorna dados mock em caso de erro
      return [
        { data: '25/08', vendas: 1500 },
        { data: '26/08', vendas: 2200 },
        { data: '27/08', vendas: 1800 },
        { data: '28/08', vendas: 2500 },
        { data: '29/08', vendas: 3200 },
      ];
    }

    const orders = ordersData.data;
    const salesByDate = {};

    orders.forEach(order => {
      const date = order.dataEmissao || order.data;
      if (date) {
        const formattedDate = new Date(date).toLocaleDateString('pt-BR', { 
          day: '2-digit', 
          month: '2-digit' 
        });
        salesByDate[formattedDate] = (salesByDate[formattedDate] || 0) + (order.total || 0);
      }
    });

    return Object.entries(salesByDate).map(([data, vendas]) => ({
      data,
      vendas
    }));
  };

  const chartData = generateChartData();

  return (
    <div className="container">
      <h2 className="mb-20">Dashboard</h2>
      
      {/* Mostrar erros se houver */}
      {(dashboardError || ordersError) && (
        <div className="error mb-20">
          <strong>Aviso:</strong> Alguns dados podem não estar atualizados devido a problemas na conexão com o Bling ERP.
          {ordersError && <br />}
          {ordersError && `Pedidos: ${ordersError}`}
        </div>
      )}
      
      {/* Cards de Métricas */}
      <div className="metrics-grid">
        <MetricsCard
          title="Total de Vendas"
          value={metrics.totalSales || 0}
          icon="💰"
        />
        <MetricsCard
          title="Pedidos"
          value={metrics.totalOrders || 0}
          icon="📋"
        />
        <MetricsCard
          title="Produtos"
          value={metrics.productsCount || 0}
          icon="📦"
        />
        <MetricsCard
          title="Ticket Médio"
          value={metrics.avgOrderValue || 0}
          icon="📊"
        />
      </div>

      {/* Gráfico de Vendas */}
      <SalesChart 
        data={chartData}
        loading={dashboardLoading || ordersLoading}
        title={ordersError ? "Vendas (Dados de Exemplo)" : "Vendas por Data"}
      />

      {/* Tabela de Pedidos Recentes */}
      <OrdersTable
        orders={ordersData?.data || []}
        loading={ordersLoading}
        title={ordersError ? "Pedidos Recentes (Indisponível)" : "Pedidos Recentes"}
      />

      {/* Status da Integração */}
      <div className="mt-20 p-20" style={{ backgroundColor: 'var(--card-background)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
        <h3 style={{ marginBottom: '10px' }}>Status da Integração</h3>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          <p>Dashboard: {dashboardError ? '❌ Erro' : '✅ OK'}</p>
          <p>Pedidos: {ordersError ? '❌ Erro' : '✅ OK'}</p>
          {dashboardData && (
            <>
              <p>Produtos: {dashboardData.products?.error ? '❌ Erro' : '✅ OK'}</p>
              <p>Categorias: {dashboardData.categories?.error ? '❌ Erro' : '✅ OK'}</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;