import React, { useState } from 'react';
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
  IconButton,
  OutlinedInput
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const CreateResearch = () => {
  const navigate = useNavigate();
  const { api } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    field: '',
    keywords: [],
    status: 'proposal',
    isPublic: false,
    methodology: '',
    findings: '',
    datasets: [],
    publications: []
  });

  const [files, setFiles] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');

  const fields = [
    'Computer Science',
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'Engineering',
    'Economics',
    'Psychology',
    'Philosophy',
    'Medicine',
    'Environmental Science',
    'Social Sciences',
    'Arts and Humanities',
    'Other'
  ];

  const statuses = [
    { value: 'proposal', label: 'Proposal' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
    { value: 'archived', label: 'Archived' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleKeywordAdd = () => {
    if (newKeyword.trim() && !formData.keywords.includes(newKeyword.trim())) {
      setFormData(prev => ({
        ...prev,
        keywords: [...prev.keywords, newKeyword.trim()]
      }));
      setNewKeyword('');
    }
  };

  const handleKeywordDelete = (keywordToDelete) => {
    setFormData(prev => ({
      ...prev,
      keywords: prev.keywords.filter(keyword => keyword !== keywordToDelete)
    }));
  };

  const handleKeywordKeyPress = (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      handleKeywordAdd();
    }
  };

  const handleFileUpload = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(prev => [...prev, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFilesToIPFS = async () => {
    const uploadedDatasets = [];
    
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.post('/ipfs/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        uploadedDatasets.push({
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
    
    return uploadedDatasets;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate form
      if (!formData.title || !formData.description || !formData.field) {
        throw new Error('Please fill in all required fields');
      }

      // Upload files to IPFS
      let datasets = [];
      if (files.length > 0) {
        datasets = await uploadFilesToIPFS();
      }

      // Create research project
      const projectData = {
        ...formData,
        datasets
      };

      const response = await api.post('/research', projectData);
      
      toast.success('Research project created successfully!');
      navigate(`/research/${response.data.id}`);
      
    } catch (error) {
      console.error('Error creating research project:', error);
      setError(error.response?.data?.message || error.message || 'Failed to create research project');
      toast.error('Failed to create research project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Create New Research Project
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
                label="Research Title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth required>
                <InputLabel>Field</InputLabel>
                <Select
                  value={formData.field}
                  onChange={(e) => handleInputChange('field', e.target.value)}
                  label="Field"
                >
                  {fields.map(field => (
                    <MenuItem key={field} value={field}>
                      {field}
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
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                  label="Status"
                >
                  {statuses.map(status => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
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

            {/* Keywords */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Keywords
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  label="Add keyword"
                  value={newKeyword}
                  onChange={(e) => setNewKeyword(e.target.value)}
                  onKeyPress={handleKeywordKeyPress}
                  size="small"
                />
                <Button
                  variant="outlined"
                  onClick={handleKeywordAdd}
                  disabled={!newKeyword.trim()}
                >
                  Add
                </Button>
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {formData.keywords.map((keyword, index) => (
                  <Chip
                    key={index}
                    label={keyword}
                    onDelete={() => handleKeywordDelete(keyword)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Grid>

            {/* Methodology */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Methodology
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Research methodology and approach"
                value={formData.methodology}
                onChange={(e) => handleInputChange('methodology', e.target.value)}
                placeholder="Describe your research methodology, data collection methods, analysis approach, etc."
              />
            </Grid>

            {/* Findings */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Findings
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Research findings and results"
                value={formData.findings}
                onChange={(e) => handleInputChange('findings', e.target.value)}
                placeholder="Document your research findings, results, and conclusions..."
              />
            </Grid>

            {/* Publications */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Publications
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Related publications"
                value={formData.publications.join('\n')}
                onChange={(e) => handleInputChange('publications', e.target.value.split('\n').filter(pub => pub.trim()))}
                placeholder="Enter publication references, one per line..."
                helperText="Enter each publication reference on a new line"
              />
            </Grid>

            {/* File Upload */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Research Data & Files
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

            {/* Submit Button */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/research')}
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
                  {loading ? 'Creating...' : 'Create Research Project'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default CreateResearch; 