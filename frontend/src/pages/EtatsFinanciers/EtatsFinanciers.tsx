import React from 'react';
import { Box, Typography, Card, CardContent, Grid, Button } from '@mui/material';
import { Assessment, PictureAsPdf, GetApp } from '@mui/icons-material';

const EtatsFinanciers: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          États Financiers SYCEBNL
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Bilan, compte de résultat et flux de trésorerie
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assessment sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Bilan SYCEBNL
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                État de la situation financière
              </Typography>
              <Button variant="contained" startIcon={<PictureAsPdf />}>
                Générer PDF
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assessment sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Compte de Résultat
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Emplois et ressources
              </Typography>
              <Button variant="contained" startIcon={<PictureAsPdf />}>
                Générer PDF
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Assessment sx={{ fontSize: 48, color: 'warning.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Flux de Trésorerie
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Tableau des flux
              </Typography>
              <Button variant="contained" startIcon={<PictureAsPdf />}>
                Générer PDF
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EtatsFinanciers;