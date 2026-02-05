
import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, AuthResponse } from '../types';
import axiosClient from '../services/axiosClient';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (credentials: any) => {
    try {
      const response = await axiosClient.post<AuthResponse>('/auth/users/auth', credentials);
      const { token, payload } = response.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(payload));
      setToken(token);
      setUser(payload);
    } catch (err: any) {
      console.error('Login error detail:', err);
      throw err;
    }
  };

  const register = async (data: any) => {
    await axiosClient.post('/auth/users/add', data);
  };

  const logout = async () => {
    try {
      if (token) {
        await axiosClient.post('/auth/users/logout').catch(() => { });
      }
    } finally {
      localStorage.clear();
      setToken(null);
      setUser(null);
      window.location.hash = '/login';
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
};

