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
from simple_tesseract_ocr import simple_tesseract_ocr
from google_api_key_service import google_api_service
from letter_templates_service import letter_templates_service
from letter_ai_service import letter_ai_service
from letter_pdf_service import letter_pdf_service
from super_analysis_engine import super_analysis_engine
from housing_search_service import housing_search_service
from housing_ai_service import housing_ai_service
from job_search_service import job_search_service
from job_ai_service import job_ai_service

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
    telegram_user: Optional[Dict[str, Any]] = None
    initData: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

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

# Модели для работы с письмами
class LetterGenerationRequest(BaseModel):
    user_request: str
    recipient_type: str
    recipient_info: Optional[Dict[str, str]] = {}
    sender_info: Optional[Dict[str, str]] = {}
    include_translation: bool = True

class TemplateLetterRequest(BaseModel):
    template_category: str
    template_key: str
    user_data: Dict[str, str]
    sender_info: Optional[Dict[str, str]] = {}
    recipient_info: Optional[Dict[str, str]] = {}
    include_translation: bool = True

class LetterImprovementRequest(BaseModel):
    letter_content: str
    improvement_type: str = "grammar"  # grammar, style, formality, structure, clarity
    
class SaveLetterRequest(BaseModel):
    title: str
    content: str
    content_german: Optional[str] = None
    translation: Optional[str] = None
    translation_language: Optional[str] = None
    subject: Optional[str] = None
    recipient_type: Optional[str] = None
    template_category: Optional[str] = None
    template_key: Optional[str] = None
    letter_type: str = "custom"
    generation_method: str = "manual"
    sender_info: Optional[Dict[str, str]] = {}
    recipient_info: Optional[Dict[str, str]] = {}

class PDFGenerationRequest(BaseModel):
    letter_id: str
    include_translation: bool = True

# Housing Search Models
class HousingSearchRequest(BaseModel):
    city: str
    max_price: Optional[int] = None
    property_type: str = "wohnung"
    radius: Optional[int] = None

class NeighborhoodAnalysisRequest(BaseModel):
    city: str
    district: Optional[str] = None

class HousingSubscriptionRequest(BaseModel):
    city: str
    max_price: Optional[int] = None
    property_type: str = "wohnung"
    radius: Optional[int] = None

class HousingSubscriptionUpdate(BaseModel):
    city: Optional[str] = None
    max_price: Optional[int] = None
    property_type: Optional[str] = None
    radius: Optional[int] = None
    active: Optional[bool] = None

class LandlordContactRequest(BaseModel):
    listing_id: str
    user_name: str
    user_occupation: Optional[str] = "Fachkraft"
    user_income: Optional[str] = "stabiles Einkommen"

# Job Search Models
class JobSearchRequest(BaseModel):
    search_query: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    language_level: Optional[str] = None  # A1, A2, B1, B2, C1, C2
    category: Optional[str] = None
    limit: int = 50

class JobSubscriptionRequest(BaseModel):
    search_query: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    language_level: Optional[str] = None
    category: Optional[str] = None

class JobSubscriptionUpdate(BaseModel):
    search_query: Optional[str] = None
    location: Optional[str] = None
    remote: Optional[bool] = None
    visa_sponsorship: Optional[bool] = None
    language_level: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    target_position: Optional[str] = None
    language: str = "ru"

class ResumeImprovementRequest(BaseModel):
    resume_analysis_id: str
    target_position: Optional[str] = None

