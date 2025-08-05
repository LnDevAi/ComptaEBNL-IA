import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Pagination,
  Button,
  TreeView,
  TreeItem,
  Collapse,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search,
  AccountBalanceWallet,
  ExpandMore,
  ChevronRight,
  FilterList,
  Download,
  Visibility,
  Info,
} from '@mui/icons-material';
import { apiClient } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';

// Types
interface CompteComptable {
  id: number;
  numero_compte: string;
  libelle_compte: string;
  classe: string;
  niveau: number;
  actif: boolean;
  type_compte?: string;
  parent_compte?: string;
}

interface StatsComptables {
  total_comptes: number;
  repartition_classes: { [key: string]: number };
  comptes_utilises: number;
  comptes_non_utilises: number;
}

// Configuration des classes SYCEBNL
const CLASSES_SYCEBNL = {
  '1': { nom: 'Capitaux propres et dotation', couleur: '#1976d2' },
  '2': { nom: 'Immobilisations', couleur: '#388e3c' },
  '3': { nom: 'Stocks et en-cours', couleur: '#f57c00' },
  '4': { nom: 'Comptes de tiers', couleur: '#7b1fa2' },
  '5': { nom: 'Comptes financiers', couleur: '#d32f2f' },
  '6': { nom: 'Charges', couleur: '#795548' },
  '7': { nom: 'Produits', couleur: '#0288d1' },
  '8': { nom: 'Comptes spéciaux', couleur: '#5d4037' },
  '9': { nom: 'Contributions volontaires en nature', couleur: '#e91e63' },
};

