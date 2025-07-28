#!/usr/bin/env node

const path = require('path');
const fs = require('fs');
const { Sequelize } = require('sequelize');
const bcrypt = require('bcryptjs');

// Set up database path
const dbPath = process.env.DATABASE_PATH || path.join(__dirname, '../../database.sqlite');
const dbDir = path.dirname(dbPath);

// Create database directory if it doesn't exist
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}

// Database models
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: dbPath,
  logging: false
});

// Define models (matching the main models)
const User = sequelize.define('User', {
  id: {
    type: Sequelize.UUID,
    defaultValue: Sequelize.UUIDV4,
    primaryKey: true
  },
  username: {
    type: Sequelize.STRING,
    unique: true,
    allowNull: false
  },
  email: {
    type: Sequelize.STRING,
    unique: true,
    allowNull: false
  },
  password: {
    type: Sequelize.STRING,
    allowNull: false
  },
  role: {
    type: Sequelize.ENUM('student', 'instructor', 'researcher', 'admin'),
    defaultValue: 'student'
  },
  profile: {
    type: Sequelize.JSON,
    defaultValue: {}
  },
  isActive: {
    type: Sequelize.BOOLEAN,
    defaultValue: true
  },
  lastLogin: {
    type: Sequelize.DATE
  }
});

const Course = sequelize.define('Course', {
  id: {
    type: Sequelize.UUID,
    defaultValue: Sequelize.UUIDV4,
    primaryKey: true
  },
  title: {
    type: Sequelize.STRING,
    allowNull: false
  },
  description: {
    type: Sequelize.TEXT
  },
  category: {
    type: Sequelize.STRING,
    defaultValue: 'general'
  },
  status: {
    type: Sequelize.ENUM('draft', 'active', 'archived'),
    defaultValue: 'draft'
  },
  instructorId: {
    type: Sequelize.UUID,
    allowNull: false
  },
  content: {
    type: Sequelize.JSON,
    defaultValue: []
  },
  settings: {
    type: Sequelize.JSON,
    defaultValue: {}
  },
  ipfsHash: {
    type: Sequelize.STRING
  }
});

const ResearchProject = sequelize.define('ResearchProject', {
  id: {
    type: Sequelize.UUID,
    defaultValue: Sequelize.UUIDV4,
    primaryKey: true
  },
  title: {
    type: Sequelize.STRING,
    allowNull: false
  },
  description: {
    type: Sequelize.TEXT
  },
  category: {
    type: Sequelize.STRING,
    defaultValue: 'general'
  },
  status: {
    type: Sequelize.ENUM('planning', 'active', 'completed', 'archived'),
    defaultValue: 'planning'
  },
  visibility: {
    type: Sequelize.ENUM('public', 'private', 'restricted'),
    defaultValue: 'private'
  },
  leaderId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  data: {
    type: Sequelize.JSON,
    defaultValue: {}
  },
  ipfsHash: {
    type: Sequelize.STRING
  }
});

const Collaboration = sequelize.define('Collaboration', {
  id: {
    type: Sequelize.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: Sequelize.STRING,
    allowNull: false
  },
  description: {
    type: Sequelize.TEXT
  },
  type: {
    type: Sequelize.ENUM('project', 'study_group', 'research', 'general'),
    defaultValue: 'general'
  },
  status: {
    type: Sequelize.ENUM('active', 'paused', 'completed', 'archived'),
    defaultValue: 'active'
  },
  visibility: {
    type: Sequelize.ENUM('public', 'private', 'restricted'),
    defaultValue: 'private'
  },
  creatorId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  settings: {
    type: Sequelize.JSON,
    defaultValue: {}
  },
  ipfsHash: {
    type: Sequelize.STRING
  }
});

