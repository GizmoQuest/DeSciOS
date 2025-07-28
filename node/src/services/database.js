const { Sequelize, DataTypes } = require('sequelize');
const path = require('path');
const fs = require('fs');

// Initialize Sequelize with SQLite
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: process.env.DATABASE_PATH || path.join(__dirname, '../data/academic_platform.db'),
  logging: process.env.NODE_ENV === 'development' ? console.log : false,
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000
  }
});

// User model
const User = sequelize.define('User', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  username: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false,
    validate: {
      len: [3, 30]
    }
  },
  email: {
    type: DataTypes.STRING,
    unique: true,
    allowNull: false,
    validate: {
      isEmail: true
    }
  },
  password: {
    type: DataTypes.STRING,
    allowNull: false
  },
  role: {
    type: DataTypes.ENUM('student', 'instructor', 'researcher', 'admin'),
    defaultValue: 'student'
  },
  profile: {
    type: DataTypes.JSON,
    defaultValue: {}
  },
  isActive: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  lastLogin: {
    type: DataTypes.DATE
  }
});

// Course model
const Course = sequelize.define('Course', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT
  },
  category: {
    type: DataTypes.STRING,
    allowNull: false
  },
  difficulty: {
    type: DataTypes.ENUM('beginner', 'intermediate', 'advanced'),
    defaultValue: 'beginner'
  },
  isPublic: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  status: {
    type: DataTypes.ENUM('draft', 'published', 'archived'),
    defaultValue: 'draft'
  },
  syllabus: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  resources: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  ipfsHash: {
    type: DataTypes.STRING // Store IPFS hash for course content
  }
});

// Research Project model
const ResearchProject = sequelize.define('ResearchProject', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT
  },
  field: {
    type: DataTypes.STRING,
    allowNull: false
  },
  keywords: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  status: {
    type: DataTypes.ENUM('proposal', 'active', 'completed', 'archived'),
    defaultValue: 'proposal'
  },
  isPublic: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  methodology: {
    type: DataTypes.TEXT
  },
  findings: {
    type: DataTypes.TEXT
  },
  datasets: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  publications: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  ipfsHash: {
    type: DataTypes.STRING // Store IPFS hash for research data
  }
});

// Collaboration model
const Collaboration = sequelize.define('Collaboration', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  title: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT
  },
  type: {
    type: DataTypes.ENUM('course', 'research', 'peer_review', 'study_group'),
    allowNull: false
  },
  status: {
    type: DataTypes.ENUM('active', 'completed', 'archived'),
    defaultValue: 'active'
  },
  documents: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  ipfsHash: {
    type: DataTypes.STRING // Store IPFS hash for collaboration files
  }
});

// Document model for version control
const Document = sequelize.define('Document', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  filename: {
    type: DataTypes.STRING,
    allowNull: false
  },
  version: {
    type: DataTypes.INTEGER,
    defaultValue: 1
  },
  size: {
    type: DataTypes.INTEGER
  },
  mimeType: {
    type: DataTypes.STRING
  },
  ipfsHash: {
    type: DataTypes.STRING,
    allowNull: false
  },
  isLatest: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  metadata: {
    type: DataTypes.JSON,
    defaultValue: {}
  }
});

// Peer Review model
const PeerReview = sequelize.define('PeerReview', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  rating: {
    type: DataTypes.INTEGER,
    validate: {
      min: 1,
      max: 5
    }
  },
  feedback: {
    type: DataTypes.TEXT
  },
  status: {
    type: DataTypes.ENUM('pending', 'submitted', 'approved', 'rejected'),
    defaultValue: 'pending'
  },
  isAnonymous: {
    type: DataTypes.BOOLEAN,
    defaultValue: true
  },
  criteria: {
    type: DataTypes.JSON,
    defaultValue: {}
  }
});

// Message model for real-time communication
const Message = sequelize.define('Message', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  content: {
    type: DataTypes.TEXT,
    allowNull: false
  },
  type: {
    type: DataTypes.ENUM('text', 'file', 'code', 'image'),
    defaultValue: 'text'
  },
  parentId: {
    type: DataTypes.UUID // For threaded conversations
  },
  metadata: {
    type: DataTypes.JSON,
    defaultValue: {}
  },
  isEdited: {
    type: DataTypes.BOOLEAN,
    defaultValue: false
  },
  ipfsHash: {
    type: DataTypes.STRING // For file messages
  }
});

// Define associations
User.hasMany(Course, { foreignKey: 'instructorId' });
Course.belongsTo(User, { foreignKey: 'instructorId', as: 'instructor' });

User.hasMany(ResearchProject, { foreignKey: 'leaderId' });
ResearchProject.belongsTo(User, { foreignKey: 'leaderId', as: 'leader' });

User.hasMany(Collaboration, { foreignKey: 'ownerId' });
Collaboration.belongsTo(User, { foreignKey: 'ownerId', as: 'owner' });

User.hasMany(Document, { foreignKey: 'uploaderId' });
Document.belongsTo(User, { foreignKey: 'uploaderId', as: 'uploader' });

User.hasMany(PeerReview, { foreignKey: 'reviewerId' });
PeerReview.belongsTo(User, { foreignKey: 'reviewerId', as: 'reviewer' });

User.hasMany(Message, { foreignKey: 'senderId' });
Message.belongsTo(User, { foreignKey: 'senderId', as: 'sender' });

// Many-to-many associations
const CourseEnrollment = sequelize.define('CourseEnrollment', {
  enrolledAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  },
  progress: {
    type: DataTypes.FLOAT,
    defaultValue: 0
  },
  completedAt: {
    type: DataTypes.DATE
  }
});

const ResearchCollaborator = sequelize.define('ResearchCollaborator', {
  role: {
    type: DataTypes.ENUM('collaborator', 'reviewer', 'advisor'),
    defaultValue: 'collaborator'
  },
  joinedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  },
  permissions: {
    type: DataTypes.JSON,
    defaultValue: {}
  }
});

const CollaborationMember = sequelize.define('CollaborationMember', {
  role: {
    type: DataTypes.ENUM('member', 'moderator', 'admin'),
    defaultValue: 'member'
  },
  joinedAt: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  },
  permissions: {
    type: DataTypes.JSON,
    defaultValue: {}
  }
});

// Set up many-to-many relationships
User.belongsToMany(Course, { through: CourseEnrollment });
Course.belongsToMany(User, { through: CourseEnrollment });

User.belongsToMany(ResearchProject, { through: ResearchCollaborator });
ResearchProject.belongsToMany(User, { through: ResearchCollaborator });

User.belongsToMany(Collaboration, { through: CollaborationMember });
Collaboration.belongsToMany(User, { through: CollaborationMember });

// Initialize database
async function initializeDatabase() {
  try {
    // Ensure data directory exists
    const dataDir = path.join(__dirname, '../data');
    if (!fs.existsSync(dataDir)) {
      fs.mkdirSync(dataDir, { recursive: true });
    }

    // Test connection
    await sequelize.authenticate();
    console.log('✅ Database connection established successfully');

    // Sync models
    await sequelize.sync({ alter: true });
    console.log('✅ Database models synchronized');

    return true;
  } catch (error) {
    console.error('❌ Unable to connect to database:', error);
    throw error;
  }
}

module.exports = {
  sequelize,
  User,
  Course,
  ResearchProject,
  Collaboration,
  Document,
  PeerReview,
  Message,
  CourseEnrollment,
  ResearchCollaborator,
  CollaborationMember,
  initializeDatabase
}; 