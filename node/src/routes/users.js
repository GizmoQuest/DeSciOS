const express = require('express');
const { body, validationResult } = require('express-validator');
const { User, Course, ResearchProject, Collaboration, Document } = require('../services/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Search users
router.get('/search', authenticateToken, async (req, res) => {
  try {
    const { q, role, limit = 10 } = req.query;
    
    if (!q || q.length < 2) {
      return res.status(400).json({ error: 'Search query must be at least 2 characters' });
    }

    const where = {
      isActive: true,
      $or: [
        { username: { $like: `%${q}%` } },
        { email: { $like: `%${q}%` } },
        { 'profile.firstName': { $like: `%${q}%` } },
        { 'profile.lastName': { $like: `%${q}%` } }
      ]
    };

    if (role) {
      where.role = role;
    }

    const users = await User.findAll({
      where,
      attributes: ['id', 'username', 'email', 'role', 'profile', 'createdAt'],
      limit: parseInt(limit),
      order: [['username', 'ASC']]
    });

    res.json({ users });
  } catch (error) {
    console.error('Error searching users:', error);
    res.status(500).json({ error: 'Failed to search users' });
  }
});

// Get user by ID
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id, {
      attributes: ['id', 'username', 'email', 'role', 'profile', 'createdAt']
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({ user });
  } catch (error) {
    console.error('Error fetching user:', error);
    res.status(500).json({ error: 'Failed to fetch user' });
  }
});

// Get user's public profile with stats
router.get('/:id/profile', async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id, {
      attributes: ['id', 'username', 'role', 'profile', 'createdAt']
    });

    if (!user || !user.isActive) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Get user's public courses
    const courses = await Course.findAll({
      where: { 
        instructorId: user.id,
        isPublic: true,
        status: 'published'
      },
      attributes: ['id', 'title', 'description', 'category', 'difficulty', 'createdAt'],
      order: [['createdAt', 'DESC']],
      limit: 5
    });

    // Get user's public research projects
    const researchProjects = await ResearchProject.findAll({
      where: { 
        leaderId: user.id,
        isPublic: true
      },
      attributes: ['id', 'title', 'description', 'field', 'status', 'createdAt'],
      order: [['createdAt', 'DESC']],
      limit: 5
    });

    // Get user's public collaborations
    const collaborations = await Collaboration.findAll({
      where: { 
        ownerId: user.id,
        status: 'active'
      },
      attributes: ['id', 'title', 'description', 'type', 'createdAt'],
      order: [['createdAt', 'DESC']],
      limit: 5
    });

    // Calculate stats
    const stats = {
      coursesCreated: courses.length,
      researchProjects: researchProjects.length,
      collaborations: collaborations.length,
      joinedAt: user.createdAt
    };

    res.json({
      user,
      stats,
      recentActivity: {
        courses,
        researchProjects,
        collaborations
      }
    });
  } catch (error) {
    console.error('Error fetching user profile:', error);
    res.status(500).json({ error: 'Failed to fetch user profile' });
  }
});

// Get user's courses (as instructor)
router.get('/:id/courses', authenticateToken, async (req, res) => {
  try {
    const { status, limit = 10, offset = 0 } = req.query;
    
    const where = { instructorId: req.params.id };
    if (status) where.status = status;
    
    // Only show public courses unless requesting own courses
    if (req.user.userId !== req.params.id) {
      where.isPublic = true;
      where.status = 'published';
    }

    const courses = await Course.findAndCountAll({
      where,
      attributes: ['id', 'title', 'description', 'category', 'difficulty', 'status', 'createdAt'],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      courses: courses.rows,
      total: courses.count,
      hasMore: courses.count > parseInt(offset) + parseInt(limit)
    });
  } catch (error) {
    console.error('Error fetching user courses:', error);
    res.status(500).json({ error: 'Failed to fetch user courses' });
  }
});

