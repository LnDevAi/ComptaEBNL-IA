import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Alert,
  Button,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Receipt,
  People,
  Notifications,
  Warning,
  CheckCircle,
  Error,
  Info,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiClient } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';

// Types
interface KPIData {
  total_dons: number;
  total_subventions: number;
  total_cotisations: number;
  total_charges: number;
  tresorerie_banque: number;
  tresorerie_caisse: number;
  nb_ecritures: number;
  ratio_autonomie: number;
  ratio_liquidite: number;
}

interface NotificationItem {
  id: string;
  titre: string;
  message: string;
  type: string;
  date_creation: string;
  lu: boolean;
}

interface HealthMetrics {
  score_sante: number;
  niveau_sante: string;
  alertes_critiques: any[];
  metriques_sante: {
    ecritures_en_brouillard: number;
    exercices_ouverts: number;
    activite_7_jours: number;
    utilisateurs_actifs: number;
  };
}

// Composant KPI Card
const KPICard: React.FC<{
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactElement;
  color: string;
  trend?: number;
}> = ({ title, value, subtitle, icon, color, trend }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Avatar sx={{ bgcolor: `${color}.main`, mr: 2 }}>
          {icon}
        </Avatar>
        <Box>
          <Typography variant="h6" component="div">
            {typeof value === 'number' ? value.toLocaleString('fr-FR') : value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
        </Box>
      </Box>
      
      {subtitle && (
        <Typography variant="caption" color="text.secondary">
          {subtitle}
        </Typography>
      )}
      
      {trend !== undefined && (
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          {trend > 0 ? (
            <TrendingUp color="success" fontSize="small" />
          ) : (
            <TrendingDown color="error" fontSize="small" />
          )}
          <Typography
            variant="caption"
            color={trend > 0 ? 'success.main' : 'error.main'}
            sx={{ ml: 0.5 }}
          >
            {Math.abs(trend)}%
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  const { showError } = useNotification();
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [healthMetrics, setHealthMetrics] = useState<HealthMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  // Données mockées pour les graphiques
  const evolutionTresorerie = [
    { mois: 'Jan', montant: 15000 },
    { mois: 'Fév', montant: 18000 },
    { mois: 'Mar', montant: 16500 },
    { mois: 'Avr', montant: 21000 },
    { mois: 'Mai', montant: 19500 },
    { mois: 'Jun', montant: 23000 },
  ];

  const repartitionRessources = [
    { name: 'Dons', value: 45, color: '#8884d8' },
    { name: 'Subventions', value: 35, color: '#82ca9d' },
    { name: 'Cotisations', value: 15, color: '#ffc658' },
    { name: 'Autres', value: 5, color: '#ff7300' },
  ];

  const activiteComptable = [
    { mois: 'Jan', ecritures: 45 },
    { mois: 'Fév', ecritures: 52 },
    { mois: 'Mar', ecritures: 48 },
    { mois: 'Avr', ecritures: 61 },
    { mois: 'Mai', ecritures: 55 },
    { mois: 'Jun', ecritures: 67 },
  ];

  // Charger les données du tableau de bord
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);

        // Charger les KPI
        const kpiResponse = await apiClient.get('/api/v1/dashboard/kpi');
        if (kpiResponse.data.success) {
          setKpiData(kpiResponse.data.data.kpis);
        }

        // Charger les notifications
        const notifResponse = await apiClient.get('/api/v1/notifications?limit=5');
        if (notifResponse.data.success) {
          setNotifications(notifResponse.data.data.notifications);
        }

        // Charger les métriques de santé
        const healthResponse = await apiClient.get('/api/v1/alertes/tableau-bord');
        if (healthResponse.data.success) {
          setHealthMetrics(healthResponse.data.data);
        }

      } catch (error) {
        console.error('Erreur lors du chargement du tableau de bord:', error);
        showError('Erreur lors du chargement des données');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [showError]);

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2, textAlign: 'center' }}>
          Chargement du tableau de bord...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* En-tête du tableau de bord */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Tableau de bord
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Vue d'ensemble de votre comptabilité EBNL
        </Typography>
      </Box>

      {/* Métriques de santé globale */}
      {healthMetrics && (
        <Alert
          severity={
            healthMetrics.niveau_sante === 'excellent' ? 'success' :
            healthMetrics.niveau_sante === 'bon' ? 'info' : 'warning'
          }
          sx={{ mb: 3 }}
        >
          <Typography variant="body2">
            <strong>Santé du système :</strong> {healthMetrics.score_sante}% ({healthMetrics.niveau_sante})
            {healthMetrics.alertes_critiques.length > 0 && (
              <span> - {healthMetrics.alertes_critiques.length} alerte(s) critique(s)</span>
            )}
          </Typography>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* KPI Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Dons"
            value={`${kpiData?.total_dons?.toLocaleString('fr-FR') || 0} €`}
            subtitle="Dons reçus cette année"
            icon={<TrendingUp />}
            color="success"
            trend={12}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Subventions"
            value={`${kpiData?.total_subventions?.toLocaleString('fr-FR') || 0} €`}
            subtitle="Subventions publiques"
            icon={<AccountBalance />}
            color="primary"
            trend={8}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Trésorerie"
            value={`${((kpiData?.tresorerie_banque || 0) + (kpiData?.tresorerie_caisse || 0)).toLocaleString('fr-FR')} €`}
            subtitle="Banque + Caisse"
            icon={<AccountBalance />}
            color="info"
            trend={-3}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Écritures"
            value={kpiData?.nb_ecritures || 0}
            subtitle="Cette période"
            icon={<Receipt />}
            color="warning"
            trend={15}
          />
        </Grid>

        {/* Graphique d'évolution de la trésorerie */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Évolution de la trésorerie
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={evolutionTresorerie}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mois" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value} €`, 'Montant']} />
                  <Area
                    type="monotone"
                    dataKey="montant"
                    stroke="#1976d2"
                    fill="#1976d2"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Répartition des ressources */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Répartition des ressources
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={repartitionRessources}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {repartitionRessources.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Activité comptable */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Activité comptable mensuelle
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={activiteComptable}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="mois" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="ecritures" fill="#388e3c" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Notifications récentes */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Notifications récentes
              </Typography>
              
              {notifications.length > 0 ? (
                <List>
                  {notifications.slice(0, 4).map((notif, index) => (
                    <React.Fragment key={notif.id}>
                      <ListItem alignItems="flex-start">
                        <ListItemAvatar>
                          <Avatar sx={{ 
                            bgcolor: notif.type === 'success' ? 'success.main' :
                                     notif.type === 'warning' ? 'warning.main' :
                                     notif.type === 'error' ? 'error.main' : 'info.main'
                          }}>
                            {notif.type === 'success' ? <CheckCircle /> :
                             notif.type === 'warning' ? <Warning /> :
                             notif.type === 'error' ? <Error /> : <Info />}
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={notif.titre}
                          secondary={
                            <>
                              <Typography variant="body2" color="text.secondary">
                                {notif.message}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {new Date(notif.date_creation).toLocaleDateString('fr-FR')}
                              </Typography>
                            </>
                          }
                        />
                        {!notif.lu && (
                          <Chip label="Non lu" size="small" color="primary" />
                        )}
                      </ListItem>
                      {index < notifications.length - 1 && <Divider variant="inset" component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  Aucune notification récente
                </Typography>
              )}
              
              <Button fullWidth variant="outlined" sx={{ mt: 2 }}>
                Voir toutes les notifications
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Ratios financiers */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ratios financiers EBNL
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Ratio d'autonomie financière
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={kpiData?.ratio_autonomie || 0}
                          sx={{ height: 10, borderRadius: 5 }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {kpiData?.ratio_autonomie || 0}%
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Ratio de liquidité
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(kpiData?.ratio_liquidite || 0, 100)}
                          sx={{ height: 10, borderRadius: 5 }}
                          color="secondary"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {kpiData?.ratio_liquidite || 0}%
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Activité comptable
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={75} // Valeur fixe pour la démo
                          sx={{ height: 10, borderRadius: 5 }}
                          color="info"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        75%
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;