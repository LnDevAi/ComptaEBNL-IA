import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';

const Notifications: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Notifications & Alertes
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Centre de notifications et alertes système
        </Typography>
      </Box>

      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <NotificationsIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Centre de Notifications
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Alertes automatiques et notifications système
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Notifications;