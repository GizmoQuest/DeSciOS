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
  Switch,
  FormControlLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
  Storage as StorageIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const Settings = () => {
  const { user, api } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [settings, setSettings] = useState({
    account: {
      emailNotifications: true,
      pushNotifications: false,
      marketingEmails: false,
      language: 'en',
      timezone: 'UTC'
    },
    privacy: {
      profileVisibility: 'public',
      showEmail: false,
      showLastSeen: true,
      allowMessages: true
    },
    appearance: {
      theme: 'light',
      compactMode: false,
      showAnimations: true
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 30,
      requirePasswordChange: false
    }
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      // In a real app, you would fetch user settings from the backend
      // For now, we'll use localStorage or default settings
      const savedSettings = localStorage.getItem('user-settings');
      if (savedSettings) {
        setSettings(JSON.parse(savedSettings));
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      // In a real app, you would save settings to the backend
      localStorage.setItem('user-settings', JSON.stringify(settings));
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const resetSettings = () => {
    if (window.confirm('Are you sure you want to reset all settings to default?')) {
      setSettings({
        account: {
          emailNotifications: true,
          pushNotifications: false,
          marketingEmails: false,
          language: 'en',
          timezone: 'UTC'
        },
        privacy: {
          profileVisibility: 'public',
          showEmail: false,
          showLastSeen: true,
          allowMessages: true
        },
        appearance: {
          theme: 'light',
          compactMode: false,
          showAnimations: true
        },
        security: {
          twoFactorAuth: false,
          sessionTimeout: 30,
          requirePasswordChange: false
        }
      });
      localStorage.removeItem('user-settings');
      toast.success('Settings reset to default');
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

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Settings
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={resetSettings}
            >
              Reset to Default
            </Button>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={saveSettings}
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Account" />
            <Tab label="Privacy" />
            <Tab label="Appearance" />
            <Tab label="Security" />
          </Tabs>
        </Box>

        {/* Account Settings Tab */}
        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <NotificationsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Notifications
                  </Typography>
                  
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Email Notifications"
                        secondary="Receive notifications via email"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.account.emailNotifications}
                          onChange={(e) => handleSettingChange('account', 'emailNotifications', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText
                        primary="Push Notifications"
                        secondary="Receive browser push notifications"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.account.pushNotifications}
                          onChange={(e) => handleSettingChange('account', 'pushNotifications', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText
                        primary="Marketing Emails"
                        secondary="Receive promotional and marketing emails"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.account.marketingEmails}
                          onChange={(e) => handleSettingChange('account', 'marketingEmails', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <LanguageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Language & Region
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={settings.account.language}
                      onChange={(e) => handleSettingChange('account', 'language', e.target.value)}
                      label="Language"
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Español</MenuItem>
                      <MenuItem value="fr">Français</MenuItem>
                      <MenuItem value="de">Deutsch</MenuItem>
                      <MenuItem value="zh">中文</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <FormControl fullWidth>
                    <InputLabel>Timezone</InputLabel>
                    <Select
                      value={settings.account.timezone}
                      onChange={(e) => handleSettingChange('account', 'timezone', e.target.value)}
                      label="Timezone"
                    >
                      <MenuItem value="UTC">UTC</MenuItem>
                      <MenuItem value="EST">Eastern Time</MenuItem>
                      <MenuItem value="PST">Pacific Time</MenuItem>
                      <MenuItem value="GMT">GMT</MenuItem>
                      <MenuItem value="CET">Central European Time</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Privacy Settings Tab */}
        {activeTab === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <VisibilityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Profile Visibility
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Profile Visibility</InputLabel>
                    <Select
                      value={settings.privacy.profileVisibility}
                      onChange={(e) => handleSettingChange('privacy', 'profileVisibility', e.target.value)}
                      label="Profile Visibility"
                    >
                      <MenuItem value="public">Public</MenuItem>
                      <MenuItem value="private">Private</MenuItem>
                      <MenuItem value="friends">Friends Only</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Show Email Address"
                        secondary="Make your email visible to other users"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.privacy.showEmail}
                          onChange={(e) => handleSettingChange('privacy', 'showEmail', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText
                        primary="Show Last Seen"
                        secondary="Show when you were last active"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.privacy.showLastSeen}
                          onChange={(e) => handleSettingChange('privacy', 'showLastSeen', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText
                        primary="Allow Messages"
                        secondary="Allow other users to send you messages"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.privacy.allowMessages}
                          onChange={(e) => handleSettingChange('privacy', 'allowMessages', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Appearance Settings Tab */}
        {activeTab === 2 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <PaletteIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Theme & Display
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Theme</InputLabel>
                    <Select
                      value={settings.appearance.theme}
                      onChange={(e) => handleSettingChange('appearance', 'theme', e.target.value)}
                      label="Theme"
                    >
                      <MenuItem value="light">Light</MenuItem>
                      <MenuItem value="dark">Dark</MenuItem>
                      <MenuItem value="auto">Auto (System)</MenuItem>
                    </Select>
                  </FormControl>
                  
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Compact Mode"
                        secondary="Use a more compact layout"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.appearance.compactMode}
                          onChange={(e) => handleSettingChange('appearance', 'compactMode', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText
                        primary="Show Animations"
                        secondary="Enable interface animations"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.appearance.showAnimations}
                          onChange={(e) => handleSettingChange('appearance', 'showAnimations', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Security Settings Tab */}
        {activeTab === 3 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Security Settings
                  </Typography>
                  
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Two-Factor Authentication"
                        secondary="Add an extra layer of security to your account"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.security.twoFactorAuth}
                          onChange={(e) => handleSettingChange('security', 'twoFactorAuth', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    <ListItem>
                      <ListItemText
                        primary="Require Password Change"
                        secondary="Force password change on next login"
                      />
                      <ListItemSecondaryAction>
                        <Switch
                          edge="end"
                          checked={settings.security.requirePasswordChange}
                          onChange={(e) => handleSettingChange('security', 'requirePasswordChange', e.target.checked)}
                        />
                      </ListItemSecondaryAction>
                    </ListItem>
                  </List>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <FormControl fullWidth>
                    <InputLabel>Session Timeout</InputLabel>
                    <Select
                      value={settings.security.sessionTimeout}
                      onChange={(e) => handleSettingChange('security', 'sessionTimeout', e.target.value)}
                      label="Session Timeout"
                    >
                      <MenuItem value={15}>15 minutes</MenuItem>
                      <MenuItem value={30}>30 minutes</MenuItem>
                      <MenuItem value={60}>1 hour</MenuItem>
                      <MenuItem value={120}>2 hours</MenuItem>
                      <MenuItem value={0}>Never</MenuItem>
                    </Select>
                  </FormControl>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Data & Storage
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Manage your data and storage preferences
                  </Typography>
                  
                  <Button
                    variant="outlined"
                    color="warning"
                    fullWidth
                    sx={{ mb: 2 }}
                  >
                    Export My Data
                  </Button>
                  
                  <Button
                    variant="outlined"
                    color="error"
                    fullWidth
                  >
                    Delete Account
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Paper>
    </Container>
  );
};

export default Settings; 