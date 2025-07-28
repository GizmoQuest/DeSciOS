# DeSciOS Academic Platform - Testing Guide

## Overview
This guide will help you test the updated DeSciOS Academic Platform with all newly implemented features. The platform now includes complete Course, Research, Collaboration, User Management, IPFS Manager, and Settings functionality.

## Prerequisites
- Docker installed on your system
- Access to the DeSciOS codebase
- Web browser (Firefox recommended for DeSciOS environment)

## Step 1: Build and Deploy the Updated Platform

### 1.1 Build the Docker Image
```bash
# From the DeSciOS root directory
docker build -t descios:latest .
```

### 1.2 Run the Container
```bash
docker run -d \
  --name descios \
  -p 6080:6080 \
  -p 8000:8000 \
  -p 5001:5001 \
  descios:latest
```

### 1.3 Wait for Services to Start
```bash
# Wait 30 seconds for all services to initialize
sleep 30

# Verify deployment (optional)
docker cp verify-container.sh descios:/tmp/
docker exec descios chmod +x /tmp/verify-container.sh
docker exec descios /tmp/verify-container.sh
```

## Step 2: Access the Platform

### 2.1 Access DeSciOS Desktop
- Open your browser and navigate to: `http://localhost:6080`
- You should see the DeSciOS desktop environment

### 2.2 Launch Academic Platform
- In the DeSciOS desktop, look for the "Academic Platform" desktop icon
- Double-click to launch Firefox with the platform
- Or manually open Firefox and navigate to: `http://localhost:8000`

## Step 3: Authentication Testing

### 3.1 Login with Admin Account
- **Email**: `admin@descios.org`
- **Password**: `admin123`
- Verify you can successfully log in
- Check that the dashboard loads with statistics

### 3.2 Test Notification System
- Click the notification bell (should show a number)
- Verify dropdown appears with notifications
- Test marking individual notifications as read
- Test "Mark all as read" functionality
- Refresh page and verify notification state persists

## Step 4: Course Management Testing

### 4.1 Create a New Course
1. Navigate to **Courses** in the sidebar
2. Click **"Create New Course"**
3. Fill out the form:
   - **Title**: "Introduction to DeSciOS"
   - **Description**: "Learn about decentralized science operating systems"
   - **Category**: "Computer Science"
   - **Difficulty**: "Beginner"
   - **Visibility**: "Public"
4. Add syllabus items:
   - Click **"Add Syllabus Item"**
   - Add: "Week 1: Introduction to DeSciOS"
   - Add: "Week 2: IPFS Integration"
5. Upload a course resource file (optional)
6. Click **"Create Course"**

### 4.2 View Course Details
1. Click on the created course from the courses list
2. Verify all course information is displayed correctly
3. Test the **"Enroll"** button (if not the instructor)
4. Verify course resources are listed (if uploaded)
5. Test **"Download"** functionality for resources

### 4.3 Edit Course (as Instructor/Admin)
1. In course details, click **"Edit Course"**
2. Modify some fields
3. Save changes
4. Verify changes are reflected

## Step 5: Research Management Testing

### 5.1 Create a Research Project
1. Navigate to **Research** in the sidebar
2. Click **"Create New Research"**
3. Fill out the form:
   - **Title**: "DeSciOS Performance Analysis"
   - **Description**: "Analyzing the performance of DeSciOS in academic environments"
   - **Field**: "Computer Science"
   - **Keywords**: Add "DeSciOS", "Performance", "Academic"
   - **Status**: "In Progress"
   - **Visibility**: "Public"
4. Add methodology and findings
5. Upload a dataset file (optional)
6. Click **"Create Research"**

### 5.2 View Research Details
1. Click on the created research project
2. Verify all project information is displayed
3. Test dataset download functionality
4. Verify publications list

### 5.3 Test Research Filters
1. Use the search bar to find projects
2. Test status filter (All, In Progress, Completed, etc.)
3. Test field filter
4. Switch between "All Projects" and "My Projects"

## Step 6: Collaboration Testing

### 6.1 Create a Collaboration Workspace
1. Navigate to **Collaboration** in the sidebar
2. Click **"Create New Workspace"**
3. Fill out the form:
   - **Title**: "DeSciOS Development Team"
   - **Description**: "Collaborative workspace for DeSciOS development"
   - **Type**: "Research"
   - **Visibility**: "Private"
4. Upload initial documents (optional)
5. Click **"Create Workspace"**

