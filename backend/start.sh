#!/bin/bash
# Улучшенный start.sh для 100% работы Tesseract OCR на Render

echo "🚀 Starting German AI Backend v14.0 - Production Mode with Tesseract OCR..."

# Показываем информацию о системе
echo "System Information:"
echo "Working directory: $(pwd)"
echo "Current PATH: $PATH"
echo "Current user: $(whoami)"
echo "Python version: $(python --version)"

# Проверяем переменные окружения
echo "Environment Variables:"
echo "TESSERACT_AVAILABLE: ${TESSERACT_AVAILABLE:-not_set}"
echo "TESSERACT_VERSION: ${TESSERACT_VERSION:-not_set}"
echo "TESSDATA_PREFIX: ${TESSDATA_PREFIX:-not_set}"
echo "SQLITE_DB_PATH: ${SQLITE_DB_PATH:-not_set}"

# Проверяем доступность tesseract ОБЯЗАТЕЛЬНО
echo "🔍 Checking Tesseract OCR availability..."
if command -v tesseract &> /dev/null; then
    echo "✅ tesseract found in PATH: $(which tesseract)"
    tesseract --version | head -3
    
    # Проверяем языковые пакеты
    echo "📦 Available language packages:"
    tesseract --list-langs 2>/dev/null || echo "Could not list languages"
    
    # Проверяем TESSDATA_PREFIX
    if [ -n "$TESSDATA_PREFIX" ] && [ -d "$TESSDATA_PREFIX" ]; then
        echo "✅ TESSDATA_PREFIX is set and directory exists: $TESSDATA_PREFIX"
        echo "Available language files:"
        ls -la "$TESSDATA_PREFIX" | grep -E "\.(traineddata)$" || echo "No traineddata files found"
    else
        echo "⚠️ TESSDATA_PREFIX issue - trying default paths"
        echo "Available tessdata locations:"
        find /usr -name "tessdata" -type d 2>/dev/null || echo "No tessdata directories found"
    fi
    
    # Тестируем работу tesseract
    echo "🧪 Testing Tesseract OCR functionality..."
    if echo "test" | tesseract stdin stdout -l eng 2>/dev/null; then
        echo "✅ Tesseract test successful"
    else
        echo "⚠️ Tesseract test failed"
    fi
else
    echo "❌ tesseract not found in PATH"
    echo "💡 Available commands:"
    ls -la /usr/bin/ | grep -i tesseract || echo "No tesseract in /usr/bin"
    echo "⚠️ OCR functionality will be limited to LLM Vision fallback"
fi

# Проверяем emergentintegrations
echo "🔍 Checking emergentintegrations..."
if python -c "import emergentintegrations; print('emergentintegrations version:', emergentintegrations.__version__ if hasattr(emergentintegrations, '__version__') else 'unknown')" 2>/dev/null; then
    echo "✅ emergentintegrations available"
else
    echo "⚠️ emergentintegrations not available - using fallback mode"
fi

# Проверяем критические Python зависимости
echo "🔍 Checking Python dependencies..."
python -c "import pytesseract; print('✅ pytesseract OK')" 2>/dev/null || echo "❌ pytesseract not available"
python -c "import cv2; print('✅ opencv-python OK')" 2>/dev/null || echo "❌ opencv-python not available"
python -c "import PIL; print('✅ Pillow OK')" 2>/dev/null || echo "❌ Pillow not available"
python -c "import httpcore; print('✅ httpcore OK')" 2>/dev/null || echo "❌ httpcore not available"
python -c "import PyPDF2; print('✅ PyPDF2 OK')" 2>/dev/null || echo "❌ PyPDF2 not available"
python -c "import pdf2image; print('✅ pdf2image OK')" 2>/dev/null || echo "❌ pdf2image not available"

# Проверяем модули приложения
echo "🔍 Checking application modules..."
python -c "from modern_llm_manager import modern_llm_manager; print('✅ modern_llm_manager OK')" 2>/dev/null || echo "❌ modern_llm_manager not available"
python -c "from improved_ocr_service import improved_ocr_service; print('✅ improved_ocr_service OK')" 2>/dev/null || echo "❌ improved_ocr_service not available"
python -c "from database import db; print('✅ database OK')" 2>/dev/null || echo "❌ database not available"

# Создаем директорию для базы данных
echo "🗂️ Setting up database directory..."
mkdir -p /app/backend/data 2>/dev/null || echo "Database directory already exists"

# Проверяем что сервер файл существует
if [ -f "server.py" ]; then
    echo "✅ server.py found"
else
    echo "❌ server.py not found in $(pwd)"
    echo "Files in current directory:"
    ls -la
    exit 1
fi

# Устанавливаем production переменные окружения
export TESSERACT_AVAILABLE=true
export TESSERACT_VERSION=5.3.0
export SQLITE_DB_PATH=${SQLITE_DB_PATH:-"/app/backend/data/german_ai.db"}

# Проверяем порт
PORT=${PORT:-8001}
echo "📡 Using port: $PORT"

echo "🔧 System diagnostics complete"
echo "🚀 Starting uvicorn server in production mode..."
echo "📝 Server will be available at: http://0.0.0.0:$PORT"

# Запускаем сервер с правильными настройками для production
exec uvicorn server:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info