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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Paper,
  Divider,
  Avatar,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';
import {
  EmojiEvents,
  Download,
  Share,
  Verified,
  School,
  CalendarToday,
  Person,
  CheckCircle,
  Search,
  ContentCopy,
  Visibility,
  Star,
  Grade,
  BookmarkBorder,
  Bookmark
} from '@mui/icons-material';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { apiClient } from '../../context/AuthContext';

// Types
interface Certificat {
  id: number;
  numero_certificat: string;
  nom_beneficiaire: string;
  formation: {
    id: number;
    titre: string;
    categorie: {
      nom: string;
      couleur: string;
    };
  };
  statut: 'en_cours' | 'valide' | 'expire' | 'suspendu';
  date_obtention: string;
  date_expiration?: string;
  note_finale: number;
  mention: string;
  fichier_pdf?: string;
  est_valide: boolean;
}

const CertificateDashboard: React.FC = () => {
  const [certificats, setCertificats] = useState<Certificat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [verificationDialog, setVerificationDialog] = useState(false);
  const [numeroCertificat, setNumeroCertificat] = useState('');
  const [certificatVerifie, setCertificatVerifie] = useState<any>(null);
  const [verificationLoading, setVerificationLoading] = useState(false);
  const [selectedCertificat, setSelectedCertificat] = useState<Certificat | null>(null);
  const [detailDialog, setDetailDialog] = useState(false);

  useEffect(() => {
    loadCertificats();
  }, []);

  const loadCertificats = async () => {
    try {
      const response = await apiClient.get('/api/v1/mes-certificats');
      setCertificats(response.data.certificats || []);
    } catch (err) {
      setError('Erreur lors du chargement des certificats');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const verifierCertificat = async () => {
    if (!numeroCertificat.trim()) return;

    setVerificationLoading(true);
    try {
      const response = await apiClient.get(`/api/v1/certificats/${numeroCertificat}/verifier`);
      setCertificatVerifie(response.data.certificat);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Certificat non trouvé');
      setCertificatVerifie(null);
    } finally {
      setVerificationLoading(false);
    }
  };

  const copierNumero = (numero: string) => {
    navigator.clipboard.writeText(numero);
    // TODO: Ajouter une notification
  };

  const getStatutColor = (statut: string) => {
    switch (statut) {
      case 'valide': return 'success';
      case 'en_cours': return 'warning';
      case 'expire': return 'error';
      case 'suspendu': return 'default';
      default: return 'default';
    }
  };

  const getStatutIcon = (statut: string) => {
    switch (statut) {
      case 'valide': return <Verified />;
      case 'en_cours': return <School />;
      case 'expire': return <CalendarToday />;
      case 'suspendu': return <Person />;
      default: return <EmojiEvents />;
    }
  };

  const getMentionColor = (mention: string) => {
    switch (mention.toLowerCase()) {
      case 'excellent': return '#4CAF50';
      case 'très bien': return '#2196F3';
      case 'bien': return '#FF9800';
      case 'passable': return '#9C27B0';
      default: return '#757575';
    }
  };

  const formatNote = (note: number) => {
    return `${(note * 20).toFixed(1)}/20`;
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Chargement des certificats...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* En-tête */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          🏆 Mes Certificats
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Certificats officiels EBNL de l'espace OHADA
        </Typography>
      </Box>

      {/* Actions rapides */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              📋 Statistiques
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="primary">
                    {certificats.length}
                  </Typography>
                  <Typography variant="body2">Certificats</Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" color="success.main">
                    {certificats.filter(c => c.statut === 'valide').length}
                  </Typography>
                  <Typography variant="body2">Valides</Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              🔍 Vérifier un certificat
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="CEBNL-2025-F001-ABC12345"
                value={numeroCertificat}
                onChange={(e) => setNumeroCertificat(e.target.value)}
              />
              <Button
                variant="contained"
                startIcon={<Search />}
                onClick={() => setVerificationDialog(true)}
              >
                Vérifier
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Message si aucun certificat */}
      {certificats.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <EmojiEvents sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Aucun certificat obtenu
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Terminez vos formations pour obtenir des certificats officiels
          </Typography>
          <Button variant="outlined" onClick={() => window.location.href = '/learning/formations'}>
            Découvrir les formations
          </Button>
        </Paper>
      ) : (
        /* Grille des certificats */
        <Grid container spacing={3}>
          {certificats.map((certificat) => (
            <Grid item xs={12} sm={6} md={4} key={certificat.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  position: 'relative',
                  '&:hover': {
                    boxShadow: (theme) => theme.shadows[8]
                  }
                }}
              >
                {/* Badge statut */}
                <Chip
                  icon={getStatutIcon(certificat.statut)}
                  label={certificat.statut}
                  color={getStatutColor(certificat.statut) as any}
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                    textTransform: 'capitalize'
                  }}
                />

                <CardContent sx={{ flexGrow: 1, pt: 5 }}>
                  {/* Icône de certificat */}
                  <Box sx={{ textAlign: 'center', mb: 2 }}>
                    <Avatar
                      sx={{
                        width: 60,
                        height: 60,
                        bgcolor: certificat.formation.categorie.couleur,
                        mx: 'auto',
                        mb: 1
                      }}
                    >
                      <EmojiEvents sx={{ fontSize: 30 }} />
                    </Avatar>
                    <Typography variant="h6" component="h3">
                      {certificat.formation.titre}
                    </Typography>
                    <Chip
                      label={certificat.formation.categorie.nom}
                      size="small"
                      sx={{
                        backgroundColor: certificat.formation.categorie.couleur + '20',
                        color: certificat.formation.categorie.couleur,
                      }}
                    />
                  </Box>

                  {/* Informations du certificat */}
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <Person fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Bénéficiaire"
                        secondary={certificat.nom_beneficiaire}
                      />
                    </ListItem>
                    
                    <ListItem>
                      <ListItemIcon>
                        <CalendarToday fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Date d'obtention"
                        secondary={format(new Date(certificat.date_obtention), 'dd MMMM yyyy', { locale: fr })}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <Grade fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Note finale"
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              {formatNote(certificat.note_finale)}
                            </Typography>
                            <Chip
                              label={certificat.mention}
                              size="small"
                              sx={{
                                backgroundColor: getMentionColor(certificat.mention) + '20',
                                color: getMentionColor(certificat.mention),
                              }}
                            />
                          </Box>
                        }
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <Verified fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary="Numéro"
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                              {certificat.numero_certificat}
                            </Typography>
                            <IconButton
                              size="small"
                              onClick={() => copierNumero(certificat.numero_certificat)}
                            >
                              <ContentCopy fontSize="small" />
                            </IconButton>
                          </Box>
                        }
                      />
                    </ListItem>
                  </List>

                  {/* Validité */}
                  {certificat.date_expiration && (
                    <Alert 
                      severity={certificat.est_valide ? "success" : "warning"}
                      sx={{ mt: 1 }}
                    >
                      {certificat.est_valide ? 
                        `Valide jusqu'au ${format(new Date(certificat.date_expiration), 'dd/MM/yyyy')}` :
                        'Certificat expiré'
                      }
                    </Alert>
                  )}
                </CardContent>

                {/* Actions */}
                <Box sx={{ p: 2, pt: 0 }}>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Button
                        fullWidth
                        size="small"
                        startIcon={<Visibility />}
                        onClick={() => {
                          setSelectedCertificat(certificat);
                          setDetailDialog(true);
                        }}
                      >
                        Voir
                      </Button>
                    </Grid>
                    <Grid item xs={6}>
                      <Button
                        fullWidth
                        size="small"
                        startIcon={<Download />}
                        disabled={!certificat.fichier_pdf}
                      >
                        PDF
                      </Button>
                    </Grid>
                  </Grid>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dialog de vérification */}
      <Dialog 
        open={verificationDialog} 
        onClose={() => setVerificationDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>🔍 Vérifier un certificat</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Numéro de certificat"
            placeholder="CEBNL-2025-F001-ABC12345"
            value={numeroCertificat}
            onChange={(e) => setNumeroCertificat(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          {certificatVerifie && (
            <Paper sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Verified sx={{ mr: 1 }} />
                <Typography variant="h6">Certificat valide</Typography>
              </Box>
              <Typography><strong>Formation:</strong> {certificatVerifie.formation}</Typography>
              <Typography><strong>Bénéficiaire:</strong> {certificatVerifie.nom_beneficiaire}</Typography>
              <Typography><strong>Date:</strong> {certificatVerifie.date_obtention}</Typography>
              <Typography><strong>Note:</strong> {certificatVerifie.note_finale}/20</Typography>
              <Typography><strong>Mention:</strong> {certificatVerifie.mention}</Typography>
            </Paper>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerificationDialog(false)}>
            Fermer
          </Button>
          <Button 
            onClick={verifierCertificat}
            variant="contained"
            disabled={verificationLoading || !numeroCertificat.trim()}
          >
            {verificationLoading ? 'Vérification...' : 'Vérifier'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de détail */}
      <Dialog 
        open={detailDialog} 
        onClose={() => setDetailDialog(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedCertificat && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <EmojiEvents color="warning" />
                <Box>
                  <Typography variant="h6">
                    Certificat {selectedCertificat.numero_certificat}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {selectedCertificat.formation.titre}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, textAlign: 'center' }}>
                    <EmojiEvents sx={{ fontSize: 80, color: selectedCertificat.formation.categorie.couleur, mb: 2 }} />
                    <Typography variant="h5" gutterBottom>
                      Certificat de Formation
                    </Typography>
                    <Typography variant="h6" gutterBottom>
                      {selectedCertificat.formation.titre}
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      Décerné à
                    </Typography>
                    <Typography variant="h4" gutterBottom color="primary">
                      {selectedCertificat.nom_beneficiaire}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Le {format(new Date(selectedCertificat.date_obtention), 'dd MMMM yyyy', { locale: fr })}
                    </Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    Détails du certificat
                  </Typography>
                  
                  <List>
                    <ListItem>
                      <ListItemText 
                        primary="Numéro de certificat"
                        secondary={selectedCertificat.numero_certificat}
                      />
                      <ListItemSecondaryAction>
                        <IconButton onClick={() => copierNumero(selectedCertificat.numero_certificat)}>
                          <ContentCopy />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText 
                        primary="Statut"
                        secondary={
                          <Chip
                            icon={getStatutIcon(selectedCertificat.statut)}
                            label={selectedCertificat.statut}
                            color={getStatutColor(selectedCertificat.statut) as any}
                            size="small"
                          />
                        }
                      />
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText 
                        primary="Note finale"
                        secondary={`${formatNote(selectedCertificat.note_finale)} - ${selectedCertificat.mention}`}
                      />
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText 
                        primary="Catégorie"
                        secondary={selectedCertificat.formation.categorie.nom}
                      />
                    </ListItem>
                    
                    {selectedCertificat.date_expiration && (
                      <ListItem>
                        <ListItemText 
                          primary="Validité"
                          secondary={`Jusqu'au ${format(new Date(selectedCertificat.date_expiration), 'dd/MM/yyyy')}`}
                        />
                      </ListItem>
                    )}
                  </List>

                  <Box sx={{ mt: 2 }}>
                    <Button
                      fullWidth
                      variant="contained"
                      startIcon={<Download />}
                      disabled={!selectedCertificat.fichier_pdf}
                      sx={{ mb: 1 }}
                    >
                      Télécharger le PDF
                    </Button>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<Share />}
                    >
                      Partager le certificat
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailDialog(false)}>
                Fermer
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default CertificateDashboard;