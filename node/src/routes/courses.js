const express = require('express');
const { Op } = require('sequelize');
const { body, validationResult } = require('express-validator');
const { Course, User, CourseEnrollment } = require('../services/database');
const { authenticateToken, requireInstructor, requireOwnership } = require('../middleware/auth');
const { ipfsService } = require('../services/ipfs');

const router = express.Router();

// Get all public courses
router.get('/', async (req, res) => {
  try {
    const { category, difficulty, search, limit = 20, offset = 0 } = req.query;
    
    const where = { isPublic: true, status: 'published' };
    
    if (category) where.category = category;
    if (difficulty) where.difficulty = difficulty;
    if (search) {
      where[Op.or] = [
        { title: { [Op.like]: `%${search}%` } },
        { description: { [Op.like]: `%${search}%` } }
      ];
    }

    const courses = await Course.findAndCountAll({
      where,
      include: [{
        model: User,
        as: 'instructor',
        attributes: ['id', 'username', 'profile']
      }],
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
    console.error('Error fetching courses:', error);
    res.status(500).json({ error: 'Failed to fetch courses' });
  }
});

// Get course by ID
router.get('/:id', async (req, res) => {
  try {
    const course = await Course.findByPk(req.params.id, {
      include: [{
        model: User,
        as: 'instructor',
        attributes: ['id', 'username', 'profile']
      }]
    });

    if (!course) {
      return res.status(404).json({ error: 'Course not found' });
    }

    // Check if course is public or user has access
    if (!course.isPublic && req.user?.userId !== course.instructorId) {
      return res.status(403).json({ error: 'Access denied' });
    }

    // Get enrollment info if user is authenticated
    let enrollment = null;
    if (req.user) {
      try {
        enrollment = await CourseEnrollment.findOne({
          where: {
            UserId: req.user.userId,
            CourseId: course.id
          }
        });
      } catch (enrollmentError) {
        console.error('Error checking enrollment:', enrollmentError);
        // Continue without enrollment info rather than failing the whole request
      }
      
      // If enrollment exists, return it as an object
      if (enrollment) {
        enrollment = {
          enrolled: true,
          progress: enrollment.progress,
          enrolledAt: enrollment.enrolledAt || enrollment.createdAt,
          completedAt: enrollment.completedAt
        };
      }
    }

    res.json({
      course,
      enrollment: enrollment || null
    });
  } catch (error) {
    console.error('Error fetching course:', error);
    res.status(500).json({ error: 'Failed to fetch course' });
  }
});

// Create new course
router.post('/', authenticateToken, requireInstructor, [
  body('title').isLength({ min: 3, max: 200 }).trim().escape(),
  body('description').isLength({ min: 10, max: 2000 }).trim(),
  body('category').isLength({ min: 1, max: 100 }).trim().escape(),
  body('difficulty').isIn(['beginner', 'intermediate', 'advanced']),
  body('isPublic').optional().isBoolean(),
  body('syllabus').optional().isArray(),
  body('resources').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { title, description, category, difficulty, isPublic, syllabus, resources } = req.body;

    // Store course content in IPFS
    const courseContent = {
      title,
      description,
      category,
      difficulty,
      syllabus: syllabus || [],
      resources: resources || [],
      createdAt: new Date().toISOString(),
      instructor: req.user.userId
    };

    const ipfsResult = await ipfsService.storeAcademicData(courseContent, {
      type: 'course',
      author: req.user.userId,
      pin: true
    });

    const course = await Course.create({
      title,
      description,
      category,
      difficulty,
      isPublic: isPublic !== undefined ? isPublic : true,
      syllabus: syllabus || [],
      resources: resources || [],
      instructorId: req.user.userId,
      ipfsHash: ipfsResult.hash,
      status: 'published'
    });

    const courseWithInstructor = await Course.findByPk(course.id, {
      include: [{
        model: User,
        as: 'instructor',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.status(201).json({
      message: 'Course created successfully',
      course: courseWithInstructor,
      ipfs: {
        hash: ipfsResult.hash,
        gateway_url: ipfsResult.gateway_url
      }
    });
  } catch (error) {
    console.error('Error creating course:', error);
    res.status(500).json({ error: 'Failed to create course' });
  }
});

// Update course
router.put('/:id', authenticateToken, requireOwnership(Course), [
  body('title').optional().isLength({ min: 3, max: 200 }).trim().escape(),
  body('description').optional().isLength({ min: 10, max: 2000 }).trim(),
  body('category').optional().isLength({ min: 1, max: 100 }).trim().escape(),
  body('difficulty').optional().isIn(['beginner', 'intermediate', 'advanced']),
  body('isPublic').optional().isBoolean(),
  body('status').optional().isIn(['draft', 'published', 'archived']),
  body('syllabus').optional().isArray(),
  body('resources').optional().isArray()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const course = req.resource;
    const updates = req.body;

    // Update course content in IPFS if content changed
    if (updates.title || updates.description || updates.syllabus || updates.resources) {
      const courseContent = {
        title: updates.title || course.title,
        description: updates.description || course.description,
        category: updates.category || course.category,
        difficulty: updates.difficulty || course.difficulty,
        syllabus: updates.syllabus || course.syllabus,
        resources: updates.resources || course.resources,
        updatedAt: new Date().toISOString(),
        instructor: course.instructorId
      };

      const ipfsResult = await ipfsService.storeAcademicData(courseContent, {
        type: 'course',
        author: req.user.userId,
        version: 2,
        pin: true
      });

      updates.ipfsHash = ipfsResult.hash;
    }

    await course.update(updates);

    const updatedCourse = await Course.findByPk(course.id, {
      include: [{
        model: User,
        as: 'instructor',
        attributes: ['id', 'username', 'profile']
      }]
    });

    res.json({
      message: 'Course updated successfully',
      course: updatedCourse
    });
  } catch (error) {
    console.error('Error updating course:', error);
    res.status(500).json({ error: 'Failed to update course' });
  }
});

// Delete course
router.delete('/:id', authenticateToken, requireOwnership(Course), async (req, res) => {
  try {
    const course = req.resource;
    
    // Unpin from IPFS if hash exists
    if (course.ipfsHash) {
      try {
        await ipfsService.unpinContent(course.ipfsHash);
      } catch (ipfsError) {
        console.error('Error unpinning course from IPFS:', ipfsError);
      }
    }

    await course.destroy();
    res.json({ message: 'Course deleted successfully' });
  } catch (error) {
    console.error('Error deleting course:', error);
    res.status(500).json({ error: 'Failed to delete course' });
  }
});

// Enroll in course
router.post('/:id/enroll', authenticateToken, async (req, res) => {
  try {
    const course = await Course.findByPk(req.params.id);
    
    if (!course) {
      return res.status(404).json({ error: 'Course not found' });
    }

    if (!course.isPublic || course.status !== 'published') {
      return res.status(403).json({ error: 'Course not available for enrollment' });
    }

    // Check if already enrolled
    const existingEnrollment = await CourseEnrollment.findOne({
      where: {
        UserId: req.user.userId,
        CourseId: course.id
      }
    });

    if (existingEnrollment) {
      return res.status(400).json({ error: 'Already enrolled in this course' });
    }

    const enrollment = await CourseEnrollment.create({
      UserId: req.user.userId,
      CourseId: course.id
    });

    res.json({
      message: 'Enrolled successfully',
      enrollment
    });
  } catch (error) {
    console.error('Error enrolling in course:', error);
    res.status(500).json({ error: 'Failed to enroll in course' });
  }
});

// Update enrollment progress
router.put('/:id/progress', authenticateToken, [
  body('progress').isFloat({ min: 0, max: 1 })
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { progress } = req.body;
    
    const enrollment = await CourseEnrollment.findOne({
      where: {
        UserId: req.user.userId,
        CourseId: req.params.id
      }
    });

    if (!enrollment) {
      return res.status(404).json({ error: 'Enrollment not found' });
    }

    await enrollment.update({
      progress,
      completedAt: progress >= 1 ? new Date() : null
    });

    res.json({
      message: 'Progress updated successfully',
      enrollment
    });
  } catch (error) {
    console.error('Error updating progress:', error);
    res.status(500).json({ error: 'Failed to update progress' });
  }
});

// Get user's enrolled courses
router.get('/user/enrolled', authenticateToken, async (req, res) => {
  try {
    const enrollments = await CourseEnrollment.findAll({
      where: { UserId: req.user.userId },
      include: [{
        model: Course,
        include: [{
          model: User,
          as: 'instructor',
          attributes: ['id', 'username', 'profile']
        }]
      }],
      order: [['createdAt', 'DESC']]
    });

    res.json({ enrollments });
  } catch (error) {
    console.error('Error fetching enrolled courses:', error);
    res.status(500).json({ error: 'Failed to fetch enrolled courses' });
  }
});

// Get instructor's courses
router.get('/user/teaching', authenticateToken, requireInstructor, async (req, res) => {
  try {
    const courses = await Course.findAll({
      where: { instructorId: req.user.userId },
      include: [{
        model: User,
        through: { model: CourseEnrollment },
        attributes: ['id', 'username', 'profile']
      }],
      order: [['createdAt', 'DESC']]
    });

    res.json({ courses });
  } catch (error) {
    console.error('Error fetching teaching courses:', error);
    res.status(500).json({ error: 'Failed to fetch teaching courses' });
  }
});

module.exports = router; 