#!/bin/bash

# DeSciOS Academic Platform - Dockerfile Verification Script
# This script verifies that all critical files and fixes are present before building

echo "🔍 Verifying DeSciOS Academic Platform files for Docker build..."

# Check if critical files exist
CRITICAL_FILES=(
    "node/start-academic.sh"
    "node/ensure-admin.js"
    "node/src/services/ipfs.js"
    "node/src/services/database.js"
    "node/src/routes/auth.js"
    "node/src/routes/users.js"
    "node/src/routes/ipfs.js"
    "node/src/scripts/init-db.js"
    "node/src/server.js"
    "node/package.json"
    "node/frontend/package.json"
    "supervisord.conf"
    "Dockerfile"
)

echo "📁 Checking critical files..."
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Check if IPFS service has the POST fix
echo ""
echo "🔧 Checking IPFS service fix..."
if grep -q "axios.post(\`\${this.apiBase}/id\`)" node/src/services/ipfs.js; then
    echo "✅ IPFS service has POST fix for /id endpoint"
else
    echo "❌ IPFS service missing POST fix for /id endpoint"
    exit 1
fi

if grep -q "axios.post(\`\${this.apiBase}/version\`)" node/src/services/ipfs.js; then
    echo "✅ IPFS service has POST fix for /version endpoint"
else
    echo "❌ IPFS service missing POST fix for /version endpoint"
    exit 1
fi

if grep -q "axios.post(\`\${this.apiBase}/stats/repo\`)" node/src/services/ipfs.js; then
    echo "✅ IPFS service has POST fix for /stats/repo endpoint"
else
    echo "❌ IPFS service missing POST fix for /stats/repo endpoint"
    exit 1
fi

# Check if auth routes accept email for login
echo ""
echo "🔐 Checking auth routes..."
if grep -q "body('email').isEmail()" node/src/routes/auth.js; then
    echo "✅ Auth routes accept email for login"
else
    echo "❌ Auth routes missing email fix"
    exit 1
fi

# Check if database service uses DATABASE_PATH
echo ""
echo "🗄️ Checking database service..."
if grep -q "process.env.DATABASE_PATH" node/src/services/database.js; then
    echo "✅ Database service uses DATABASE_PATH environment variable"
else
    echo "❌ Database service missing DATABASE_PATH fix"
    exit 1
fi

# Check if supervisord.conf has academic platform
echo ""
echo "⚙️ Checking supervisord configuration..."
if grep -q "academic-platform" supervisord.conf; then
    echo "✅ Supervisord configured for academic platform"
else
    echo "❌ Supervisord missing academic platform configuration"
    exit 1
fi

# Check if Dockerfile has academic platform installation
echo ""
echo "🐳 Checking Dockerfile..."
if grep -q "Academic Platform" Dockerfile; then
    echo "✅ Dockerfile includes academic platform installation"
else
    echo "❌ Dockerfile missing academic platform installation"
    exit 1
fi

# Check if frontend has all necessary files
echo ""
echo "🎨 Checking frontend files..."
FRONTEND_FILES=(
    "node/frontend/public/index.html"
    "node/frontend/src/index.js"
    "node/frontend/src/App.js"
    "node/frontend/src/pages/Dashboard.js"
    "node/frontend/src/pages/Login.js"
    "node/frontend/src/components/Layout.js"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🎯 Dockerfile Verification Summary:"
echo "=================================="
echo "✅ All critical files present"
echo "✅ IPFS service has POST fix"
echo "✅ Auth routes accept email"
echo "✅ Database service uses DATABASE_PATH"
echo "✅ Supervisord configured"
echo "✅ Dockerfile includes academic platform"
echo "✅ Frontend files complete"
echo ""
echo "🚀 Ready for Docker build!"
echo ""
echo "To build the image:"
echo "docker build -t descios ."
echo ""
echo "To run the container:"
echo "docker run -d --name descios-new -p 6080:6080 -p 8000:8000 -p 5001:5001 -p 8080:8080 descios" 