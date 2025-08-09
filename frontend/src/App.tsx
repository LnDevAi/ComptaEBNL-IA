import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { fr } from 'date-fns/locale';

// Components
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import PlanComptable from './pages/PlanComptable/PlanComptable';
import Ecritures from './pages/Ecritures/Ecritures';
import EtatsFinanciers from './pages/EtatsFinanciers/EtatsFinanciers';
import Exercices from './pages/Exercices/Exercices';
import Analytics from './pages/Analytics/Analytics';
import Rapprochement from './pages/Rapprochement/Rapprochement';
import Entites from './pages/Entites/Entites';
import Notifications from './pages/Notifications/Notifications';
import Audit from './pages/Audit/Audit';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register'; // Added Register component
import Pricing from './pages/Pricing/Pricing'; // Added Pricing component
import BillingDashboard from './pages/Billing/BillingDashboard'; // Added BillingDashboard component
import EcrituresPage from './pages/Ecritures/EcrituresPage'; // Added EcrituresPage component
import EntitesPage from './pages/Entites/EntitesPage'; // Added EntitesPage component
import DocumentsPage from './pages/Documents/DocumentsPage'; // Added DocumentsPage component
import ReportsPage from './pages/Reports/ReportsPage'; // Added ReportsPage component
import LearningDashboard from './pages/Learning/LearningDashboard';
import FormationCatalog from './pages/Learning/FormationCatalog';
import FormationDetail from './pages/Learning/FormationDetail';
import LessonPlayer from './pages/Learning/LessonPlayer';
import CertificateDashboard from './pages/Learning/CertificateDashboard';

// Context
import { AuthProvider } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';

// Theme Material-UI personnalisé pour ComptaEBNL-IA
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Bleu professionnel
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#388e3c', // Vert comptabilité
      light: '#66bb6a',
      dark: '#2e7d32',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
        size: 'small',
      },
    },
  },
});

// Hook pour vérifier l'authentification
const useAuth = () => {
  // Simulation de l'authentification pour la démo
  const [isAuthenticated, setIsAuthenticated] = React.useState(() => {
    return localStorage.getItem('comptaEBNL_token') !== null;
  });

  const login = (token: string) => {
    localStorage.setItem('comptaEBNL_token', token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('comptaEBNL_token');
    setIsAuthenticated(false);
  };

  return { isAuthenticated, login, logout };
};

// Composant de protection des routes
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Composant principal de l'application
const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={fr}>
        <AuthProvider>
          <NotificationProvider>
            <Router>
              <Routes>
                {/* Route de connexion */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/pricing" element={<Pricing />} />
                
                {/* Routes protégées */}
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <Layout>
                        <Routes>
                          {/* Tableau de bord principal */}
                          <Route index element={<Dashboard />} />
                          <Route path="/dashboard" element={<Dashboard />} />
                          
                          {/* Comptabilité */}
                          <Route path="/plan-comptable" element={<PlanComptable />} />
                          <Route path="/ecritures" element={<Ecritures />} />
                          <Route path="/ecritures-page" element={<EcrituresPage />} /> {/* Added EcrituresPage route */}
                          <Route path="/etats-financiers" element={<EtatsFinanciers />} />
                          <Route path="/exercices" element={<Exercices />} />
                          
                          {/* Analyses et rapports */}
                          <Route path="/analytics" element={<Analytics />} />
                          <Route path="/rapprochement" element={<Rapprochement />} />
                          <Route path="reports" element={<ReportsPage />} /> {/* Added ReportsPage route */}
                          
                          {/* Gestion */}
                          <Route path="/entites" element={<Entites />} />
                          <Route path="/entites-page" element={<EntitesPage />} /> {/* Added EntitesPage route */}
                          <Route path="/notifications" element={<Notifications />} />
                          <Route path="/audit" element={<Audit />} />
                          <Route path="billing" element={<BillingDashboard />} /> {/* Added BillingDashboard route */}
                          <Route path="documents" element={<DocumentsPage />} /> {/* Added DocumentsPage route */}
                          
                          {/* E-learning */}
                          <Route path="/learning" element={<LearningDashboard />} />
                          <Route path="/learning/formations" element={<FormationCatalog />} />
                          <Route path="/learning/formations/:id" element={<FormationDetail />} />
                          <Route path="/learning/lecons/:id" element={<LessonPlayer />} />
                          <Route path="/learning/certificats" element={<CertificateDashboard />} />
                          
                          {/* Route par défaut */}
                          <Route path="*" element={<Navigate to="/dashboard" replace />} />
                        </Routes>
                      </Layout>
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </Router>
          </NotificationProvider>
        </AuthProvider>
      </LocalizationProvider>
    </ThemeProvider>
  );
};

export default App;
