import React from 'react';

const Sidebar = ({ activeItem, onItemClick }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'products', label: 'Produtos', icon: '📦' },
    { id: 'orders', label: 'Pedidos', icon: '🛒' }
  ];

  const handleItemClick = (e, itemId) => {
    e.preventDefault();
    if (onItemClick) {
      onItemClick(itemId);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h2>Bling Dashboard</h2>
      </div>
      
      <nav>
        <ul className="sidebar-menu">
          {menuItems.map(item => (
            <li key={item.id}>
              <button
                className={activeItem === item.id ? 'active' : ''}
                onClick={(e) => handleItemClick(e, item.id)}
                style={{
                  background: 'none',
                  border: 'none',
                  width: '100%',
                  textAlign: 'left',
                  cursor: 'pointer'
                }}
              >
                <span>{item.icon}</span> {item.label}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;