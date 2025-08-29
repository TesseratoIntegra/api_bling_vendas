import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const checkAuthStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await authAPI.checkStatus();
      setIsAuthenticated(response.authenticated);
    } catch (err) {
      setError(err.message);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const startAuth = async () => {
    try {
      const response = await authAPI.startAuth();
      window.open(response.auth_url, '_blank');
      // Verificar status após alguns segundos
      setTimeout(checkAuthStatus, 3000);
    } catch (err) {
      setError(err.message);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setIsAuthenticated(false);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  return {
    isAuthenticated,
    loading,
    error,
    startAuth,
    logout,
    checkAuthStatus
  };
};