import React from 'react';
import { 
  Box, 
  CircularProgress, 
  Typography, 
  Paper 
} from '@mui/material';

function LoadingScreen({ message = "Loading..." }) {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5'
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          {message}
        </Typography>
      </Paper>
    </Box>
  );
}

export default LoadingScreen; 