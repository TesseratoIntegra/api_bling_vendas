import React, { useState } from 'react';
import './styles/components.css';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Orders from './pages/Orders';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const getPageTitle = () => {
    switch (currentPage) {
      case 'dashboard':
        return 'Dashboard';
      case 'products':
        return 'Produtos';
      case 'orders':
        return 'Pedidos';
      default:
        return 'Bling Dashboard';
    }
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'products':
        return <Products />;
      case 'orders':
        return <Orders />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Sidebar 
        activeItem={currentPage} 
        onItemClick={setCurrentPage} 
      />
      
      <div className="main-content">
        <Header title={getPageTitle()} />
        
        <main className="page-content">
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
}

export default App;