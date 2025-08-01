import React, { useState } from 'react';
import { Box, Typography, Paper, Alert, CircularProgress } from '@mui/material';

function DeSciOS() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const handleIframeLoad = () => {
    setLoading(false);
  };

  const handleIframeError = () => {
    setLoading(false);
    setError(true);
  };

  return (
    <Box sx={{ 
      height: 'calc(100vh - 140px)', 
      display: 'flex', 
      flexDirection: 'column',
      margin: '-24px',
      padding: '24px'
    }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 1 }}>
        DeSciOS Desktop Environment
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
        Access the DeSciOS desktop environment through VNC
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 1 }}>
          Unable to connect to DeSciOS desktop environment. Please ensure the VNC server is running on port 6080.
        </Alert>
      )}
      
      <Paper 
        sx={{ 
          flex: 1, 
          overflow: 'hidden',
          border: '1px solid #e0e0e0',
          borderRadius: 2,
          position: 'relative',
          minHeight: 0,
          mt: 1
        }}
      >
        {loading && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              zIndex: 1
            }}
          >
            <CircularProgress />
          </Box>
        )}
        
        <iframe
          src="http://localhost:6080/vnc.html"
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            borderRadius: '8px',
            display: 'block'
          }}
          title="DeSciOS Desktop Environment"
          allowFullScreen
          onLoad={handleIframeLoad}
          onError={handleIframeError}
        />
      </Paper>
    </Box>
  );
}

export default DeSciOS; 