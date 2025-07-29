import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { HelmetProvider } from 'react-helmet-async';

// Components
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import LoadingScreen from './components/LoadingScreen';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Courses from './pages/Courses';
import CourseDetail from './pages/CourseDetail';
import CreateCourse from './pages/CreateCourse';
import Research from './pages/Research';
import ResearchDetail from './pages/ResearchDetail';
import CreateResearch from './pages/CreateResearch';
import EditResearch from './pages/EditResearch';
import Collaboration from './pages/Collaboration';
import CollaborationDetail from './pages/CollaborationDetail';
import CreateCollaboration from './pages/CreateCollaboration';
import Profile from './pages/Profile';
import IPFSManager from './pages/IPFSManager';
import Users from './pages/Users';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

// Hooks and Context
import { useAuth } from './hooks/useAuth';
import { AuthProvider } from './context/AuthContext';
import { SocketProvider } from './context/SocketContext';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function AppContent() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/login" 
          element={!user ? <Login /> : <Navigate to="/dashboard" replace />} 
        />
        <Route 
          path="/register" 
          element={!user ? <Register /> : <Navigate to="/dashboard" replace />} 
        />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Courses */}
            <Route path="/courses" element={<Courses />} />
            <Route path="/courses/:id" element={<CourseDetail />} />
            <Route path="/courses/create" element={<CreateCourse />} />
            
            {/* Research */}
            <Route path="/research" element={<Research />} />
            <Route path="/research/:id" element={<ResearchDetail />} />
            <Route path="/research/create" element={<CreateResearch />} />
            <Route path="/research/:id/edit" element={<EditResearch />} />
            
            {/* Collaboration */}
            <Route path="/collaboration" element={<Collaboration />} />
            <Route path="/collaboration/:id" element={<CollaborationDetail />} />
            <Route path="/collaboration/create" element={<CreateCollaboration />} />
            
            {/* User Management */}
            <Route path="/users" element={<Users />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/:id" element={<Profile />} />
            
            {/* IPFS */}
            <Route path="/ipfs" element={<IPFSManager />} />
            
            {/* Settings */}
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
        
        {/* Default Routes */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <AuthProvider>
            <SocketProvider>
              <AppContent />
              <Toaster 
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                }}
              />
            </SocketProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App; 