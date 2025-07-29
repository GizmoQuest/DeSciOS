const express = require('express');
const { body, validationResult } = require('express-validator');
const { ResearchProject, User, ResearchCollaborator, Document } = require('../services/database');
const { authenticateToken, requireResearcher, requireOwnership } = require('../middleware/auth');
const { ipfsService } = require('../services/ipfs');

const router = express.Router();

// Get all public research projects
router.get('/', async (req, res) => {
  try {
    const { field, status, search, limit = 20, offset = 0 } = req.query;
    
    const where = { isPublic: true };
    
    if (field) where.field = field;
    if (status) where.status = status;
    if (search) {
      where.$or = [
        { title: { $like: `%${search}%` } },
        { description: { $like: `%${search}%` } },
        { keywords: { $like: `%${search}%` } }
      ];
    }

    const projects = await ResearchProject.findAndCountAll({
      where,
      include: [{
        model: User,
        as: 'leader',
        attributes: ['id', 'username', 'profile']
      }],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      projects: projects.rows,
      total: projects.count,
      hasMore: projects.count > parseInt(offset) + parseInt(limit)
    });
  } catch (error) {
    console.error('Error fetching research projects:', error);
    res.status(500).json({ error: 'Failed to fetch research projects' });
  }
});

// Get authenticated user's research projects (leader or collaborator)
router.get('/my-projects', authenticateToken, async (req, res) => {
  try {
    // Projects where the user is the leader
    const leaderProjects = await ResearchProject.findAll({
      where: { leaderId: req.user.userId },
      include: [{
        model: User,
        as: 'leader',
        attributes: ['id', 'username', 'profile']
      }],
      order: [['createdAt', 'DESC']]
    });

    // Projects where the user is a collaborator (but not the leader)
    const collaborations = await ResearchCollaborator.findAll({
      where: { UserId: req.user.userId },
      include: [{
        model: ResearchProject,
        include: [{
          model: User,
          as: 'leader',
          attributes: ['id', 'username', 'profile']
        }]
      }]
    });

    // Map collaborator records to the associated projects
    const collaboratorProjects = collaborations.map(c => c.ResearchProject);

    // Merge and deduplicate projects by id
    const projectsMap = new Map();
    [...leaderProjects, ...collaboratorProjects].forEach(p => projectsMap.set(p.id, p));
    const projects = Array.from(projectsMap.values());

    res.json({ projects });
  } catch (error) {
    console.error('Error fetching user research projects:', error);
    res.status(500).json({ error: 'Failed to fetch user research projects' });
  }
});

// Get research project by ID
router.get('/:id', async (req, res) => {
  try {
    const project = await ResearchProject.findByPk(req.params.id, {
      include: [
        {
          model: User,
          as: 'leader',
          attributes: ['id', 'username', 'profile']
        },
        {
          model: User,
          through: { model: ResearchCollaborator },
          attributes: ['id', 'username', 'profile']
        }
      ]
    });

    if (!project) {
      return res.status(404).json({ error: 'Research project not found' });
    }

    // Check if project is public or user has access
    if (!project.isPublic && req.user?.userId !== project.leaderId) {
      const collaboration = await ResearchCollaborator.findOne({
        where: {
          UserId: req.user?.userId,
          ResearchProjectId: project.id
        }
      });

      if (!collaboration) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }

    res.json({ project });
  } catch (error) {
    console.error('Error fetching research project:', error);
    res.status(500).json({ error: 'Failed to fetch research project' });
  }
});

