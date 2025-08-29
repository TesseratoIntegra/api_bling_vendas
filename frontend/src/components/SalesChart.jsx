import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const SalesChart = ({ data, loading, title = "Vendas dos Últimos 30 Dias" }) => {
  // Dados mock caso não tenha dados reais
  const mockData = [
    { data: '01/08', vendas: 4000 },
    { data: '02/08', vendas: 3000 },
    { data: '03/08', vendas: 2000 },
    { data: '04/08', vendas: 2780 },
    { data: '05/08', vendas: 1890 },
    { data: '06/08', vendas: 2390 },
    { data: '07/08', vendas: 3490 },
  ];

  const chartData = data && data.length > 0 ? data : mockData;

  const formatCurrency = (value) => {
    if (!value || isNaN(value)) return 'R$ 0,00';
    return Number(value).toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    });
  };

  // Custom tooltip component para evitar erro do formatter
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: 'white',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p style={{ margin: 0, fontWeight: 'bold' }}>{`Data: ${label}`}</p>
          <p style={{ margin: 0, color: '#2563eb' }}>
            {`Vendas: ${formatCurrency(payload[0].value)}`}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="chart-container">
        <h3 className="chart-title">{title}</h3>
        <div className="loading">Carregando gráfico...</div>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <h3 className="chart-title">{title}</h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="data" />
          <YAxis tickFormatter={(value) => formatCurrency(value)} />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="vendas" 
            stroke="#2563eb" 
            strokeWidth={2}
            dot={{ fill: '#2563eb' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SalesChart;