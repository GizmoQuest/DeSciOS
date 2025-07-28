import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Avatar,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Menu,
  ListItemIcon,
  ListItemText,
  Alert,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Search,
  Add,
  FilterList,
  MoreVert,
  Edit,
  Delete,
  Visibility,
  School,
  Person,
  Schedule,
  Star,
  StarBorder,
  Group
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';
import { format } from 'date-fns';

function Courses() {
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [enrollDialog, setEnrollDialog] = useState(false);
  const [enrollingCourse, setEnrollingCourse] = useState(null);

  const { user, api } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchCourses();
  }, []);

  useEffect(() => {
    filterCourses();
  }, [courses, searchTerm, filterCategory, filterStatus]);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await api.get('/courses');
      setCourses(response.data.courses || []);
    } catch (err) {
      setError('Failed to fetch courses');
      console.error('Courses error:', err);
    } finally {
      setLoading(false);
    }
  };

  const filterCourses = () => {
    let filtered = courses;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(course =>
        course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        course.instructor.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Category filter
    if (filterCategory !== 'all') {
      filtered = filtered.filter(course => course.category === filterCategory);
    }

    // Status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(course => course.status === filterStatus);
    }

    setFilteredCourses(filtered);
  };

  const handleMenuClick = (event, course) => {
    setAnchorEl(event.currentTarget);
    setSelectedCourse(course);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedCourse(null);
  };

  const handleEnrollClick = (course) => {
    setEnrollingCourse(course);
    setEnrollDialog(true);
  };

  const handleEnrollConfirm = async () => {
    try {
      await axios.post(`/api/courses/${enrollingCourse.id}/enroll`);
      setEnrollDialog(false);
      setEnrollingCourse(null);
      fetchCourses(); // Refresh courses
    } catch (err) {
      setError('Failed to enroll in course');
      console.error('Enrollment error:', err);
    }
  };

  const handleUnenroll = async (courseId) => {
    try {
      await axios.delete(`/api/courses/${courseId}/enroll`);
      fetchCourses(); // Refresh courses
    } catch (err) {
      setError('Failed to unenroll from course');
      console.error('Unenrollment error:', err);
    }
  };

  const isEnrolled = (course) => {
    return course.students?.some(student => student.id === user?.id);
  };

  const isInstructor = (course) => {
    return course.instructor.id === user?.id;
  };

  const canEnroll = (course) => {
    return !isEnrolled(course) && !isInstructor(course) && course.status === 'active';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'default';
      default:
        return 'default';
    }
  };

  const CourseCard = ({ course }) => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" component="h2" sx={{ flexGrow: 1 }}>
            {course.title}
          </Typography>
          <IconButton
            size="small"
            onClick={(e) => handleMenuClick(e, course)}
          >
            <MoreVert />
          </IconButton>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {course.description}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            src={course.instructor.avatar}
            alt={course.instructor.name}
            sx={{ width: 32, height: 32, mr: 1 }}
          >
            {course.instructor.name?.charAt(0)}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {course.instructor.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Instructor
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <Chip
            label={course.category}
            size="small"
            color="primary"
            variant="outlined"
          />
          <Chip
            label={course.status}
            size="small"
            color={getStatusColor(course.status)}
          />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Group sx={{ fontSize: 16, mr: 0.5 }} />
            <Typography variant="caption">
              {course.students?.length || 0} students
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Schedule sx={{ fontSize: 16, mr: 0.5 }} />
            <Typography variant="caption">
              {format(new Date(course.createdAt), 'MMM dd, yyyy')}
            </Typography>
          </Box>
        </Box>

        {course.progress && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Progress: {course.progress}%
            </Typography>
            <Box sx={{ width: '100%', height: 4, bgcolor: 'grey.300', borderRadius: 2, mt: 0.5 }}>
              <Box
                sx={{
                  width: `${course.progress}%`,
                  height: '100%',
                  bgcolor: 'primary.main',
                  borderRadius: 2
                }}
              />
            </Box>
          </Box>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Button
          size="small"
          onClick={() => navigate(`/courses/${course.id}`)}
          startIcon={<Visibility />}
        >
          View
        </Button>
        
        {canEnroll(course) && (
          <Button
            size="small"
            variant="contained"
            onClick={() => handleEnrollClick(course)}
          >
            Enroll
          </Button>
        )}
        
        {isEnrolled(course) && !isInstructor(course) && (
          <Button
            size="small"
            variant="outlined"
            onClick={() => handleUnenroll(course.id)}
          >
            Unenroll
          </Button>
        )}
        
        {isInstructor(course) && (
          <Button
            size="small"
            variant="outlined"
            onClick={() => navigate(`/courses/${course.id}/edit`)}
            startIcon={<Edit />}
          >
            Edit
          </Button>
        )}
      </CardActions>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Typography>Loading courses...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Courses
        </Typography>
        {(user?.role === 'instructor' || user?.role === 'admin') && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/courses/create')}
          >
            Create Course
          </Button>
        )}
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search courses..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ minWidth: 200 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              label="Category"
            >
              <MenuItem value="all">All Categories</MenuItem>
              <MenuItem value="science">Science</MenuItem>
              <MenuItem value="technology">Technology</MenuItem>
              <MenuItem value="mathematics">Mathematics</MenuItem>
              <MenuItem value="research">Research</MenuItem>
              <MenuItem value="other">Other</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="archived">Archived</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>

      {/* Courses Grid */}
      <Grid container spacing={3}>
        {filteredCourses.length > 0 ? (
          filteredCourses.map((course) => (
            <Grid item xs={12} sm={6} md={4} key={course.id}>
              <CourseCard course={course} />
            </Grid>
          ))
        ) : (
          <Grid item xs={12}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No courses found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {searchTerm || filterCategory !== 'all' || filterStatus !== 'all'
                  ? 'Try adjusting your filters'
                  : 'No courses have been created yet'}
              </Typography>
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          navigate(`/courses/${selectedCourse?.id}`);
          handleMenuClose();
        }}>
          <ListItemIcon>
            <Visibility fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Course</ListItemText>
        </MenuItem>
        
        {selectedCourse && isInstructor(selectedCourse) && (
          <MenuItem onClick={() => {
            navigate(`/courses/${selectedCourse.id}/edit`);
            handleMenuClose();
          }}>
            <ListItemIcon>
              <Edit fontSize="small" />
            </ListItemIcon>
            <ListItemText>Edit Course</ListItemText>
          </MenuItem>
        )}
      </Menu>

      {/* Enrollment Dialog */}
      <Dialog open={enrollDialog} onClose={() => setEnrollDialog(false)}>
        <DialogTitle>Enroll in Course</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to enroll in "{enrollingCourse?.title}"?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEnrollDialog(false)}>Cancel</Button>
          <Button onClick={handleEnrollConfirm} variant="contained">
            Enroll
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Courses; 