// Get user's research projects (as leader)
router.get('/:id/research', authenticateToken, async (req, res) => {
  try {
    const { status, limit = 10, offset = 0 } = req.query;
    
    const where = { leaderId: req.params.id };
    if (status) where.status = status;
    
    // Only show public projects unless requesting own projects
    if (req.user.userId !== req.params.id) {
      where.isPublic = true;
    }

    const projects = await ResearchProject.findAndCountAll({
      where,
      attributes: ['id', 'title', 'description', 'field', 'status', 'createdAt'],
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
    console.error('Error fetching user research projects:', error);
    res.status(500).json({ error: 'Failed to fetch user research projects' });
  }
});

// Get user's documents
router.get('/:id/documents', authenticateToken, async (req, res) => {
  try {
    // Only allow users to see their own documents
    if (req.user.userId !== req.params.id) {
      return res.status(403).json({ error: 'Access denied' });
    }

    const { limit = 20, offset = 0 } = req.query;
    
    const documents = await Document.findAndCountAll({
      where: { uploaderId: req.params.id },
      attributes: ['id', 'filename', 'size', 'mimeType', 'createdAt', 'metadata'],
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

// Get user statistics
router.get('/:id/stats', authenticateToken, async (req, res) => {
  try {
    const userId = req.params.id;
    
    // Only allow users to see their own detailed stats
    if (req.user.userId !== userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Simple stats without complex joins for now
    const [
      coursesCreated,
      researchProjectsLed,
      collaborationsOwned,
      documentsUploaded
    ] = await Promise.all([
      Course.count({ where: { instructorId: userId } }).catch(() => 0),
      ResearchProject.count({ where: { leaderId: userId } }).catch(() => 0),
      Collaboration.count({ where: { creatorId: userId } }).catch(() => 0),
      Document.count({ where: { authorId: userId } }).catch(() => 0)
    ]);

    const stats = {
      courses: {
        created: coursesCreated,
        enrolled: 0 // Simplified for now
      },
      research: {
        led: researchProjectsLed,
        collaborated: 0 // Simplified for now
      },
      collaborations: {
        owned: collaborationsOwned,
        member: 0 // Simplified for now
      },
      documents: {
        uploaded: documentsUploaded
      }
    };

    res.json({ stats });
  } catch (error) {
    console.error('Error fetching user stats:', error);
    res.status(500).json({ error: 'Failed to fetch user statistics' });
  }
});

// Get user activity feed
router.get('/:id/activity', authenticateToken, async (req, res) => {
  try {
    const userId = req.params.id;
    
    // Only allow users to see their own activity feed
    if (req.user.userId !== userId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Simplified activity feed for now
    const activities = [];
    const upcomingTasks = [];

    res.json({ 
      activities,
      upcomingTasks
    });
  } catch (error) {
    console.error('Error fetching user activity:', error);
    res.status(500).json({ error: 'Failed to fetch user activity' });
  }
});

// Get all users (admin only)
router.get('/', authenticateToken, async (req, res) => {
  try {
    // Check if user is admin
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const { role, active, limit = 50, offset = 0 } = req.query;
    
    const where = {};
    if (role) where.role = role;
    if (active !== undefined) where.isActive = active === 'true';

    const users = await User.findAndCountAll({
      where,
      attributes: ['id', 'username', 'email', 'role', 'isActive', 'createdAt', 'lastLogin'],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      users: users.rows,
      total: users.count,
      hasMore: users.count > parseInt(offset) + parseInt(limit)
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

// Update user status (admin only)
router.patch('/:id/status', authenticateToken, [
  body('isActive').isBoolean(),
  body('reason').optional().isLength({ max: 500 })
], async (req, res) => {
  try {
    // Check if user is admin
    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Admin access required' });
    }

    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { isActive, reason } = req.body;
    const user = await User.findByPk(req.params.id);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    await user.update({ isActive });

    res.json({
      message: `User ${isActive ? 'activated' : 'deactivated'} successfully`,
      user: {
        id: user.id,
        username: user.username,
        isActive: user.isActive
      }
    });
  } catch (error) {
    console.error('Error updating user status:', error);
    res.status(500).json({ error: 'Failed to update user status' });
  }
});

module.exports = router; 