// Create new research project
router.post('/', authenticateToken, requireResearcher, [
  body('title').isLength({ min: 3, max: 200 }).trim().escape(),
  body('description').isLength({ min: 10, max: 2000 }).trim(),
  body('field').isLength({ min: 1, max: 100 }).trim().escape(),
  body('keywords').optional().isArray(),
  body('isPublic').optional().isBoolean(),
  body('methodology').optional().isLength({ max: 5000 }).trim(),
  body('datasets').optional().isArray(),
  body('publications').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { title, description, field, keywords, isPublic, methodology, datasets, publications } = req.body;

    // Store research project in IPFS
    const projectContent = {
      title,
      description,
      field,
      keywords: keywords || [],
      methodology: methodology || '',
      datasets: datasets || [],
      publications: publications || [],
      createdAt: new Date().toISOString(),
      leader: req.user.userId
    };

    const ipfsResult = await ipfsService.storeAcademicData(projectContent, {
      type: 'research_project',
      author: req.user.userId,
      pin: true
    });

    const project = await ResearchProject.create({
      title,
      description,
      field,
      keywords: keywords || [],
      isPublic: isPublic !== undefined ? isPublic : true,
      methodology: methodology || '',
      datasets: datasets || [],
      publications: publications || [],
      leaderId: req.user.userId,
      ipfsHash: ipfsResult.hash,
      status: 'active'
    });

    const projectWithLeader = await ResearchProject.findByPk(project.id, {
      include: [{
        model: User,
        as: 'leader',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.status(201).json({
      message: 'Research project created successfully',
      project: projectWithLeader,
      ipfs: {
        hash: ipfsResult.hash,
        gateway_url: ipfsResult.gateway_url
      }
    });
  } catch (error) {
    console.error('Error creating research project:', error);
    res.status(500).json({ error: 'Failed to create research project' });
  }
});

// Update research project
router.put('/:id', authenticateToken, requireOwnership(ResearchProject), [
  body('title').optional().isLength({ min: 3, max: 200 }).trim().escape(),
  body('description').optional().isLength({ min: 10, max: 2000 }).trim(),
  body('field').optional().isLength({ min: 1, max: 100 }).trim().escape(),
  body('keywords').optional().isArray(),
  body('isPublic').optional().isBoolean(),
  body('status').optional().isIn(['proposal', 'active', 'completed', 'archived']),
  body('methodology').optional().isLength({ max: 5000 }).trim(),
  body('findings').optional().isLength({ max: 5000 }).trim(),
  body('datasets').optional().isArray(),
  body('publications').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const project = req.resource;
    const updates = req.body;

    // Update project content in IPFS if content changed
    if (updates.title || updates.description || updates.methodology || updates.findings || updates.datasets || updates.publications) {
      const projectContent = {
        title: updates.title || project.title,
        description: updates.description || project.description,
        field: updates.field || project.field,
        keywords: updates.keywords || project.keywords,
        methodology: updates.methodology || project.methodology,
        findings: updates.findings || project.findings,
        datasets: updates.datasets || project.datasets,
        publications: updates.publications || project.publications,
        updatedAt: new Date().toISOString(),
        leader: project.leaderId
      };

      const ipfsResult = await ipfsService.storeAcademicData(projectContent, {
        type: 'research_project',
        author: req.user.userId,
        version: 2,
        pin: true
      });

      updates.ipfsHash = ipfsResult.hash;
    }

    await project.update(updates);

    const updatedProject = await ResearchProject.findByPk(project.id, {
      include: [{
        model: User,
        as: 'leader',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.json({
      message: 'Research project updated successfully',
      project: updatedProject
    });
  } catch (error) {
    console.error('Error updating research project:', error);
    res.status(500).json({ error: 'Failed to update research project' });
  }
});

// Delete research project
router.delete('/:id', authenticateToken, requireOwnership(ResearchProject), async (req, res) => {
  try {
    const project = req.resource;
    
    // Unpin from IPFS if hash exists
    if (project.ipfsHash) {
      try {
        await ipfsService.unpinContent(project.ipfsHash);
      } catch (ipfsError) {
        console.error('Error unpinning project from IPFS:', ipfsError);
      }
    }

    await project.destroy();
    res.json({ message: 'Research project deleted successfully' });
  } catch (error) {
    console.error('Error deleting research project:', error);
    res.status(500).json({ error: 'Failed to delete research project' });
  }
});

// Add collaborator to research project
router.post('/:id/collaborators', authenticateToken, requireOwnership(ResearchProject), [
  body('userId').isUUID(),
  body('role').isIn(['collaborator', 'reviewer', 'advisor']),
  body('permissions').optional().isObject()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { userId, role, permissions } = req.body;
    const project = req.resource;

    // Check if user exists
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Check if already a collaborator
    const existingCollaboration = await ResearchCollaborator.findOne({
      where: {
        UserId: userId,
        ResearchProjectId: project.id
      }
    });

    if (existingCollaboration) {
      return res.status(400).json({ error: 'User is already a collaborator' });
    }

    const collaboration = await ResearchCollaborator.create({
      UserId: userId,
      ResearchProjectId: project.id,
      role: role || 'collaborator',
      permissions: permissions || {}
    });

    res.json({
      message: 'Collaborator added successfully',
      collaboration
    });
  } catch (error) {
    console.error('Error adding collaborator:', error);
    res.status(500).json({ error: 'Failed to add collaborator' });
  }
});

// Remove collaborator from research project
router.delete('/:id/collaborators/:userId', authenticateToken, requireOwnership(ResearchProject), async (req, res) => {
  try {
    const collaboration = await ResearchCollaborator.findOne({
      where: {
        UserId: req.params.userId,
        ResearchProjectId: req.params.id
      }
    });

    if (!collaboration) {
      return res.status(404).json({ error: 'Collaboration not found' });
    }

    await collaboration.destroy();
    res.json({ message: 'Collaborator removed successfully' });
  } catch (error) {
    console.error('Error removing collaborator:', error);
    res.status(500).json({ error: 'Failed to remove collaborator' });
  }
});

// Get user's research projects
router.get('/user/projects', authenticateToken, async (req, res) => {
  try {
    const { role } = req.query;
    
    let projects;
    if (role === 'leader') {
      projects = await ResearchProject.findAll({
        where: { leaderId: req.user.userId },
        include: [{
          model: User,
          through: { model: ResearchCollaborator },
          attributes: ['id', 'username', 'profile']
        }],
        order: [['createdAt', 'DESC']]
      });
    } else {
      // Get projects where user is a collaborator
      const collaborations = await ResearchCollaborator.findAll({
        where: { UserId: req.user.userId },
        include: [{
          model: ResearchProject,
          include: [{
            model: User,
            as: 'leader',
            attributes: ['id', 'username', 'profile']
          }]
        }],
        order: [['createdAt', 'DESC']]
      });

      projects = collaborations.map(collab => collab.ResearchProject);
    }

    res.json({ projects });
  } catch (error) {
    console.error('Error fetching user research projects:', error);
    res.status(500).json({ error: 'Failed to fetch user research projects' });
  }
});

// Upload research document
router.post('/:id/documents', authenticateToken, async (req, res) => {
  try {
    const project = await ResearchProject.findByPk(req.params.id);
    if (!project) {
      return res.status(404).json({ error: 'Research project not found' });
    }

    // Check if user has access to project
    if (project.leaderId !== req.user.userId) {
      const collaboration = await ResearchCollaborator.findOne({
        where: {
          UserId: req.user.userId,
          ResearchProjectId: project.id
        }
      });

      if (!collaboration) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }

    const { filename, content, mimeType } = req.body;

    // Store document in IPFS
    const documentResult = await ipfsService.createVersionedDocument(filename, content, {
      author: req.user.userId,
      project: project.id,
      mimeType
    });

    const document = await Document.create({
      filename,
      size: Buffer.byteLength(content),
      mimeType,
      ipfsHash: documentResult.hash,
      uploaderId: req.user.userId,
      metadata: {
        project: project.id,
        version: documentResult.version
      }
    });

    res.status(201).json({
      message: 'Document uploaded successfully',
      document,
      ipfs: {
        hash: documentResult.hash,
        gateway_url: documentResult.gateway_url
      }
    });
  } catch (error) {
    console.error('Error uploading document:', error);
    res.status(500).json({ error: 'Failed to upload document' });
  }
});

// Get research project documents
router.get('/:id/documents', authenticateToken, async (req, res) => {
  try {
    const project = await ResearchProject.findByPk(req.params.id);
    if (!project) {
      return res.status(404).json({ error: 'Research project not found' });
    }

    // Check if user has access to project
    if (project.leaderId !== req.user.userId && !project.isPublic) {
      const collaboration = await ResearchCollaborator.findOne({
        where: {
          UserId: req.user.userId,
          ResearchProjectId: project.id
        }
      });

      if (!collaboration) {
        return res.status(403).json({ error: 'Access denied' });
      }
    }

    const documents = await Document.findAll({
      where: {
        'metadata.project': project.id
      },
      include: [{
        model: User,
        as: 'uploader',
        attributes: ['id', 'username', 'profile']
      }],
      order: [['createdAt', 'DESC']]
    });

    res.json({ documents });
  } catch (error) {
    console.error('Error fetching documents:', error);
    res.status(500).json({ error: 'Failed to fetch documents' });
  }
});

module.exports = router; 