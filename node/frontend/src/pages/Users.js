import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const Users = () => {
  return (
    <Container maxWidth="lg">
      <Box py={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Users
        </Typography>
        <Typography variant="body1" color="text.secondary">
          User management page - Coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default Users; 