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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Group as GroupIcon,
  AccessTime as AccessTimeIcon,
  Person as PersonIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Forum as ForumIcon,
  CloudUpload as CloudUploadIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const CollaborationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, api } = useAuth();
  const [workspace, setWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [addMemberDialogOpen, setAddMemberDialogOpen] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [memberRole, setMemberRole] = useState('member');

  useEffect(() => {
    fetchWorkspace();
  }, [id]);

  const fetchWorkspace = async () => {
    try {
      const response = await api.get(`/collaboration/${id}`);
      setWorkspace(response.data.collaboration || response.data);
    } catch (error) {
      console.error('Error fetching collaboration workspace:', error);
      setError('Failed to load collaboration workspace details');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/collaboration/${id}`);
      toast.success('Collaboration workspace deleted successfully');
      navigate('/collaboration');
    } catch (error) {
      console.error('Error deleting workspace:', error);
      toast.error('Failed to delete workspace');
    } finally {
      setDeleteDialogOpen(false);
    }
  };

  const handleAddMember = async () => {
    try {
      await api.post(`/collaboration/${id}/members`, {
        email: newMemberEmail,
        role: memberRole
      });
      toast.success('Member added successfully');
      setAddMemberDialogOpen(false);
      setNewMemberEmail('');
      setMemberRole('member');
      fetchWorkspace();
    } catch (error) {
      console.error('Error adding member:', error);
      toast.error('Failed to add member');
    }
  };

  const handleRemoveMember = async (memberId) => {
    try {
      await api.delete(`/collaboration/${id}/members/${memberId}`);
      toast.success('Member removed successfully');
      fetchWorkspace();
    } catch (error) {
      console.error('Error removing member:', error);
      toast.error('Failed to remove member');
    }
  };

  const downloadDocument = async (document) => {
    try {
      const response = await api.get(`/ipfs/download/${document.ipfsHash}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${document.name}`);
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
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

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !workspace) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          {error || 'Collaboration workspace not found'}
        </Alert>
      </Container>
    );
  }

  const isOwner = user && workspace.creatorId === user.id;
  const canEdit = isOwner || user?.role === 'admin';
  const isMember = workspace.Users?.some(member => member.id === user?.id) || isOwner;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {workspace.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={getStatusLabel(workspace.status)} 
                color={getStatusColor(workspace.status)}
                size="small"
              />
              <Chip 
                label={getTypeLabel(workspace.type)} 
                color={getTypeColor(workspace.type)}
                size="small"
              />
              {workspace.isPublic ? (
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
                  onClick={() => navigate(`/collaboration/${id}/edit`)}
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
            
            {isOwner && (
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setAddMemberDialogOpen(true)}
              >
                Add Member
              </Button>
            )}
          </Box>
        </Box>

        {/* Workspace Info */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Typography variant="body1" paragraph>
              {workspace.description}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Workspace Information
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Owner: {workspace.owner?.username || 'Unknown'}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccessTimeIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Created: {new Date(workspace.createdAt).toLocaleDateString()}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <GroupIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Members: {workspace.Users?.length || 0}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Members" />
            <Tab label="Documents" />
            <Tab label="Discussions" />
            <Tab label="Activity" />
          </Tabs>
        </Box>

        {/* Members Tab */}
        {activeTab === 0 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Workspace Members
              </Typography>
              {isOwner && (
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => setAddMemberDialogOpen(true)}
                >
                  Add Member
                </Button>
              )}
            </Box>
            
            {workspace.Users && workspace.Users.length > 0 ? (
              <List>
                {workspace.Users.map((member, index) => (
                  <ListItem key={index}>
                    <Avatar sx={{ mr: 2 }}>
                      {member.user?.username?.charAt(0)?.toUpperCase() || 'U'}
                    </Avatar>
                    <ListItemText
                      primary={member.user?.username || 'Unknown User'}
                      secondary={`Role: ${member.role} • Joined: ${new Date(member.createdAt).toLocaleDateString()}`}
                    />
                    {isOwner && member.userId !== user?.id && (
                      <IconButton
                        color="error"
                        onClick={() => handleRemoveMember(member.userId)}
                      >
                        <RemoveIcon />
                      </IconButton>
                    )}
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No members in this workspace.
              </Typography>
            )}
          </Box>
        )}

        {/* Documents Tab */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Shared Documents
            </Typography>
            
            {workspace.documents && workspace.documents.length > 0 ? (
              <Grid container spacing={2}>
                {workspace.documents.map((document, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <ForumIcon sx={{ mr: 1, color: 'primary.main' }} />
                          <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                            {document.name}
                          </Typography>
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {(document.size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                        
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Uploaded: {new Date(document.uploadedAt).toLocaleDateString()}
                        </Typography>
                        
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<DownloadIcon />}
                          onClick={() => downloadDocument(document)}
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
                No documents shared in this workspace.
              </Typography>
            )}
          </Box>
        )}

        {/* Discussions Tab */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Discussions
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time discussion features coming soon...
            </Typography>
          </Box>
        )}

        {/* Activity Tab */}
        {activeTab === 3 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Activity tracking features coming soon...
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Collaboration Workspace</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{workspace.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Member Dialog */}
      <Dialog open={addMemberDialogOpen} onClose={() => setAddMemberDialogOpen(false)}>
        <DialogTitle>Add Member</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Email"
            value={newMemberEmail}
            onChange={(e) => setNewMemberEmail(e.target.value)}
            sx={{ mb: 2, mt: 1 }}
          />
          <FormControl fullWidth>
            <InputLabel>Role</InputLabel>
            <Select
              value={memberRole}
              onChange={(e) => setMemberRole(e.target.value)}
              label="Role"
            >
              <MenuItem value="member">Member</MenuItem>
              <MenuItem value="moderator">Moderator</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddMemberDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddMember} variant="contained" disabled={!newMemberEmail}>
            Add Member
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default CollaborationDetail; 