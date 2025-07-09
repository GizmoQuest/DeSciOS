const express = require('express');
const { body, validationResult } = require('express-validator');
const { Collaboration, User, CollaborationMember, Message, Document } = require('../services/database');
const { authenticateToken, requireOwnership } = require('../middleware/auth');
const { ipfsService } = require('../services/ipfs');

const router = express.Router();

// Get user's collaborations
router.get('/user', authenticateToken, async (req, res) => {
  try {
    const { type } = req.query;
    
    const where = {};
    if (type) where.type = type;

    const collaborations = await CollaborationMember.findAll({
      where: { UserId: req.user.userId },
      include: [{
        model: Collaboration,
        where,
        include: [{
          model: User,
          as: 'owner',
          attributes: ['id', 'username', 'profile']
        }]
      }],
      order: [['createdAt', 'DESC']]
    });

    res.json({ collaborations: collaborations.map(c => c.Collaboration) });
  } catch (error) {
    console.error('Error fetching collaborations:', error);
    res.status(500).json({ error: 'Failed to fetch collaborations' });
  }
});

// Get collaboration by ID
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const collaboration = await Collaboration.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'owner',
          attributes: ['id', 'username', 'profile']
        },
        {
          model: User,
          through: { model: CollaborationMember },
          attributes: ['id', 'username', 'profile']
        }
      ]
    });

    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has access to collaboration
    const membership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!membership && collaboration.ownerId !== req.user.userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    res.json({ collaboration, membership });
  } catch (error) {
    console.error('Error fetching collaboration:', error);
    res.status(500).json({ error: 'Failed to fetch collaboration' });
  }
});