const Document = sequelize.define('Document', {
  id: {
    type: Sequelize.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  title: {
    type: Sequelize.STRING,
    allowNull: false
  },
  content: {
    type: Sequelize.TEXT
  },
  type: {
    type: Sequelize.ENUM('text', 'markdown', 'code', 'data', 'image', 'pdf', 'other'),
    defaultValue: 'text'
  },
  authorId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  ipfsHash: {
    type: Sequelize.STRING
  },
  version: {
    type: Sequelize.INTEGER,
    defaultValue: 1
  },
  parentId: {
    type: Sequelize.INTEGER
  }
});

const PeerReview = sequelize.define('PeerReview', {
  id: {
    type: Sequelize.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  documentId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  reviewerId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  rating: {
    type: Sequelize.INTEGER,
    validate: {
      min: 1,
      max: 5
    }
  },
  comments: {
    type: Sequelize.TEXT
  },
  status: {
    type: Sequelize.ENUM('pending', 'completed', 'rejected'),
    defaultValue: 'pending'
  },
  data: {
    type: Sequelize.JSON,
    defaultValue: {}
  }
});

const Message = sequelize.define('Message', {
  id: {
    type: Sequelize.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  content: {
    type: Sequelize.TEXT,
    allowNull: false
  },
  type: {
    type: Sequelize.ENUM('text', 'file', 'image', 'system'),
    defaultValue: 'text'
  },
  senderId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  targetType: {
    type: Sequelize.ENUM('user', 'course', 'research', 'collaboration'),
    allowNull: false
  },
  targetId: {
    type: Sequelize.INTEGER,
    allowNull: false
  },
  metadata: {
    type: Sequelize.JSON,
    defaultValue: {}
  },
  isRead: {
    type: Sequelize.BOOLEAN,
    defaultValue: false
  }
});

// Define associations
User.hasMany(Course, { foreignKey: 'instructorId' });
Course.belongsTo(User, { foreignKey: 'instructorId', as: 'instructor' });

User.hasMany(ResearchProject, { foreignKey: 'leaderId' });
ResearchProject.belongsTo(User, { foreignKey: 'leaderId', as: 'leader' });

User.hasMany(Collaboration, { foreignKey: 'creatorId' });
Collaboration.belongsTo(User, { foreignKey: 'creatorId', as: 'creator' });

User.hasMany(Document, { foreignKey: 'authorId' });
Document.belongsTo(User, { foreignKey: 'authorId', as: 'author' });

User.hasMany(PeerReview, { foreignKey: 'reviewerId' });
PeerReview.belongsTo(User, { foreignKey: 'reviewerId', as: 'reviewer' });

Document.hasMany(PeerReview, { foreignKey: 'documentId' });
PeerReview.belongsTo(Document, { foreignKey: 'documentId' });

User.hasMany(Message, { foreignKey: 'senderId' });
Message.belongsTo(User, { foreignKey: 'senderId', as: 'sender' });

// Junction tables for many-to-many relationships
const CourseStudents = sequelize.define('CourseStudents', {
  courseId: {
    type: Sequelize.INTEGER,
    references: {
      model: Course,
      key: 'id'
    }
  },
  studentId: {
    type: Sequelize.INTEGER,
    references: {
      model: User,
      key: 'id'
    }
  },
  enrolledAt: {
    type: Sequelize.DATE,
    defaultValue: Sequelize.NOW
  },
  progress: {
    type: Sequelize.INTEGER,
    defaultValue: 0
  }
});

const ResearchCollaborators = sequelize.define('ResearchCollaborators', {
  projectId: {
    type: Sequelize.INTEGER,
    references: {
      model: ResearchProject,
      key: 'id'
    }
  },
  collaboratorId: {
    type: Sequelize.INTEGER,
    references: {
      model: User,
      key: 'id'
    }
  },
  role: {
    type: Sequelize.STRING,
    defaultValue: 'collaborator'
  },
  joinedAt: {
    type: Sequelize.DATE,
    defaultValue: Sequelize.NOW
  }
});

const CollaborationMembers = sequelize.define('CollaborationMembers', {
  collaborationId: {
    type: Sequelize.INTEGER,
    references: {
      model: Collaboration,
      key: 'id'
    }
  },
  memberId: {
    type: Sequelize.INTEGER,
    references: {
      model: User,
      key: 'id'
    }
  },
  role: {
    type: Sequelize.STRING,
    defaultValue: 'member'
  },
  joinedAt: {
    type: Sequelize.DATE,
    defaultValue: Sequelize.NOW
  }
});

// Set up associations
Course.belongsToMany(User, { 
  through: CourseStudents, 
  as: 'students', 
  foreignKey: 'courseId', 
  otherKey: 'studentId' 
});

User.belongsToMany(Course, { 
  through: CourseStudents, 
  as: 'enrolledCourses', 
  foreignKey: 'studentId', 
  otherKey: 'courseId' 
});

ResearchProject.belongsToMany(User, { 
  through: ResearchCollaborators, 
  as: 'collaborators', 
  foreignKey: 'projectId', 
  otherKey: 'collaboratorId' 
});

User.belongsToMany(ResearchProject, { 
  through: ResearchCollaborators, 
  as: 'researchProjects', 
  foreignKey: 'collaboratorId', 
  otherKey: 'projectId' 
});

Collaboration.belongsToMany(User, { 
  through: CollaborationMembers, 
  as: 'members', 
  foreignKey: 'collaborationId', 
  otherKey: 'memberId' 
});

User.belongsToMany(Collaboration, { 
  through: CollaborationMembers, 
  as: 'collaborations', 
  foreignKey: 'memberId', 
  otherKey: 'collaborationId' 
});

async function initializeDatabase() {
  try {
    console.log('🔄 Initializing database...');
    
    // Check if database already has users
    let shouldReinitialize = true;
    try {
      await sequelize.authenticate();
      const userCount = await User.count();
      if (userCount > 0) {
        console.log(`✅ Database already contains ${userCount} users, skipping initialization`);
        shouldReinitialize = false;
      }
    } catch (error) {
      console.log('📊 Database needs initialization');
    }
    
    if (shouldReinitialize) {
      // Create database and tables
      await sequelize.sync({ force: true });
      console.log('✅ Database tables created');
      
      // Create default admin user
      const hashedPassword = await bcrypt.hash('admin123', 10);
      const adminUser = await User.create({
        username: 'admin',
        email: 'admin@descios.org',
        password: hashedPassword,
        role: 'admin',
        profile: {
          name: 'Admin User',
          institution: 'DeSciOS',
          bio: 'System Administrator'
        },
        isActive: true
      });
      
      console.log('✅ Default admin user created');
      console.log('📧 Admin email: admin@descios.org');
      console.log('🔑 Admin password: admin123');
      
      // Create sample instructor
      const instructorPassword = await bcrypt.hash('instructor123', 10);
      const instructor = await User.create({
        username: 'janesmith',
        email: 'instructor@descios.org',
        password: instructorPassword,
        role: 'instructor',
        profile: {
          name: 'Dr. Jane Smith',
          institution: 'DeSciOS University',
          bio: 'Computer Science Professor'
        },
        isActive: true
      });
      
      // Create sample researcher
      const researcherPassword = await bcrypt.hash('researcher123', 10);
      const researcher = await User.create({
        username: 'johndoe',
        email: 'researcher@descios.org',
        password: researcherPassword,
        role: 'researcher',
        profile: {
          name: 'Dr. John Doe',
          institution: 'DeSciOS Research Institute',
          bio: 'Data Science Researcher'
        },
        isActive: true
      });
      
      // Create sample student
      const studentPassword = await bcrypt.hash('student123', 10);
      const student = await User.create({
        username: 'alicejohnson',
        email: 'student@descios.org',
        password: studentPassword,
        role: 'student',
        profile: {
          name: 'Alice Johnson',
          institution: 'DeSciOS University',
          bio: 'Computer Science Student'
        },
        isActive: true
      });
      
      console.log('✅ Sample users created');
      
      // Create sample course
      const course = await Course.create({
        title: 'Introduction to Decentralized Science',
        description: 'Learn about decentralized science, IPFS, and collaborative research.',
        category: 'science',
        status: 'active',
        instructorId: instructor.id,
        content: [
          {
            type: 'lesson',
            title: 'What is DeSci?',
            content: 'Introduction to decentralized science and its principles.'
          },
          {
            type: 'lesson',
            title: 'IPFS and Distributed Storage',
            content: 'Understanding IPFS and how it enables decentralized storage.'
          }
        ],
        settings: {
          enrollmentOpen: true,
          maxStudents: 100
        }
      });
      
      // Enroll student in course
      await course.addStudent(student);
      
      console.log('✅ Sample course created');
      
      // Create sample research project
      const research = await ResearchProject.create({
        title: 'Blockchain in Scientific Publishing',
        description: 'Exploring the use of blockchain technology in scientific publishing.',
        category: 'research',
        status: 'active',
        visibility: 'public',
        leaderId: researcher.id,
        data: {
          methodology: 'Mixed methods research',
          timeline: '6 months',
          budget: 50000
        }
      });
      
      // Add collaborator to research
      await research.addCollaborator(instructor);
      
      console.log('✅ Sample research project created');
      
      // Create sample collaboration
      const collaboration = await Collaboration.create({
        name: 'DeSci Development Team',
        description: 'Collaborative workspace for DeSci platform development.',
        type: 'project',
        status: 'active',
        visibility: 'private',
        creatorId: adminUser.id,
        settings: {
          allowFileSharing: true,
          allowMessaging: true
        }
      });
      
      // Add members to collaboration
      await collaboration.addMembers([instructor, researcher, student]);
      
      console.log('✅ Sample collaboration created');
    }
    
    console.log('🎉 Database initialization completed successfully!');
    console.log('🚀 You can now start the academic platform');
    
  } catch (error) {
    console.error('❌ Database initialization failed:', error);
    process.exit(1);
  } finally {
    await sequelize.close();
  }
}

// Run initialization if called directly
if (require.main === module) {
  initializeDatabase();
}

module.exports = { initializeDatabase }; 