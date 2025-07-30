const express = require('express');
const multer = require('multer');
const { body, validationResult } = require('express-validator');
const { authenticateToken } = require('../middleware/auth');
const { ipfsService } = require('../services/ipfs');
const { Document } = require('../services/database');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ 
  storage,
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
});

// Get IPFS node status
router.get('/status', async (req, res) => {
  try {
    const stats = await ipfsService.getStats();
    const isConnected = ipfsService.isConnectedToIPFS();
    
    res.json({
      connected: isConnected,
      node: stats,
      gateway: 'http://localhost:8080',
      api: 'http://localhost:5001'
    });
  } catch (error) {
    console.error('Error fetching IPFS status:', error);
    res.status(500).json({ error: 'Failed to fetch IPFS status' });
  }
});

// Get IPFS statistics
router.get('/stats', async (req, res) => {
  try {
    const stats = await ipfsService.getStats();
    const isConnected = ipfsService.isConnectedToIPFS();
    
    res.json({
      repoSize: stats.repoSize || 0,
      numObjects: stats.numObjects || 0,
      peers: stats.peers || 0,
      connected: isConnected
    });
  } catch (error) {
    console.error('Error fetching IPFS stats:', error);
    res.status(500).json({ error: 'Failed to fetch IPFS stats' });
  }
});

// Get all files (documents)
router.get('/files', authenticateToken, async (req, res) => {
  try {
    const { limit = 50, offset = 0 } = req.query;
    
    const documents = await Document.findAndCountAll({
      where: { uploaderId: req.user.userId },
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    const files = documents.rows.map(doc => ({
      hash: doc.ipfsHash,
      name: doc.filename,
      size: doc.size,
      uploadedAt: doc.createdAt,
      pinned: doc.metadata?.pinned || false
    }));

    res.json({
      files,
      total: documents.count,
      hasMore: documents.count > parseInt(offset) + parseInt(limit)
    });
  } catch (error) {
    console.error('Error fetching files:', error);
    res.status(500).json({ error: 'Failed to fetch files' });
  }
});

// Get pinned files
router.get('/pinned', authenticateToken, async (req, res) => {
  try {
    const documents = await Document.findAll({
      where: { 
        uploaderId: req.user.userId
      },
      order: [['createdAt', 'DESC']]
    });

    // Filter documents that are pinned
    const pinnedFiles = documents
      .filter(doc => doc.metadata && doc.metadata.pinned === true)
      .map(doc => ({
        hash: doc.ipfsHash,
        name: doc.filename,
        size: doc.size,
        pinnedAt: doc.metadata.pinnedAt || doc.updatedAt,
        uploadedAt: doc.createdAt
      }));

    res.json({
      pinned: pinnedFiles
    });
  } catch (error) {
    console.error('Error fetching pinned files:', error);
    res.status(500).json({ error: 'Failed to fetch pinned files' });
  }
});

// Add data to IPFS
router.post('/add', authenticateToken, [
  body('data').exists(),
  body('pin').optional().isBoolean(),
  body('metadata').optional().isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { data, pin = true, metadata = {} } = req.body;

    const result = await ipfsService.storeAcademicData(data, {
      ...metadata,
      author: req.user.userId,
      pin
    });

    res.json({
      message: 'Data added to IPFS successfully',
      hash: result.hash,
      gateway_url: result.gateway_url,
      timestamp: result.timestamp
    });
  } catch (error) {
    console.error('Error adding data to IPFS:', error);
    res.status(500).json({ error: 'Failed to add data to IPFS' });
  }
});

// Get data from IPFS
router.get('/get/:hash', async (req, res) => {
  try {
    const { hash } = req.params;
    const { format = 'json' } = req.query;

    let data;
    if (format === 'raw') {
      data = await ipfsService.getData(hash);
      res.send(data);
    } else if (format === 'string') {
      data = await ipfsService.getDataAsString(hash);
      res.send(data);
    } else {
      data = await ipfsService.retrieveAcademicData(hash);
      res.json(data);
    }
  } catch (error) {
    console.error('Error getting data from IPFS:', error);
    res.status(500).json({ error: 'Failed to get data from IPFS' });
  }
});

// Download file from IPFS
router.get('/download/:hash', authenticateToken, async (req, res) => {
  try {
    const { hash } = req.params;

    // Try to find the document in the database
    let document = await Document.findOne({ where: { ipfsHash: hash } });

    // If not found, use generic headers
    let filename = document ? document.filename : `${hash}`;
    let mimeType = document ? document.mimeType : 'application/octet-stream';

    // Get file data from IPFS
    const fileData = await ipfsService.getData(hash);

    // Check if the data is a JSON document with base64 content (old format) or raw binary (new format)
    let binaryData;
    try {
      const jsonData = JSON.parse(fileData.toString());
      if (jsonData.content) {
        // Old format: JSON document with base64 content
        binaryData = Buffer.from(jsonData.content, 'base64');
      } else {
        // Raw binary data
        binaryData = fileData;
      }
    } catch (error) {
      // Not JSON, treat as raw binary data (new format)
      binaryData = fileData;
    }

    res.setHeader('Content-Type', mimeType);
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Length', binaryData.length);

    res.send(binaryData);
  } catch (error) {
    console.error('Error downloading file:', error);
    res.status(500).json({ error: 'Failed to download file' });
  }
});

// Upload file to IPFS
router.post('/upload', authenticateToken, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { buffer, originalname, mimetype, size } = req.file;
    const { pin = true, metadata = {} } = req.body;

    // Store binary file directly
    const result = await ipfsService.storeBinaryFile(
      originalname,
      buffer,
      {
        author: req.user.userId,
        mimeType: mimetype,
        size,
        ...metadata
      }
    );

    // Store in database
    const document = await Document.create({
      filename: originalname,
      size,
      mimeType: mimetype,
      ipfsHash: result.hash,
      uploaderId: req.user.userId,
      metadata: {
        ...metadata,
        version: result.version
      }
    });

    res.json({
      message: 'File uploaded to IPFS successfully',
      document,
      ipfs: {
        hash: result.hash,
        gateway_url: result.gateway_url,
        version: result.version
      }
    });
  } catch (error) {
    console.error('Error uploading file to IPFS:', error);
    res.status(500).json({ error: 'Failed to upload file to IPFS' });
  }
});

