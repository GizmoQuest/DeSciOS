import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Link,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Science as ScienceIcon,
  AccessTime as AccessTimeIcon,
  Person as PersonIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  ExpandMore as ExpandMoreIcon,
  Article as ArticleIcon,
  DataObject as DataObjectIcon,
  Group as GroupIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const ResearchDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, api } = useAuth();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    fetchProject();
  }, [id]);

  const fetchProject = async () => {
    try {
      const response = await api.get(`/research/${id}`);
      setProject(response.data);
    } catch (error) {
      console.error('Error fetching research project:', error);
      setError('Failed to load research project details');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/research/${id}`);
      toast.success('Research project deleted successfully');
      navigate('/research');
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Failed to delete project');
    } finally {
      setDeleteDialogOpen(false);
    }
  };

  const downloadDataset = async (dataset) => {
    try {
      const response = await api.get(`/ipfs/download/${dataset.ipfsHash}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', dataset.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${dataset.name}`);
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'primary';
      case 'proposal': return 'warning';
      case 'archived': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'active': return 'Active';
      case 'completed': return 'Completed';
      case 'proposal': return 'Proposal';
      case 'archived': return 'Archived';
      default: return status;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !project) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          {error || 'Research project not found'}
        </Alert>
      </Container>
    );
  }

  const isLeader = user && project.leaderId === user.id;
  const canEdit = isLeader || user?.role === 'admin';

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {project.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={getStatusLabel(project.status)} 
                color={getStatusColor(project.status)}
                size="small"
              />
              <Chip 
                label={project.field} 
                size="small"
                variant="outlined"
              />
              {project.isPublic ? (
                <Chip 
                  label="Public" 
                  icon={<VisibilityIcon />}
                  size="small"
                />
              ) : (
                <Chip 
                  label="Private" 
                  icon={<VisibilityOffIcon />}
                  size="small"
                />
              )}
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            {canEdit && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => navigate(`/research/${id}/edit`)}
                >
                  Edit
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => setDeleteDialogOpen(true)}
                >
                  Delete
                </Button>
              </>
            )}
          </Box>
        </Box>

        {/* Project Info */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Typography variant="body1" paragraph>
              {project.description}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Project Information
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Leader: {project.leader?.username || 'Unknown'}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccessTimeIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Created: {new Date(project.createdAt).toLocaleDateString()}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ScienceIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Field: {project.field}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Keywords */}
        {project.keywords && project.keywords.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Keywords
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {project.keywords.map((keyword, index) => (
                <Chip
                  key={index}
                  label={keyword}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Methodology" />
            <Tab label="Findings" />
            <Tab label="Datasets" />
            <Tab label="Publications" />
            <Tab label="Collaborators" />
          </Tabs>
        </Box>

        {/* Methodology Tab */}
        {activeTab === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Research Methodology
            </Typography>
            
            {project.methodology ? (
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {project.methodology}
              </Typography>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No methodology information available for this project.
              </Typography>
            )}
          </Box>
        )}

        {/* Findings Tab */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Research Findings
            </Typography>
            
            {project.findings ? (
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {project.findings}
              </Typography>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No findings available for this project.
              </Typography>
            )}
          </Box>
        )}

        {/* Datasets Tab */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Research Datasets
            </Typography>
            
            {project.datasets && project.datasets.length > 0 ? (
              <Grid container spacing={2}>
                {project.datasets.map((dataset, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <DataObjectIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                            {dataset.name}
                          </Typography>
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {(dataset.size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Uploaded: {new Date(dataset.uploadedAt).toLocaleDateString()}
                        </Typography>
                        
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<DownloadIcon />}
                          onClick={() => downloadDataset(dataset)}
                          fullWidth
                        >
                          Download
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No datasets available for this project.
              </Typography>
            )}
          </Box>
        )}

        {/* Publications Tab */}
        {activeTab === 3 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Related Publications
            </Typography>
            
            {project.publications && project.publications.length > 0 ? (
              <List>
                {project.publications.map((publication, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <ArticleIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body1">
                              {publication}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < project.publications.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No publications available for this project.
              </Typography>
            )}
          </Box>
        )}

        {/* Collaborators Tab */}
        {activeTab === 4 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Project Collaborators
            </Typography>
            
            {project.collaborators && project.collaborators.length > 0 ? (
              <List>
                {project.collaborators.map((collaborator, index) => (
                  <ListItem key={index}>
                    <Avatar sx={{ mr: 2 }}>
                      {collaborator.user?.username?.charAt(0)?.toUpperCase() || 'U'}
                    </Avatar>
                    <ListItemText
                      primary={collaborator.user?.username || 'Unknown User'}
                      secondary={`Role: ${collaborator.role} • Joined: ${new Date(collaborator.createdAt).toLocaleDateString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No collaborators for this project.
              </Typography>
            )}
          </Box>
        )}
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Research Project</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{project.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ResearchDetail; 