// Create new collaboration
router.post('/', authenticateToken, [
  body('title').isLength({ min: 3, max: 200 }).trim().escape(),
  body('description').optional().isLength({ max: 2000 }).trim(),
  body('type').isIn(['course', 'research', 'peer_review', 'study_group']),
  body('documents').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { title, description, type, documents } = req.body;

    // Store collaboration metadata in IPFS
    const collaborationContent = {
      title,
      description: description || '',
      type,
      documents: documents || [],
      createdAt: new Date().toISOString(),
      owner: req.user.userId
    };

    const ipfsResult = await ipfsService.storeAcademicData(collaborationContent, {
      type: 'collaboration',
      author: req.user.userId,
      pin: true
    });

    const collaboration = await Collaboration.create({
      title,
      description: description || '',
      type,
      documents: documents || [],
      ownerId: req.user.userId,
      ipfsHash: ipfsResult.hash
    });

    // Add owner as admin member
    await CollaborationMember.create({
      UserId: req.user.userId,
      CollaborationId: collaboration.id,
      role: 'admin'
    });

    const collaborationWithOwner = await Collaboration.findByPk(collaboration.id, {
      include: [{
        model: User,
        as: 'owner',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.status(201).json({
      message: 'Collaboration created successfully',
      collaboration: collaborationWithOwner,
      ipfs: {
        hash: ipfsResult.hash,
        gateway_url: ipfsResult.gateway_url
      }
    });
  } catch (error) {
    console.error('Error creating collaboration:', error);
    res.status(500).json({ error: 'Failed to create collaboration' });
  }
});

// Update collaboration
router.put('/:id', authenticateToken, requireOwnership(Collaboration), [
  body('title').optional().isLength({ min: 3, max: 200 }).trim().escape(),
  body('description').optional().isLength({ max: 2000 }).trim(),
  body('status').optional().isIn(['active', 'completed', 'archived']),
  body('documents').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const collaboration = req.resource;
    const updates = req.body;

    // Update collaboration content in IPFS if content changed
    if (updates.title || updates.description || updates.documents) {
      const collaborationContent = {
        title: updates.title || collaboration.title,
        description: updates.description || collaboration.description,
        type: collaboration.type,
        documents: updates.documents || collaboration.documents,
        updatedAt: new Date().toISOString(),
        owner: collaboration.ownerId
      };

      const ipfsResult = await ipfsService.storeAcademicData(collaborationContent, {
        type: 'collaboration',
        author: req.user.userId,
        version: 2,
        pin: true
      });

      updates.ipfsHash = ipfsResult.hash;
    }

    await collaboration.update(updates);

    const updatedCollaboration = await Collaboration.findByPk(collaboration.id, {
      include: [{
        model: User,
        as: 'owner',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.json({
      message: 'Collaboration updated successfully',
      collaboration: updatedCollaboration
    });
  } catch (error) {
    console.error('Error updating collaboration:', error);
    res.status(500).json({ error: 'Failed to update collaboration' });
  }
});

// Delete collaboration
router.delete('/:id', authenticateToken, requireOwnership(Collaboration), async (req, res) => {
  try {
    const collaboration = req.resource;
    
    // Unpin from IPFS if hash exists
    if (collaboration.ipfsHash) {
      try {
        await ipfsService.unpinContent(collaboration.ipfsHash);
      } catch (ipfsError) {
        console.error('Error unpinning collaboration from IPFS:', ipfsError);
      }
    }

    await collaboration.destroy();
    res.json({ message: 'Collaboration deleted successfully' });
  } catch (error) {
    console.error('Error deleting collaboration:', error);
    res.status(500).json({ error: 'Failed to delete collaboration' });
  }
});

// Add member to collaboration
router.post('/:id/members', authenticateToken, [
  body('userId').isUUID(),
  body('role').optional().isIn(['member', 'moderator', 'admin']),
  body('permissions').optional().isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, role, permissions } = req.body;
    const collaboration = await Collaboration.findByPk(req.params.id);

    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has permission to add members
    const userMembership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!userMembership || (userMembership.role !== 'admin' && userMembership.role !== 'moderator')) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    // Check if user exists
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Check if already a member
    const existingMembership = await CollaborationMember.findOne({
      where: {
        UserId: userId,
        CollaborationId: collaboration.id
      }
    });

    if (existingMembership) {
      return res.status(400).json({ error: 'User is already a member' });
    }

    const membership = await CollaborationMember.create({
      UserId: userId,
      CollaborationId: collaboration.id,
      role: role || 'member',
      permissions: permissions || {}
    });

    res.json({
      message: 'Member added successfully',
      membership
    });
  } catch (error) {
    console.error('Error adding member:', error);
    res.status(500).json({ error: 'Failed to add member' });
  }
});

// Remove member from collaboration
router.delete('/:id/members/:userId', authenticateToken, async (req, res) => {
  try {
    const collaboration = await Collaboration.findByPk(req.params.id);
    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has permission to remove members
    const userMembership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!userMembership || (userMembership.role !== 'admin' && req.user.userId !== req.params.userId)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    const membership = await CollaborationMember.findOne({
      where: {
        UserId: req.params.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!membership) {
      return res.status(404).json({ error: 'Membership not found' });
    }

    await membership.destroy();
    res.json({ message: 'Member removed successfully' });
  } catch (error) {
    console.error('Error removing member:', error);
    res.status(500).json({ error: 'Failed to remove member' });
  }
});

// Get collaboration messages
router.get('/:id/messages', authenticateToken, async (req, res) => {
  try {
    const { limit = 50, offset = 0 } = req.query;
    const collaboration = await Collaboration.findByPk(req.params.id);

    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has access to collaboration
    const membership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!membership) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const messages = await Message.findAll({
      where: {
        'metadata.collaboration': collaboration.id
      },
      include: [{
        model: User,
        as: 'sender',
        attributes: ['id', 'username', 'profile']
      }],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({ messages });
  } catch (error) {
    console.error('Error fetching messages:', error);
    res.status(500).json({ error: 'Failed to fetch messages' });
  }
});

// Send message to collaboration
router.post('/:id/messages', authenticateToken, [
  body('content').isLength({ min: 1, max: 2000 }).trim(),
  body('type').optional().isIn(['text', 'file', 'code', 'image']),
  body('parentId').optional().isUUID()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { content, type, parentId } = req.body;
    const collaboration = await Collaboration.findByPk(req.params.id);

    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has access to collaboration
    const membership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!membership) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const message = await Message.create({
      content,
      type: type || 'text',
      parentId: parentId || null,
      senderId: req.user.userId,
      metadata: {
        collaboration: collaboration.id
      }
    });

    const messageWithSender = await Message.findByPk(message.id, {
      include: [{
        model: User,
        as: 'sender',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.status(201).json({
      message: 'Message sent successfully',
      messageData: messageWithSender
    });
  } catch (error) {
    console.error('Error sending message:', error);
    res.status(500).json({ error: 'Failed to send message' });
  }
});

// Upload file to collaboration
router.post('/:id/files', authenticateToken, [
  body('filename').isLength({ min: 1, max: 255 }).trim(),
  body('content').exists(),
  body('mimeType').optional().isLength({ max: 100 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { filename, content, mimeType } = req.body;
    const collaboration = await Collaboration.findByPk(req.params.id);

    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has access to collaboration
    const membership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!membership) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Store file in IPFS
    const fileResult = await ipfsService.createVersionedDocument(filename, content, {
      author: req.user.userId,
      collaboration: collaboration.id,
      mimeType: mimeType || 'application/octet-stream'
    });

    const document = await Document.create({
      filename,
      size: Buffer.byteLength(content),
      mimeType: mimeType || 'application/octet-stream',
      ipfsHash: fileResult.hash,
      uploaderId: req.user.userId,
      metadata: {
        collaboration: collaboration.id,
        version: fileResult.version
      }
    });

    res.status(201).json({
      message: 'File uploaded successfully',
      document,
      ipfs: {
        hash: fileResult.hash,
        gateway_url: fileResult.gateway_url
      }
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    res.status(500).json({ error: 'Failed to upload file' });
  }
});

// Get collaboration files
router.get('/:id/files', authenticateToken, async (req, res) => {
  try {
    const collaboration = await Collaboration.findByPk(req.params.id);
    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    // Check if user has access to collaboration
    const membership = await CollaborationMember.findOne({
      where: {
        UserId: req.user.userId,
        CollaborationId: collaboration.id
      }
    });

    if (!membership) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const files = await Document.findAll({
      where: {
        'metadata.collaboration': collaboration.id
      },
      include: [{
        model: User,
        as: 'uploader',
        attributes: ['id', 'username', 'profile']
      }],
      order: [['createdAt', 'DESC']]
    });

    res.json({ files });
  } catch (error) {
    console.error('Error fetching files:', error);
    res.status(500).json({ error: 'Failed to fetch files' });
  }
});

module.exports = router; 