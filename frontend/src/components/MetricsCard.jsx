import React from 'react';

const MetricsCard = ({ title, value, change, changeType, icon }) => {
  const formatValue = (val) => {
    if (typeof val === 'number') {
      return val.toLocaleString('pt-BR');
    }
    return val;
  };

  const formatCurrency = (val) => {
    if (typeof val === 'number') {
      return val.toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
      });
    }
    return val;
  };

  const displayValue = title.toLowerCase().includes('vendas') || title.toLowerCase().includes('receita') 
    ? formatCurrency(value) 
    : formatValue(value);

  return (
    <div className="metrics-card">
      <div className="card-title">
        {icon && <span style={{ marginRight: '8px' }}>{icon}</span>}
        {title}
      </div>
      
      <div className="card-value">
        {displayValue}
      </div>
      
      {change && (
        <div className={`card-change ${changeType || 'neutral'}`}>
          {changeType === 'positive' && '↗ '}
          {changeType === 'negative' && '↘ '}
          {change}
        </div>
      )}
    </div>
  );
};

export default MetricsCard;