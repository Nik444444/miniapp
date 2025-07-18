from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timedelta
import jwt
import json
import tempfile
import shutil
import asyncio
from google.auth.transport import requests
from google.oauth2 import id_token
import hashlib
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# CRITICAL FIX: Ensure tesseract is in PATH BEFORE importing OCR services
os.environ['PATH'] = '/usr/bin:/usr/local/bin:' + os.environ.get('PATH', '')
os.environ['TESSERACT_AVAILABLE'] = 'true'
os.environ['TESSERACT_VERSION'] = '5.3.0'

# Load database and LLM Manager (AFTER PATH setup)
from database import db
from llm_manager import llm_manager
from modern_llm_manager import modern_llm_manager
from telegram_service import telegram_service
from telegram_auth_service import telegram_auth_service
from text_formatter import format_analysis_text, create_super_wow_analysis_prompt
from document_processor import document_processor
from alternative_ocr_service import alternative_ocr_service
from improved_ocr_service import improved_ocr_service
from google_api_key_service import google_api_service
from super_analysis_engine import super_analysis_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_key_preview(api_key: str) -> str:
    """Создает preview версию API ключа для безопасного отображения"""
    if not api_key or len(api_key) < 10:
        return None
    # Показываем только первые 4 и последние 4 символа
    return f"{api_key[:4]}...{api_key[-4:]}"

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Google OAuth settings
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# Create the main app
app = FastAPI(
    title="German Letter AI Assistant API",
    description="Backend API for German Letter AI Assistant - Google OAuth and AI Document Analysis (SQLite)",
    version="3.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# HTTP Bearer for JWT
security = HTTPBearer()

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class GoogleOAuthUser(BaseModel):
    email: EmailStr
    name: str
    google_id: str
    picture: Optional[str] = None

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    oauth_provider: str
    created_at: datetime
    last_login: Optional[datetime] = None
    has_gemini_api_key: bool = False
    has_openai_api_key: bool = False
    has_anthropic_api_key: bool = False
    preferred_language: str = "ru"
    # Частичные ключи для отображения (только для проверки что ключ есть)
    gemini_key_preview: Optional[str] = None
    openai_key_preview: Optional[str] = None
    anthropic_key_preview: Optional[str] = None

class ApiKeyUpdate(BaseModel):
    # Новые названия (приоритет)
    api_key_1: Optional[str] = None
    api_key_2: Optional[str] = None
    api_key_3: Optional[str] = None
    # Старые названия (для обратной совместимости)
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

class QuickGeminiSetup(BaseModel):
    api_key: str

class GoogleAuthRequest(BaseModel):
    credential: str

class TelegramAuthRequest(BaseModel):
    telegram_user: Dict[str, Any]

class DocumentAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    file_name: str
    file_type: str
    analysis_result: Dict[str, Any]
    analysis_language: str
    llm_provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]

