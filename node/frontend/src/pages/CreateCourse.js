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
  IconButton
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const CreateCourse = () => {
  const navigate = useNavigate();
  const { api } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    difficulty: 'beginner',
    isPublic: true,
    syllabus: [{ title: '', description: '', duration: '' }],
    resources: []
  });

  const [files, setFiles] = useState([]);

  const categories = [
    'Computer Science',
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'Engineering',
    'Economics',
    'Psychology',
    'Philosophy',
    'Literature',
    'History',
    'Art',
    'Music',
    'Other'
  ];

  const difficulties = [
    { value: 'beginner', label: 'Beginner' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSyllabusChange = (index, field, value) => {
    const newSyllabus = [...formData.syllabus];
    newSyllabus[index] = {
      ...newSyllabus[index],
      [field]: value
    };
    setFormData(prev => ({
      ...prev,
      syllabus: newSyllabus
    }));
  };

  const addSyllabusItem = () => {
    setFormData(prev => ({
      ...prev,
      syllabus: [...prev.syllabus, { title: '', description: '', duration: '' }]
    }));
  };

  const removeSyllabusItem = (index) => {
    setFormData(prev => ({
      ...prev,
      syllabus: prev.syllabus.filter((_, i) => i !== index)
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
    const uploadedResources = [];
    
    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.post('/ipfs/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        uploadedResources.push({
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
    
    return uploadedResources;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate form
      if (!formData.title || !formData.description || !formData.category) {
        throw new Error('Please fill in all required fields');
      }

      // Upload files to IPFS
      let resources = [];
      if (files.length > 0) {
        resources = await uploadFilesToIPFS();
      }

      // Create course
      const courseData = {
        ...formData,
        resources,
        status: 'draft'
      };

      const response = await api.post('/courses', courseData);
      
      toast.success('Course created successfully!');
      navigate(`/courses/${response.data.id}`);
      
    } catch (error) {
      console.error('Error creating course:', error);
      setError(error.response?.data?.message || error.message || 'Failed to create course');
      toast.error('Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Create New Course
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
                label="Course Title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth required>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  label="Category"
                >
                  {categories.map(category => (
                    <MenuItem key={category} value={category}>
                      {category}
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
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  value={formData.difficulty}
                  onChange={(e) => handleInputChange('difficulty', e.target.value)}
                  label="Difficulty Level"
                >
                  {difficulties.map(difficulty => (
                    <MenuItem key={difficulty.value} value={difficulty.value}>
                      {difficulty.label}
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

            {/* Syllabus */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Course Syllabus
                </Typography>
                <IconButton 
                  onClick={addSyllabusItem}
                  color="primary"
                  sx={{ ml: 1 }}
                >
                  <AddIcon />
                </IconButton>
              </Box>
              
              {formData.syllabus.map((item, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <TextField
                          fullWidth
                          label="Module Title"
                          value={item.title}
                          onChange={(e) => handleSyllabusChange(index, 'title', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Description"
                          value={item.description}
                          onChange={(e) => handleSyllabusChange(index, 'description', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={1}>
                        <TextField
                          fullWidth
                          label="Hours"
                          type="number"
                          value={item.duration}
                          onChange={(e) => handleSyllabusChange(index, 'duration', e.target.value)}
                        />
                      </Grid>
                      <Grid item xs={12} md={1}>
                        <IconButton 
                          onClick={() => removeSyllabusItem(index)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))}
            </Grid>

            {/* File Upload */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Course Resources
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
                  onClick={() => navigate('/courses')}
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
                  {loading ? 'Creating...' : 'Create Course'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default CreateCourse; 