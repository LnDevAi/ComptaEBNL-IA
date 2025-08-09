import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Container,
  Avatar,
  InputAdornment,
  IconButton,
  Alert,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import {
  AccountBalance,
  Email,
  Lock,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();
  const { showError, showSuccess } = useNotification();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // Gestion des changements de formulaire
  const handleChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    
    // Effacer l'erreur du champ modifié
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  // Validation du formulaire
  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.email) {
      newErrors.email = 'L\'email est requis';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Format d\'email invalide';
    }

    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Gestion de la soumission
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const success = await login(formData.email, formData.password);
      
      if (success) {
        showSuccess('Connexion réussie ! Bienvenue sur ComptaEBNL-IA');
        navigate('/dashboard');
      } else {
        showError('Email ou mot de passe incorrect');
      }
    } catch (error) {
      showError('Erreur de connexion. Veuillez réessayer.');
      console.error('Erreur de connexion:', error);
    }
  };

  // Basculer la visibilité du mot de passe
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Connexion de démonstration
  const handleDemoLogin = () => {
    setFormData({
      email: 'admin@comptaebnl.fr',
      password: 'demo123',
    });
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1976d2 0%, #42a5f5 100%)',
        p: 2,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={10}
          sx={{
            p: 4,
            borderRadius: 3,
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Avatar
              sx={{
                mx: 'auto',
                mb: 2,
                bgcolor: 'primary.main',
                width: 64,
                height: 64,
              }}
            >
              <AccountBalance sx={{ fontSize: 32 }} />
            </Avatar>
            
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
              ComptaEBNL-IA
            </Typography>
            
            <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
              Plateforme de comptabilité EBNL avec Intelligence Artificielle
            </Typography>
            
            <Typography variant="body2" color="text.secondary">
              Connectez-vous pour accéder à votre espace comptable
            </Typography>
          </Box>

          {/* Bouton de démonstration */}
          <Card sx={{ mb: 3, backgroundColor: 'info.light', color: 'white' }}>
            <CardContent sx={{ py: 2 }}>
              <Typography variant="body2" gutterBottom>
                🚀 Mode Démonstration
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                Utilisez les identifiants de test pour découvrir la plateforme
              </Typography>
              <Button
                variant="contained"
                size="small"
                onClick={handleDemoLogin}
                sx={{ backgroundColor: 'white', color: 'info.main' }}
              >
                Utiliser les identifiants de démo
              </Button>
            </CardContent>
          </Card>

          {/* Formulaire de connexion */}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <TextField
              fullWidth
              label="Adresse email"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              error={!!errors.email}
              helperText={errors.email}
              margin="normal"
              autoComplete="email"
              autoFocus
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Mot de passe"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange('password')}
              error={!!errors.password}
              helperText={errors.password}
              margin="normal"
              autoComplete="current-password"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={togglePasswordVisibility} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={isLoading}
              sx={{
                mt: 3,
                mb: 2,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 600,
                borderRadius: 2,
              }}
            >
              {isLoading ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Connexion en cours...
                </>
              ) : (
                'Se connecter'
              )}
            </Button>
          </Box>

          {/* Informations supplémentaires */}
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              © 2024 ComptaEBNL-IA - Système Comptable des Entités à But Non Lucratif
            </Typography>
          </Box>

          {/* Identifiants de démonstration (visible en mode développement) */}
          {process.env.NODE_ENV === 'development' && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" component="div">
                <strong>Identifiants de démonstration :</strong><br />
                Email: admin@comptaebnl.fr<br />
                Mot de passe: demo123
              </Typography>
            </Alert>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default Login;