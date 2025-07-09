import React, { createContext, useContext, useReducer, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

// Initial state
const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  loading: true,
  error: null
};

// Action types
const AuthActions = {
  SET_LOADING: 'SET_LOADING',
  SET_USER: 'SET_USER',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  LOGOUT: 'LOGOUT'
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case AuthActions.SET_LOADING:
      return { ...state, loading: action.payload };
    case AuthActions.SET_USER:
      return { 
        ...state, 
        user: action.payload.user, 
        token: action.payload.token,
        loading: false,
        error: null
      };
    case AuthActions.SET_ERROR:
      return { 
        ...state, 
        error: action.payload, 
        loading: false
      };
    case AuthActions.CLEAR_ERROR:
      return { ...state, error: null };
    case AuthActions.LOGOUT:
      return { 
        ...state, 
        user: null, 
        token: null, 
        loading: false,
        error: null
      };
    default:
      return state;
  }
}

// Create context
const AuthContext = createContext();

// API instance
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Provider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize authentication
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        dispatch({ type: AuthActions.SET_LOADING, payload: false });
        return;
      }

      try {
        const response = await api.get('/auth/profile');
        dispatch({ 
          type: AuthActions.SET_USER, 
          payload: { 
            user: response.data.user, 
            token 
          } 
        });
      } catch (error) {
        console.error('Auth initialization error:', error);
        localStorage.removeItem('token');
        dispatch({ type: AuthActions.SET_LOADING, payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      dispatch({ type: AuthActions.SET_LOADING, payload: true });
      dispatch({ type: AuthActions.CLEAR_ERROR });

      const response = await api.post('/auth/login', credentials);
      const { user, token } = response.data;

      localStorage.setItem('token', token);
      dispatch({ type: AuthActions.SET_USER, payload: { user, token } });
      
      toast.success('Login successful!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed';
      dispatch({ type: AuthActions.SET_ERROR, payload: errorMessage });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      dispatch({ type: AuthActions.SET_LOADING, payload: true });
      dispatch({ type: AuthActions.CLEAR_ERROR });

      const response = await api.post('/auth/register', userData);
      const { user, token } = response.data;

      localStorage.setItem('token', token);
      dispatch({ type: AuthActions.SET_USER, payload: { user, token } });
      
      toast.success('Registration successful!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Registration failed';
      dispatch({ type: AuthActions.SET_ERROR, payload: errorMessage });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      dispatch({ type: AuthActions.LOGOUT });
      toast.success('Logged out successfully');
    }
  };

  // Update profile function
  const updateProfile = async (profileData) => {
    try {
      dispatch({ type: AuthActions.SET_LOADING, payload: true });
      
      const response = await api.put('/auth/profile', profileData);
      const { user } = response.data;

      dispatch({ 
        type: AuthActions.SET_USER, 
        payload: { 
          user, 
          token: state.token 
        } 
      });
      
      toast.success('Profile updated successfully!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Profile update failed';
      dispatch({ type: AuthActions.SET_ERROR, payload: errorMessage });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Change password function
  const changePassword = async (passwordData) => {
    try {
      dispatch({ type: AuthActions.SET_LOADING, payload: true });
      
      await api.post('/auth/change-password', passwordData);
      
      toast.success('Password changed successfully!');
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Password change failed';
      dispatch({ type: AuthActions.SET_ERROR, payload: errorMessage });
      toast.error(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  // Refresh token function
  const refreshToken = async () => {
    try {
      const response = await api.post('/auth/refresh');
      const { token } = response.data;
      
      localStorage.setItem('token', token);
      dispatch({ 
        type: AuthActions.SET_USER, 
        payload: { 
          user: state.user, 
          token 
        } 
      });
      
      return { success: true };
    } catch (error) {
      console.error('Token refresh error:', error);
      logout();
      return { success: false };
    }
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AuthActions.CLEAR_ERROR });
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshToken,
    clearError,
    api
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext; 