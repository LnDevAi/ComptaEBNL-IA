import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';

const Analytics: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Analytics & Rapports
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Analyses avancées et tableaux de bord personnalisés
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <TrendingUp sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Module Analytics Avancé
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Analyses financières et rapports personnalisés pour EBNL
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Analytics;