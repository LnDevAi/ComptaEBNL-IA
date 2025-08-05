import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { CalendarToday } from '@mui/icons-material';

const Exercices: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gestion des Exercices
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Périodes comptables et clôture d'exercice
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <CalendarToday sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Module Exercices Comptables
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Gestion des périodes comptables et procédures de clôture
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Exercices;