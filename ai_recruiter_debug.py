#!/usr/bin/env python3
"""
🎯 AI RECRUITER DEBUG ANALYSIS

This script will add debug logging to understand exactly where the error is coming from
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_ai_recruiter():
    """Debug AI recruiter with detailed logging"""
    
    # Get backend URL
    frontend_env_path = Path("/app/frontend/.env")
    backend_url = "https://miniapp-wvsxfa.fly.dev"
    
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    break
    
    logger.info(f"🔍 Debug AI Recruiter at: {backend_url}")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Authenticate
        telegram_auth_data = {
            "telegram_user": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User", 
                "username": "testuser",
                "language_code": "ru"
            }
        }
        
        logger.debug("🔐 Authenticating...")
        async with session.post(f"{backend_url}/api/auth/telegram/verify", json=telegram_auth_data) as response:
            auth_data = await response.json()
            auth_token = auth_data.get("access_token")
            logger.debug(f"Auth response: {auth_data}")
            
        if not auth_token:
            logger.error("❌ Failed to get auth token")
            return
            
        logger.info("✅ Authentication successful")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Step 2: Test AI recruiter start with detailed logging
        logger.info("\n🔍 Testing POST /api/ai-recruiter/start with debug...")
        start_data = {"user_language": "ru"}
        
        logger.debug(f"Request URL: {backend_url}/api/ai-recruiter/start")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request data: {start_data}")
        
        async with session.post(f"{backend_url}/api/ai-recruiter/start", json=start_data, headers=headers) as response:
            logger.debug(f"Response status: {response.status}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            start_response = await response.json()
            logger.debug(f"Raw response: {start_response}")
            
            logger.info(f"🚀 Start Response: {json.dumps(start_response, indent=2, ensure_ascii=False)}")
            
            # Analyze the error in detail
            if start_response.get("status") == "error":
                error_message = start_response.get("message", "")
                error_details = start_response.get("error", "")
                
                logger.error(f"❌ AI RECRUITER START ERROR ANALYSIS:")
                logger.error(f"   Status: {start_response.get('status')}")
                logger.error(f"   Message: {error_message}")
                logger.error(f"   Error: {error_details}")
                logger.error(f"   All keys: {list(start_response.keys())}")
                
                # Check if this is the exact error user is experiencing
                if "unavailable" in error_message.lower() or "disabled" in error_details.lower():
                    logger.error("🎯 THIS IS THE SERVICE UNAVAILABLE ERROR!")
                    logger.error("🔍 This suggests the AI recruiter service is hardcoded to return this error")
                    logger.error("🔍 Need to check if there's a service availability flag or feature toggle")

if __name__ == "__main__":
    asyncio.run(debug_ai_recruiter())