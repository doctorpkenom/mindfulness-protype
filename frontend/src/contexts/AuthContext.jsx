import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_BASE_URL = 'http://localhost:8000';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  // Set up axios interceptor for auth token - only on initial load
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      
      // Verify token and get user info
      axios.get(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${storedToken}`
        }
      })
        .then(response => {
          setUser(response.data);
          setToken(storedToken); // Sync state
          setLoading(false);
        })
        .catch((error) => {
          console.error('Token verification failed on load:', error.response?.data || error.message);
          // Token invalid, clear it
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []); // Only run once on mount

  const login = async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const { access_token } = response.data;
      
      if (!access_token) {
        return { 
          success: false, 
          error: 'No token received from server' 
        };
      }
      
      // Store token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user info with explicit header
      try {
        const userResponse = await axios.get(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        setUser(userResponse.data);
        return { success: true };
      } catch (meError) {
        console.error('Failed to get user info after login:', meError);
        return { 
          success: true, 
          warning: 'Logged in! Please refresh the page.' 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Login failed' 
      };
    }
  };

  const signup = async (email, username, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/signup`, {
        email,
        username,
        password
      });
      
      console.log('Signup response:', response.data); // Debug
      
      const { access_token, token_type } = response.data;
      
      if (!access_token) {
        console.error('No access token in response:', response.data);
        return { 
          success: false, 
          error: 'No token received from server' 
        };
      }
      
      console.log('Token received, length:', access_token.length); // Debug
      
      // Store token
      localStorage.setItem('token', access_token);
      setToken(access_token);
      
      // Set axios default header for all future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user info with explicit header
      try {
        console.log('Fetching user info with token...'); // Debug
        const userResponse = await axios.get(`${API_BASE_URL}/api/auth/me`, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        
        console.log('User info received:', userResponse.data); // Debug
        setUser(userResponse.data);
        return { success: true };
      } catch (meError) {
        console.error('Failed to get user info after signup:', meError);
        console.error('Error details:', {
          status: meError.response?.status,
          data: meError.response?.data,
          headers: meError.response?.headers
        });
        
        // Even if /me fails, signup was successful
        // Store token anyway - user can refresh page
        return { 
          success: true, 
          warning: 'Account created! Please refresh the page to continue.' 
        };
      }
    } catch (error) {
      console.error('Signup error:', error);
      console.error('Error response:', error.response?.data);
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Signup failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
