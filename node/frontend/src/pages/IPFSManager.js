import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  TextField,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  DataObject as DataObjectIcon,
  Link as LinkIcon,
  Visibility as VisibilityIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

const IPFSManager = () => {
  const { api } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [files, setFiles] = useState([]);
  const [pinnedFiles, setPinnedFiles] = useState([]);
  const [ipfsStats, setIpfsStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchIPFSData();
  }, []);

  const fetchIPFSData = async () => {
    try {
      setLoading(true);
      
      // Fetch IPFS stats
      const statsResponse = await api.get('/ipfs/stats');
      setIpfsStats(statsResponse.data);
      
      // Fetch pinned files
      const pinnedResponse = await api.get('/ipfs/pinned');
      setPinnedFiles(pinnedResponse.data.pinned || []);
      
      // Fetch recent files
      const filesResponse = await api.get('/ipfs/files');
      setFiles(filesResponse.data.files || []);
      
    } catch (error) {
      console.error('Error fetching IPFS data:', error);
      setError('Failed to load IPFS data');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;
    
    setUploading(true);
    try {
      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);
        
        await api.post('/ipfs/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      }
      
      toast.success(`${selectedFiles.length} file(s) uploaded successfully`);
      setUploadDialogOpen(false);
      setSelectedFiles([]);
      fetchIPFSData();
      
    } catch (error) {
      console.error('Error uploading files:', error);
      toast.error('Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  const downloadFile = async (file) => {
    try {
      const response = await api.get(`/ipfs/download/${file.hash}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', file.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${file.name}`);
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
  };

  const copyHash = (hash) => {
    navigator.clipboard.writeText(hash);
    toast.success('Hash copied to clipboard');
  };

  const pinFile = async (hash) => {
    try {
      await api.post(`/ipfs/pin/${hash}`);
      toast.success('File pinned successfully');
      fetchIPFSData();
    } catch (error) {
      console.error('Error pinning file:', error);
      toast.error('Failed to pin file');
    }
  };

  const unpinFile = async (hash) => {
    try {
      await api.delete(`/ipfs/pin/${hash}`);
      toast.success('File unpinned successfully');
      fetchIPFSData();
    } catch (error) {
      console.error('Error unpinning file:', error);
      toast.error('Failed to unpin file');
    }
  };

  const deleteFile = async (hash) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;
    
    try {
      await api.delete(`/ipfs/files/${hash}`);
      toast.success('File deleted successfully');
      fetchIPFSData();
    } catch (error) {
      console.error('Error deleting file:', error);
      toast.error('Failed to delete file');
    }
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredFiles = files.filter(file => 
    file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    file.hash.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredPinnedFiles = pinnedFiles.filter(file => 
    file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    file.hash.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            IPFS File Manager
          </Typography>
          
          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Upload Files
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* IPFS Statistics */}
        {ipfsStats && (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <StorageIcon sx={{ mr: 2, color: 'primary.main' }} />
                    <Box>
                      <Typography variant="h4">{formatBytes(ipfsStats.repoSize || 0)}</Typography>
                      <Typography variant="body2" color="text.secondary">Repository Size</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <DataObjectIcon sx={{ mr: 2, color: 'secondary.main' }} />
                    <Box>
                      <Typography variant="h4">{ipfsStats.numObjects || 0}</Typography>
                      <Typography variant="body2" color="text.secondary">Total Objects</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <LinkIcon sx={{ mr: 2, color: 'success.main' }} />
                    <Box>
                      <Typography variant="h4">{pinnedFiles.length}</Typography>
                      <Typography variant="body2" color="text.secondary">Pinned Files</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <NetworkIcon sx={{ mr: 2, color: 'info.main' }} />
                    <Box>
                      <Typography variant="h4">{ipfsStats.peers || 0}</Typography>
                      <Typography variant="body2" color="text.secondary">Connected Peers</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Search */}
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            placeholder="Search files by name or hash..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
        </Box>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label={`All Files (${files.length})`} />
            <Tab label={`Pinned Files (${pinnedFiles.length})`} />
          </Tabs>
        </Box>

        {/* All Files Tab */}
        {activeTab === 0 && (
          <Box>
            {filteredFiles.length === 0 ? (
              <Box textAlign="center" py={4}>
                <DataObjectIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No files found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {searchTerm ? 'Try adjusting your search' : 'Upload your first file to get started'}
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>File</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>Hash</TableCell>
                      <TableCell>Uploaded</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredFiles.map((file) => (
                      <TableRow key={file.hash}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <DataObjectIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body2">
                              {file.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{formatBytes(file.size)}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                              {file.hash.substring(0, 12)}...
                            </Typography>
                            <IconButton size="small" onClick={() => copyHash(file.hash)}>
                              <CopyIcon />
                            </IconButton>
                          </Box>
                        </TableCell>
                        <TableCell>
                          {new Date(file.uploadedAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton size="small" onClick={() => downloadFile(file)}>
                              <DownloadIcon />
                            </IconButton>
                            <IconButton size="small" onClick={() => pinFile(file.hash)}>
                              <LinkIcon />
                            </IconButton>
                            <IconButton size="small" color="error" onClick={() => deleteFile(file.hash)}>
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}

        {/* Pinned Files Tab */}
        {activeTab === 1 && (
          <Box>
            {filteredPinnedFiles.length === 0 ? (
              <Box textAlign="center" py={4}>
                <LinkIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No pinned files
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Pin important files to keep them permanently available
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>File</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>Hash</TableCell>
                      <TableCell>Pinned</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredPinnedFiles.map((file) => (
                      <TableRow key={file.hash}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <LinkIcon sx={{ mr: 1, color: 'success.main' }} />
                            <Typography variant="body2">
                              {file.name}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{formatBytes(file.size)}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                              {file.hash.substring(0, 12)}...
                            </Typography>
                            <IconButton size="small" onClick={() => copyHash(file.hash)}>
                              <CopyIcon />
                            </IconButton>
                          </Box>
                        </TableCell>
                        <TableCell>
                          {new Date(file.pinnedAt).toLocaleDateString()}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <IconButton size="small" onClick={() => downloadFile(file)}>
                              <DownloadIcon />
                            </IconButton>
                            <IconButton size="small" color="warning" onClick={() => unpinFile(file.hash)}>
                              <LinkIcon />
                            </IconButton>
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </Paper>

      {/* Upload Dialog */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Files to IPFS</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
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
                fullWidth
                sx={{ mb: 2 }}
              >
                Select Files
              </Button>
            </label>
            
            {selectedFiles.length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Selected Files:
                </Typography>
                {selectedFiles.map((file, index) => (
                  <Chip
                    key={index}
                    label={`${file.name} (${formatBytes(file.size)})`}
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={uploadFiles} 
            variant="contained" 
            disabled={selectedFiles.length === 0 || uploading}
            startIcon={uploading ? <CircularProgress size={20} /> : null}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default IPFSManager; 