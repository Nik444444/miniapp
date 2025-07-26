#!/usr/bin/env python3
"""
Test script to verify AI Recruiter functionality after fixing API endpoints
"""

import asyncio
import aiohttp
import json
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ai_recruiter_endpoints():
    """Test AI Recruiter endpoints for functionality"""
    
    backend_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health check
        logger.info("🏥 Testing backend health...")
        try:
            async with session.get(f"{backend_url}/health") as response:
                health_data = await response.json()
                logger.info(f"✅ Health check: {health_data.get('status', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
        
        # Test 2: AI Recruiter endpoints (should require auth)
        logger.info("\n🤖 Testing AI Recruiter endpoints (should require auth)...")
        
        # Test without auth token (should get 401/403)
        test_endpoints = [
            ("/api/ai-recruiter/profile", "GET"),
            ("/api/ai-recruiter/start", "POST"),
            ("/api/ai-recruiter/continue", "POST")
        ]
        
        auth_required_count = 0
        
        for endpoint, method in test_endpoints:
            try:
                if method == "GET":
                    async with session.get(f"{backend_url}{endpoint}") as response:
                        status = response.status
                        if status in [401, 403]:
                            logger.info(f"✅ {endpoint} correctly requires authentication (Status: {status})")
                            auth_required_count += 1
                        else:
                            logger.warning(f"⚠️ {endpoint} returned unexpected status: {status}")
                
                elif method == "POST":
                    test_data = {"user_language": "ru"} if "start" in endpoint else {"user_message": "test"}
                    async with session.post(f"{backend_url}{endpoint}", json=test_data) as response:
                        status = response.status
                        if status in [401, 403]:
                            logger.info(f"✅ {endpoint} correctly requires authentication (Status: {status})")
                            auth_required_count += 1
                        else:
                            logger.warning(f"⚠️ {endpoint} returned unexpected status: {status}")
                            
            except Exception as e:
                logger.error(f"❌ Error testing {endpoint}: {e}")
        
        # Test 3: Check other AI job assistant endpoints
        logger.info("\n💼 Testing job assistant endpoints...")
        
        job_endpoints = [
            "/api/job-compatibility",
            "/api/translate-job", 
            "/api/generate-cover-letter",
            "/api/ai-job-recommendations"
        ]
        
        job_auth_count = 0
        
        for endpoint in job_endpoints:
            try:
                test_data = {"job_description": "test", "user_profile": "test"}
                async with session.post(f"{backend_url}{endpoint}", json=test_data) as response:
                    status = response.status
                    if status in [401, 403]:
                        logger.info(f"✅ {endpoint} correctly requires authentication (Status: {status})")
                        job_auth_count += 1
                    else:
                        logger.warning(f"⚠️ {endpoint} returned unexpected status: {status}")
                        
            except Exception as e:
                logger.error(f"❌ Error testing {endpoint}: {e}")
        
        # Test 4: Check telegram notifications endpoint
        logger.info("\n📱 Testing telegram notifications endpoint...")
        
        try:
            test_data = {"message": "test", "user_id": "test"}
            async with session.post(f"{backend_url}/api/telegram-notifications/send", json=test_data) as response:
                status = response.status
                if status in [401, 403]:
                    logger.info(f"✅ telegram-notifications/send correctly requires authentication (Status: {status})")
                else:
                    logger.warning(f"⚠️ telegram-notifications/send returned unexpected status: {status}")
                    
        except Exception as e:
            logger.error(f"❌ Error testing telegram notifications: {e}")
        
        # Summary
        logger.info(f"\n📊 Test Summary:")
        logger.info(f"✅ AI Recruiter endpoints with auth: {auth_required_count}/3")
        logger.info(f"✅ Job Assistant endpoints with auth: {job_auth_count}/4") 
        
        if auth_required_count == 3 and job_auth_count == 4:
            logger.info("🎉 ALL AI RECRUITER ENDPOINTS ARE PROPERLY CONFIGURED!")
            return True
        else:
            logger.error("❌ Some endpoints may have issues")
            return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting AI Recruiter endpoint test...")
    
    success = await test_ai_recruiter_endpoints()
    
    if success:
        logger.info("\n✅ AI RECRUITER FIX VERIFICATION COMPLETE - ALL SYSTEMS GO!")
        sys.exit(0)
    else:
        logger.error("\n❌ AI RECRUITER FIX VERIFICATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())