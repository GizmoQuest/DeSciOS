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
  Link
} from '@mui/material';
import {
  School as SchoolIcon,
  AccessTime as AccessTimeIcon,
  Person as PersonIcon,
  Download as DownloadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, api } = useAuth();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [enrolled, setEnrolled] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    fetchCourse();
  }, [id]);

  const fetchCourse = async () => {
    try {
      const response = await api.get(`/courses/${id}`);
      setCourse(response.data.course || response.data);
      
      // Check if user is enrolled
      if (user && response.data.enrollment) {
        setEnrolled(true);
      }
    } catch (error) {
      console.error('Error fetching course:', error);
      setError('Failed to load course details');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    try {
      await api.post(`/courses/${id}/enroll`);
      setEnrolled(true);
      toast.success('Successfully enrolled in course!');
    } catch (error) {
      console.error('Error enrolling:', error);
      toast.error('Failed to enroll in course');
    }
  };

  const handleUnenroll = async () => {
    try {
      await api.delete(`/courses/${id}/enroll`);
      setEnrolled(false);
      toast.success('Successfully unenrolled from course');
    } catch (error) {
      console.error('Error unenrolling:', error);
      toast.error('Failed to unenroll from course');
    }
  };

  const handleDelete = async () => {
    try {
      await api.delete(`/courses/${id}`);
      toast.success('Course deleted successfully');
      navigate('/courses');
    } catch (error) {
      console.error('Error deleting course:', error);
      toast.error('Failed to delete course');
    } finally {
      setDeleteDialogOpen(false);
    }
  };

  const downloadResource = async (resource) => {
    try {
      const response = await api.get(`/ipfs/download/${resource.ipfsHash}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', resource.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${resource.name}`);
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'success';
      case 'intermediate': return 'warning';
      case 'advanced': return 'error';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'success';
      case 'draft': return 'warning';
      case 'archived': return 'error';
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

  if (error || !course) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          {error || 'Course not found'}
        </Alert>
      </Container>
    );
  }

  const isInstructor = user && course.instructorId === user.id;
  const canEdit = isInstructor || user?.role === 'admin';

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              {course.title}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip 
                label={course.difficulty} 
                color={getDifficultyColor(course.difficulty)}
                size="small"
              />
              <Chip 
                label={course.status} 
                color={getStatusColor(course.status)}
                size="small"
              />
              <Chip 
                label={course.isPublic ? 'Public' : 'Private'} 
                icon={course.isPublic ? <VisibilityIcon /> : <VisibilityOffIcon />}
                size="small"
              />
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            {canEdit && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => navigate(`/courses/${id}/edit`)}
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
            
            {user && !isInstructor && (
              <Button
                variant="contained"
                onClick={enrolled ? handleUnenroll : handleEnroll}
                color={enrolled ? 'error' : 'primary'}
              >
                {enrolled ? 'Unenroll' : 'Enroll'}
              </Button>
            )}
          </Box>
        </Box>

        {/* Course Info */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Typography variant="body1" paragraph>
              {course.description}
            </Typography>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Course Information
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <SchoolIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Category: {course.category}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PersonIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Instructor: {course.instructor?.username || 'Unknown'}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <AccessTimeIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2">
                    Duration: {course.syllabus?.reduce((total, item) => total + (parseInt(item.duration) || 0), 0)} hours
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Syllabus" />
            <Tab label="Resources" />
            <Tab label="Students" />
          </Tabs>
        </Box>

        {/* Syllabus Tab */}
        {activeTab === 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Course Syllabus
            </Typography>
            
            {course.syllabus && course.syllabus.length > 0 ? (
              <List>
                {course.syllabus.map((item, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="subtitle1">
                              Module {index + 1}: {item.title}
                            </Typography>
                            <Chip 
                              label={`${item.duration || 0} hours`} 
                              size="small" 
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={item.description}
                      />
                    </ListItem>
                    {index < course.syllabus.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No syllabus available for this course.
              </Typography>
            )}
          </Box>
        )}

        {/* Resources Tab */}
        {activeTab === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Course Resources
            </Typography>
            
            {course.resources && course.resources.length > 0 ? (
              <Grid container spacing={2}>
                {course.resources.map((resource, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card>
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          {resource.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {(resource.size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<DownloadIcon />}
                          onClick={() => downloadResource(resource)}
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
                No resources available for this course.
              </Typography>
            )}
          </Box>
        )}

        {/* Students Tab */}
        {activeTab === 2 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Enrolled Students
            </Typography>
            
            {course.enrollments && course.enrollments.length > 0 ? (
              <List>
                {course.enrollments.map((enrollment, index) => (
                  <ListItem key={index}>
                    <Avatar sx={{ mr: 2 }}>
                      {enrollment.student?.username?.charAt(0)?.toUpperCase() || 'U'}
                    </Avatar>
                    <ListItemText
                      primary={enrollment.student?.username || 'Unknown User'}
                      secondary={`Enrolled: ${new Date(enrollment.createdAt).toLocaleDateString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No students enrolled in this course.
              </Typography>
            )}
          </Box>
        )}
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Course</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{course.title}"? This action cannot be undone.
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

export default CourseDetail; 