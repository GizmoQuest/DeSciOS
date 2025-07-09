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
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Chip,
  LinearProgress,
  IconButton,
  Divider,
  Alert
} from '@mui/material';
import {
  School,
  Science,
  Group,
  Storage,
  Add,
  TrendingUp,
  Notifications,
  Person,
  CloudDownload,
  Timeline,
  AssignmentTurnedIn,
  Schedule
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useSocket } from '../context/SocketContext';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({
    courses: 0,
    research: 0,
    collaborations: 0,
    ipfsFiles: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [upcomingTasks, setUpcomingTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const { user } = useAuth();
  const { connected, onlineUsers } = useSocket();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsResponse, activityResponse] = await Promise.all([
        axios.get('/api/users/stats'),
        axios.get('/api/users/activity')
      ]);

      setStats(statsResponse.data);
      setRecentActivity(activityResponse.data.recentActivity || []);
      setUpcomingTasks(activityResponse.data.upcomingTasks || []);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'instructor':
        return 'warning';
      case 'researcher':
        return 'info';
      default:
        return 'default';
    }
  };

  const StatCard = ({ title, value, icon: Icon, color, onClick }) => (
    <Card 
      sx={{ 
        height: '100%', 
        cursor: onClick ? 'pointer' : 'default',
        '&:hover': onClick ? { transform: 'translateY(-2px)' } : {}
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Icon sx={{ color: `${color}.main`, mr: 1 }} />
          <Typography variant="h6" color="text.secondary">
            {title}
          </Typography>
        </Box>
        <Typography variant="h3" component="div">
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  const QuickActionCard = ({ title, description, icon: Icon, color, onClick }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Icon sx={{ color: `${color}.main`, mr: 1 }} />
          <Typography variant="h6">
            {title}
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small" onClick={onClick} startIcon={<Add />}>
          Create
        </Button>
      </CardActions>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
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

      {/* Welcome Section */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            src={user?.avatar}
            alt={user?.name}
            sx={{ width: 64, height: 64, mr: 2 }}
          >
            {user?.name?.charAt(0)}
          </Avatar>
          <Box>
            <Typography variant="h4" gutterBottom>
              {getGreeting()}, {user?.name}!
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={user?.role || 'Student'}
                color={getRoleColor(user?.role)}
                size="small"
              />
              <Chip
                label={user?.institution || 'No Institution'}
                variant="outlined"
                size="small"
              />
              <Box sx={{ display: 'flex', alignItems: 'center', ml: 2 }}>
                <Box
                  sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: connected ? 'success.main' : 'error.main',
                    mr: 1
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  {connected ? 'Connected' : 'Disconnected'}
                </Typography>
              </Box>
            </Box>
          </Box>
        </Box>
      </Paper>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Courses"
            value={stats.courses}
            icon={School}
            color="primary"
            onClick={() => navigate('/courses')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Research Projects"
            value={stats.research}
            icon={Science}
            color="info"
            onClick={() => navigate('/research')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Collaborations"
            value={stats.collaborations}
            icon={Group}
            color="success"
            onClick={() => navigate('/collaboration')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="IPFS Files"
            value={stats.ipfsFiles}
            icon={Storage}
            color="warning"
            onClick={() => navigate('/ipfs')}
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <QuickActionCard
            title="New Course"
            description="Create a new course for teaching and learning"
            icon={School}
            color="primary"
            onClick={() => navigate('/courses/create')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <QuickActionCard
            title="Research Project"
            description="Start a new research project and collaborate"
            icon={Science}
            color="info"
            onClick={() => navigate('/research/create')}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <QuickActionCard
            title="Collaboration"
            description="Create a collaborative workspace"
            icon={Group}
            color="success"
            onClick={() => navigate('/collaboration/create')}
          />
        </Grid>
      </Grid>

      {/* Content Grid */}
      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {recentActivity.length > 0 ? (
                recentActivity.map((activity, index) => (
                  <ListItem key={index} divider>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        <Timeline />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={activity.title}
                      secondary={activity.description}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {activity.timestamp}
                    </Typography>
                  </ListItem>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No recent activity
                </Typography>
              )}
            </List>
          </Paper>
        </Grid>

        {/* Upcoming Tasks */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Upcoming Tasks
            </Typography>
            <List>
              {upcomingTasks.length > 0 ? (
                upcomingTasks.map((task, index) => (
                  <ListItem key={index} divider>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'warning.main' }}>
                        <Schedule />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={task.title}
                      secondary={task.description}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {task.dueDate}
                    </Typography>
                  </ListItem>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No upcoming tasks
                </Typography>
              )}
            </List>
          </Paper>
        </Grid>

        {/* Online Users */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Online Users ({onlineUsers.length})
            </Typography>
            <List>
              {onlineUsers.slice(0, 5).map((user, index) => (
                <ListItem key={index} divider>
                  <ListItemAvatar>
                    <Avatar src={user.avatar} alt={user.name}>
                      {user.name?.charAt(0)}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={user.name}
                    secondary={user.role}
                  />
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: 'success.main'
                    }}
                  />
                </ListItem>
              ))}
              {onlineUsers.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  No users online
                </Typography>
              )}
            </List>
          </Paper>
        </Grid>

        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Real-time Connection</Typography>
                <Chip
                  label={connected ? 'Connected' : 'Disconnected'}
                  color={connected ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">IPFS Network</Typography>
                <Chip
                  label="Connected"
                  color="success"
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Database</Typography>
                <Chip
                  label="Operational"
                  color="success"
                  size="small"
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard; 