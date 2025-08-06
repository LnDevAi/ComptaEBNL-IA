import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  LinearProgress,
  IconButton,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Drawer,
  AppBar,
  Toolbar,
  Alert,
  CircularProgress,
  Breadcrumbs,
  Link
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  SkipNext,
  SkipPrevious,
  MenuBook,
  Quiz,
  CheckCircle,
  Close,
  Menu,
  AccessTime,
  School,
  ArrowBack,
  Fullscreen,
  FullscreenExit,
  Speed,
  VolumeUp,
  VolumeOff,
  Bookmark,
  BookmarkBorder,
  Note
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '../../context/AuthContext';

// Types
interface Lecon {
  id: number;
  titre: string;
  description: string;
  contenu: string;
  type_contenu: 'video' | 'texte' | 'pdf' | 'quiz';
  duree_estimee: number;
  ordre: number;
  gratuit: boolean;
  url_video?: string;
  fichier_pdf?: string;
  module: {
    id: number;
    titre: string;
    formation: {
      id: number;
      titre: string;
    };
  };
  progression?: {
    temps_passe: number;
    pourcentage_completion: number;
    statut: string;
  };
}

interface Navigation {
  lecon_precedente?: { id: number; titre: string };
  lecon_suivante?: { id: number; titre: string };
}

