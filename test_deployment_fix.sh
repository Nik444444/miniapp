#!/bin/bash

# Test deployment configuration for Telegram Mini App
echo "🚀 Testing Deployment Configuration for Telegram Mini App"
echo "======================================================="

# Test 1: Check if emergentintegrations has been removed from requirements.txt
echo "📋 Checking requirements.txt for emergentintegrations..."
if grep -q "emergentintegrations" /app/backend/requirements.txt; then
    echo "❌ ERROR: emergentintegrations found in requirements.txt"
    echo "   This will cause deployment failure!"
    exit 1
else
    echo "✅ GOOD: emergentintegrations not in requirements.txt"
fi

# Test 2: Check Dockerfile has emergentintegrations installation
echo ""
echo "🐳 Checking Dockerfile for emergentintegrations installation..."
if grep -q "pip install emergentintegrations --extra-index-url" /app/Dockerfile; then
    echo "✅ GOOD: Dockerfile has emergentintegrations installation with correct index URL"
else
    echo "❌ ERROR: Dockerfile missing emergentintegrations installation"
    exit 1
fi

# Test 3: Test installing packages from requirements.txt
echo ""
echo "📦 Testing pip install from requirements.txt..."
cd /app/backend
pip install --dry-run -r requirements.txt > /tmp/pip_test.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ GOOD: All packages in requirements.txt can be installed"
else
    echo "❌ ERROR: Issue with requirements.txt packages"
    echo "Last few lines of error:"
    tail -10 /tmp/pip_test.log
    exit 1
fi

# Test 4: Check if services are running
echo ""
echo "⚙️ Checking service status..."
sudo supervisorctl status

# Test 5: Test backend health
echo ""
echo "🏥 Testing backend health..."
curl -s http://localhost:8001/health | jq .

# Test 6: Check AI recruiter endpoints are accessible
echo ""
echo "🤖 Testing AI recruiter endpoints (should require auth)..."
for endpoint in "/api/ai-recruiter/profile" "/api/ai-recruiter/start" "/api/ai-recruiter/continue"; do
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001$endpoint")
    if [ "$status_code" = "403" ] || [ "$status_code" = "401" ]; then
        echo "✅ $endpoint correctly requires authentication ($status_code)"
    else
        echo "⚠️ $endpoint returned unexpected status: $status_code"
    fi
done

echo ""
echo "🎉 DEPLOYMENT CONFIGURATION TEST COMPLETE!"
echo "The deployment should now work without the emergentintegrations error."
echo ""
echo "Next steps:"
echo "1. Deploy to fly.io: flyctl deploy"
echo "2. Test the deployed application"
echo "3. Verify AI recruiter functionality works in Telegram Mini App"