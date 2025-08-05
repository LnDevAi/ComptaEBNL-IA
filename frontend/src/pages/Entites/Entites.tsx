import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Business } from '@mui/icons-material';

const Entites: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Gestion Multi-Entités EBNL
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Administration de plusieurs associations et fondations
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Business sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Module Multi-Entités
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Gestion centralisée de plusieurs entités EBNL
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Entites;