const PlanComptable: React.FC = () => {
  const { showError, showSuccess } = useNotification();
  
  const [comptes, setComptes] = useState<CompteComptable[]>([]);
  const [stats, setStats] = useState<StatsComptables | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClasse, setSelectedClasse] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedCompte, setSelectedCompte] = useState<CompteComptable | null>(null);

  // Charger les données du plan comptable
  useEffect(() => {
    loadPlanComptable();
    loadStats();
  }, [page, searchTerm, selectedClasse]);

  const loadPlanComptable = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '50',
        ...(searchTerm && { search: searchTerm }),
        ...(selectedClasse && { classe: selectedClasse }),
      });

      const response = await apiClient.get(`/api/v1/plan-comptable?${params}`);
      
      if (response.data.success) {
        setComptes(response.data.data.comptes);
        setTotalPages(response.data.data.pagination?.pages || 1);
      }
    } catch (error) {
      console.error('Erreur lors du chargement du plan comptable:', error);
      showError('Erreur lors du chargement du plan comptable');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiClient.get('/api/v1/plan-comptable/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    setPage(1); // Reset to first page when searching
  };

  const handleClasseChange = (event: any) => {
    setSelectedClasse(event.target.value);
    setPage(1);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, newPage: number) => {
    setPage(newPage);
  };

  const handleExportPlan = async () => {
    try {
      const response = await apiClient.get('/api/v1/export/plan-comptable?format=csv', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'plan_comptable_sycebnl.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      showSuccess('Plan comptable exporté avec succès');
    } catch (error) {
      showError('Erreur lors de l\'export du plan comptable');
    }
  };

  const getClasseColor = (classe: string): string => {
    return CLASSES_SYCEBNL[classe as keyof typeof CLASSES_SYCEBNL]?.couleur || '#757575';
  };

  const getClasseNom = (classe: string): string => {
    return CLASSES_SYCEBNL[classe as keyof typeof CLASSES_SYCEBNL]?.nom || `Classe ${classe}`;
  };

  return (
    <Box>
      {/* En-tête */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Plan Comptable SYCEBNL
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Système Comptable des Entités à But Non Lucratif
        </Typography>
      </Box>

      {/* Statistiques rapides */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary.main">
                  {stats.total_comptes}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Comptes SYCEBNL
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {stats.comptes_utilises}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Comptes utilisés
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="warning.main">
                  {Object.keys(stats.repartition_classes).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Classes actives
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {((stats.comptes_utilises / stats.total_comptes) * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Taux d'utilisation
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Grid container spacing={3}>
        {/* Filtres et actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Rechercher un compte"
                    value={searchTerm}
                    onChange={handleSearchChange}
                    placeholder="Numéro, libellé..."
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Search />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth>
                    <InputLabel>Classe comptable</InputLabel>
                    <Select
                      value={selectedClasse}
                      onChange={handleClasseChange}
                      label="Classe comptable"
                    >
                      <MenuItem value="">Toutes les classes</MenuItem>
                      {Object.entries(CLASSES_SYCEBNL).map(([numero, info]) => (
                        <MenuItem key={numero} value={numero}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Box
                              sx={{
                                width: 12,
                                height: 12,
                                borderRadius: '50%',
                                backgroundColor: info.couleur,
                                mr: 1,
                              }}
                            />
                            Classe {numero} - {info.nom}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={3}>
                  <Button
                    variant="outlined"
                    startIcon={<Download />}
                    onClick={handleExportPlan}
                    fullWidth
                  >
                    Exporter CSV
                  </Button>
                </Grid>
                
                <Grid item xs={12} md={2}>
                  <Button
                    variant="contained"
                    startIcon={<FilterList />}
                    fullWidth
                  >
                    Filtres avancés
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Classes comptables - Vue rapide */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Classes SYCEBNL
              </Typography>
              
              <List dense>
                {Object.entries(CLASSES_SYCEBNL).map(([numero, info]) => (
                  <ListItem
                    key={numero}
                    button
                    onClick={() => setSelectedClasse(numero)}
                    selected={selectedClasse === numero}
                    sx={{ borderRadius: 1, mb: 0.5 }}
                  >
                    <Box
                      sx={{
                        width: 16,
                        height: 16,
                        borderRadius: '50%',
                        backgroundColor: info.couleur,
                        mr: 2,
                      }}
                    />
                    <ListItemText
                      primary={`Classe ${numero}`}
                      secondary={info.nom}
                      primaryTypographyProps={{ fontWeight: 500 }}
                    />
                    <Chip
                      label={stats?.repartition_classes[numero] || 0}
                      size="small"
                      sx={{ bgcolor: info.couleur, color: 'white' }}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Table des comptes */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Comptes comptables
                  {selectedClasse && ` - Classe ${selectedClasse}`}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {comptes.length} compte(s)
                </Typography>
              </Box>

              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Numéro</strong></TableCell>
                      <TableCell><strong>Libellé</strong></TableCell>
                      <TableCell><strong>Classe</strong></TableCell>
                      <TableCell><strong>Niveau</strong></TableCell>
                      <TableCell><strong>Statut</strong></TableCell>
                      <TableCell><strong>Actions</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4 }}>
                          Chargement des comptes...
                        </TableCell>
                      </TableRow>
                    ) : comptes.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4 }}>
                          Aucun compte trouvé
                        </TableCell>
                      </TableRow>
                    ) : (
                      comptes.map((compte) => (
                        <TableRow
                          key={compte.id}
                          hover
                          onClick={() => setSelectedCompte(compte)}
                          sx={{ cursor: 'pointer' }}
                        >
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {compte.numero_compte}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {compte.libelle_compte}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={`Classe ${compte.classe}`}
                              size="small"
                              sx={{
                                bgcolor: getClasseColor(compte.classe),
                                color: 'white',
                              }}
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={`Niveau ${compte.niveau}`}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={compte.actif ? 'Actif' : 'Inactif'}
                              size="small"
                              color={compte.actif ? 'success' : 'default'}
                            />
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Voir les détails">
                              <IconButton size="small">
                                <Visibility fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Informations">
                              <IconButton size="small">
                                <Info fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Pagination */}
              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={handlePageChange}
                    color="primary"
                    showFirstButton
                    showLastButton
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Détails du compte sélectionné */}
        {selectedCompte && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Détails du compte {selectedCompte.numero_compte}
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" color="text.secondary">
                      Libellé complet
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {selectedCompte.libelle_compte}
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Classe comptable
                    </Typography>
                    <Chip
                      label={getClasseNom(selectedCompte.classe)}
                      sx={{
                        bgcolor: getClasseColor(selectedCompte.classe),
                        color: 'white',
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <Typography variant="body2" color="text.secondary">
                      Niveau hiérarchique
                    </Typography>
                    <Typography variant="body1">
                      Niveau {selectedCompte.niveau}
                    </Typography>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<AccountBalanceWallet />}
                    sx={{ mr: 1 }}
                  >
                    Voir les écritures
                  </Button>
                  <Button variant="outlined">
                    Modifier le compte
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default PlanComptable;