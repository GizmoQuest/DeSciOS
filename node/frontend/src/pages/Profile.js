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
  TextField,
  Avatar,
  IconButton,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Person as PersonIcon,
  School as SchoolIcon,
  Science as ScienceIcon,
  Group as GroupIcon,
  AccessTime as AccessTimeIcon,
  Email as EmailIcon,
  Work as WorkIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Profile = () => {
  const { user, api } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get(`/users/${user.id}/profile`);
      const profileData = response.data.user || response.data;
      setProfile({
        ...profileData,
        stats: response.data.stats || {},
        recentActivity: response.data.recentActivity || {}
      });
      setEditForm({
        username: profileData.username,
        email: profileData.email,
        profile: {
          name: profileData.profile?.name || profileData.profile?.firstName || '',
          institution: profileData.profile?.institution || '',
          bio: profileData.profile?.bio || '',
          website: profileData.profile?.website || '',
          location: profileData.profile?.location || ''
        }
      });
    } catch (error) {
      console.error('Error fetching profile:', error);
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      await api.put('/auth/profile', {
        username: editForm.username,
        email: editForm.email,
        profile: editForm.profile
      });
      toast.success('Profile updated successfully');
      setEditing(false);
      fetchProfile();
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    }
  };

  const handleCancelEdit = () => {
    setEditForm({
      username: profile.username,
      email: profile.email,
      profile: {
        name: profile.profile?.name || '',
        institution: profile.profile?.institution || '',
        bio: profile.profile?.bio || '',
        website: profile.profile?.website || '',
        location: profile.profile?.location || ''
      }
    });
    setEditing(false);
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'error';
      case 'instructor': return 'primary';
      case 'researcher': return 'secondary';
      case 'student': return 'success';
      default: return 'default';
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'admin': return 'Admin';
      case 'instructor': return 'Instructor';
      case 'researcher': return 'Researcher';
      case 'student': return 'Student';
      default: return role;
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

  if (error || !profile) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          {error || 'Profile not found'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar
              sx={{ width: 80, height: 80, mr: 3 }}
            >
              {profile.username.charAt(0).toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h4" gutterBottom>
                {profile.profile?.name || profile.username}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <Chip
                  label={getRoleLabel(profile.role)}
                  color={getRoleColor(profile.role)}
                  size="small"
                />
                <Chip
                  label={profile.isActive ? 'Active' : 'Inactive'}
                  color={profile.isActive ? 'success' : 'default'}
                  size="small"
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                Member since {new Date(profile.createdAt).toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
          
          <Box>
            {editing ? (
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveProfile}
                >
                  Save
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={handleCancelEdit}
                >
                  Cancel
                </Button>
              </Box>
            ) : (
              <Button
                variant="outlined"
                startIcon={<EditIcon />}
                onClick={() => setEditing(true)}
              >
                Edit Profile
              </Button>
            )}
          </Box>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SchoolIcon sx={{ mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="h4">{profile.stats?.coursesCreated || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Courses Created</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ScienceIcon sx={{ mr: 2, color: 'secondary.main' }} />
                  <Box>
                    <Typography variant="h4">{profile.stats?.researchProjects || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Research Projects</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <GroupIcon sx={{ mr: 2, color: 'info.main' }} />
                  <Box>
                    <Typography variant="h4">{profile.stats?.collaborations || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Collaborations</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AccessTimeIcon sx={{ mr: 2, color: 'warning.main' }} />
                  <Box>
                    <Typography variant="h4">{profile.stats?.documentsUploaded || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Documents</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Profile" />
            <Tab label="Activity" />
            <Tab label="Settings" />
          </Tabs>
        </Box>

        {/* Profile Tab */}
        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              {editing ? (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Personal Information
                  </Typography>
                  
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Username"
                        value={editForm.username}
                        onChange={(e) => setEditForm(prev => ({ ...prev, username: e.target.value }))}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Email"
                        value={editForm.email}
                        onChange={(e) => setEditForm(prev => ({ ...prev, email: e.target.value }))}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Full Name"
                        value={editForm.profile.name}
                        onChange={(e) => setEditForm(prev => ({ 
                          ...prev, 
                          profile: { ...prev.profile, name: e.target.value }
                        }))}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Institution"
                        value={editForm.profile.institution}
                        onChange={(e) => setEditForm(prev => ({ 
                          ...prev, 
                          profile: { ...prev.profile, institution: e.target.value }
                        }))}
                      />
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <TextField
                        fullWidth
                        label="Location"
                        value={editForm.profile.location}
                        onChange={(e) => setEditForm(prev => ({ 
                          ...prev, 
                          profile: { ...prev.profile, location: e.target.value }
                        }))}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="Website"
                        value={editForm.profile.website}
                        onChange={(e) => setEditForm(prev => ({ 
                          ...prev, 
                          profile: { ...prev.profile, website: e.target.value }
                        }))}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        multiline
                        rows={4}
                        label="Bio"
                        value={editForm.profile.bio}
                        onChange={(e) => setEditForm(prev => ({ 
                          ...prev, 
                          profile: { ...prev.profile, bio: e.target.value }
                        }))}
                      />
                    </Grid>
                  </Grid>
                </Box>
              ) : (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Personal Information
                  </Typography>
                  
                  <List>
                    <ListItem>
                      <ListItemAvatar>
                        <PersonIcon />
                      </ListItemAvatar>
                      <ListItemText
                        primary="Username"
                        secondary={profile.username}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemAvatar>
                        <EmailIcon />
                      </ListItemAvatar>
                      <ListItemText
                        primary="Email"
                        secondary={profile.email}
                      />
                    </ListItem>
                    {profile.profile?.name && (
                      <ListItem>
                        <ListItemAvatar>
                          <PersonIcon />
                        </ListItemAvatar>
                        <ListItemText
                          primary="Full Name"
                          secondary={profile.profile.name}
                        />
                      </ListItem>
                    )}
                    {profile.profile?.institution && (
                      <ListItem>
                        <ListItemAvatar>
                          <WorkIcon />
                        </ListItemAvatar>
                        <ListItemText
                          primary="Institution"
                          secondary={profile.profile.institution}
                        />
                      </ListItem>
                    )}
                    {profile.profile?.location && (
                      <ListItem>
                        <ListItemAvatar>
                          <AccessTimeIcon />
                        </ListItemAvatar>
                        <ListItemText
                          primary="Location"
                          secondary={profile.profile.location}
                        />
                      </ListItem>
                    )}
                    {profile.profile?.website && (
                      <ListItem>
                        <ListItemAvatar>
                          <WorkIcon />
                        </ListItemAvatar>
                        <ListItemText
                          primary="Website"
                          secondary={
                            <a href={profile.profile.website} target="_blank" rel="noopener noreferrer">
                              {profile.profile.website}
                            </a>
                          }
                        />
                      </ListItem>
                    )}
                  </List>
                  
                  {profile.profile?.bio && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Bio
                      </Typography>
                      <Typography variant="body1">
                        {profile.profile.bio}
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Account Information
                  </Typography>
                  
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="Role"
                        secondary={
                          <Chip
                            label={getRoleLabel(profile.role)}
                            color={getRoleColor(profile.role)}
                            size="small"
                          />
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Status"
                        secondary={
                          <Chip
                            label={profile.isActive ? 'Active' : 'Inactive'}
                            color={profile.isActive ? 'success' : 'default'}
                            size="small"
                          />
                        }
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Member Since"
                        secondary={new Date(profile.createdAt).toLocaleDateString()}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Last Login"
                        secondary={profile.lastLogin 
                          ? new Date(profile.lastLogin).toLocaleDateString()
                          : 'Never'
                        }
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Activity Tab */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            
            {profile.recentActivity && (
              <Grid container spacing={3}>
                {/* Courses */}
                {profile.recentActivity.courses && profile.recentActivity.courses.length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          <SchoolIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Recent Courses
                        </Typography>
                        <List dense>
                          {profile.recentActivity.courses.map((course) => (
                            <ListItem key={course.id}>
                              <ListItemText
                                primary={course.title}
                                secondary={`${course.category} • ${new Date(course.createdAt).toLocaleDateString()}`}
                              />
                              <Chip
                                label={course.status}
                                size="small"
                                color={course.status === 'published' ? 'success' : 'warning'}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* Research Projects */}
                {profile.recentActivity.researchProjects && profile.recentActivity.researchProjects.length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          <ScienceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Recent Research Projects
                        </Typography>
                        <List dense>
                          {profile.recentActivity.researchProjects.map((project) => (
                            <ListItem key={project.id}>
                              <ListItemText
                                primary={project.title}
                                secondary={`${project.field} • ${new Date(project.createdAt).toLocaleDateString()}`}
                              />
                              <Chip
                                label={project.status}
                                size="small"
                                color={project.status === 'active' ? 'success' : 'warning'}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {/* Collaborations */}
                {profile.recentActivity.collaborations && profile.recentActivity.collaborations.length > 0 && (
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          <GroupIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                          Recent Collaborations
                        </Typography>
                        <List dense>
                          {profile.recentActivity.collaborations.map((collab) => (
                            <ListItem key={collab.id}>
                              <ListItemText
                                primary={collab.title}
                                secondary={`${collab.type} • ${new Date(collab.createdAt).toLocaleDateString()}`}
                              />
                              <Chip
                                label={collab.status}
                                size="small"
                                color={collab.status === 'active' ? 'success' : 'warning'}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            )}

            {(!profile.recentActivity || 
              (!profile.recentActivity.courses?.length && 
               !profile.recentActivity.researchProjects?.length && 
               !profile.recentActivity.collaborations?.length)) && (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  No recent activity to display. Start creating courses, research projects, or collaborations to see your activity here.
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {/* Settings Tab */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Account Settings
            </Typography>
            
            <Grid container spacing={3}>
              {/* Notification Settings */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Notification Preferences
                    </Typography>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Email Notifications</InputLabel>
                      <Select
                        value="all"
                        label="Email Notifications"
                      >
                        <MenuItem value="all">All notifications</MenuItem>
                        <MenuItem value="important">Important only</MenuItem>
                        <MenuItem value="none">No notifications</MenuItem>
                      </Select>
                    </FormControl>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Course Updates</InputLabel>
                      <Select
                        value="enrolled"
                        label="Course Updates"
                      >
                        <MenuItem value="enrolled">Enrolled courses only</MenuItem>
                        <MenuItem value="all">All courses</MenuItem>
                        <MenuItem value="none">No updates</MenuItem>
                      </Select>
                    </FormControl>
                    <FormControl fullWidth>
                      <InputLabel>Research Updates</InputLabel>
                      <Select
                        value="collaborating"
                        label="Research Updates"
                      >
                        <MenuItem value="collaborating">Collaborating projects</MenuItem>
                        <MenuItem value="all">All projects</MenuItem>
                        <MenuItem value="none">No updates</MenuItem>
                      </Select>
                    </FormControl>
                  </CardContent>
                </Card>
              </Grid>

              {/* Privacy Settings */}
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Privacy Settings
                    </Typography>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Profile Visibility</InputLabel>
                      <Select
                        value="public"
                        label="Profile Visibility"
                      >
                        <MenuItem value="public">Public</MenuItem>
                        <MenuItem value="registered">Registered users only</MenuItem>
                        <MenuItem value="private">Private</MenuItem>
                      </Select>
                    </FormControl>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>Activity Visibility</InputLabel>
                      <Select
                        value="public"
                        label="Activity Visibility"
                      >
                        <MenuItem value="public">Public</MenuItem>
                        <MenuItem value="registered">Registered users only</MenuItem>
                        <MenuItem value="private">Private</MenuItem>
                      </Select>
                    </FormControl>
                    <FormControl fullWidth>
                      <InputLabel>Search Visibility</InputLabel>
                      <Select
                        value="public"
                        label="Search Visibility"
                      >
                        <MenuItem value="public">Searchable</MenuItem>
                        <MenuItem value="private">Not searchable</MenuItem>
                      </Select>
                    </FormControl>
                  </CardContent>
                </Card>
              </Grid>

              {/* Account Management */}
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Account Management
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={() => toast.info('Password change feature coming soon')}
                      >
                        Change Password
                      </Button>
                      <Button
                        variant="outlined"
                        color="secondary"
                        onClick={() => toast.info('Two-factor authentication coming soon')}
                      >
                        Enable 2FA
                      </Button>
                      <Button
                        variant="outlined"
                        color="warning"
                        onClick={() => toast.info('Account export feature coming soon')}
                      >
                        Export Data
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        onClick={() => toast.error('Account deletion is not available')}
                      >
                        Delete Account
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default Profile; 