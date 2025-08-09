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
  ListItemText,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CreditCard,
  Download,
  Receipt,
  Upgrade,
  Cancel,
  History,
  CheckCircle,
  Warning,
  Error,
  Phone,
  AccountBalance,
  Refresh,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { apiClient } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';

// Types
interface Subscription {
  id: number;
  plan: {
    nom: string;
    type_plan: string;
    prix_mensuel: number;
    prix_annuel?: number;
  };
  statut: string;
  date_debut: string;
  date_fin: string;
  periode_facturation: string;
  montant: number;
  devise: string;
  est_actif: boolean;
  jours_restants: number;
  utilisation: {
    ecritures_mois: number;
    documents_mois: number;
  };
}

interface Payment {
  id: number;
  montant: number;
  devise: string;
  methode_paiement: string;
  statut: string;
  transaction_id: string;
  numero_telephone?: string;
  operateur_mobile?: string;
  date_creation: string;
  date_traitement?: string;
}

const BillingDashboard: React.FC = () => {
  const { showError, showSuccess, showInfo } = useNotification();
  
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelDialog, setCancelDialog] = useState(false);
  const [upgradeDialog, setUpgradeDialog] = useState(false);

  useEffect(() => {
    loadBillingData();
  }, []);

  const loadBillingData = async () => {
    try {
      setLoading(true);
      
      // Charger l'abonnement actuel
      const subResponse = await apiClient.get('/api/v1/mon-abonnement');
      if (subResponse.data.success && subResponse.data.data.abonnement) {
        setSubscription(subResponse.data.data.abonnement);
      }

      // Charger l'historique des paiements (simulation)
      // En production, ajouter l'endpoint dans l'API
      setPayments([
        {
          id: 1,
          montant: 30.00,
          devise: 'EUR',
          methode_paiement: 'mtn_mobile_money',
          statut: 'reussi',
          transaction_id: 'MTN-abc123def456',
          numero_telephone: '+221 77 123 45 67',
          operateur_mobile: 'MTN',
          date_creation: '2024-01-15T10:30:00Z',
          date_traitement: '2024-01-15T10:32:15Z'
        },
        {
          id: 2,
          montant: 30.00,
          devise: 'EUR',
          methode_paiement: 'stripe',
          statut: 'reussi',
          transaction_id: 'pi_xyz789uvw123',
          date_creation: '2023-12-15T14:20:00Z',
          date_traitement: '2023-12-15T14:20:45Z'
        }
      ]);

    } catch (error) {
      showError('Erreur lors du chargement des données de facturation');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'actif':
      case 'reussi':
        return 'success';
      case 'expire':
      case 'echoue':
        return 'error';
      case 'suspendu':
      case 'en_attente':
        return 'warning';
      case 'annule':
        return 'default';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      actif: 'Actif',
      expire: 'Expiré',
      suspendu: 'Suspendu',
      annule: 'Annulé',
      en_attente: 'En attente',
      reussi: 'Réussi',
      echoue: 'Échoué',
      rembourse: 'Remboursé'
    };
    return labels[status] || status;
  };

  const getPaymentMethodIcon = (method: string) => {
    if (method.includes('mobile_money') || method === 'wave' || method === 'orange_money') {
      return <Phone fontSize="small" />;
    } else if (method === 'paypal') {
      return <AccountBalance fontSize="small" />;
    } else {
      return <CreditCard fontSize="small" />;
    }
  };

  const getPaymentMethodLabel = (method: string) => {
    const labels: { [key: string]: string } = {
      stripe: 'Carte bancaire',
      paypal: 'PayPal',
      mtn_mobile_money: 'MTN Mobile Money',
      orange_money: 'Orange Money',
      wave: 'Wave',
      moov_money: 'Moov Money',
      airtel_money: 'Airtel Money'
    };
    return labels[method] || method;
  };

  const calculateUsagePercentage = (used: number, max: number) => {
    if (max === -1) return 0; // Illimité
    return Math.min((used / max) * 100, 100);
  };

  const handleCancelSubscription = async () => {
    try {
      // API call pour annuler l'abonnement
      showInfo('Fonctionnalité en développement');
      setCancelDialog(false);
    } catch (error) {
      showError('Erreur lors de l\'annulation');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Chargement de votre facturation...
        </Typography>
      </Container>
    );
  }

  if (!subscription) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 6 }}>
            <Typography variant="h5" gutterBottom>
              Aucun abonnement actif
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Vous n'avez pas encore d'abonnement à ComptaEBNL-IA
            </Typography>
            <Button
              variant="contained"
              size="large"
              href="/pricing"
              startIcon={<Upgrade />}
            >
              Voir les plans d'abonnement
            </Button>
          </CardContent>
        </Card>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* En-tête */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Facturation et Abonnement
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Gérez votre abonnement ComptaEBNL-IA et consultez votre historique de paiements
        </Typography>
      </Box>

      <Grid container spacing={4}>
        {/* Informations sur l'abonnement */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Plan {subscription.plan.nom}
                  </Typography>
                  <Chip
                    label={getStatusLabel(subscription.statut)}
                    color={getStatusColor(subscription.statut) as any}
                    icon={subscription.est_actif ? <CheckCircle /> : <Warning />}
                    sx={{ mb: 2 }}
                  />
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="h4" color="primary.main">
                    {subscription.montant}€
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    /{subscription.periode_facturation === 'mensuel' ? 'mois' : 'an'}
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ my: 3 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Date de début
                  </Typography>
                  <Typography variant="body1">
                    {format(new Date(subscription.date_debut), 'dd MMMM yyyy', { locale: fr })}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Prochaine facturation
                  </Typography>
                  <Typography variant="body1">
                    {format(new Date(subscription.date_fin), 'dd MMMM yyyy', { locale: fr })}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Jours restants
                  </Typography>
                  <Typography variant="body1" color={subscription.jours_restants < 7 ? 'warning.main' : 'text.primary'}>
                    {subscription.jours_restants} jours
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Type de facturation
                  </Typography>
                  <Typography variant="body1">
                    {subscription.periode_facturation === 'mensuel' ? 'Mensuelle' : 'Annuelle'}
                  </Typography>
                </Grid>
              </Grid>

              <Box sx={{ mt: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<Upgrade />}
                  onClick={() => setUpgradeDialog(true)}
                >
                  Changer de plan
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<Cancel />}
                  onClick={() => setCancelDialog(true)}
                >
                  Annuler l'abonnement
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={loadBillingData}
                >
                  Actualiser
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Historique des paiements */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Historique des paiements
                </Typography>
                <Button
                  startIcon={<Download />}
                  size="small"
                  onClick={() => showInfo('Export en développement')}
                >
                  Exporter
                </Button>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Montant</TableCell>
                      <TableCell>Méthode</TableCell>
                      <TableCell>Statut</TableCell>
                      <TableCell>Transaction</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {payments.map((payment) => (
                      <TableRow key={payment.id}>
                        <TableCell>
                          {format(new Date(payment.date_creation), 'dd/MM/yyyy HH:mm', { locale: fr })}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {payment.montant}€
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getPaymentMethodIcon(payment.methode_paiement)}
                            <Box>
                              <Typography variant="body2">
                                {getPaymentMethodLabel(payment.methode_paiement)}
                              </Typography>
                              {payment.numero_telephone && (
                                <Typography variant="caption" color="text.secondary">
                                  {payment.numero_telephone}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={getStatusLabel(payment.statut)}
                            color={getStatusColor(payment.statut) as any}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                            {payment.transaction_id}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Télécharger la facture">
                            <IconButton
                              size="small"
                              onClick={() => showInfo('Téléchargement de facture en développement')}
                            >
                              <Receipt fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {payments.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Aucun paiement trouvé
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Utilisation et statistiques */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Utilisation ce mois-ci
              </Typography>

              {/* Écritures */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    Écritures comptables
                  </Typography>
                  <Typography variant="body2">
                    {subscription.utilisation.ecritures_mois}
                    {subscription.plan.type_plan !== 'gratuit' ? ' / ∞' : ' / 100'}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={subscription.plan.type_plan === 'gratuit' 
                    ? calculateUsagePercentage(subscription.utilisation.ecritures_mois, 100)
                    : 25 // Simulation pour les plans payants
                  }
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              {/* Documents */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">
                    Documents traités
                  </Typography>
                  <Typography variant="body2">
                    {subscription.utilisation.documents_mois}
                    {subscription.plan.type_plan === 'gratuit' ? ' / 10' : ' / ∞'}
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={subscription.plan.type_plan === 'gratuit' 
                    ? calculateUsagePercentage(subscription.utilisation.documents_mois, 10)
                    : 15 // Simulation pour les plans payants
                  }
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              {/* Alertes d'utilisation */}
              {subscription.plan.type_plan === 'gratuit' && 
               subscription.utilisation.ecritures_mois > 80 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Vous approchez de votre limite d'écritures. 
                  <Button size="small" href="/pricing">
                    Passer au plan Pro
                  </Button>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Recommandations */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommandations
              </Typography>

              {subscription.plan.type_plan === 'gratuit' && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2" gutterBottom>
                    <strong>Débloquez plus de fonctionnalités !</strong>
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Passez au plan Professionnel pour :
                  </Typography>
                  <List dense>
                    <ListItem disablePadding>
                      <ListItemText primary="• Écritures illimitées" />
                    </ListItem>
                    <ListItem disablePadding>
                      <ListItemText primary="• IA avancée et OCR" />
                    </ListItem>
                    <ListItem disablePadding>
                      <ListItemText primary="• États financiers avancés" />
                    </ListItem>
                  </List>
                  <Button
                    variant="contained"
                    size="small"
                    fullWidth
                    href="/pricing"
                    sx={{ mt: 2 }}
                  >
                    Voir les plans
                  </Button>
                </Alert>
              )}

              {subscription.jours_restants < 7 && (
                <Alert severity="warning">
                  <Typography variant="body2">
                    Votre abonnement expire dans {subscription.jours_restants} jours.
                    Renouvelez-le pour continuer à utiliser ComptaEBNL-IA.
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Dialog d'annulation */}
      <Dialog open={cancelDialog} onClose={() => setCancelDialog(false)}>
        <DialogTitle>Annuler l'abonnement</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Êtes-vous sûr de vouloir annuler votre abonnement ?
          </Typography>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Cette action est irréversible. Vous perdrez l'accès aux fonctionnalités premium
            à la fin de votre période de facturation actuelle.
          </Alert>
          <Typography variant="body2" color="text.secondary">
            Votre abonnement restera actif jusqu'au {subscription && format(new Date(subscription.date_fin), 'dd MMMM yyyy', { locale: fr })}.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialog(false)}>
            Conserver l'abonnement
          </Button>
          <Button 
            color="error" 
            variant="contained"
            onClick={handleCancelSubscription}
          >
            Confirmer l'annulation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de changement de plan */}
      <Dialog open={upgradeDialog} onClose={() => setUpgradeDialog(false)}>
        <DialogTitle>Changer de plan</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Vous souhaitez changer votre plan d'abonnement ?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Vous pouvez passer à un plan supérieur ou inférieur. 
            Les changements prendront effet lors de votre prochaine facturation.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpgradeDialog(false)}>
            Annuler
          </Button>
          <Button 
            variant="contained"
            href="/pricing"
            onClick={() => setUpgradeDialog(false)}
          >
            Voir les plans
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BillingDashboard;