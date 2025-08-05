import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { AccountBalance } from '@mui/icons-material';

const Rapprochement: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Rapprochement Bancaire
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Réconciliation automatique avec les relevés bancaires
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <AccountBalance sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Module Rapprochement Bancaire
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Rapprochement automatique et validation des mouvements bancaires
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Rapprochement;