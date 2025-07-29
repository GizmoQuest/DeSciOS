import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Fab,
  Alert,
  CircularProgress,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Add as AddIcon,
  Search as SearchIcon,
  Group as GroupIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  FilterList as FilterIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Forum as ForumIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Collaboration = () => {
  const navigate = useNavigate();
  const { user, api } = useAuth();
  const [workspaces, setWorkspaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [showMyWorkspaces, setShowMyWorkspaces] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workspaceToDelete, setWorkspaceToDelete] = useState(null);

  useEffect(() => {
    fetchWorkspaces();
  }, [showMyWorkspaces]);

  const fetchWorkspaces = async () => {
    try {
      const endpoint = showMyWorkspaces ? '/collaboration/my-workspaces' : '/collaboration';
      const response = await api.get(endpoint);
      setWorkspaces(response.data.workspaces || []);
    } catch (error) {
      console.error('Error fetching collaboration workspaces:', error);
      setError('Failed to load collaboration workspaces');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!workspaceToDelete) return;
    
    try {
      await api.delete(`/collaboration/${workspaceToDelete.id}`);
      toast.success('Collaboration workspace deleted successfully');
      fetchWorkspaces();
    } catch (error) {
      console.error('Error deleting workspace:', error);
      toast.error('Failed to delete workspace');
    } finally {
      setDeleteDialogOpen(false);
      setWorkspaceToDelete(null);
    }
  };

  const confirmDelete = (workspace) => {
    setWorkspaceToDelete(workspace);
    setDeleteDialogOpen(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'primary';
      case 'archived': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'active': return 'Active';
      case 'completed': return 'Completed';
      case 'archived': return 'Archived';
      default: return status;
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'course': return 'Course';
      case 'research': return 'Research';
      case 'peer_review': return 'Peer Review';
      case 'study_group': return 'Study Group';
      default: return type;
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'course': return 'primary';
      case 'research': return 'secondary';
      case 'peer_review': return 'warning';
      case 'study_group': return 'info';
      default: return 'default';
    }
  };

  const filteredWorkspaces = workspaces.filter(workspace => {
    const matchesSearch = workspace.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         workspace.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || workspace.status === statusFilter;
    const matchesType = typeFilter === 'all' || workspace.type === typeFilter;
    
    return matchesSearch && matchesStatus && matchesType;
  });

  const types = [...new Set(workspaces.map(w => w.type))];
  const statuses = ['active', 'completed', 'archived'];

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          Collaboration Workspaces
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant={showMyWorkspaces ? 'contained' : 'outlined'}
            onClick={() => setShowMyWorkspaces(!showMyWorkspaces)}
            startIcon={<PersonIcon />}
          >
            {showMyWorkspaces ? 'All Workspaces' : 'My Workspaces'}
          </Button>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/collaboration/create')}
          >
            New Workspace
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search workspaces..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  {statuses.map(status => (
                    <MenuItem key={status} value={status}>
                      {getStatusLabel(status)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  label="Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  {types.map(type => (
                    <MenuItem key={type} value={type}>
                      {getTypeLabel(type)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setTypeFilter('all');
                }}
                startIcon={<FilterIcon />}
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Workspaces Grid */}
      {filteredWorkspaces.length === 0 ? (
        <Box textAlign="center" py={4}>
          <GroupIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No collaboration workspaces found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm || statusFilter !== 'all' || typeFilter !== 'all' 
              ? 'Try adjusting your filters' 
              : 'Get started by creating your first collaboration workspace'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredWorkspaces.map((workspace) => (
            <Grid item xs={12} md={6} lg={4} key={workspace.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" component="h2" sx={{ 
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical'
                    }}>
                      {workspace.title}
                    </Typography>
                    
                    <Chip
                      label={getStatusLabel(workspace.status)}
                      color={getStatusColor(workspace.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2, 
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {workspace.description}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <PersonIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      Owner: {workspace.owner?.username || 'Unknown'}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <CalendarIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {new Date(workspace.createdAt).toLocaleDateString()}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip
                      label={getTypeLabel(workspace.type)}
                      color={getTypeColor(workspace.type)}
                      size="small"
                    />
                    {workspace.isPublic ? (
                      <Chip
                        label="Public"
                        size="small"
                        icon={<VisibilityIcon />}
                        variant="outlined"
                      />
                    ) : (
                      <Chip
                        label="Private"
                        size="small"
                        icon={<VisibilityOffIcon />}
                        variant="outlined"
                      />
                    )}
                  </Box>
                  
                  {/* Member count */}
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                    <GroupIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      {workspace.Users?.length || 0} members
                    </Typography>
                  </Box>
                  
                  {/* Document count */}
                  {workspace.documents && workspace.documents.length > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <ForumIcon sx={{ mr: 1, fontSize: 16, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        {workspace.documents.length} documents
                      </Typography>
                    </Box>
                  )}
                </CardContent>
                
                <CardActions sx={{ justifyContent: 'space-between' }}>
                  <Button
                    size="small"
                    onClick={() => navigate(`/collaboration/${workspace.id}`)}
                  >
                    View Details
                  </Button>
                  
                  {(user?.id === workspace.creatorId || user?.role === 'admin') && (
                    <Box>
                      <Button
                        size="small"
                        onClick={() => navigate(`/collaboration/${workspace.id}/edit`)}
                      >
                        Edit
                      </Button>
                      <Button
                        size="small"
                        color="error"
                        onClick={() => confirmDelete(workspace)}
                      >
                        Delete
                      </Button>
                    </Box>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => navigate('/collaboration/create')}
      >
        <AddIcon />
      </Fab>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Collaboration Workspace</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{workspaceToDelete?.title}"? This action cannot be undone.
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

export default Collaboration; 