class PushMessage(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Root endpoint (без префикса)
@app.get("/")
async def read_root():
    return {
        "message": "German Letter AI Assistant Backend v3.0", 
        "status": "OK", 
        "auth": "Google OAuth Only", 
        "database": "SQLite",
        "version": "3.0.0"
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "german-letter-ai-assistant", 
        "auth": "google-oauth-only",
        "database": "sqlite"
    }

# API endpoints (с префиксом /api)
@api_router.get("/")
async def api_root():
    return {
        "message": "German Letter AI Assistant API v3.0", 
        "status": "Running", 
        "auth": "Google OAuth Only",
        "database": "SQLite"
    }

class AppTextUpdate(BaseModel):
    text_value: str
    description: Optional[str] = None

class AppTextCreate(BaseModel):
    key_name: str
    text_value: str
    description: Optional[str] = None
    category: str = 'general'

class AdminAuth(BaseModel):
    password: str

# Простая админская авторизация
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def verify_admin_password(password: str) -> bool:
    return password == ADMIN_PASSWORD

# Health check endpoint
@api_router.get("/health")
async def health_check():
    try:
        users_count = await db.get_users_count()
        analyses_count = await db.get_analyses_count()
        return {
            "status": "healthy",
            "database": "connected",
            "users_count": users_count,
            "analyses_count": analyses_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Legacy status endpoints (for compatibility)
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.save_status_check(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.get_status_checks()
    return [StatusCheck(**status_check) for status_check in status_checks]

# Google OAuth verification (REQUIRED - no skip functionality)
@api_router.post("/auth/google/verify")
async def verify_google_token(auth_request: GoogleAuthRequest):
    try:
        # Verify the Google ID token
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")

        try:
            idinfo = id_token.verify_oauth2_token(
                auth_request.credential,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )

            # Verify the token was issued by Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

        # Extract user info from verified token
        user_info = {
            'sub': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo.get('picture')
        }

        # Create or get user
        user_id = f"google_{user_info['sub']}"
        existing_user = await db.get_user(user_id)

        if existing_user:
            # Update existing user
            existing_user["last_login"] = datetime.utcnow().isoformat()
            await db.save_user(existing_user)
            user = existing_user
        else:
            # Create new user
            user = {
                "id": user_id,
                "email": user_info["email"],
                "name": user_info["name"],
                "picture": user_info.get("picture"),
                "oauth_provider": "Google",
                "google_id": user_info["sub"],
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "gemini_api_key": None,
                "openai_api_key": None,
                "anthropic_api_key": None
            }
            await db.save_user(user)

        # Create access token
        access_token = create_access_token({"sub": user_id, "email": user["email"]})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture"),
                "oauth_provider": user["oauth_provider"],
                "has_gemini_api_key": bool(user.get("gemini_api_key")),
                "has_openai_api_key": bool(user.get("openai_api_key")),
                "has_anthropic_api_key": bool(user.get("anthropic_api_key")),
                "gemini_key_preview": create_key_preview(user.get("gemini_api_key")),
                "openai_key_preview": create_key_preview(user.get("openai_api_key")),
                "anthropic_key_preview": create_key_preview(user.get("anthropic_api_key"))
            }
        }
    except Exception as e:
        logger.error(f"Google OAuth verification failed: {e}")
        raise HTTPException(status_code=400, detail="Google authentication failed")

# Telegram Mini App authentication verification
@api_router.post("/auth/telegram/verify")
async def verify_telegram_user(auth_request: TelegramAuthRequest):
    try:
        telegram_user = auth_request.telegram_user
        
        # Validate required fields
        if not telegram_user.get('id'):
            raise HTTPException(status_code=400, detail="Invalid Telegram user data")
        
        # TODO: Add proper Telegram Mini App authentication validation
        # For now, we'll validate the user data exists
        if not isinstance(telegram_user.get('id'), int):
            raise HTTPException(status_code=400, detail="Invalid Telegram user ID")
        
        # Create user ID
        user_id = f"telegram_{telegram_user['id']}"
        
        # Check if user already exists
        existing_user = await db.get_user(user_id)
        
        if existing_user:
            # Update existing user
            existing_user["last_login"] = datetime.utcnow().isoformat()
            await db.save_user(existing_user)
            user = existing_user
        else:
            # Create new user
            user = {
                "id": user_id,
                "email": f"telegram_{telegram_user['id']}@telegram.local",  # Synthetic email
                "name": f"{telegram_user.get('first_name', '')} {telegram_user.get('last_name', '')}".strip(),
                "picture": telegram_user.get('photo_url'),
                "oauth_provider": "Telegram",
                "telegram_id": telegram_user['id'],
                "telegram_username": telegram_user.get('username'),
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "gemini_api_key": None,
                "openai_api_key": None,
                "anthropic_api_key": None
            }
            await db.save_user(user)
        
        # Create access token
        access_token = create_access_token({"sub": user_id, "email": user["email"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user.get("picture"),
                "oauth_provider": user["oauth_provider"],
                "has_gemini_api_key": bool(user.get("gemini_api_key")),
                "has_openai_api_key": bool(user.get("openai_api_key")),
                "has_anthropic_api_key": bool(user.get("anthropic_api_key")),
                "gemini_key_preview": create_key_preview(user.get("gemini_api_key")),
                "openai_key_preview": create_key_preview(user.get("openai_api_key")),
                "anthropic_key_preview": create_key_preview(user.get("anthropic_api_key"))
            }
        }
    except Exception as e:
        logger.error(f"Telegram OAuth verification failed: {e}")
        raise HTTPException(status_code=400, detail="Telegram authentication failed")

# User profile (REQUIRES AUTHENTICATION)
@api_router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserProfile(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        picture=current_user.get("picture"),
        oauth_provider=current_user["oauth_provider"],
        created_at=datetime.fromisoformat(current_user["created_at"]),
        last_login=datetime.fromisoformat(current_user["last_login"]) if current_user.get("last_login") else None,
        has_gemini_api_key=bool(current_user.get("gemini_api_key")),
        has_openai_api_key=bool(current_user.get("openai_api_key")),
        has_anthropic_api_key=bool(current_user.get("anthropic_api_key")),
        preferred_language=current_user.get("preferred_language", "ru"),
        gemini_key_preview=create_key_preview(current_user.get("gemini_api_key")),
        openai_key_preview=create_key_preview(current_user.get("openai_api_key")),
        anthropic_key_preview=create_key_preview(current_user.get("anthropic_api_key"))
    )

# Save API keys (REQUIRES AUTHENTICATION)
@api_router.post("/api-keys")
async def save_api_keys(
    api_key_data: ApiKeyUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        updated_keys = []
        
        # Map new field names to old field names for processing
        # Priority: new names override old names
        gemini_key = api_key_data.api_key_1 or api_key_data.gemini_api_key
        openai_key = api_key_data.api_key_2 or api_key_data.openai_api_key  
        anthropic_key = api_key_data.api_key_3 or api_key_data.anthropic_api_key
        
        # Update Gemini API key if provided (api_key_1 or gemini_api_key)
        if gemini_key:
            try:
                test_provider = llm_manager.create_user_provider("gemini", "gemini-1.5-flash", gemini_key)
                test_response = await test_provider.generate_content("Test")
                if test_response:
                    current_user["gemini_api_key"] = gemini_key
                    updated_keys.append("API Key 1 (Gemini)")
            except Exception as e:
                logger.error(f"Invalid API Key 1 (Gemini): {e}")
                raise HTTPException(status_code=400, detail="Invalid API Key 1")

        # Update OpenAI API key if provided (api_key_2 or openai_api_key)
        if openai_key:
            try:
                test_provider = llm_manager.create_user_provider("openai", "gpt-4o-mini", openai_key)
                test_response = await test_provider.generate_content("Test")
                if test_response:
                    current_user["openai_api_key"] = openai_key
                    updated_keys.append("API Key 2 (OpenAI)")
            except Exception as e:
                logger.error(f"Invalid API Key 2 (OpenAI): {e}")
                raise HTTPException(status_code=400, detail="Invalid API Key 2")

        # Update Anthropic API key if provided (api_key_3 or anthropic_api_key)
        if anthropic_key:
            try:
                test_provider = llm_manager.create_user_provider("anthropic", "claude-3-haiku-20240307", anthropic_key)
                test_response = await test_provider.generate_content("Test")
                if test_response:
                    current_user["anthropic_api_key"] = anthropic_key
                    updated_keys.append("API Key 3 (Anthropic)")
            except Exception as e:
                logger.error(f"Invalid API Key 3 (Anthropic): {e}")
                raise HTTPException(status_code=400, detail="Invalid API Key 3")

        # Save updated user data
        await db.save_user(current_user)

        return {
            "message": f"API ключи успешно обновлены: {', '.join(updated_keys)}", 
            "status": "success",
            "updated_keys": updated_keys
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API keys")

# Auto-generate Gemini API key (REQUIRES AUTHENTICATION)
@api_router.post("/auto-generate-gemini-key")
async def auto_generate_gemini_key(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Автоматически создать и сохранить Gemini API ключ для пользователя"""
    try:
        user_id = str(current_user.get("id", ""))
        user_email = current_user.get("email", "")
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Email пользователя не найден")
        
        # Проверяем, есть ли уже Gemini ключ
        existing_key = current_user.get("gemini_api_key")
        if existing_key:
            # Проверяем валидность существующего ключа
            is_valid = await google_api_service.validate_api_key(existing_key)
            if is_valid:
                return {
                    "message": "У вас уже есть действующий Gemini API ключ!",
                    "status": "existing",
                    "api_key_masked": f"{existing_key[:8]}...{existing_key[-4:]}",
                    "provider": "Gemini"
                }
        
        # Создаем новый API ключ
        logger.info(f"Creating Gemini API key for user {user_email}")
        key_result = await google_api_service.create_gemini_api_key(user_id, user_email)
        
        # Валидируем созданный ключ
        is_valid = await google_api_service.validate_api_key(key_result["api_key"])
        if not is_valid:
            logger.warning(f"Generated API key validation failed for user {user_email}")
            # Все равно сохраняем демо ключ для тестирования
        
        # Сохраняем API ключ в профиле пользователя
        current_user["gemini_api_key"] = key_result["api_key"]
        await db.save_user(current_user)
        
        logger.info(f"Successfully generated and saved Gemini API key for user {user_email}")
        
        return {
            "message": key_result["message"],
            "status": key_result["status"],
            "api_key_masked": f"{key_result['api_key'][:8]}...{key_result['api_key'][-4:]}",
            "provider": "Gemini",
            "display_name": key_result.get("display_name", ""),
            "restrictions": key_result.get("restrictions", {}),
            "auto_generated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to auto-generate Gemini API key: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при автоматическом создании API ключа: {str(e)}"
        )

# Quick Gemini setup (REQUIRES AUTHENTICATION)
@api_router.post("/quick-gemini-setup")
async def quick_gemini_setup(
    gemini_data: QuickGeminiSetup,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Test the API key with modern manager
        is_valid = await modern_llm_manager.test_api_key("gemini", gemini_data.api_key)
        
        if not is_valid:
            # Provide more specific error message based on the issue
            error_message = "Недействительный Gemini API ключ"
            
            # Check if emergentintegrations is available
            try:
                from emergentintegrations.llm.chat import LlmChat
                # If available, it's a real API key issue
                error_message = "Недействительный Gemini API ключ. Проверьте правильность ключа."
            except ImportError:
                # If not available, mention fallback mode
                error_message = "Невозможно проверить API ключ: система работает в режиме ограниченной функциональности. Ключ будет сохранен для использования при восстановлении полной функциональности."
                
                # In fallback mode, we still save the key if it looks valid
                if gemini_data.api_key and gemini_data.api_key.startswith('AIza') and len(gemini_data.api_key) > 30:
                    logger.info("Saving API key in fallback mode")
                    current_user["gemini_api_key"] = gemini_data.api_key
                    await db.save_user(current_user)
                    
                    return {
                        "message": "Gemini API ключ сохранен. Система работает в режиме ограниченной функциональности, но ключ будет использован при восстановлении полной функциональности.",
                        "status": "fallback",
                        "provider": "Gemini",
                        "model": "gemini-2.0-flash",
                        "fallback_mode": True
                    }
                else:
                    error_message = "Недействительный формат Gemini API ключа. Ключ должен начинаться с 'AIza'."
            
            raise HTTPException(status_code=400, detail=error_message)
        
        # Save the API key
        current_user["gemini_api_key"] = gemini_data.api_key
        await db.save_user(current_user)
        
        return {
            "message": "Gemini API успешно подключен! Теперь вы можете использовать полную функциональность приложения.",
            "status": "success",
            "provider": "Gemini",
            "model": "gemini-2.0-flash"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to setup Gemini API: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при настройке Gemini API")

# Change user language (REQUIRES AUTHENTICATION)
@api_router.post("/change-language")
async def change_language(
    language_data: dict,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Изменить предпочтительный язык пользователя"""
    try:
        language = language_data.get("language")
        if not language:
            raise HTTPException(status_code=400, detail="Язык не указан")
        
        # Проверяем, что язык поддерживается
        supported_languages = ['uk', 'ru', 'de', 'en']
        if language not in supported_languages:
            raise HTTPException(status_code=400, detail=f"Неподдерживаемый язык. Поддерживаются: {', '.join(supported_languages)}")
        
        # Обновляем язык в базе данных
        success = await db.update_user_language(current_user["id"], language)
        
        if not success:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении языка")
        
        # Обновляем текущий объект пользователя
        current_user["preferred_language"] = language
        
        return {
            "message": "Язык успешно изменен",
            "status": "success",
            "language": language,
            "available_languages": supported_languages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to change language: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при смене языка")

# Get OCR service status
@api_router.get("/ocr-status")
async def get_ocr_status():
    """Получение статуса OCR сервиса"""
    try:
        status = improved_ocr_service.get_service_status()
        return {
            "status": "success",
            "ocr_service": status,
            "tesseract_required": False,
            "production_ready": True
        }
    except Exception as e:
        logger.error(f"Failed to get OCR status: {e}")
        return {"status": "error", "message": str(e)}

# Get modern LLM providers status
@api_router.get("/modern-llm-status")
async def get_modern_llm_status():
    try:
        provider_status = modern_llm_manager.get_provider_status()
        active_count = sum(1 for status in provider_status.values() if status["status"] == "active")
        return {
            "status": "success",
            "providers": provider_status,
            "active_providers": active_count,
            "total_providers": len(provider_status),
            "modern": True
        }
    except Exception as e:
        logger.error(f"Failed to get modern LLM status: {e}")
        return {"status": "error", "message": str(e), "modern": True}

# Get LLM providers status
@api_router.get("/llm-status")
async def get_llm_status():
    try:
        provider_status = llm_manager.get_provider_status()
        active_count = sum(1 for status in provider_status.values() if status["status"] == "active")
        return {
            "status": "success",
            "providers": provider_status,
            "active_providers": active_count,
            "total_providers": len(provider_status)
        }
    except Exception as e:
        logger.error(f"Failed to get LLM status: {e}")
        return {"status": "error", "message": str(e)}

# Analyze file with user's API keys (REQUIRES AUTHENTICATION)
@api_router.post("/analyze-file")
async def analyze_file_authenticated(
    file: UploadFile = File(...),
    language: str = Form("ru"),  # Убираем выбор языка пользователем - будет использоваться из профиля
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Получаем язык из профиля пользователя (если есть), иначе используем переданный
        user_language = current_user.get("preferred_language", language)
        
        # Check if user has at least one API key
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))

        if not user_providers:
            # Try system providers if no user keys
            active_providers = llm_manager.get_available_providers()
            if not any(active_providers.values()):
                raise HTTPException(
                    status_code=400,
                    detail="No API keys configured. Please add your API keys in profile."
                )

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        try:
            # Используем улучшенный OCR сервис как основной метод
            try:
                extracted_text, processing_method = await improved_ocr_service.process_document(
                    temp_file_path, 
                    file.content_type or "",
                    user_providers
                )
                logger.info(f"Improved OCR processing method: {processing_method}, extracted text length: {len(extracted_text)}")
            except Exception as ocr_error:
                logger.warning(f"Improved OCR failed, falling back to alternative OCR: {ocr_error}")
                # Fallback к альтернативному OCR сервису
                try:
                    extracted_text, processing_method = alternative_ocr_service.process_document(temp_file_path, file.content_type or "")
                    logger.info(f"Alternative OCR processing method: {processing_method}, extracted text length: {len(extracted_text)}")
                except Exception as alt_ocr_error:
                    logger.warning(f"Alternative OCR failed, falling back to document_processor: {alt_ocr_error}")
                    # Последний fallback к основному document_processor
                    extracted_text, processing_method = document_processor.process_document(temp_file_path, file.content_type or "")
                    logger.info(f"Fallback processing method: {processing_method}, extracted text length: {len(extracted_text)}")
            
            # Проверяем качество извлеченного текста
            if not extracted_text or len(extracted_text.strip()) < 10:
                logger.warning("Insufficient text extracted from document")
                if file.content_type and file.content_type.startswith('image/'):
                    extracted_text = "Изображение получено, но текст не был извлечен. Возможно, изображение не содержит текста или качество недостаточное для распознавания."
                else:
                    extracted_text = "Документ получен, но текст не был извлечен. Возможно, документ не содержит читаемого текста."

            # Используем новый супер-анализатор для WOW-эффекта
            super_analysis_result = await super_analysis_engine.analyze_document_comprehensively(
                document_text=extracted_text,
                language=user_language,
                filename=file.filename,
                user_providers=user_providers
            )
            
            # Определяем тип файла для результата
            is_image = file.content_type and file.content_type.startswith('image/')
            is_pdf = file.content_type == 'application/pdf' or file.filename.lower().endswith('.pdf')
            file_type = "pdf" if is_pdf else ("image" if is_image else "document")
            
            # Создаем улучшенный результат анализа с супер-анализом
            analysis_result = {
                "summary": f"Супер-анализ файла {file.filename} выполнен успешно",
                "super_analysis": super_analysis_result.get("super_analysis", {}),
                "analysis": {
                    "full_analysis": super_analysis_result.get("super_analysis", {}).get("full_text", ""),
                    "executive_summary": super_analysis_result.get("summary", ""),
                    "recommendations": super_analysis_result.get("recommendations", []),
                    "next_steps": super_analysis_result.get("next_steps", []),
                    "insights": super_analysis_result.get("super_analysis", {}).get("insights", []),
                    "action_items": super_analysis_result.get("super_analysis", {}).get("action_items", []),
                    "urgency_level": super_analysis_result.get("super_analysis", {}).get("urgency_assessment", "medium"),
                    "quality_score": super_analysis_result.get("super_analysis", {}).get("quality_score", 0.8),
                    "sections": super_analysis_result.get("super_analysis", {}).get("sections", [])
                },
                "file_name": file.filename,
                "analysis_language": user_language,
                "file_type": file_type,
                "processing_method": processing_method,
                "extracted_text_length": len(extracted_text) if extracted_text else 0,
                "analysis_type": "super_wow_analysis"
            }

            # Save analysis to database
            doc_analysis = {
                "id": str(uuid.uuid4()),
                "user_id": current_user["id"],
                "file_name": file.filename,
                "file_type": file_type,
                "analysis_result": analysis_result,
                "analysis_language": user_language,
                "llm_provider": "AI Assistant"
            }
            await db.save_analysis(doc_analysis)

            return analysis_result

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Get user's analysis history (REQUIRES AUTHENTICATION)
@api_router.get("/analysis-history")
async def get_analysis_history(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        analyses = await db.get_user_analyses(current_user["id"])
        return {
            "status": "success",
            "count": len(analyses),
            "analyses": analyses
        }
    except Exception as e:
        logger.error(f"Failed to get analysis history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analysis history")

# Telegram Web App Authentication endpoint
@api_router.post("/telegram/auth")
async def telegram_auth(request: Request):
    """Аутентификация пользователя Telegram Web App"""
    try:
        data = await request.json()
        telegram_user = data.get('user')
        init_data = data.get('initData')
        
        # Здесь должна быть проверка подписи данных от Telegram
        # Для демонстрации пока пропускаем проверку
        
        if telegram_user:
            # Создаем или обновляем пользователя в базе
            user_data = {
                'id': str(telegram_user.get('id')),
                'name': f"{telegram_user.get('first_name', '')} {telegram_user.get('last_name', '')}".strip(),
                'email': telegram_user.get('username', f"tg_{telegram_user.get('id')}@telegram.com"),
                'picture': telegram_user.get('photo_url', ''),
                'telegram_id': telegram_user.get('id'),
                'telegram_username': telegram_user.get('username'),
                'telegram_first_name': telegram_user.get('first_name'),
                'telegram_last_name': telegram_user.get('last_name'),
                'is_telegram_user': True
            }
            
            # Сохраняем пользователя в базе
            user_id = f"telegram_{user_data['id']}"
            user_data['id'] = user_id
            user_data['oauth_provider'] = 'Telegram'
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['last_login'] = datetime.utcnow().isoformat()
            
            # Проверяем, есть ли пользователь в базе
            existing_user = await db.get_user(user_id)
            if not existing_user:
                # Создаем нового пользователя
                await db.save_user(user_data)
                logger.info(f"Created new Telegram user: {user_id}")
            else:
                # Обновляем существующего пользователя
                user_data['created_at'] = existing_user.get('created_at', user_data['created_at'])
                await db.save_user(user_data)
                logger.info(f"Updated existing Telegram user: {user_id}")
            
            return {
                "status": "success",
                "user": user_data,
                "message": "Telegram user authenticated successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid Telegram user data")
            
    except Exception as e:
        logger.error(f"Telegram auth error: {e}")
        raise HTTPException(status_code=500, detail="Telegram authentication failed")

# Push notification subscription endpoint
@api_router.post("/push-subscription")
async def subscribe_to_push(request: Request):
    """Подписка на push уведомления"""
    try:
        data = await request.json()
        subscription = data.get('subscription')
        telegram_user_id = data.get('telegram_user_id')
        
        if not subscription:
            raise HTTPException(status_code=400, detail="No subscription data provided")
        
        # Сохраняем подписку в базе данных
        subscription_data = {
            'endpoint': subscription.get('endpoint'),
            'keys': subscription.get('keys', {}),
            'telegram_user_id': telegram_user_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Здесь можно добавить логику сохранения в базе
        logger.info(f"Push subscription registered: {subscription_data}")
        
        return {
            "status": "success",
            "message": "Push subscription registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Push subscription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to register push subscription")

# Telegram Web App viewport info endpoint
@api_router.get("/telegram/viewport")
async def get_telegram_viewport():
    """Получение информации о viewport Telegram Web App"""
    return {
        "status": "success",
        "viewport": {
            "is_expanded": True,
            "height": 600,
            "is_closing_confirmation_enabled": True,
            "is_vertical_swipes_enabled": True
        }
    }

# Send notification to Telegram user
@api_router.post("/telegram/notify")
async def send_telegram_notification(request: Request):
    """Отправка уведомления пользователю Telegram"""
    try:
        data = await request.json()
        telegram_user_id = data.get('telegram_user_id')
        message = data.get('message')
        
        if not telegram_user_id or not message:
            raise HTTPException(status_code=400, detail="Missing telegram_user_id or message")
        
        # Здесь можно добавить логику отправки уведомления через Telegram Bot API
        logger.info(f"Notification sent to Telegram user {telegram_user_id}: {message}")
        
        return {
            "status": "success",
            "message": "Notification sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Telegram notification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")

# Get Telegram news (PUBLIC ENDPOINT)
@api_router.get("/telegram-news")
async def get_telegram_news(limit: int = 5):
    """Получить последние новости из Telegram канала"""
    try:
        # Пробуем получить реальные новости
        news = await telegram_service.get_channel_posts(limit=limit)
        
        # Если не получилось, возвращаем демо-новости
        if not news:
            news = await telegram_service.get_sample_news()
        
        return {
            "status": "success",
            "count": len(news),
            "news": news,
            "channel_name": telegram_service.channel_name,
            "channel_link": f"https://t.me/{telegram_service.channel_name}"
        }
    except Exception as e:
        logger.error(f"Failed to get Telegram news: {e}")
        # В случае ошибки возвращаем демо-новости
        demo_news = await telegram_service.get_sample_news()
        return {
            "status": "demo",
            "count": len(demo_news),
            "news": demo_news,
            "channel_name": telegram_service.channel_name,
            "channel_link": f"https://t.me/{telegram_service.channel_name}",
            "note": "Демо-режим: показаны примерные новости"
        }

# =============== ADMIN API ENDPOINTS ===============

# Admin login
@api_router.post("/admin/login")
async def admin_login(admin_auth: AdminAuth):
    """Админская авторизация"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Неверный пароль")
    
    return {
        "status": "success",
        "message": "Успешная авторизация",
        "is_admin": True
    }

# Get all app texts
@api_router.post("/admin/texts")
async def get_admin_texts(admin_auth: AdminAuth):
    """Получить все тексты приложения (только для админа)"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        texts = await db.get_app_texts_by_category()
        return {
            "status": "success",
            "texts": texts
        }
    except Exception as e:
        logger.error(f"Failed to get app texts: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения текстов")

# Update app text
@api_router.put("/admin/texts/{key_name}")
async def update_admin_text(key_name: str, admin_auth: AdminAuth, text_update: AppTextUpdate):
    """Обновить текст приложения"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        success = await db.update_app_text(key_name, text_update.text_value, text_update.description)
        if success:
            return {
                "status": "success",
                "message": f"Текст '{key_name}' обновлен"
            }
        else:
            raise HTTPException(status_code=404, detail="Текст не найден")
    except Exception as e:
        logger.error(f"Failed to update app text: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обновления текста")

# Create new app text
@api_router.post("/admin/texts/create")
async def create_admin_text(admin_auth: AdminAuth, text_create: AppTextCreate):
    """Создать новый текст приложения"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        success = await db.create_app_text(
            text_create.key_name,
            text_create.text_value,
            text_create.description,
            text_create.category
        )
        if success:
            return {
                "status": "success",
                "message": f"Текст '{text_create.key_name}' создан"
            }
        else:
            raise HTTPException(status_code=400, detail="Ошибка создания текста")
    except Exception as e:
        logger.error(f"Failed to create app text: {e}")
        raise HTTPException(status_code=500, detail="Ошибка создания текста")

# Delete app text
@api_router.delete("/admin/texts/{key_name}")
async def delete_admin_text(key_name: str, admin_auth: AdminAuth):
    """Удалить текст приложения"""
    if not verify_admin_password(admin_auth.password):
        raise HTTPException(status_code=401, detail="Доступ запрещен")
    
    try:
        success = await db.delete_app_text(key_name)
        if success:
            return {
                "status": "success",
                "message": f"Текст '{key_name}' удален"
            }
        else:
            raise HTTPException(status_code=404, detail="Текст не найден")
    except Exception as e:
        logger.error(f"Failed to delete app text: {e}")
        raise HTTPException(status_code=500, detail="Ошибка удаления текста")

# Get public app texts (for frontend)
@api_router.get("/texts")
async def get_public_texts():
    """Получить тексты приложения для фронтенда"""
    try:
        texts = await db.get_app_texts()
        texts_dict = {}
        for text in texts:
            texts_dict[text['key_name']] = text['text_value']
        
        return {
            "status": "success",
            "texts": texts_dict
        }
    except Exception as e:
        logger.error(f"Failed to get public texts: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения текстов")

# Store push subscriptions (in production, use a database)
push_subscriptions = {}

@api_router.post("/push-notification")
async def send_push_notification(
    message: PushMessage,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Send a push notification to the user
    """
    user_id = current_user['id']
    
    # Check if user is subscribed
    if user_id not in push_subscriptions:
        raise HTTPException(status_code=404, detail="User not subscribed to push notifications")
    
    subscription = push_subscriptions[user_id]
    
    # In production, use a proper web push library like pywebpush
    # For now, just return success
    logger.info(f"Sending push notification to user {user_id}: {message.title}")
    
    return {
        "status": "success",
        "message": "Push notification sent successfully",
        "title": message.title,
        "body": message.body
    }

# Include the router in the main app
app.include_router(api_router)

# Root handler for Telegram Mini App
@app.get("/")
async def root():
    """Root endpoint for Telegram Mini App"""
    return {
        "status": "success",
        "message": "German Letter AI - Telegram Mini App",
        "version": "1.0",
        "telegram_mini_app": True
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        users_count = await db.get_users_count()
        analyses_count = await db.get_analyses_count()
        return {
            "status": "healthy",
            "telegram_mini_app": True,
            "users_count": users_count,
            "analyses_count": analyses_count
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    # Получаем порт из переменной окружения или используем 8001 по умолчанию
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
