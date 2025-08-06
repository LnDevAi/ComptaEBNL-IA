import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Avatar,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Divider,
  Alert
} from '@mui/material';
import {
  School,
  EmojiEvents,
  TrendingUp,
  AccessTime,
  PlayArrow,
  MenuBook,
  Quiz,
  Star,
  CheckCircle,
  Bookmark,
  ArrowForward,
  CalendarToday,
  Person,
  Speed
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { apiClient } from '../../context/AuthContext';

// Types
interface FormationInscrite {
  id: number;
  titre: string;
  categorie: {
    nom: string;
    couleur: string;
  };
  inscription: {
    pourcentage_completion: number;
    temps_passe: number;
    derniere_activite: string;
  };
  prochaine_lecon?: {
    id: number;
    titre: string;
    type_contenu: string;
  };
}

interface Statistiques {
  nb_formations_inscrites: number;
  nb_formations_terminees: number;
  temps_total_apprentissage: number;
  nb_certificats: number;
  niveau_global: string;
  points_total: number;
}

interface ActiviteRecente {
  id: number;
  type: 'lecon_terminee' | 'quiz_reussi' | 'formation_commencee' | 'certificat_obtenu';
  titre: string;
  formation: string;
  date: string;
  note?: number;
}

const LearningDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [formations, setFormations] = useState<FormationInscrite[]>([]);
  const [stats, setStats] = useState<Statistiques | null>(null);
  const [activites, setActivites] = useState<ActiviteRecente[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [formationsRes, activitesRes] = await Promise.all([
        apiClient.get('/api/v1/mes-formations'),
        apiClient.get('/api/v1/activites-recentes')
      ]);

      setFormations(formationsRes.data.formations || []);
      setStats(formationsRes.data.statistiques || null);
      setActivites(activitesRes.data.activites || []);
    } catch (err) {
      setError('Erreur lors du chargement du tableau de bord');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const continuerFormation = (formation: FormationInscrite) => {
    if (formation.prochaine_lecon) {
      navigate(`/learning/lecons/${formation.prochaine_lecon.id}`);
    } else {
      navigate(`/learning/formations/${formation.id}`);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎥';
      case 'texte': return '📖';
      case 'pdf': return '📄';
      case 'quiz': return '❓';
      default: return '📚';
    }
  };

  const getActiviteIcon = (type: string) => {
    switch (type) {
      case 'lecon_terminee': return <CheckCircle color="success" />;
      case 'quiz_reussi': return <Quiz color="primary" />;
      case 'formation_commencee': return <School color="info" />;
      case 'certificat_obtenu': return <EmojiEvents color="warning" />;
      default: return <MenuBook />;
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
        <Typography sx={{ mt: 2 }}>Chargement de votre tableau de bord...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* En-tête */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          📚 Mon Apprentissage
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Tableau de bord de vos formations EBNL
        </Typography>
      </Box>

      {/* Statistiques principales */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <School sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                <Typography variant="h4" color="primary">
                  {stats.nb_formations_inscrites}
                </Typography>
                <Typography variant="body2">Formations inscrites</Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <CheckCircle sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                <Typography variant="h4" color="success.main">
                  {stats.nb_formations_terminees}
                </Typography>
                <Typography variant="body2">Formations terminées</Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <AccessTime sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                <Typography variant="h4" color="info.main">
                  {formatDuration(stats.temps_total_apprentissage)}
                </Typography>
                <Typography variant="body2">Temps d'apprentissage</Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <EmojiEvents sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                <Typography variant="h4" color="warning.main">
                  {stats.nb_certificats}
                </Typography>
                <Typography variant="body2">Certificats obtenus</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Grid container spacing={4}>
        {/* Formations en cours */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">📖 Mes formations en cours</Typography>
              <Button 
                endIcon={<ArrowForward />}
                onClick={() => navigate('/learning/formations')}
              >
                Voir toutes
              </Button>
            </Box>

            {formations.length === 0 ? (
              <Alert severity="info">
                Vous n'êtes inscrit à aucune formation.
                <Button 
                  variant="text" 
                  onClick={() => navigate('/learning/formations')}
                  sx={{ ml: 1 }}
                >
                  Découvrir les formations
                </Button>
              </Alert>
            ) : (
              <List>
                {formations.slice(0, 5).map((formation, index) => (
                  <React.Fragment key={formation.id}>
                    <ListItem 
                      sx={{ 
                        px: 0,
                        '&:hover': { bgcolor: 'action.hover', cursor: 'pointer' }
                      }}
                      onClick={() => continuerFormation(formation)}
                    >
                      <ListItemIcon>
                        <Avatar 
                          sx={{ 
                            bgcolor: formation.categorie.couleur,
                            width: 48,
                            height: 48
                          }}
                        >
                          <School />
                        </Avatar>
                      </ListItemIcon>
                      
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="h6">{formation.titre}</Typography>
                            <Chip
                              label={formation.categorie.nom}
                              size="small"
                              sx={{
                                backgroundColor: formation.categorie.couleur + '20',
                                color: formation.categorie.couleur,
                              }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box sx={{ mt: 1 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                              <Typography variant="body2">
                                Progression: {Math.round(formation.inscription.pourcentage_completion)}%
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {formatDuration(formation.inscription.temps_passe)}
                              </Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={formation.inscription.pourcentage_completion}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                            {formation.prochaine_lecon && (
                              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                Prochaine leçon: {getTypeIcon(formation.prochaine_lecon.type_contenu)} {formation.prochaine_lecon.titre}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      
                      <IconButton color="primary">
                        <PlayArrow />
                      </IconButton>
                    </ListItem>
                    {index < formations.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Paper>

          {/* Actions rapides */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🚀 Actions rapides
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<School />}
                  onClick={() => navigate('/learning/formations')}
                  sx={{ py: 2 }}
                >
                  Découvrir les formations
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<EmojiEvents />}
                  onClick={() => navigate('/learning/certificats')}
                  sx={{ py: 2 }}
                >
                  Mes certificats
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Niveau et progression */}
          {stats && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                🏆 Votre niveau
              </Typography>
              <Box sx={{ textAlign: 'center', mb: 2 }}>
                <Avatar 
                  sx={{ 
                    width: 80, 
                    height: 80, 
                    bgcolor: 'primary.main', 
                    mx: 'auto', 
                    mb: 1,
                    fontSize: 24
                  }}
                >
                  {stats.niveau_global.charAt(0)}
                </Avatar>
                <Typography variant="h5">{stats.niveau_global}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {stats.points_total} points
                </Typography>
              </Box>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" gutterBottom>
                  Taux de réussite: {stats.nb_formations_inscrites > 0 ? 
                    Math.round((stats.nb_formations_terminees / stats.nb_formations_inscrites) * 100) : 0}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={stats.nb_formations_inscrites > 0 ? 
                    (stats.nb_formations_terminees / stats.nb_formations_inscrites) * 100 : 0}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
            </Paper>
          )}

          {/* Activités récentes */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              📈 Activités récentes
            </Typography>
            
            {activites.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Aucune activité récente
              </Typography>
            ) : (
              <List dense>
                {activites.slice(0, 8).map((activite) => (
                  <ListItem key={activite.id} sx={{ px: 0 }}>
                    <ListItemIcon>
                      {getActiviteIcon(activite.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={activite.titre}
                      secondary={
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            {activite.formation}
                          </Typography>
                          <br />
                          <Typography variant="caption" color="text.secondary">
                            {format(new Date(activite.date), 'dd MMM à HH:mm', { locale: fr })}
                          </Typography>
                          {activite.note && (
                            <>
                              <br />
                              <Typography variant="caption" color="primary">
                                Note: {(activite.note * 20).toFixed(1)}/20
                              </Typography>
                            </>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default LearningDashboard;