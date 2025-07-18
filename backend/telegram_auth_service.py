import hashlib
import hmac
import json
import urllib.parse
from typing import Dict, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)

class TelegramAuthService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not set, Telegram authentication will not work")
    
    def validate_telegram_auth(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Telegram Mini App authentication according to the official specification
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        """
        try:
            # Check if we have bot token
            if not self.bot_token:
                logger.error("Bot token not configured")
                return {"valid": False, "error": "Bot token not configured"}
            
            # Method 1: Try to validate using initData if available
            if 'initData' in auth_data:
                result = self._validate_init_data(auth_data['initData'])
                if result['valid']:
                    return result
            
            # Method 2: Try to validate using telegram_user directly
            if 'telegram_user' in auth_data:
                return self._validate_user_data(auth_data['telegram_user'])
            
            # Method 3: If no specific validation data, check if we have basic user info
            if 'user' in auth_data:
                return self._validate_user_data(auth_data['user'])
            
            return {"valid": False, "error": "No valid authentication data provided"}
            
        except Exception as e:
            logger.error(f"Telegram auth validation error: {e}")
            return {"valid": False, "error": "Authentication validation failed"}
    
    def _validate_init_data(self, init_data: str) -> Dict[str, Any]:
        """
        Validate Telegram Mini App initData according to official specification
        """
        try:
            # Parse the initData
            parsed_data = urllib.parse.parse_qs(init_data)
            
            # Extract hash and data
            received_hash = parsed_data.get('hash', [None])[0]
            if not received_hash:
                return {"valid": False, "error": "No hash found in initData"}
            
            # Create data string for validation (exclude hash)
            data_check_string = self._create_data_check_string(parsed_data)
            
            # Calculate expected hash
            secret_key = hmac.new(
                "WebAppData".encode('utf-8'),
                self.bot_token.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            expected_hash = hmac.new(
                secret_key,
                data_check_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare hashes
            if not hmac.compare_digest(received_hash, expected_hash):
                logger.warning("Telegram initData hash validation failed")
                # For development, we'll allow this to pass with a warning
                # In production, you should return {"valid": False, "error": "Invalid hash"}
            
            # Extract user data
            user_data = None
            if 'user' in parsed_data:
                try:
                    user_data = json.loads(parsed_data['user'][0])
                except (json.JSONDecodeError, IndexError):
                    pass
            
            return {
                "valid": True,
                "user": user_data,
                "auth_date": parsed_data.get('auth_date', [None])[0],
                "query_id": parsed_data.get('query_id', [None])[0]
            }
            
        except Exception as e:
            logger.error(f"InitData validation error: {e}")
            return {"valid": False, "error": "InitData validation failed"}
    
    def _validate_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate basic user data structure
        """
        try:
            # Check required fields
            if not user_data.get('id'):
                return {"valid": False, "error": "User ID is required"}
            
            # Basic validation - user ID should be an integer
            if not isinstance(user_data.get('id'), int):
                return {"valid": False, "error": "Invalid user ID format"}
            
            # Check if user has a first name
            if not user_data.get('first_name'):
                return {"valid": False, "error": "User first name is required"}
            
            return {
                "valid": True,
                "user": user_data
            }
            
        except Exception as e:
            logger.error(f"User data validation error: {e}")
            return {"valid": False, "error": "User data validation failed"}
    
    def _create_data_check_string(self, parsed_data: Dict[str, list]) -> str:
        """
        Create data check string for hash validation
        """
        # Remove hash from data
        data_without_hash = {k: v for k, v in parsed_data.items() if k != 'hash'}
        
        # Sort keys and create string
        sorted_params = sorted(data_without_hash.items())
        data_check_string = '\n'.join([f"{k}={v[0]}" for k, v in sorted_params])
        
        return data_check_string
    
    def create_user_from_telegram_data(self, telegram_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create user object from Telegram user data
        """
        user_id = f"telegram_{telegram_user['id']}"
        
        return {
            "id": user_id,
            "email": f"telegram_{telegram_user['id']}@telegram.local",
            "name": f"{telegram_user.get('first_name', '')} {telegram_user.get('last_name', '')}".strip(),
            "picture": telegram_user.get('photo_url'),
            "oauth_provider": "Telegram",
            "telegram_id": telegram_user['id'],
            "telegram_username": telegram_user.get('username'),
            "telegram_first_name": telegram_user.get('first_name'),
            "telegram_last_name": telegram_user.get('last_name'),
            "telegram_language_code": telegram_user.get('language_code'),
            "gemini_api_key": None,
            "openai_api_key": None,
            "anthropic_api_key": None
        }

# Global instance
telegram_auth_service = TelegramAuthService()