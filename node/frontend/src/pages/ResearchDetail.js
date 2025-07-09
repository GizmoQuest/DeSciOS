import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const ResearchDetail = () => {
  return (
    <Container maxWidth="lg">
      <Box py={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Research Project Detail
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Research project details page - Coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default ResearchDetail; 