// Pin content to IPFS
router.post('/pin/:hash', authenticateToken, async (req, res) => {
  try {
    const { hash } = req.params;
    
    // Find the document in database
    const document = await Document.findOne({
      where: { 
        ipfsHash: hash,
        uploaderId: req.user.userId
      }
    });

    if (!document) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Pin in IPFS
    await ipfsService.pinContent(hash);
    
    // Update database metadata
    await document.update({
      metadata: {
        ...document.metadata,
        pinned: true,
        pinnedAt: new Date().toISOString()
      }
    });
    
    res.json({
      message: 'Content pinned successfully',
      hash
    });
  } catch (error) {
    console.error('Error pinning content:', error);
    res.status(500).json({ error: 'Failed to pin content' });
  }
});

// Unpin content from IPFS
router.delete('/pin/:hash', authenticateToken, async (req, res) => {
  try {
    const { hash } = req.params;
    
    // Find the document in database
    const document = await Document.findOne({
      where: { 
        ipfsHash: hash,
        uploaderId: req.user.userId
      }
    });

    if (!document) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Unpin from IPFS
    await ipfsService.unpinContent(hash);
    
    // Update database metadata
    await document.update({
      metadata: {
        ...document.metadata,
        pinned: false,
        unpinnedAt: new Date().toISOString()
      }
    });
    
    res.json({
      message: 'Content unpinned successfully',
      hash
    });
  } catch (error) {
    console.error('Error unpinning content:', error);
    res.status(500).json({ error: 'Failed to unpin content' });
  }
});

// List pinned content
router.get('/pins', authenticateToken, async (req, res) => {
  try {
    const pins = await ipfsService.listPinnedContent();
    
    res.json({ pins });
  } catch (error) {
    console.error('Error listing pinned content:', error);
    res.status(500).json({ error: 'Failed to list pinned content' });
  }
});

// Get user's uploaded documents
router.get('/user/documents', authenticateToken, async (req, res) => {
  try {
    const { limit = 20, offset = 0 } = req.query;
    
    const documents = await Document.findAndCountAll({
      where: { uploaderId: req.user.userId },
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      documents: documents.rows,
      total: documents.count,
      hasMore: documents.count > parseInt(offset) + parseInt(limit)
    });
  } catch (error) {
    console.error('Error fetching user documents:', error);
    res.status(500).json({ error: 'Failed to fetch user documents' });
  }
});

