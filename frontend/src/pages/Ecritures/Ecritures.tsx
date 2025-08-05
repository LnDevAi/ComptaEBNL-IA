import React from 'react';
import { Box, Typography, Card, CardContent, Button } from '@mui/material';
import { Receipt, Add } from '@mui/icons-material';

const Ecritures: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Écritures Comptables
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Gestion des écritures et des journaux comptables
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Receipt sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Module Écritures Comptables
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Interface de saisie et gestion des écritures comptables SYCEBNL
          </Typography>
          <Button variant="contained" startIcon={<Add />}>
            Nouvelle écriture
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Ecritures;