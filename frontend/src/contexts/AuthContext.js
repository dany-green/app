import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/lib/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authAPI.login(email, password);
      const { access_token } = response;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const isAdmin = () => user?.role === 'Администратор';
  const isCurator = () => user?.role === 'Куратор студии';
  const isLeadDecorator = () => user?.role === 'Ведущий декоратор';
  const isFlorist = () => user?.role === 'Флорист';

  const canEditFinalList = () => isAdmin() || isCurator();
  const canManageUsers = () => isAdmin();
  const canManageInventory = () => isAdmin() || isCurator();

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAdmin,
    isCurator,
    isLeadDecorator,
    isFlorist,
    canEditFinalList,
    canManageUsers,
    canManageInventory,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