// Get document by ID
router.get('/documents/:id', authenticateToken, async (req, res) => {
  try {
    const document = await Document.findByPk(req.params.id, {
      include: [{
        model: User,
        as: 'uploader',
        attributes: ['id', 'username', 'profile']
      }]
    });

    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    // Check if user has access to document
    if (document.uploaderId !== req.user.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    res.json({
      document,
      gateway_url: ipfsService.getGatewayURL(document.ipfsHash)
    });
  } catch (error) {
    console.error('Error fetching document:', error);
    res.status(500).json({ error: 'Failed to fetch document' });
  }
});

// Delete document
router.delete('/documents/:id', authenticateToken, async (req, res) => {
  try {
    const document = await Document.findByPk(req.params.id);
    
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    // Check if user owns the document
    if (document.uploaderId !== req.user.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Unpin from IPFS
    try {
      await ipfsService.unpinContent(document.ipfsHash);
    } catch (ipfsError) {
      console.error('Error unpinning document from IPFS:', ipfsError);
    }

    await document.destroy();
    
    res.json({ message: 'Document deleted successfully' });
  } catch (error) {
    console.error('Error deleting document:', error);
    res.status(500).json({ error: 'Failed to delete document' });
  }
});

// Delete file by hash
router.delete('/files/:hash', authenticateToken, async (req, res) => {
  try {
    const { hash } = req.params;
    
    const document = await Document.findOne({
      where: { 
        ipfsHash: hash,
        uploaderId: req.user.userId
      }
    });
    
    if (!document) {
      return res.status(404).json({ error: 'File not found' });
    }

    // Unpin from IPFS
    try {
      await ipfsService.unpinContent(hash);
    } catch (ipfsError) {
      console.error('Error unpinning file from IPFS:', ipfsError);
    }

    await document.destroy();
    
    res.json({ message: 'File deleted successfully' });
  } catch (error) {
    console.error('Error deleting file:', error);
    res.status(500).json({ error: 'Failed to delete file' });
  }
});

// Create shared link for document
router.post('/documents/:id/share', authenticateToken, async (req, res) => {
  try {
    const document = await Document.findByPk(req.params.id);
    
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }

    // Check if user owns the document
    if (document.uploaderId !== req.user.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const sharedLink = {
      hash: document.ipfsHash,
      filename: document.filename,
      gateway_url: ipfsService.getGatewayURL(document.ipfsHash),
      api_url: ipfsService.getAPIURL(document.ipfsHash),
      shared_at: new Date().toISOString(),
      shared_by: req.user.userId
    };

    res.json({
      message: 'Shared link created successfully',
      link: sharedLink
    });
  } catch (error) {
    console.error('Error creating shared link:', error);
    res.status(500).json({ error: 'Failed to create shared link' });
  }
});

// Batch upload files
router.post('/batch-upload', authenticateToken, upload.array('files', 10), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No files uploaded' });
    }

    const { pin = true, metadata = {} } = req.body;
    const results = [];

    for (const file of req.files) {
      try {
        const result = await ipfsService.storeBinaryFile(
          file.originalname,
          file.buffer,
          {
            author: req.user.userId,
            mimeType: file.mimetype,
            size: file.size,
            ...metadata
          }
        );

        const document = await Document.create({
          filename: file.originalname,
          size: file.size,
          mimeType: file.mimetype,
          ipfsHash: result.hash,
          uploaderId: req.user.userId,
          metadata: {
            ...metadata,
            version: result.version
          }
        });

        results.push({
          filename: file.originalname,
          document,
          ipfs: {
            hash: result.hash,
            gateway_url: result.gateway_url,
            version: result.version
          }
        });
      } catch (error) {
        console.error(`Error uploading ${file.originalname}:`, error);
        results.push({
          filename: file.originalname,
          error: error.message
        });
      }
    }

    res.json({
      message: 'Batch upload completed',
      results,
      successful: results.filter(r => !r.error).length,
      failed: results.filter(r => r.error).length
    });
  } catch (error) {
    console.error('Error in batch upload:', error);
    res.status(500).json({ error: 'Failed to batch upload files' });
  }
});

module.exports = router; 