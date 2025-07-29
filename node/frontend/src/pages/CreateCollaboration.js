import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Chip,
  Grid,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  IconButton
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const CreateCollaboration = ({ editing = false, initialData = null }) => {
  const navigate = useNavigate();
  const { api } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState(initialData || {
    title: '',
    description: '',
    type: 'study_group',
    isPublic: true,
    documents: []
  });

  useEffect(() => {
    if (initialData) {
      setFormData({ ...initialData });
    }
  }, [initialData]);

  const [files, setFiles] = useState([]);

  const types = [
    { value: 'course', label: 'Course Collaboration' },
    { value: 'research', label: 'Research Collaboration' },
    { value: 'peer_review', label: 'Peer Review' },
    { value: 'study_group', label: 'Study Group' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileUpload = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFilesToIPFS = async () => {
    const uploadedDocuments = [];
    
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.post('/ipfs/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        uploadedDocuments.push({
          name: file.name,
          size: file.size,
          type: file.type,
          ipfsHash: response.data.hash,
          uploadedAt: new Date().toISOString()
        });
      } catch (error) {
        console.error('Error uploading file:', error);
        throw new Error(`Failed to upload ${file.name}`);
      }
    }
    
    return uploadedDocuments;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate form
      if (!formData.title || !formData.description) {
        throw new Error('Please fill in all required fields');
      }

      // Upload files to IPFS
      let documents = [];
      if (files.length > 0) {
        documents = await uploadFilesToIPFS();
      }

      let response;
      if (editing) {
        const workspaceData = { ...formData, documents };
        response = await api.put(`/collaboration/${initialData.id}`, workspaceData);
      } else {
        const workspaceData = { ...formData, documents, status: 'active' };
        response = await api.post('/collaboration', workspaceData);
      }
      
      toast.success(`Collaboration workspace ${editing ? 'updated' : 'created'} successfully!`);
      navigate(`/collaboration/${editing ? initialData.id : response.data.collaboration.id}`);
      
    } catch (error) {
      console.error('Error creating collaboration workspace:', error);
      setError(error.response?.data?.message || error.message || 'Failed to create collaboration workspace');
      toast.error('Failed to create collaboration workspace');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          {editing ? 'Edit Collaboration Workspace' : 'Create New Collaboration Workspace'}
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Workspace Title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth required>
                <InputLabel>Type</InputLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  label="Type"
                >
                  {types.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                required
                placeholder="Describe the purpose and goals of this collaboration workspace..."
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Visibility</InputLabel>
                <Select
                  value={formData.isPublic}
                  onChange={(e) => handleInputChange('isPublic', e.target.value)}
                  label="Visibility"
                >
                  <MenuItem value={true}>Public</MenuItem>
                  <MenuItem value={false}>Private</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* File Upload */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Initial Documents
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <input
                  accept="*/*"
                  style={{ display: 'none' }}
                  id="file-upload"
                  multiple
                  type="file"
                  onChange={handleFileUpload}
                />
                <label htmlFor="file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<CloudUploadIcon />}
                  >
                    Upload Files
                  </Button>
                </label>
              </Box>
              
              {files.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Selected Files:
                  </Typography>
                  {files.map((file, index) => (
                    <Chip
                      key={index}
                      label={`${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`}
                      onDelete={() => removeFile(index)}
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              )}
            </Grid>

            {/* Workspace Features Info */}
            <Grid item xs={12}>
              <Card sx={{ bgcolor: 'grey.50' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Collaboration Features
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    This workspace will include:
                  </Typography>
                  <Box component="ul" sx={{ pl: 2 }}>
                    <Typography component="li" variant="body2" color="text.secondary">
                      Real-time document collaboration
                    </Typography>
                    <Typography component="li" variant="body2" color="text.secondary">
                      Member management and permissions
                    </Typography>
                    <Typography component="li" variant="body2" color="text.secondary">
                      File sharing and version control
                    </Typography>
                    <Typography component="li" variant="body2" color="text.secondary">
                      Discussion forums and messaging
                    </Typography>
                    <Typography component="li" variant="body2" color="text.secondary">
                      IPFS-based decentralized storage
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Submit Button */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/collaboration')}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                >
                  {loading ? (editing ? 'Updating...' : 'Creating...') : (editing ? 'Save Changes' : 'Create Workspace')}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default CreateCollaboration; 