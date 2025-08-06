import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Divider,
  Rating,
  Avatar,
  IconButton,
  Tooltip,
  Breadcrumbs,
  Link,
  Alert
} from '@mui/material';
import {
  ExpandMore,
  PlayArrow,
  Lock,
  CheckCircle,
  AccessTime,
  Person,
  School,
  MenuBook,
  Quiz,
  EmojiEvents,
  Star,
  ArrowBack,
  Bookmark,
  BookmarkBorder,
  Share,
  Download,
  Verified
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../../context/AuthContext';

// Types
interface Formation {
  id: number;
  titre: string;
  description: string;
  objectifs: string[];
  categorie: {
    nom: string;
    couleur: string;
  };
  niveau: string;
  duree_estimee: number;
  prix: number;
  plan_requis: string;
  note_moyenne: number;
  nb_evaluations: number;
  nb_inscrits: number;
  modules: Module[];
  inscription?: {
    id: number;
    statut: string;
    pourcentage_completion: number;
    temps_passe: number;
  };
}

interface Module {
  id: number;
  titre: string;
  description: string;
  ordre: number;
  duree_estimee: number;
  lecons: Lecon[];
}

interface Lecon {
  id: number;
  titre: string;
  type_contenu: string;
  ordre: number;
  duree_estimee: number;
  gratuit: boolean;
  a_quiz: boolean;
}

const FormationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [formation, setFormation] = useState<Formation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [inscriptionDialog, setInscriptionDialog] = useState(false);
  const [inscriptionLoading, setInscriptionLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (id) {
      loadFormation(parseInt(id));
    }
  }, [id]);

  const loadFormation = async (formationId: number) => {
    try {
      const response = await apiClient.get(`/api/v1/formations/${formationId}`);
      setFormation(response.data.formation);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du chargement de la formation');
    } finally {
      setLoading(false);
    }
  };

  const handleInscription = async () => {
    if (!formation) return;
    
    setInscriptionLoading(true);
    try {
      await apiClient.post(`/api/v1/formations/${formation.id}/inscrire`);
      setInscriptionDialog(false);
      // Recharger la formation pour voir l'inscription
      await loadFormation(formation.id);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors de l\'inscription');
    } finally {
      setInscriptionLoading(false);
    }
  };

  const startLesson = (leconId: number) => {
    navigate(`/learning/lecons/${leconId}`);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎥';
      case 'texte': return '📖';
      case 'pdf': return '📄';
      case 'quiz': return '❓';
      case 'exercice': return '✏️';
      default: return '📚';
    }
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

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h${mins > 0 ? ` ${mins}min` : ''}` : `${mins}min`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Chargement de la formation...</Typography>
      </Container>
    );
  }

  if (error || !formation) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Formation non trouvée'}</Alert>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate('/learning/formations')}
          sx={{ mt: 2 }}
        >
          Retour aux formations
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link 
          color="inherit" 
          onClick={() => navigate('/learning/formations')}
          sx={{ cursor: 'pointer' }}
        >
          Formations
        </Link>
        <Typography color="text.primary">{formation.titre}</Typography>
      </Breadcrumbs>

      <Grid container spacing={4}>
        {/* Contenu principal */}
        <Grid item xs={12} md={8}>
          {/* En-tête de la formation */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ flex: 1 }}>
                <Chip
                  label={formation.categorie.nom}
                  sx={{ 
                    mb: 2,
                    backgroundColor: formation.categorie.couleur + '20',
                    color: formation.categorie.couleur,
                  }}
                />
                <Typography variant="h4" component="h1" gutterBottom>
                  {formation.titre}
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
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
                    label={`${formation.modules.length} modules`}
                    size="small"
                    variant="outlined"
                  />
                  <Chip
                    icon={<Person />}
                    label={`${formation.nb_inscrits} inscrits`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                {/* Note */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Rating value={formation.note_moyenne} size="small" readOnly precision={0.1} />
                  <Typography variant="body2">
                    {formation.note_moyenne.toFixed(1)} ({formation.nb_evaluations} avis)
                  </Typography>
                </Box>
              </Box>

              {/* Actions */}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, ml: 2 }}>
                <IconButton onClick={() => setSaved(!saved)}>
                  {saved ? <Bookmark color="primary" /> : <BookmarkBorder />}
                </IconButton>
                <IconButton>
                  <Share />
                </IconButton>
              </Box>
            </Box>

            {/* Progression si inscrit */}
            {formation.inscription && (
              <Box sx={{ mt: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="h6">Votre progression</Typography>
                  <Typography variant="h6" color="primary">
                    {Math.round(formation.inscription.pourcentage_completion)}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={formation.inscription.pourcentage_completion}
                  sx={{ height: 8, borderRadius: 4, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Temps passé: {Math.round(formation.inscription.temps_passe)} minutes
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Objectifs de la formation */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              🎯 Objectifs pédagogiques
            </Typography>
            <List>
              {formation.objectifs.map((objectif, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemIcon>
                    <CheckCircle color="success" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText primary={objectif} />
                </ListItem>
              ))}
            </List>
          </Paper>

          {/* Modules de la formation */}
          <Typography variant="h5" gutterBottom>
            📚 Contenu de la formation
          </Typography>
          
          {formation.modules.map((module, moduleIndex) => (
            <Accordion key={module.id} defaultExpanded={moduleIndex === 0}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6">
                      Module {module.ordre}: {module.titre}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {module.description}
                    </Typography>
                  </Box>
                  <Chip
                    icon={<AccessTime />}
                    label={formatDuration(module.duree_estimee)}
                    size="small"
                    variant="outlined"
                    sx={{ ml: 2 }}
                  />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {module.lecons.map((lecon) => (
                    <ListItem 
                      key={lecon.id}
                      sx={{ 
                        border: '1px solid',
                        borderColor: 'divider',
                        borderRadius: 1,
                        mb: 1,
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => formation.inscription && startLesson(lecon.id)}
                    >
                      <ListItemIcon>
                        <Typography sx={{ fontSize: 20 }}>
                          {getTypeIcon(lecon.type_contenu)}
                        </Typography>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography>{lecon.titre}</Typography>
                            {lecon.gratuit && (
                              <Chip label="Gratuit" size="small" color="success" />
                            )}
                            {lecon.a_quiz && (
                              <Quiz fontSize="small" color="primary" />
                            )}
                          </Box>
                        }
                        secondary={`${formatDuration(lecon.duree_estimee)} • ${lecon.type_contenu}`}
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {formation.inscription ? (
                          <PlayArrow color="primary" />
                        ) : lecon.gratuit ? (
                          <PlayArrow />
                        ) : (
                          <Lock color="disabled" />
                        )}
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Card d'inscription */}
          <Card sx={{ mb: 3, position: 'sticky', top: 24 }}>
            <CardContent>
              {formation.inscription ? (
                <>
                  <Typography variant="h6" gutterBottom color="success.main">
                    ✅ Vous êtes inscrit
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Statut: {formation.inscription.statut}
                  </Typography>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={() => {
                      // Aller à la première leçon disponible
                      const firstModule = formation.modules[0];
                      if (firstModule?.lecons[0]) {
                        startLesson(firstModule.lecons[0].id);
                      }
                    }}
                  >
                    Continuer la formation
                  </Button>
                </>
              ) : (
                <>
                  <Typography variant="h6" gutterBottom>
                    Plan requis: {formation.plan_requis}
                  </Typography>
                  <Typography variant="h4" gutterBottom>
                    {formation.prix === 0 ? 'Gratuit' : `${formation.prix}€`}
                  </Typography>
                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    startIcon={<School />}
                    onClick={() => setInscriptionDialog(true)}
                  >
                    S'inscrire maintenant
                  </Button>
                </>
              )}

              <Divider sx={{ my: 2 }} />

              {/* Informations complémentaires */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Durée totale</Typography>
                <Typography variant="body2">{formatDuration(formation.duree_estimee)}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Modules</Typography>
                <Typography variant="body2">{formation.modules.length}</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Leçons</Typography>
                <Typography variant="body2">
                  {formation.modules.reduce((total, module) => total + module.lecons.length, 0)}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Quiz</Typography>
                <Typography variant="body2">
                  {formation.modules.reduce((total, module) => 
                    total + module.lecons.filter(lecon => lecon.a_quiz).length, 0
                  )}
                </Typography>
              </Box>
            </CardContent>
          </Card>

          {/* Certificat */}
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <EmojiEvents color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Certificat inclus</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Obtenez un certificat officiel reconnu dans l'espace OHADA après avoir terminé cette formation.
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Verified fontSize="small" color="primary" />
                <Typography variant="caption">
                  Certificat vérifiable en ligne
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Dialog d'inscription */}
      <Dialog open={inscriptionDialog} onClose={() => setInscriptionDialog(false)}>
        <DialogTitle>Confirmer l'inscription</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            Vous allez vous inscrire à la formation "{formation.titre}".
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Cette formation nécessite un abonnement {formation.plan_requis}.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInscriptionDialog(false)}>
            Annuler
          </Button>
          <Button 
            onClick={handleInscription}
            variant="contained"
            disabled={inscriptionLoading}
          >
            {inscriptionLoading ? 'Inscription...' : 'Confirmer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FormationDetail;