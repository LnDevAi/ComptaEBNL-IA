import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Rating,
  LinearProgress,
  IconButton,
  Tooltip,
  Paper,
  Divider,
  Avatar,
  Stack
} from '@mui/material';
import {
  Search,
  FilterList,
  School,
  AccessTime,
  Person,
  Star,
  PlayArrow,
  Lock,
  CheckCircle,
  MenuBook,
  Quiz,
  EmojiEvents,
  Bookmark,
  BookmarkBorder
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../../context/AuthContext';

// Types
interface Category {
  id: number;
  nom: string;
  description: string;
  icone: string;
  couleur: string;
  nb_formations: number;
}

interface Formation {
  id: number;
  titre: string;
  description: string;
  objectifs: string[];
  categorie: Category;
  niveau: 'debutant' | 'intermediaire' | 'avance' | 'expert';
  duree_estimee: number;
  prix: number;
  image_couverture?: string;
  plan_requis: 'gratuit' | 'professionnel' | 'enterprise';
  note_moyenne: number;
  nb_evaluations: number;
  nb_inscrits: number;
  nb_modules: number;
  accessible: boolean;
  inscription?: {
    id: number;
    statut: string;
    pourcentage_completion: number;
  };
}

const FormationCatalog: React.FC = () => {
  const navigate = useNavigate();
  const [formations, setFormations] = useState<Formation[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filtres
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | ''>('');
  const [selectedLevel, setSelectedLevel] = useState<string | ''>('');
  const [selectedPlan, setSelectedPlan] = useState<string | ''>('');
  const [showFilters, setShowFilters] = useState(false);
  const [savedFormations, setSavedFormations] = useState<number[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [formationsRes, categoriesRes] = await Promise.all([
        apiClient.get('/api/v1/formations'),
        apiClient.get('/api/v1/categories')
      ]);

      setFormations(formationsRes.data.formations || []);
      setCategories(categoriesRes.data.categories || []);
    } catch (err) {
      setError('Erreur lors du chargement des formations');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredFormations = formations.filter(formation => {
    const matchesSearch = formation.titre.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         formation.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || formation.categorie.id === selectedCategory;
    const matchesLevel = !selectedLevel || formation.niveau === selectedLevel;
    const matchesPlan = !selectedPlan || formation.plan_requis === selectedPlan;

    return matchesSearch && matchesCategory && matchesLevel && matchesPlan;
  });

  const handleFormationClick = (formation: Formation) => {
    navigate(`/learning/formations/${formation.id}`);
  };

  const toggleSaveFormation = (formationId: number) => {
    setSavedFormations(prev => 
      prev.includes(formationId) 
        ? prev.filter(id => id !== formationId)
        : [...prev, formationId]
    );
  };

  const getNiveauColor = (niveau: string) => {
    switch (niveau) {
      case 'debutant': return '#4CAF50';
      case 'intermediaire': return '#FF9800';
      case 'avance': return '#F44336';
      case 'expert': return '#9C27B0';
      default: return '#757575';
    }
  };

  const getPlanIcon = (plan: string) => {
    switch (plan) {
      case 'gratuit': return '🆓';
      case 'professionnel': return '💼';
      case 'enterprise': return '🏢';
      default: return '❓';
    }
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h${mins > 0 ? ` ${mins}min` : ''}` : `${mins}min`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Chargement des formations...</Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography color="error">{error}</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* En-tête */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          📚 Formations EBNL
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Spécialisées dans la comptabilité des Entités à But Non Lucratif de l'espace OHADA
        </Typography>
      </Box>

      {/* Statistiques rapides */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="primary">{formations.length}</Typography>
            <Typography variant="body2">Formations</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="secondary">{categories.length}</Typography>
            <Typography variant="body2">Catégories</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="success.main">
              {formations.filter(f => f.plan_requis === 'gratuit').length}
            </Typography>
            <Typography variant="body2">Gratuites</Typography>
          </Paper>
        </Grid>
        <Grid item xs={6} md={3}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="warning.main">
              {formations.reduce((total, f) => total + f.nb_inscrits, 0)}
            </Typography>
            <Typography variant="body2">Inscrits</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Catégories en chips */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>Catégories</Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Chip
            label="Toutes"
            onClick={() => setSelectedCategory('')}
            color={selectedCategory === '' ? 'primary' : 'default'}
            variant={selectedCategory === '' ? 'filled' : 'outlined'}
          />
          {categories.map((category) => (
            <Chip
              key={category.id}
              label={`${category.nom} (${category.nb_formations})`}
              onClick={() => setSelectedCategory(category.id)}
              color={selectedCategory === category.id ? 'primary' : 'default'}
              variant={selectedCategory === category.id ? 'filled' : 'outlined'}
              sx={{ 
                backgroundColor: selectedCategory === category.id ? category.couleur : undefined,
                '&:hover': { backgroundColor: category.couleur + '20' }
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* Barre de recherche et filtres */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Rechercher une formation..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Niveau</InputLabel>
                <Select
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  label="Niveau"
                >
                  <MenuItem value="">Tous</MenuItem>
                  <MenuItem value="debutant">Débutant</MenuItem>
                  <MenuItem value="intermediaire">Intermédiaire</MenuItem>
                  <MenuItem value="avance">Avancé</MenuItem>
                  <MenuItem value="expert">Expert</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Plan</InputLabel>
                <Select
                  value={selectedPlan}
                  onChange={(e) => setSelectedPlan(e.target.value)}
                  label="Plan"
                >
                  <MenuItem value="">Tous</MenuItem>
                  <MenuItem value="gratuit">🆓 Gratuit</MenuItem>
                  <MenuItem value="professionnel">💼 Pro</MenuItem>
                  <MenuItem value="enterprise">🏢 Enterprise</MenuItem>
                </Select>
              </FormControl>

              <Button
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => setShowFilters(!showFilters)}
              >
                Filtres
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Résultats */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6">
          {filteredFormations.length} formation{filteredFormations.length > 1 ? 's' : ''} trouvée{filteredFormations.length > 1 ? 's' : ''}
        </Typography>
      </Box>

      {/* Grille des formations */}
      <Grid container spacing={3}>
        {filteredFormations.map((formation) => (
          <Grid item xs={12} sm={6} md={4} key={formation.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: (theme) => theme.shadows[8]
                }
              }}
              onClick={() => handleFormationClick(formation)}
            >
              {/* Image de couverture */}
              <CardMedia
                component="div"
                sx={{
                  height: 160,
                  bgcolor: formation.categorie.couleur + '20',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  position: 'relative'
                }}
              >
                <School sx={{ fontSize: 60, color: formation.categorie.couleur }} />
                
                {/* Badge plan */}
                <Chip
                  label={`${getPlanIcon(formation.plan_requis)} ${formation.plan_requis}`}
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 8,
                    left: 8,
                    textTransform: 'capitalize'
                  }}
                />

                {/* Bouton sauvegarder */}
                <IconButton
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    bgcolor: 'rgba(255,255,255,0.9)'
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleSaveFormation(formation.id);
                  }}
                >
                  {savedFormations.includes(formation.id) ? 
                    <Bookmark color="primary" /> : 
                    <BookmarkBorder />
                  }
                </IconButton>

                {/* Badge accessible */}
                {!formation.accessible && (
                  <Box
                    sx={{
                      position: 'absolute',
                      bottom: 8,
                      right: 8,
                      bgcolor: 'rgba(0,0,0,0.7)',
                      color: 'white',
                      px: 1,
                      py: 0.5,
                      borderRadius: 1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5
                    }}
                  >
                    <Lock fontSize="small" />
                    <Typography variant="caption">Premium</Typography>
                  </Box>
                )}
              </CardMedia>

              <CardContent sx={{ flexGrow: 1, pb: 1 }}>
                {/* Titre et catégorie */}
                <Typography variant="h6" component="h3" gutterBottom>
                  {formation.titre}
                </Typography>
                
                <Chip
                  label={formation.categorie.nom}
                  size="small"
                  sx={{ 
                    mb: 1,
                    backgroundColor: formation.categorie.couleur + '20',
                    color: formation.categorie.couleur,
                    border: `1px solid ${formation.categorie.couleur}40`
                  }}
                />

                {/* Description */}
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  sx={{ 
                    mb: 2,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                  }}
                >
                  {formation.description}
                </Typography>

                {/* Métadonnées */}
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  <Chip
                    label={formation.niveau}
                    size="small"
                    sx={{ 
                      backgroundColor: getNiveauColor(formation.niveau) + '20',
                      color: getNiveauColor(formation.niveau),
                      textTransform: 'capitalize'
                    }}
                  />
                  <Chip
                    icon={<AccessTime />}
                    label={formatDuration(formation.duree_estimee)}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    icon={<MenuBook />}
                    label={`${formation.nb_modules} modules`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                {/* Progression si inscrit */}
                {formation.inscription && (
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption">Progression</Typography>
                      <Typography variant="caption">
                        {Math.round(formation.inscription.pourcentage_completion)}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={formation.inscription.pourcentage_completion}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                )}

                {/* Note et inscrits */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Rating 
                      value={formation.note_moyenne} 
                      size="small" 
                      readOnly 
                      precision={0.1}
                    />
                    <Typography variant="caption">
                      ({formation.nb_evaluations})
                    </Typography>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {formation.nb_inscrits} inscrits
                  </Typography>
                </Box>
              </CardContent>

              {/* Actions */}
              <Box sx={{ p: 2, pt: 0 }}>
                <Button
                  fullWidth
                  variant={formation.inscription ? "outlined" : "contained"}
                  startIcon={
                    formation.inscription ? 
                      <PlayArrow /> : 
                      formation.accessible ? <School /> : <Lock />
                  }
                  disabled={!formation.accessible && !formation.inscription}
                >
                  {formation.inscription ? 
                    'Continuer' : 
                    formation.accessible ? 
                      'Commencer' : 
                      `Nécessite ${formation.plan_requis}`
                  }
                </Button>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Message si aucun résultat */}
      {filteredFormations.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center', mt: 4 }}>
          <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Aucune formation trouvée
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Essayez de modifier vos critères de recherche
          </Typography>
          <Button 
            variant="outlined" 
            onClick={() => {
              setSearchTerm('');
              setSelectedCategory('');
              setSelectedLevel('');
              setSelectedPlan('');
            }}
          >
            Réinitialiser les filtres
          </Button>
        </Paper>
      )}
    </Container>
  );
};

export default FormationCatalog;