#!/usr/bin/env python3
"""
🎯 AI RECRUITER DETAILED ERROR ANALYSIS

This script will examine the exact error messages returned by AI recruiter endpoints
to understand why users are getting "Ошибка запуска AI рекрутера"
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def analyze_ai_recruiter_errors():
    """Analyze detailed error responses from AI recruiter endpoints"""
    
    # Get backend URL
    frontend_env_path = Path("/app/frontend/.env")
    backend_url = "https://miniapp-wvsxfa.fly.dev"
    
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.split('=', 1)[1].strip()
                    break
    
    logger.info(f"🔍 Analyzing AI Recruiter errors at: {backend_url}")
    
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
        
        async with session.post(f"{backend_url}/api/auth/telegram/verify", json=telegram_auth_data) as response:
            auth_data = await response.json()
            auth_token = auth_data.get("access_token")
            
        if not auth_token:
            logger.error("❌ Failed to get auth token")
            return
            
        logger.info("✅ Authentication successful")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Step 2: Test AI recruiter profile
        logger.info("\n🔍 Testing GET /api/ai-recruiter/profile...")
        async with session.get(f"{backend_url}/api/ai-recruiter/profile", headers=headers) as response:
            profile_data = await response.json()
            logger.info(f"📋 Profile Response: {json.dumps(profile_data, indent=2, ensure_ascii=False)}")
        
        # Step 3: Test AI recruiter start
        logger.info("\n🔍 Testing POST /api/ai-recruiter/start...")
        start_data = {"user_language": "ru"}
        async with session.post(f"{backend_url}/api/ai-recruiter/start", json=start_data, headers=headers) as response:
            start_response = await response.json()
            logger.info(f"🚀 Start Response: {json.dumps(start_response, indent=2, ensure_ascii=False)}")
            
            # Analyze the error
            if start_response.get("status") == "error":
                error_message = start_response.get("message", "")
                error_details = start_response.get("error", "")
                
                logger.error(f"❌ AI RECRUITER START ERROR FOUND:")
                logger.error(f"   Message: {error_message}")
                logger.error(f"   Error: {error_details}")
                
                # Check if this matches user's reported error
                if "Ошибка запуска AI рекрутера" in error_message or "AI рекрутер" in error_message:
                    logger.error("🎯 THIS IS THE EXACT ERROR USER IS EXPERIENCING!")
                
        # Step 4: Test AI recruiter continue
        logger.info("\n🔍 Testing POST /api/ai-recruiter/continue...")
        continue_data = {
            "user_message": "Я ищу работу разработчика в Берлине",
            "conversation_data": {"conversation_id": "test_conversation", "messages": []}
        }
        async with session.post(f"{backend_url}/api/ai-recruiter/continue", json=continue_data, headers=headers) as response:
            continue_response = await response.json()
            logger.info(f"💬 Continue Response: {json.dumps(continue_response, indent=2, ensure_ascii=False)}")
            
            # Analyze the error
            if continue_response.get("status") == "error":
                error_message = continue_response.get("message", "")
                error_details = continue_response.get("error", "")
                
                logger.error(f"❌ AI RECRUITER CONTINUE ERROR FOUND:")
                logger.error(f"   Message: {error_message}")
                logger.error(f"   Error: {error_details}")

if __name__ == "__main__":
    asyncio.run(analyze_ai_recruiter_errors())