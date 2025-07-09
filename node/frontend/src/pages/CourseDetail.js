import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const CourseDetail = () => {
  return (
    <Container maxWidth="lg">
      <Box py={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          Course Detail
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Course details page - Coming soon...
        </Typography>
      </Box>
    </Container>
  );
};

export default CourseDetail; 