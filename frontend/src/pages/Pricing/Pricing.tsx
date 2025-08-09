import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Divider,
  Paper,
} from '@mui/material';
import {
  Check,
  Close,
  Star,
  CreditCard,
  Phone,
  AccountBalance,
  Security,
  CloudUpload,
  Analytics,
  Support,
} from '@mui/icons-material';
import { apiClient } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';

// Types
interface Plan {
  id: number;
  nom: string;
  type_plan: string;
  prix_mensuel: number;
  prix_annuel?: number;
  devise: string;
  limitations: {
    max_entites: number;
    max_ecritures_mois: number;
    max_utilisateurs: number;
    max_documents_mois: number;
  };
  fonctionnalites: {
    ia_avancee: boolean;
    ocr_documents: boolean;
    etats_financiers_avances: boolean;
    rapprochement_bancaire: boolean;
    audit_trail: boolean;
    support_prioritaire: boolean;
    api_access: boolean;
  };
  description: string;
  economie_annuelle?: number;
  pourcentage_economie?: number;
}

interface PaymentMethod {
  id: string;
  name: string;
  icon: React.ReactElement;
  description: string;
  countries?: string[];
}

const Pricing: React.FC = () => {
  const { showError, showSuccess, showInfo } = useNotification();
  
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAnnual, setIsAnnual] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [paymentDialog, setPaymentDialog] = useState(false);
  const [paymentData, setPaymentData] = useState({
    methode_paiement: '',
    numero_telephone: '',
    code_coupon: '',
    devise: 'EUR'
  });
  const [processing, setProcessing] = useState(false);

  // Méthodes de paiement disponibles
  const paymentMethods: PaymentMethod[] = [
    {
      id: 'stripe',
      name: 'Carte Bancaire',
      icon: <CreditCard />,
      description: 'Visa, Mastercard, American Express'
    },
    {
      id: 'paypal',
      name: 'PayPal',
      icon: <AccountBalance />,
      description: 'Paiement sécurisé via PayPal'
    },
    {
      id: 'mtn_mobile_money',
      name: 'MTN Mobile Money',
      icon: <Phone />,
      description: 'Paiement mobile MTN (*126#)',
      countries: ['Cameroun', 'Côte d\'Ivoire', 'Ghana', 'Ouganda']
    },
    {
      id: 'orange_money',
      name: 'Orange Money',
      icon: <Phone />,
      description: 'Paiement mobile Orange (#144#)',
      countries: ['Sénégal', 'Mali', 'Burkina Faso', 'Niger']
    },
    {
      id: 'wave',
      name: 'Wave',
      icon: <Phone />,
      description: 'Paiement via l\'app Wave',
      countries: ['Sénégal', 'Côte d\'Ivoire', 'Mali']
    },
    {
      id: 'moov_money',
      name: 'Moov Money',
      icon: <Phone />,
      description: 'Paiement mobile Moov',
      countries: ['Bénin', 'Togo', 'Côte d\'Ivoire']
    }
  ];

  // Charger les plans
  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/v1/plans');
      
      if (response.data.success) {
        setPlans(response.data.data.plans);
      }
    } catch (error) {
      showError('Erreur lors du chargement des plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = (plan: Plan) => {
    setSelectedPlan(plan);
    setPaymentData({
      ...paymentData,
      devise: plan.devise
    });
    setPaymentDialog(true);
  };

  const handlePayment = async () => {
    if (!selectedPlan) return;

    try {
      setProcessing(true);

      const subscriptionData = {
        plan_id: selectedPlan.id,
        periode: isAnnual ? 'annuel' : 'mensuel',
        methode_paiement: paymentData.methode_paiement,
        devise: paymentData.devise,
        ...(paymentData.numero_telephone && { numero_telephone: paymentData.numero_telephone }),
        ...(paymentData.code_coupon && { code_coupon: paymentData.code_coupon })
      };

      const response = await apiClient.post('/api/v1/souscrire', subscriptionData);

      if (response.data.success) {
        const result = response.data.data;
        
        if (result.payment_url) {
          // Redirection vers la page de paiement
          window.open(result.payment_url, '_blank');
        }

        showSuccess('Abonnement créé avec succès !');
        setPaymentDialog(false);
        
        // Afficher les instructions si Mobile Money
        if (response.data.data.instructions) {
          showInfo(response.data.message || 'Suivez les instructions pour finaliser le paiement');
        }
      } else {
        showError(response.data.error || 'Erreur lors de la création de l\'abonnement');
      }
    } catch (error: any) {
      showError(error.response?.data?.error || 'Erreur lors du paiement');
    } finally {
      setProcessing(false);
    }
  };

  const getPlanPrice = (plan: Plan) => {
    if (isAnnual && plan.prix_annuel) {
      return plan.prix_annuel;
    }
    return isAnnual ? plan.prix_mensuel * 12 : plan.prix_mensuel;
  };

  const getPlanPeriodText = (plan: Plan) => {
    if (isAnnual && plan.prix_annuel) {
      return `${plan.prix_annuel}€/an`;
    }
    return isAnnual ? `${plan.prix_mensuel * 12}€/an` : `${plan.prix_mensuel}€/mois`;
  };

  const isMobileMoneyMethod = (method: string) => {
    return ['mtn_mobile_money', 'orange_money', 'wave', 'moov_money', 'airtel_money'].includes(method);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Chargement des plans d'abonnement...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      {/* En-tête */}
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Choisissez votre plan
        </Typography>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          Comptabilité EBNL avec Intelligence Artificielle
        </Typography>

        {/* Switch Mensuel/Annuel */}
        <Paper sx={{ display: 'inline-flex', p: 1, mb: 4 }}>
          <FormControlLabel
            control={
              <Switch
                checked={isAnnual}
                onChange={(e) => setIsAnnual(e.target.checked)}
                color="primary"
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Typography variant="body1">
                  Facturation annuelle
                </Typography>
                <Chip 
                  label="2 mois gratuits !" 
                  color="success" 
                  size="small" 
                  sx={{ ml: 1 }}
                />
              </Box>
            }
          />
        </Paper>
      </Box>

      {/* Plans d'abonnement */}
      <Grid container spacing={4} justifyContent="center">
        {plans.map((plan) => (
          <Grid item xs={12} md={4} key={plan.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                border: plan.type_plan === 'professionnel' ? '2px solid' : '1px solid',
                borderColor: plan.type_plan === 'professionnel' ? 'primary.main' : 'divider',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6
                }
              }}
            >
              {/* Badge populaire */}
              {plan.type_plan === 'professionnel' && (
                <Chip
                  label="Le plus populaire"
                  color="primary"
                  icon={<Star />}
                  sx={{
                    position: 'absolute',
                    top: -12,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    zIndex: 1
                  }}
                />
              )}

              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                {/* En-tête du plan */}
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <Typography variant="h5" component="h3" gutterBottom>
                    {plan.nom}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {plan.description}
                  </Typography>
                  
                  {/* Prix */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="h3" component="span" color="primary.main">
                      {getPlanPrice(plan)}€
                    </Typography>
                    <Typography variant="h6" component="span" color="text.secondary">
                      /{isAnnual ? 'an' : 'mois'}
                    </Typography>
                  </Box>

                  {/* Économie annuelle */}
                  {isAnnual && plan.pourcentage_economie && (
                    <Chip
                      label={`Économisez ${plan.pourcentage_economie}%`}
                      color="success"
                      size="small"
                    />
                  )}
                </Box>

                {/* Limitations */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom color="text.secondary">
                    INCLUS :
                  </Typography>
                  <List dense>
                    <ListItem disablePadding>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Check color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          plan.limitations.max_entites === -1 
                            ? "Entités EBNL illimitées"
                            : `${plan.limitations.max_entites} entité${plan.limitations.max_entites > 1 ? 's' : ''} EBNL`
                        }
                      />
                    </ListItem>
                    
                    <ListItem disablePadding>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Check color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          plan.limitations.max_ecritures_mois === -1 
                            ? "Écritures illimitées"
                            : `${plan.limitations.max_ecritures_mois} écritures/mois`
                        }
                      />
                    </ListItem>
                    
                    <ListItem disablePadding>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Check color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={
                          plan.limitations.max_utilisateurs === -1 
                            ? "Utilisateurs illimités"
                            : `${plan.limitations.max_utilisateurs} utilisateur${plan.limitations.max_utilisateurs > 1 ? 's' : ''}`
                        }
                      />
                    </ListItem>
                  </List>
                </Box>

                {/* Fonctionnalités */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom color="text.secondary">
                    FONCTIONNALITÉS :
                  </Typography>
                  <List dense>
                    {Object.entries(plan.fonctionnalites).map(([key, enabled]) => (
                      <ListItem key={key} disablePadding>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          {enabled ? (
                            <Check color="success" fontSize="small" />
                          ) : (
                            <Close color="disabled" fontSize="small" />
                          )}
                        </ListItemIcon>
                        <ListItemText 
                          primary={getFunctionalityLabel(key)}
                          sx={{ 
                            '& .MuiListItemText-primary': { 
                              color: enabled ? 'text.primary' : 'text.disabled' 
                            }
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>

                {/* Bouton d'abonnement */}
                <Button
                  variant={plan.type_plan === 'professionnel' ? 'contained' : 'outlined'}
                  fullWidth
                  size="large"
                  onClick={() => handleSubscribe(plan)}
                  sx={{ mt: 'auto' }}
                >
                  {plan.prix_mensuel === 0 ? 'Commencer gratuitement' : 'S\'abonner'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Méthodes de paiement supportées */}
      <Box sx={{ mt: 8, textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          Méthodes de paiement supportées
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Paiements sécurisés avec options Mobile Money pour l'Afrique
        </Typography>
        
        <Grid container spacing={2} justifyContent="center">
          {paymentMethods.map((method) => (
            <Grid item xs={6} sm={4} md={2} key={method.id}>
              <Paper 
                sx={{ 
                  p: 2, 
                  textAlign: 'center',
                  '&:hover': { boxShadow: 3 }
                }}
              >
                <Box sx={{ color: 'primary.main', mb: 1 }}>
                  {method.icon}
                </Box>
                <Typography variant="caption" display="block">
                  {method.name}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Dialog de paiement */}
      <Dialog 
        open={paymentDialog} 
        onClose={() => setPaymentDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Finaliser l'abonnement
          {selectedPlan && (
            <Typography variant="body2" color="text.secondary">
              Plan {selectedPlan.nom} - {getPlanPeriodText(selectedPlan)}
            </Typography>
          )}
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            {/* Méthode de paiement */}
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Méthode de paiement</InputLabel>
              <Select
                value={paymentData.methode_paiement}
                onChange={(e) => setPaymentData({
                  ...paymentData,
                  methode_paiement: e.target.value
                })}
                label="Méthode de paiement"
              >
                {paymentMethods.map((method) => (
                  <MenuItem key={method.id} value={method.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      {method.icon}
                      <Box sx={{ ml: 2 }}>
                        <Typography variant="body2">{method.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {method.description}
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Numéro de téléphone pour Mobile Money */}
            {isMobileMoneyMethod(paymentData.methode_paiement) && (
              <TextField
                fullWidth
                label="Numéro de téléphone"
                value={paymentData.numero_telephone}
                onChange={(e) => setPaymentData({
                  ...paymentData,
                  numero_telephone: e.target.value
                })}
                placeholder="+221 77 123 45 67"
                sx={{ mb: 3 }}
                helperText="Numéro associé à votre compte Mobile Money"
              />
            )}

            {/* Code coupon */}
            <TextField
              fullWidth
              label="Code coupon (optionnel)"
              value={paymentData.code_coupon}
              onChange={(e) => setPaymentData({
                ...paymentData,
                code_coupon: e.target.value
              })}
              sx={{ mb: 3 }}
              placeholder="PROMO2024"
            />

            {/* Résumé */}
            {selectedPlan && (
              <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Résumé de la commande :
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Plan {selectedPlan.nom}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {getPlanPrice(selectedPlan)}€
                  </Typography>
                </Box>
                <Divider sx={{ my: 1 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="subtitle2">Total :</Typography>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {getPlanPrice(selectedPlan)}€
                  </Typography>
                </Box>
              </Paper>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setPaymentDialog(false)}>
            Annuler
          </Button>
          <Button 
            variant="contained" 
            onClick={handlePayment}
            disabled={!paymentData.methode_paiement || processing}
            startIcon={processing ? <CircularProgress size={20} /> : <Security />}
          >
            {processing ? 'Traitement...' : 'Confirmer le paiement'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

// Helper function pour les labels des fonctionnalités
const getFunctionalityLabel = (key: string): string => {
  const labels: { [key: string]: string } = {
    ia_avancee: 'IA avancée',
    ocr_documents: 'OCR documents',
    etats_financiers_avances: 'États financiers avancés',
    rapprochement_bancaire: 'Rapprochement bancaire',
    audit_trail: 'Piste d\'audit',
    support_prioritaire: 'Support prioritaire',
    api_access: 'Accès API'
  };
  return labels[key] || key;
};

export default Pricing;