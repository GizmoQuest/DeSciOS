import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box py={3} display="flex" flexDirection="column" alignItems="center" textAlign="center">
        <Typography variant="h1" component="h1" gutterBottom sx={{ fontSize: '4rem' }}>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          The page you are looking for does not exist.
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 2 }}
        >
          Go to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

export default NotFound; 