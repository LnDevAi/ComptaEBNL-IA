import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Security } from '@mui/icons-material';

const Audit: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Piste d'Audit
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Traçabilité complète des opérations et conformité
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Security sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Module Piste d'Audit
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Traçabilité complète et conformité réglementaire
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Audit;