### 6.2 View Collaboration Details
1. Click on the created workspace
2. Verify workspace information is displayed
3. Check the **Members** tab
4. Check the **Documents** tab
5. Test document download functionality

### 6.3 Test Collaboration Filters
1. Use search functionality
2. Test status and type filters
3. Switch between "All Workspaces" and "My Workspaces"

## Step 7: User Management Testing (Admin Only)

### 7.1 View User Management
1. Navigate to **Users** in the sidebar (admin only)
2. Verify user table is displayed
3. Check user statistics cards
4. Test search functionality
5. Test role and status filters

### 7.2 Edit User (Admin Only)
1. Click **"Edit"** on a user row
2. Modify user details
3. Save changes
4. Verify changes are reflected

## Step 8: IPFS Manager Testing

### 8.1 View IPFS Statistics
1. Navigate to **IPFS Manager** in the sidebar
2. Verify IPFS node statistics are displayed:
   - Repository size
   - Number of objects
   - Number of peers
   - Number of pinned files

### 8.2 Test File Management
1. Go to **"All Files"** tab
2. Upload a test file
3. Verify file appears in the list
4. Test **"Download"** functionality
5. Test **"Copy Hash"** functionality
6. Test **"Pin"** functionality

### 8.3 Test Pinned Files
1. Go to **"Pinned Files"** tab
2. Verify pinned files are listed
3. Test **"Unpin"** functionality
4. Test **"Delete"** functionality

### 8.4 Test Search
1. Use the search bar to find files
2. Verify search results are accurate

## Step 9: Profile and Settings Testing

### 9.1 View Profile
1. Click on your username in the top-right corner
2. Select **"Profile"**
3. Verify profile information is displayed
4. Check statistics section

### 9.2 Edit Profile
1. Click **"Edit Profile"**
2. Modify personal information
3. Save changes
4. Verify changes are reflected

### 9.3 Test Settings
1. Navigate to **Settings** in the sidebar
2. Test **Account** tab:
   - Toggle notification settings
   - Change language/timezone
3. Test **Privacy** tab:
   - Toggle profile visibility
   - Toggle email visibility
4. Test **Appearance** tab:
   - Toggle theme settings
   - Toggle compact mode
5. Test **Security** tab:
   - Verify settings are displayed

## Step 10: Error Handling Testing

### 10.1 Test Invalid Login
1. Try logging in with wrong credentials
2. Verify error message is displayed

### 10.2 Test Form Validation
1. Try submitting forms with missing required fields
2. Verify validation messages appear

### 10.3 Test Network Errors
1. Temporarily stop the backend service
2. Try to access platform features
3. Verify error handling works correctly

## Step 11: Performance Testing

### 11.1 Test Page Load Times
1. Navigate between different pages
2. Verify pages load within reasonable time
3. Test with multiple browser tabs

### 11.2 Test Data Loading
1. Create multiple courses/research projects
2. Verify lists load efficiently
3. Test pagination if implemented

## Step 12: Cross-Browser Testing

### 12.1 Test in Different Browsers
1. Test in Firefox (primary)
2. Test in Chrome (if available)
3. Verify consistent functionality

## Expected Results

### ✅ Successful Tests Should Show:
- All pages load without errors
- Forms submit successfully
- Data is displayed correctly
- File uploads/downloads work
- Search and filter functionality works
- Navigation is smooth
- Error messages are helpful
- Settings persist across sessions

### ❌ Issues to Report:
- Pages not loading
- Forms not submitting
- Data not displaying
- File operations failing
- Search/filter not working
- Navigation errors
- Missing error handling
- Settings not persisting

## Troubleshooting

### Common Issues:

1. **Platform not accessible**
   - Check if container is running: `docker ps`
   - Check if port 8000 is exposed: `docker port descios`
   - Restart container if needed: `docker restart descios`

2. **Login issues**
   - Verify admin credentials: `admin@descios.org` / `admin123`
   - Check backend logs: `docker logs descios`

3. **File upload issues**
   - Check IPFS daemon: `docker exec descios ipfs id`
   - Verify IPFS API is accessible

4. **Database issues**
   - Check database file: `docker exec descios ls -la /home/deScier/.academic/`
   - Reinitialize if needed: `docker exec descios node /home/deScier/DeSciOS/node/ensure-admin.js`

## Reporting Results

After completing the tests, please report:
1. Which features worked correctly
2. Any issues encountered
3. Performance observations
4. Suggestions for improvements

This will help ensure the platform is fully functional and ready for production use. 