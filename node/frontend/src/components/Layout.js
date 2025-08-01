import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  School,
  Science,
  Group,
  Person,
  Storage,
  Settings,
  Logout,
  People,
  Notifications,
  AccountCircle,
  DesktopMac
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';
import { useSocket } from '../context/SocketContext';

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: Dashboard, path: '/dashboard' },
  { text: 'DeSciOS', icon: DesktopMac, path: '/descios' },
  { text: 'Courses', icon: School, path: '/courses' },
  { text: 'Research', icon: Science, path: '/research' },
  { text: 'Collaboration', icon: Group, path: '/collaboration' },
  { text: 'Users', icon: People, path: '/users' },
  { text: 'IPFS Manager', icon: Storage, path: '/ipfs' },
  { text: 'Profile', icon: Person, path: '/profile' },
  { text: 'Settings', icon: Settings, path: '/settings' },
];

function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchorEl, setNotificationAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState(() => {
    // Load notifications from localStorage on component mount
    const savedNotifications = localStorage.getItem('descios-notifications');
    if (savedNotifications) {
      return JSON.parse(savedNotifications);
    }
    // Default notifications if none saved
    return [
      {
        id: 1,
        title: 'Welcome to DeSciOS Academic Platform!',
        message: 'Your account has been successfully set up.',
        time: '2 hours ago',
        read: false
      },
      {
        id: 2,
        title: 'Database initialized successfully',
        message: 'Your academic platform database is ready.',
        time: '1 hour ago',
        read: false
      },
      {
        id: 3,
        title: 'IPFS connection established',
        message: 'Decentralized storage is now available.',
        time: '30 minutes ago',
        read: false
      },
      {
        id: 4,
        title: 'Ready to create your first course',
        message: 'Start building your academic content.',
        time: 'Just now',
        read: false
      }
    ];
  });
  const { user, logout } = useAuth();
  const { connected, onlineUsers } = useSocket();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleClose();
    await logout();
    navigate('/login');
  };

  const handleProfileClick = () => {
    handleClose();
    navigate('/profile');
  };

  const handleSettingsClick = () => {
    handleClose();
    navigate('/settings');
  };

  const handleNotificationMenu = (event) => {
    setNotificationAnchorEl(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationAnchorEl(null);
  };

  const markNotificationAsRead = (notificationId) => {
    setNotifications(prev => {
      const updated = prev.map(notification => 
        notification.id === notificationId 
          ? { ...notification, read: true }
          : notification
      );
      // Save to localStorage
      localStorage.setItem('descios-notifications', JSON.stringify(updated));
      return updated;
    });
  };

  const markAllAsRead = () => {
    setNotifications(prev => {
      const updated = prev.map(notification => ({ ...notification, read: true }));
      // Save to localStorage
      localStorage.setItem('descios-notifications', JSON.stringify(updated));
      return updated;
    });
    setNotificationAnchorEl(null);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

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

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          DeSciOS Academic
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>
                <item.icon />
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Connection Status
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: connected ? 'success.main' : 'error.main',
              mr: 1
            }}
          />
          <Typography variant="body2" color="text.secondary">
            {connected ? 'Connected' : 'Disconnected'}
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          {onlineUsers.length} users online
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Academic Platform
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Chip
              label={user?.role || 'Student'}
              color={getRoleColor(user?.role)}
              size="small"
            />
            
            <IconButton 
              color="inherit"
              onClick={handleNotificationMenu}
              aria-controls="notification-menu"
              aria-haspopup="true"
            >
              <Badge badgeContent={unreadCount} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            
            <Menu
              id="notification-menu"
              anchorEl={notificationAnchorEl}
              open={Boolean(notificationAnchorEl)}
              onClose={handleNotificationClose}
              PaperProps={{
                sx: {
                  width: 320,
                  maxHeight: 400
                }
              }}
            >
              <MenuItem sx={{ borderBottom: '1px solid #eee', backgroundColor: '#f8f9fa' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                  Notifications ({notifications.length})
                </Typography>
              </MenuItem>
              {notifications.map((notification) => (
                <MenuItem 
                  key={notification.id}
                  onClick={() => markNotificationAsRead(notification.id)}
                  sx={{ 
                    backgroundColor: notification.read ? 'transparent' : '#f0f8ff',
                    '&:hover': {
                      backgroundColor: notification.read ? '#f5f5f5' : '#e6f3ff'
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '100%' }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: notification.read ? 'normal' : 'medium',
                        color: notification.read ? 'text.secondary' : 'text.primary'
                      }}
                    >
                      {notification.title}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {notification.message}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {notification.time}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
              <MenuItem sx={{ borderTop: '1px solid #eee', backgroundColor: '#f8f9fa' }}>
                <Typography 
                  variant="body2" 
                  color="primary" 
                  sx={{ 
                    cursor: 'pointer', 
                    textAlign: 'center', 
                    width: '100%' 
                  }}
                  onClick={markAllAsRead}
                >
                  Mark all as read
                </Typography>
              </MenuItem>
            </Menu>
            
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar
                src={user?.avatar}
                alt={user?.name}
                sx={{ width: 32, height: 32 }}
              >
                {user?.name?.charAt(0)}
              </Avatar>
            </IconButton>
            
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleProfileClick}>
                <ListItemIcon>
                  <AccountCircle fontSize="small" />
                </ListItemIcon>
                Profile
              </MenuItem>
              <MenuItem onClick={handleSettingsClick}>
                <ListItemIcon>
                  <Settings fontSize="small" />
                </ListItemIcon>
                Settings
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <Logout fontSize="small" />
                </ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}

export default Layout; 