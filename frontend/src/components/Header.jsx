import React from 'react';
import { useAuth } from '../hooks/useAuth';

const Header = ({ title }) => {
  const { isAuthenticated, loading, startAuth, logout } = useAuth();

  return (
    <header className="header">
      <h1>{title}</h1>
      
      <div className="auth-status">
        {loading ? (
          <span className="status-badge">Verificando...</span>
        ) : (
          <>
            <span className={`status-badge ${isAuthenticated ? 'status-authenticated' : 'status-not-authenticated'}`}>
              {isAuthenticated ? 'Conectado ao Bling' : 'Desconectado'}
            </span>
            
            {isAuthenticated ? (
              <button className="btn btn-danger" onClick={logout}>
                Desconectar
              </button>
            ) : (
              <button className="btn btn-primary" onClick={startAuth}>
                Conectar Bling
              </button>
            )}
          </>
        )}
      </div>
    </header>
  );
};

export default Header;