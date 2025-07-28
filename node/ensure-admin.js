#!/usr/bin/env node

const bcrypt = require('bcryptjs');
const { User } = require('./src/services/database');

async function ensureAdminUser() {
  try {
    console.log('🔍 Checking for admin user...');
    
    // Check if admin user already exists
    const existingUser = await User.findOne({
      where: { email: 'admin@descios.org' }
    });
    
    if (existingUser) {
      console.log('✅ Admin user already exists');
      return;
    }
    
    console.log('📝 Creating admin user...');
    
    // Create admin user
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
    
    console.log('✅ Admin user created successfully');
    console.log('📧 Email: admin@descios.org');
    console.log('🔑 Password: admin123');
    
  } catch (error) {
    console.error('❌ Error ensuring admin user:', error.message);
  }
}

// Run if called directly
if (require.main === module) {
  ensureAdminUser().then(() => {
    process.exit(0);
  }).catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

module.exports = { ensureAdminUser }; 