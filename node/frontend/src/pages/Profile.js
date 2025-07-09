import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Profile = () => {
  return (
    <Container maxWidth="lg">
      <Box py={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          User profile page - Coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Profile; 