const LessonPlayer: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [lecon, setLecon] = useState<Lecon | null>(null);
  const [navigation, setNavigation] = useState<Navigation>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [progression, setProgression] = useState(0);
  const [tempsDebut, setTempsDebut] = useState<Date | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [showNotes, setShowNotes] = useState(false);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    if (id) {
      loadLecon(parseInt(id));
    }
  }, [id]);

  useEffect(() => {
    // Démarrer automatiquement si pas encore commencé
    if (lecon && !lecon.progression && !tempsDebut) {
      commencerLecon();
    }
  }, [lecon]);

  const loadLecon = async (leconId: number) => {
    try {
      const response = await apiClient.get(`/api/v1/lecons/${leconId}`);
      setLecon(response.data.lecon);
      setNavigation(response.data.navigation || {});
      
      if (response.data.lecon.progression) {
        setProgression(response.data.lecon.progression.pourcentage_completion);
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Erreur lors du chargement de la leçon');
    } finally {
      setLoading(false);
    }
  };

  const commencerLecon = async () => {
    if (!lecon) return;
    
    try {
      await apiClient.post(`/api/v1/lecons/${lecon.id}/commencer`);
      setTempsDebut(new Date());
      setIsPlaying(true);
    } catch (err) {
      console.error('Erreur lors du démarrage:', err);
    }
  };

  const terminerLecon = async () => {
    if (!lecon || !tempsDebut) return;
    
    try {
      const tempsPasse = Math.floor((Date.now() - tempsDebut.getTime()) / 1000 / 60);
      await apiClient.post(`/api/v1/lecons/${lecon.id}/terminer`, {
        temps_passe: tempsPasse
      });
      setProgression(100);
      setIsPlaying(false);
    } catch (err) {
      console.error('Erreur lors de la finalisation:', err);
    }
  };

  const naviguerVers = (leconId: number) => {
    navigate(`/learning/lecons/${leconId}`);
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

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h${mins > 0 ? ` ${mins}min` : ''}` : `${mins}min`;
  };

  const renderContenu = () => {
    if (!lecon) return null;

    switch (lecon.type_contenu) {
      case 'video':
        return (
          <Box sx={{ width: '100%', bgcolor: 'black', borderRadius: 1 }}>
            {lecon.url_video ? (
              <video
                controls
                style={{ width: '100%', height: 'auto' }}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              >
                <source src={lecon.url_video} type="video/mp4" />
                Votre navigateur ne supporte pas la lecture vidéo.
              </video>
            ) : (
              <Box 
                sx={{ 
                  height: 300, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'white'
                }}
              >
                <Typography>Vidéo non disponible</Typography>
              </Box>
            )}
          </Box>
        );

      case 'pdf':
        return (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" gutterBottom>
              Document PDF
            </Typography>
            <Typography color="text.secondary" paragraph>
              {lecon.description}
            </Typography>
            {lecon.fichier_pdf && (
              <Button
                variant="contained"
                href={lecon.fichier_pdf}
                target="_blank"
                startIcon={<MenuBook />}
              >
                Ouvrir le document
              </Button>
            )}
          </Box>
        );

      case 'texte':
        return (
          <Paper sx={{ p: 3 }}>
            <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
              {lecon.contenu}
            </Typography>
          </Paper>
        );

      case 'quiz':
        return (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Quiz sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Quiz disponible
            </Typography>
            <Typography color="text.secondary" paragraph>
              Testez vos connaissances sur cette leçon
            </Typography>
            <Button
              variant="contained"
              size="large"
              startIcon={<Quiz />}
              onClick={() => navigate(`/learning/quiz/${lecon.id}`)}
            >
              Commencer le quiz
            </Button>
          </Box>
        );

      default:
        return (
          <Typography>Type de contenu non supporté</Typography>
        );
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !lecon) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error || 'Leçon non trouvée'}</Alert>
        <Button 
          startIcon={<ArrowBack />} 
          onClick={() => navigate(-1)}
          sx={{ mt: 2 }}
        >
          Retour
        </Button>
      </Container>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Barre d'outils */}
      <AppBar position="static" color="default" elevation={1}>
        <Toolbar variant="dense">
          <IconButton onClick={() => setDrawerOpen(true)} sx={{ mr: 2 }}>
            <Menu />
          </IconButton>
          
          <Box sx={{ flex: 1 }}>
            <Breadcrumbs>
              <Link 
                color="inherit" 
                onClick={() => navigate(`/learning/formations/${lecon.module.formation.id}`)}
                sx={{ cursor: 'pointer' }}
              >
                {lecon.module.formation.titre}
              </Link>
              <Typography color="text.primary">{lecon.titre}</Typography>
            </Breadcrumbs>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={<Typography sx={{ fontSize: 16 }}>{getTypeIcon(lecon.type_contenu)}</Typography>}
              label={lecon.type_contenu}
              size="small"
              variant="outlined"
            />
            <Chip
              icon={<AccessTime />}
              label={formatDuration(lecon.duree_estimee)}
              size="small"
              variant="outlined"
            />
            <IconButton onClick={() => setBookmarked(!bookmarked)}>
              {bookmarked ? <Bookmark color="primary" /> : <BookmarkBorder />}
            </IconButton>
            <IconButton onClick={() => setShowNotes(true)}>
              <Note />
            </IconButton>
            <IconButton onClick={() => setFullscreen(!fullscreen)}>
              {fullscreen ? <FullscreenExit /> : <Fullscreen />}
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Barre de progression */}
      <LinearProgress 
        variant="determinate" 
        value={progression} 
        sx={{ height: 4 }}
      />

      {/* Contenu principal */}
      <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Box sx={{ flex: 1, p: 2 }}>
          {/* En-tête de la leçon */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" gutterBottom>
              {lecon.titre}
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              {lecon.description}
            </Typography>
          </Box>

          {/* Contenu */}
          <Box sx={{ mb: 3 }}>
            {renderContenu()}
          </Box>

          {/* Navigation */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
            <Button
              startIcon={<SkipPrevious />}
              disabled={!navigation.lecon_precedente}
              onClick={() => navigation.lecon_precedente && naviguerVers(navigation.lecon_precedente.id)}
            >
              {navigation.lecon_precedente?.titre || 'Précédent'}
            </Button>

            <Box sx={{ display: 'flex', gap: 2 }}>
              {progression < 100 && (
                <Button
                  variant="contained"
                  onClick={terminerLecon}
                  startIcon={<CheckCircle />}
                >
                  Marquer comme terminé
                </Button>
              )}
            </Box>

            <Button
              endIcon={<SkipNext />}
              disabled={!navigation.lecon_suivante}
              onClick={() => navigation.lecon_suivante && naviguerVers(navigation.lecon_suivante.id)}
            >
              {navigation.lecon_suivante?.titre || 'Suivant'}
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Drawer de navigation */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        <Box sx={{ width: 300, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            {lecon.module.titre}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Module de la formation "{lecon.module.formation.titre}"
          </Typography>
          
          <Button
            fullWidth
            variant="outlined"
            startIcon={<ArrowBack />}
            onClick={() => navigate(`/learning/formations/${lecon.module.formation.id}`)}
            sx={{ mb: 2 }}
          >
            Retour à la formation
          </Button>

          {/* Navigation vers d'autres leçons */}
          <Typography variant="subtitle2" gutterBottom>
            Navigation
          </Typography>
          <List>
            {navigation.lecon_precedente && (
              <ListItem disablePadding>
                <ListItemButton onClick={() => naviguerVers(navigation.lecon_precedente!.id)}>
                  <ListItemIcon>
                    <SkipPrevious />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Précédent"
                    secondary={navigation.lecon_precedente.titre}
                  />
                </ListItemButton>
              </ListItem>
            )}
            
            <ListItem disablePadding>
              <ListItemButton disabled>
                <ListItemIcon>
                  <PlayArrow color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary="Actuel"
                  secondary={lecon.titre}
                />
              </ListItemButton>
            </ListItem>

            {navigation.lecon_suivante && (
              <ListItem disablePadding>
                <ListItemButton onClick={() => naviguerVers(navigation.lecon_suivante!.id)}>
                  <ListItemIcon>
                    <SkipNext />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Suivant"
                    secondary={navigation.lecon_suivante.titre}
                  />
                </ListItemButton>
              </ListItem>
            )}
          </List>
        </Box>
      </Drawer>

      {/* Dialog des notes */}
      <Dialog 
        open={showNotes} 
        onClose={() => setShowNotes(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>📝 Mes notes</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Prenez des notes sur cette leçon pour mieux retenir les concepts importants.
          </Typography>
          <textarea
            rows={10}
            style={{ 
              width: '100%', 
              border: '1px solid #ddd', 
              borderRadius: 4, 
              padding: 8,
              fontFamily: 'inherit'
            }}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Vos notes sur cette leçon..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowNotes(false)}>Fermer</Button>
          <Button variant="contained">Sauvegarder</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LessonPlayer;