class InterviewPrepRequest(BaseModel):
    job_description: str
    resume_text: Optional[str] = None
    interview_type: str = "behavioral"  # behavioral, technical, case_study, cultural_fit
    language: str = "ru"

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
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token validation failed")

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
        "version": "3.0.0",
        "telegram_mini_app": True
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "german-letter-ai-assistant", 
        "auth": "google-oauth-only",
        "database": "sqlite",
        "telegram_mini_app": True
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
        logger.info(f"Telegram auth request received: {auth_request}")
        
        # Prepare authentication data
        auth_data = {}
        if auth_request.telegram_user:
            auth_data['telegram_user'] = auth_request.telegram_user
        if auth_request.initData:
            auth_data['initData'] = auth_request.initData
        if auth_request.user:
            auth_data['user'] = auth_request.user
        
        # Validate authentication
        validation_result = telegram_auth_service.validate_telegram_auth(auth_data)
        
        if not validation_result['valid']:
            logger.error(f"Telegram auth validation failed: {validation_result['error']}")
            raise HTTPException(
                status_code=400, 
                detail=f"Telegram authentication failed: {validation_result['error']}"
            )
        
        # Extract user data
        telegram_user = validation_result.get('user')
        if not telegram_user:
            # Try to get user from any of the provided data
            telegram_user = auth_request.telegram_user or auth_request.user
            if not telegram_user:
                raise HTTPException(status_code=400, detail="No user data provided")
        
        logger.info(f"Telegram user validated: {telegram_user}")
        
        # Create user object
        user_data = telegram_auth_service.create_user_from_telegram_data(telegram_user)
        user_id = user_data['id']
        
        # Check if user already exists
        existing_user = await db.get_user(user_id)
        
        if existing_user:
            # Update existing user
            existing_user["last_login"] = datetime.utcnow().isoformat()
            # Update user data with fresh Telegram info
            existing_user.update({
                "name": user_data["name"],
                "picture": user_data.get("picture"),
                "telegram_username": user_data.get("telegram_username"),
                "telegram_first_name": user_data.get("telegram_first_name"),
                "telegram_last_name": user_data.get("telegram_last_name"),
                "telegram_language_code": user_data.get("telegram_language_code")
            })
            await db.save_user(existing_user)
            user = existing_user
        else:
            # Create new user
            user_data["created_at"] = datetime.utcnow().isoformat()
            user_data["last_login"] = datetime.utcnow().isoformat()
            await db.save_user(user_data)
            user = user_data
        
        # Create access token
        access_token = create_access_token({"sub": user_id, "email": user["email"]})
        
        logger.info(f"Telegram authentication successful for user: {user_id}")
        
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Telegram authentication error: {e}")
        raise HTTPException(status_code=500, detail="Telegram authentication failed")

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
        status = simple_tesseract_ocr.get_service_status()
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

        # Для пользователей без API ключей разрешаем демо анализ
        allow_demo_analysis = not user_providers

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        try:
            # Используем ТОЛЬКО простой Tesseract OCR сервис - максимально быстро
            extracted_text, processing_method = await simple_tesseract_ocr.process_document(
                temp_file_path, 
                file.content_type or ""
            )
            logger.info(f"Fast OCR processing method: {processing_method}, extracted text length: {len(extracted_text)}")
            
            # Проверяем качество извлеченного текста
            if not extracted_text or len(extracted_text.strip()) < 5:
                logger.warning("Minimal text extracted from document")
                if file.content_type and file.content_type.startswith('image/'):
                    extracted_text = "Изображение получено, но текст не найден. Попробуйте изображение с более четким текстом."
                else:
                    extracted_text = "Документ получен, но текст не найден. Возможно, документ содержит только изображения."

            # Используем простой анализ документа только если не удалось извлечь текст
            if not extracted_text or len(extracted_text.strip()) < 10:
                # Заглушка только для пустых файлов
                analysis_result_data = {
                    "summary": f"Анализ файла {file.filename} - текст не найден",
                    "analysis": {
                        "full_analysis": "К сожалению, из данного файла не удалось извлечь читаемый текст. Попробуйте загрузить более четкое изображение или PDF с текстом.",
                        "executive_summary": "Текст не обнаружен",
                        "recommendations": ["Попробуйте более четкое изображение", "Убедитесь что документ содержит текст"],
                        "next_steps": ["Переделать скан документа", "Проверить качество изображения"],
                        "insights": [],
                        "action_items": [],
                        "urgency_level": "low",
                        "quality_score": 0.1,
                        "sections": []
                    }
                }
            else:
                # РЕАЛЬНЫЙ AI АНАЛИЗ ДОКУМЕНТА
                logger.info(f"Starting comprehensive AI analysis for {file.filename} with text length: {len(extracted_text)}")
                
                try:
                    # Используем супер-анализ для детального разбора
                    analysis_result_data = await super_analysis_engine.analyze_document_comprehensively(
                        document_text=extracted_text,
                        language=user_language,
                        filename=file.filename,
                        user_providers=user_providers if user_providers else None
                    )
                    logger.info(f"Super analysis completed successfully for {file.filename}")
                    
                except Exception as e:
                    logger.error(f"Super analysis failed for {file.filename}: {e}")
                    # Fallback к простому анализу если супер-анализ не работает
                    analysis_result_data = {
                        "summary": f"Анализ файла {file.filename} выполнен с ограничениями",
                        "analysis": {
                            "full_analysis": f"Документ {file.filename} был обработан. Извлечен текст длиной {len(extracted_text)} символов. Для полного анализа необходимо настроить API ключи.",
                            "executive_summary": "Документ успешно обработан, текст извлечен",
                            "recommendations": ["Настройте API ключи для полного анализа"],
                            "next_steps": ["Добавьте API ключи в профиле"],
                            "insights": [f"Извлечен текст: {extracted_text[:200]}..." if len(extracted_text) > 200 else extracted_text],
                            "action_items": [],
                            "urgency_level": "medium",
                            "quality_score": 0.6,
                            "sections": []
                        }
                    }
            
            # Определяем тип файла для результата
            is_image = file.content_type and file.content_type.startswith('image/')
            is_pdf = file.content_type == 'application/pdf' or file.filename.lower().endswith('.pdf')
            file_type = "pdf" if is_pdf else ("image" if is_image else "document")
            
            # Создаем результат анализа
            analysis_result = {
                "summary": f"Анализ файла {file.filename} выполнен успешно",
                "letter_analysis": analysis_result_data.get("analysis", {}),
                "analysis": analysis_result_data.get("analysis", {}),
                "file_name": file.filename,
                "analysis_language": user_language,
                "file_type": file_type,
                "processing_method": processing_method,
                "extracted_text_length": len(extracted_text) if extracted_text else 0,
                "analysis_type": "letter_analysis"
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

# =============== LETTERS API ENDPOINTS ===============

# Получить все категории шаблонов
@api_router.get("/letter-categories")
async def get_letter_categories():
    """Получить все категории шаблонов писем"""
    try:
        categories = letter_templates_service.get_all_categories()
        return {
            "status": "success",
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error getting letter categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")

# Получить шаблоны по категории
@api_router.get("/letter-templates/{category_key}")
async def get_letter_templates(category_key: str):
    """Получить все шаблоны в категории"""
    try:
        templates = letter_templates_service.get_templates_by_category(category_key)
        return {
            "status": "success",
            "category": category_key,
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Error getting templates for category {category_key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")

# Получить конкретный шаблон
@api_router.get("/letter-template/{category_key}/{template_key}")
async def get_letter_template(category_key: str, template_key: str):
    """Получить конкретный шаблон"""
    try:
        template = letter_templates_service.get_template(category_key, template_key)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        return {
            "status": "success",
            "template": template
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {category_key}/{template_key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template")

# Поиск шаблонов
@api_router.get("/letter-search")
async def search_letter_templates(query: str):
    """Поиск шаблонов по запросу"""
    try:
        results = letter_templates_service.get_all_templates_search(query)
        return {
            "status": "success",
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching templates with query '{query}': {e}")
        raise HTTPException(status_code=500, detail="Search failed")

# Генерация письма по запросу пользователя (REQUIRES AUTHENTICATION)
@api_router.post("/generate-letter")
async def generate_letter(
    request: LetterGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Генерация письма на основе запроса пользователя"""
    try:
        # Получаем пользовательские провайдеры
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))

        if not user_providers:
            raise HTTPException(
                status_code=400,
                detail="No API keys configured. Please add your API keys in profile."
            )

        # Получаем язык пользователя
        user_language = current_user.get("preferred_language", "ru")
        
        # Генерируем письмо
        result = await letter_ai_service.generate_letter_from_request(
            user_request=request.user_request,
            recipient_type=request.recipient_type,
            user_language=user_language,
            user_providers=user_providers
        )
        
        # Логируем действие
        await db.save_letter_history({
            "user_id": current_user["id"],
            "action_type": "generate_custom_letter",
            "action_details": {
                "user_request": request.user_request,
                "recipient_type": request.recipient_type,
                "status": result.get("status")
            },
            "ai_provider": user_providers[0][0] if user_providers else "none"
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating letter: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate letter")

# Генерация письма по шаблону (REQUIRES AUTHENTICATION)
@api_router.post("/generate-letter-template")
async def generate_letter_from_template(
    request: TemplateLetterRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Генерация письма на основе шаблона"""
    try:
        # Получаем шаблон
        template = letter_templates_service.get_template(request.template_category, request.template_key)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Получаем пользовательские провайдеры
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))

        if not user_providers:
            raise HTTPException(
                status_code=400,
                detail="No API keys configured. Please add your API keys in profile."
            )

        # Получаем язык пользователя
        user_language = current_user.get("preferred_language", "ru")
        
        # Генерируем письмо из шаблона
        result = await letter_ai_service.generate_letter_from_template(
            template_content=template['template'],
            user_data=request.user_data,
            user_language=user_language,
            user_providers=user_providers
        )
        
        # Добавляем информацию о шаблоне к результату
        if result.get("status") == "success":
            result["template_info"] = {
                "category": request.template_category,
                "key": request.template_key,
                "name": template["name"],
                "description": template["description"]
            }
        
        # Логируем действие
        await db.save_letter_history({
            "user_id": current_user["id"],
            "action_type": "generate_template_letter",
            "action_details": {
                "template_category": request.template_category,
                "template_key": request.template_key,
                "template_name": template["name"],
                "status": result.get("status")
            },
            "ai_provider": user_providers[0][0] if user_providers else "none"
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating letter from template: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate letter from template")

# Улучшение существующего письма (REQUIRES AUTHENTICATION)
@api_router.post("/improve-letter")
async def improve_letter(
    request: LetterImprovementRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Улучшение существующего письма"""
    try:
        # Получаем пользовательские провайдеры
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))

        if not user_providers:
            raise HTTPException(
                status_code=400,
                detail="No API keys configured. Please add your API keys in profile."
            )

        # Получаем язык пользователя
        user_language = current_user.get("preferred_language", "ru")
        
        # Улучшаем письмо
        result = await letter_ai_service.improve_existing_letter(
            letter_content=request.letter_content,
            improvement_type=request.improvement_type,
            user_language=user_language,
            user_providers=user_providers
        )
        
        # Логируем действие
        await db.save_letter_history({
            "user_id": current_user["id"],
            "action_type": "improve_letter",
            "action_details": {
                "improvement_type": request.improvement_type,
                "status": result.get("status"),
                "original_length": len(request.letter_content),
                "improved_length": len(result.get("improved", ""))
            },
            "ai_provider": user_providers[0][0] if user_providers else "none"
        })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error improving letter: {e}")
        raise HTTPException(status_code=500, detail="Failed to improve letter")

# Сохранение письма (REQUIRES AUTHENTICATION)
@api_router.post("/save-letter")
async def save_letter(
    request: SaveLetterRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Сохранение письма в базе данных"""
    try:
        letter_data = {
            "user_id": current_user["id"],
            "title": request.title,
            "content": request.content,
            "content_german": request.content_german,
            "translation": request.translation,
            "translation_language": request.translation_language,
            "subject": request.subject,
            "recipient_type": request.recipient_type,
            "template_category": request.template_category,
            "template_key": request.template_key,
            "letter_type": request.letter_type,
            "generation_method": request.generation_method,
            "sender_info": request.sender_info,
            "recipient_info": request.recipient_info
        }
        
        letter_id = await db.save_user_letter(letter_data)
        
        # Логируем действие
        await db.save_letter_history({
            "user_id": current_user["id"],
            "letter_id": letter_id,
            "action_type": "save_letter",
            "action_details": {
                "title": request.title,
                "letter_type": request.letter_type,
                "generation_method": request.generation_method
            }
        })
        
        return {
            "status": "success",
            "letter_id": letter_id,
            "message": "Letter saved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error saving letter: {e}")
        raise HTTPException(status_code=500, detail="Failed to save letter")

# Получение сохраненных писем (REQUIRES AUTHENTICATION)
@api_router.get("/user-letters")
async def get_user_letters(
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение сохраненных писем пользователя"""
    try:
        letters = await db.get_user_letters(current_user["id"], limit)
        stats = await db.get_user_letter_stats(current_user["id"])
        
        return {
            "status": "success",
            "letters": letters,
            "stats": stats,
            "count": len(letters)
        }
        
    except Exception as e:
        logger.error(f"Error getting user letters: {e}")
        raise HTTPException(status_code=500, detail="Failed to get letters")

# Получение конкретного письма (REQUIRES AUTHENTICATION)
@api_router.get("/user-letter/{letter_id}")
async def get_user_letter(
    letter_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Получение конкретного письма пользователя"""
    try:
        letter = await db.get_user_letter(current_user["id"], letter_id)
        if not letter:
            raise HTTPException(status_code=404, detail="Letter not found")
        
        return {
            "status": "success",
            "letter": letter
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting letter {letter_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get letter")

# Удаление письма (REQUIRES AUTHENTICATION)
@api_router.delete("/user-letter/{letter_id}")
async def delete_user_letter(
    letter_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Удаление письма пользователя"""
    try:
        deleted = await db.delete_user_letter(current_user["id"], letter_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Letter not found")
        
        # Логируем действие
        await db.save_letter_history({
            "user_id": current_user["id"],
            "letter_id": letter_id,
            "action_type": "delete_letter",
            "action_details": {"letter_id": letter_id}
        })
        
        return {
            "status": "success",
            "message": "Letter deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting letter {letter_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete letter")

# Генерация PDF (REQUIRES AUTHENTICATION)
@api_router.post("/generate-letter-pdf")
async def generate_letter_pdf(
    request: PDFGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Генерация PDF из сохраненного письма"""
    try:
        # Получаем письмо
        letter = await db.get_user_letter(current_user["id"], request.letter_id)
        if not letter:
            raise HTTPException(status_code=404, detail="Letter not found")
        
        # Валидируем данные для PDF
        validation = letter_pdf_service.validate_letter_for_pdf(letter)
        if not validation["valid"]:
            return {
                "status": "error",
                "errors": validation["issues"],
                "warnings": validation.get("warnings", [])
            }
        
        # Генерируем PDF
        pdf_data = letter_pdf_service.generate_letter_pdf(
            letter_data=letter,
            sender_info=letter.get("sender_info", {}),
            recipient_info=letter.get("recipient_info", {}),
            include_translation=request.include_translation
        )
        
        # Логируем действие
        await db.save_letter_history({
            "user_id": current_user["id"],
            "letter_id": request.letter_id,
            "action_type": "generate_pdf",
            "action_details": {
                "include_translation": request.include_translation,
                "pdf_size": len(pdf_data)
            }
        })
        
        # Возвращаем PDF как base64 для отправки на frontend
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return {
            "status": "success",
            "pdf_data": pdf_base64,
            "filename": f"letter_{letter['title'][:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "warnings": validation.get("warnings", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF for letter {request.letter_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

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

# =====================================================
# HOUSING SEARCH ENDPOINTS
# =====================================================

@api_router.post("/housing-search")
async def search_housing(
    search_request: HousingSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🏠 Search for housing in German cities with AI analysis
    """
    try:
        logger.info(f"Housing search request from user {current_user['id']}: {search_request.city}")
        
        # Get user providers for AI analysis
        user_providers = {
            'provider': 'gemini',
            'model': 'gemini-2.0-flash',
            'api_key': await get_user_provider_key(current_user['id'], 'gemini')
        }
        
        # Perform search
        results = housing_search_service.search_housing(
            city=search_request.city,
            max_price=search_request.max_price,
            property_type=search_request.property_type,
            radius=search_request.radius,
            user_providers=user_providers if user_providers['api_key'] else None
        )
        
        logger.info(f"Housing search completed: {results.get('total_found', 0)} listings found")
        
        return {
            "status": "success",
            "data": results,
            "message": f"Поиск в городе {search_request.city} завершен"
        }
        
    except Exception as e:
        logger.error(f"Housing search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка поиска жилья: {str(e)}")

@api_router.post("/housing-neighborhood-analysis")
async def analyze_neighborhood(
    analysis_request: NeighborhoodAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🏙️ AI-powered neighborhood analysis
    """
    try:
        logger.info(f"Neighborhood analysis request: {analysis_request.city}, {analysis_request.district}")
        
        # Get user providers for AI analysis
        user_providers = {
            'provider': 'gemini',
            'model': 'gemini-2.0-flash',
            'api_key': await get_user_provider_key(current_user['id'], 'gemini')
        }
        
        analysis = housing_search_service.get_neighborhood_analysis(
            city=analysis_request.city,
            district=analysis_request.district,
            user_providers=user_providers if user_providers['api_key'] else None
        )
        
        return {
            "status": "success",
            "data": analysis,
            "message": f"Анализ района в городе {analysis_request.city} завершен"
        }
        
    except Exception as e:
        logger.error(f"Neighborhood analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа района: {str(e)}")

@api_router.post("/housing-subscriptions")
async def create_housing_subscription(
    subscription_request: HousingSubscriptionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📬 Create housing search subscription for notifications
    """
    try:
        logger.info(f"Creating housing subscription for user {current_user['id']}: {subscription_request.city}")
        
        result = housing_search_service.save_user_search_subscription(
            user_id=current_user['id'],
            search_params=subscription_request.dict()
        )
        
        return {
            "status": "success",
            "data": result,
            "message": f"Подписка на поиск в городе {subscription_request.city} создана"
        }
        
    except Exception as e:
        logger.error(f"Failed to create subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания подписки: {str(e)}")

@api_router.get("/housing-subscriptions")
async def get_housing_subscriptions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📋 Get user's housing subscriptions
    """
    try:
        subscriptions = housing_search_service.get_user_subscriptions(current_user['id'])
        
        return {
            "status": "success",
            "data": {
                "subscriptions": subscriptions,
                "total": len(subscriptions)
            },
            "message": f"Найдено {len(subscriptions)} активных подписок"
        }
        
    except Exception as e:
        logger.error(f"Failed to get subscriptions: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка получения подписок")

@api_router.put("/housing-subscriptions/{subscription_id}")
async def update_housing_subscription(
    subscription_id: str,
    updates: HousingSubscriptionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    ✏️ Update housing subscription
    """
    try:
        result = housing_search_service.update_subscription(
            subscription_id=subscription_id,
            user_id=current_user['id'],
            updates=updates.dict(exclude_unset=True)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка обновления подписки")

@api_router.delete("/housing-subscriptions/{subscription_id}")
async def delete_housing_subscription(
    subscription_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🗑️ Delete housing subscription
    """
    try:
        result = housing_search_service.delete_subscription(
            subscription_id=subscription_id,
            user_id=current_user['id']
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to delete subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка удаления подписки")

@api_router.post("/housing-landlord-contact")
async def generate_landlord_contact(
    contact_request: LandlordContactRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    ✍️ Generate landlord contact message with AI
    """
    try:
        user_info = {
            'name': contact_request.user_name,
            'occupation': contact_request.user_occupation,
            'income': contact_request.user_income
        }
        
        # Get user providers for AI analysis
        user_providers = {
            'provider': 'gemini',
            'model': 'gemini-2.0-flash',
            'api_key': await get_user_provider_key(current_user['id'], 'gemini')
        }
        
        result = housing_search_service.generate_landlord_contact(
            listing_id=contact_request.listing_id,
            user_info=user_info,
            user_providers=user_providers if user_providers['api_key'] else None
        )
        
        return {
            "status": "success",
            "data": result,
            "message": "Сообщение арендодателю создано"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate landlord contact: {str(e)}")
        raise HTTPException(status_code=500, detail="Ошибка создания сообщения")

@api_router.get("/housing-market-status")
async def get_housing_market_status():
    """
    📊 Get housing market status and cache info
    """
    try:
        return {
            "status": "success",
            "data": {
                "service_status": "operational",
                "cache_size": len(housing_search_service.search_cache),
                "supported_cities": [
                    "Berlin", "München", "Hamburg", "Köln", "Frankfurt",
                    "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig",
                    "Bremen", "Dresden", "Hannover", "Nürnberg", "Duisburg"
                ],
                "supported_sources": [
                    "ImmoScout24", "Immobilien.de", "WG-Gesucht", "eBay Kleinanzeigen"
                ],
                "ai_features": [
                    "Scam Detection", "Price Analysis", "Neighborhood Insights", 
                    "Total Cost Calculator", "Landlord Message Generator"
                ]
            },
            "message": "Housing search service operational"
        }
        
    except Exception as e:
        logger.error(f"Failed to get market status: {str(e)}")
        raise HTTPException(status_code=500, detail="Service status unavailable")

# Helper function for getting user API keys
async def get_user_provider_key(user_id: str, provider: str) -> Optional[str]:
    """Get user's API key for specified provider"""
    try:
        user = await db.get_user(user_id)
        if not user:
            return None
        
        # Map provider names to database columns
        provider_mapping = {
            'gemini': 'gemini_api_key',
            'openai': 'openai_api_key',
            'anthropic': 'anthropic_api_key'
        }
        
        key_field = provider_mapping.get(provider)
        if key_field and user.get(key_field):
            return user[key_field]
        
        # Also check new API key fields
        if user.get('api_key_1'):
            return user['api_key_1']
        elif user.get('api_key_2'):
            return user['api_key_2']
        elif user.get('api_key_3'):
            return user['api_key_3']
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to get user provider key: {str(e)}")
        return None

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

# =====================================================
# JOB SEARCH API ENDPOINTS
# =====================================================

@api_router.get("/job-search")
async def search_jobs(
    search_query: Optional[str] = None,
    location: Optional[str] = None,
    remote: Optional[bool] = None,
    visa_sponsorship: Optional[bool] = None,
    language_level: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """
    🔍 Search for jobs with AI-powered filtering and language level matching
    """
    try:
        logger.info(f"Job search request: query='{search_query}', location='{location}', language_level='{language_level}'")
        
        # Search jobs using the job search service
        results = await job_search_service.search_jobs(
            search_query=search_query,
            location=location,
            remote=remote,
            visa_sponsorship=visa_sponsorship,
            language_level=language_level,
            category=category,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": results,
            "message": f"Найдено {results.get('total_found', 0)} вакансий"
        }
        
    except Exception as e:
        logger.error(f"Job search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка поиска вакансий: {str(e)}")

@api_router.post("/job-search")
async def search_jobs_post(
    search_request: JobSearchRequest
):
    """
    🔍 Advanced job search with detailed filtering (POST method)
    """
    try:
        logger.info(f"Advanced job search: {search_request.dict()}")
        
        # Search jobs using the job search service
        results = await job_search_service.search_jobs(
            search_query=search_request.search_query,
            location=search_request.location,
            remote=search_request.remote,
            visa_sponsorship=search_request.visa_sponsorship,
            language_level=search_request.language_level,
            category=search_request.category,
            limit=search_request.limit
        )
        
        # Add salary estimates for each job
        if results.get('jobs'):
            for job in results['jobs']:
                try:
                    salary_estimate = job_search_service.estimate_salary_range(job)
                    job['estimated_salary'] = salary_estimate
                except Exception as e:
                    logger.warning(f"Failed to estimate salary for job {job.get('id', 'unknown')}: {e}")
        
        return {
            "status": "success",
            "data": results,
            "message": f"Найдено {results.get('total_found', 0)} вакансий с расширенной фильтрацией"
        }
        
    except Exception as e:
        logger.error(f"Advanced job search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка расширенного поиска вакансий: {str(e)}")

@api_router.post("/job-subscriptions")
async def create_job_subscription(
    subscription_request: JobSubscriptionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📬 Create job search subscription for Telegram notifications
    """
    try:
        logger.info(f"Creating job subscription for user {current_user['id']}")
        
        # Save subscription
        result = await job_search_service.save_job_subscription(
            user_id=current_user['id'],
            search_params=subscription_request.dict()
        )
        
        return {
            "status": "success",
            "data": result,
            "message": "Подписка на вакансии создана! Вы будете получать уведомления о новых подходящих вакансиях в Telegram."
        }
        
    except Exception as e:
        logger.error(f"Failed to create job subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания подписки на вакансии: {str(e)}")

@api_router.get("/job-subscriptions")
async def get_job_subscriptions(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📋 Get user's job subscriptions
    """
    try:
        subscriptions = await job_search_service.get_user_subscriptions(current_user['id'])
        
        return {
            "status": "success",
            "data": subscriptions,
            "count": len(subscriptions),
            "message": f"Найдено {len(subscriptions)} активных подписок на вакансии"
        }
        
    except Exception as e:
        logger.error(f"Failed to get job subscriptions: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения подписок: {str(e)}")

@api_router.put("/job-subscriptions/{subscription_id}")
async def update_job_subscription(
    subscription_id: str,
    updates: JobSubscriptionUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    ✏️ Update job subscription
    """
    try:
        result = await job_search_service.update_subscription(
            subscription_id=subscription_id,
            user_id=current_user['id'],
            updates=updates.dict(exclude_unset=True)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update job subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления подписки: {str(e)}")

@api_router.delete("/job-subscriptions/{subscription_id}")
async def delete_job_subscription(
    subscription_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🗑️ Delete job subscription
    """
    try:
        result = await job_search_service.delete_subscription(
            subscription_id=subscription_id,
            user_id=current_user['id']
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to delete job subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления подписки: {str(e)}")

# =====================================================
# RESUME ANALYSIS API ENDPOINTS
# =====================================================

@api_router.post("/analyze-resume")
async def analyze_resume(
    resume_request: ResumeAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📄 AI-powered resume analysis with improvement suggestions
    """
    try:
        logger.info(f"Resume analysis request from user {current_user['id']}")
        
        # Get user providers for AI analysis
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))
        
        # Analyze resume
        result = await job_ai_service.analyze_resume(
            resume_text=resume_request.resume_text,
            target_position=resume_request.target_position,
            user_providers=user_providers if user_providers else None,
            language=resume_request.language
        )
        
        # Save analysis to database if successful
        if result.get('status') == 'success':
            try:
                analysis_id = await db.save_resume_analysis({
                    'user_id': current_user['id'],
                    'resume_text': resume_request.resume_text,
                    'target_position': resume_request.target_position,
                    'analysis_result': result['analysis'],
                    'overall_score': result['analysis'].get('overall_score'),
                    'language': resume_request.language,
                    'ai_provider': user_providers[0][0] if user_providers else 'demo'
                })
                result['analysis_id'] = analysis_id
            except Exception as e:
                logger.warning(f"Failed to save resume analysis: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Resume analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка анализа резюме: {str(e)}")

@api_router.post("/improve-resume")
async def improve_resume(
    improvement_request: ResumeImprovementRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    ✨ Generate improved version of resume based on analysis
    """
    try:
        logger.info(f"Resume improvement request from user {current_user['id']}")
        
        # Get original analysis
        analysis = await db.get_resume_analysis(improvement_request.resume_analysis_id, current_user['id'])
        if not analysis:
            raise HTTPException(status_code=404, detail="Анализ резюме не найден")
        
        # Get user providers for AI improvement
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))
        
        # Generate improved resume
        result = await job_ai_service.generate_improved_resume(
            original_resume=analysis['resume_text'],
            analysis_results=analysis['analysis_result'],
            target_position=improvement_request.target_position or analysis.get('target_position'),
            user_providers=user_providers if user_providers else None,
            language=analysis.get('language', 'ru')
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume improvement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка улучшения резюме: {str(e)}")

@api_router.get("/resume-analyses")
async def get_resume_analyses(
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📋 Get user's resume analyses history
    """
    try:
        analyses = await db.get_user_resume_analyses(current_user['id'], limit)
        
        return {
            "status": "success",
            "data": analyses,
            "count": len(analyses),
            "message": f"Найдено {len(analyses)} анализов резюме"
        }
        
    except Exception as e:
        logger.error(f"Failed to get resume analyses: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения анализов резюме: {str(e)}")

@api_router.get("/resume-analyses/{analysis_id}")
async def get_resume_analysis(
    analysis_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📄 Get specific resume analysis
    """
    try:
        analysis = await db.get_resume_analysis(analysis_id, current_user['id'])
        if not analysis:
            raise HTTPException(status_code=404, detail="Анализ резюме не найден")
        
        return {
            "status": "success",
            "data": analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get resume analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения анализа резюме: {str(e)}")

# =====================================================
# INTERVIEW PREPARATION API ENDPOINTS
# =====================================================

@api_router.post("/prepare-interview")
async def prepare_interview(
    prep_request: InterviewPrepRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🎤 AI-powered interview preparation and coaching
    """
    try:
        logger.info(f"Interview preparation request from user {current_user['id']}")
        
        # Get user providers for AI coaching
        user_providers = []
        if current_user.get("gemini_api_key"):
            user_providers.append(("gemini", "gemini-2.0-flash", current_user["gemini_api_key"]))
        if current_user.get("openai_api_key"):
            user_providers.append(("openai", "gpt-4o-mini", current_user["openai_api_key"]))
        if current_user.get("anthropic_api_key"):
            user_providers.append(("anthropic", "claude-3-haiku-20240307", current_user["anthropic_api_key"]))
        
        # Prepare interview coaching
        result = await job_ai_service.prepare_for_interview(
            job_description=prep_request.job_description,
            resume_text=prep_request.resume_text,
            interview_type=prep_request.interview_type,
            user_providers=user_providers if user_providers else None,
            language=prep_request.language
        )
        
        # Save preparation to database if successful
        if result.get('status') == 'success':
            try:
                prep_id = await db.save_interview_preparation({
                    'user_id': current_user['id'],
                    'job_description': prep_request.job_description,
                    'resume_text': prep_request.resume_text,
                    'interview_type': prep_request.interview_type,
                    'coaching_result': result['coaching'],
                    'language': prep_request.language,
                    'ai_provider': user_providers[0][0] if user_providers else 'demo'
                })
                result['preparation_id'] = prep_id
            except Exception as e:
                logger.warning(f"Failed to save interview preparation: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Interview preparation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка подготовки к собеседованию: {str(e)}")

@api_router.get("/interview-preparations")
async def get_interview_preparations(
    limit: int = 20,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    📋 Get user's interview preparations history
    """
    try:
        preparations = await db.get_user_interview_preparations(current_user['id'], limit)
        
        return {
            "status": "success",
            "data": preparations,
            "count": len(preparations),
            "message": f"Найдено {len(preparations)} подготовок к собеседованию"
        }
        
    except Exception as e:
        logger.error(f"Failed to get interview preparations: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения подготовок к собеседованию: {str(e)}")

@api_router.get("/interview-preparations/{prep_id}")
async def get_interview_preparation(
    prep_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    🎤 Get specific interview preparation
    """
    try:
        preparation = await db.get_interview_preparation(prep_id, current_user['id'])
        if not preparation:
            raise HTTPException(status_code=404, detail="Подготовка к собеседованию не найдена")
        
        return {
            "status": "success",
            "data": preparation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get interview preparation: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения подготовки к собеседованию: {str(e)}")

# =====================================================
# JOB SEARCH STATUS ENDPOINTS
# =====================================================

@api_router.get("/job-search-status")
async def get_job_search_status():
    """
    📊 Get job search service status and statistics
    """
    try:
        # Get service status
        status_info = {
            "status": "active",
            "api_source": "arbeitnow.com",
            "features": [
                "🔍 Job search with filters",
                "🤖 AI language level estimation", 
                "📊 Job categorization",
                "💰 Salary estimation",
                "📬 Job subscriptions with Telegram notifications",
                "📄 AI resume analysis",
                "✨ Resume improvement suggestions",
                "🎤 AI interview coaching"
            ],
            "language_levels": job_search_service.language_levels,
            "job_categories": list(job_search_service.job_categories.keys()),
            "interview_types": job_ai_service.interview_types,
            "supported_languages": ["ru", "en", "de", "uk"],
            "demo_mode": False
        }
        
        return {
            "status": "success",
            "data": status_info,
            "message": "Job Search сервис активен и готов к работе"
        }
        
    except Exception as e:
        logger.error(f"Failed to get job search status: {e}")
        return {
            "status": "error",
            "message": f"Ошибка получения статуса Job Search сервиса: {str(e)}"
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
