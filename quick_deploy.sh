#!/bin/bash

# Quick Deployment Script для German Letter AI Assistant
# Этот скрипт поможет быстро подготовить проект к развертыванию

echo "🚀 German Letter AI Assistant - Quick Deployment Setup"
echo "================================================="

# Создание необходимых .dockerignore файлов
echo "📦 Создание .dockerignore файлов..."

# Backend .dockerignore
cat > backend/.dockerignore << 'EOL'
*.md
*.txt
.git
.gitignore
.env.example
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
venv
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
.idea
.vscode
*.sqlite
*.db
EOL

# Frontend .dockerignore
cat > frontend/.dockerignore << 'EOL'
*.md
.git
.gitignore
.env.example
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.DS_Store
.idea
.vscode
*.log
build
.eslintcache
EOL

echo "✅ .dockerignore файлы созданы"

# Проверка существования необходимых файлов
echo "🔍 Проверка файлов проекта..."

required_files=(
    "backend/server.py"
    "backend/database.py"
    "backend/llm_manager.py"
    "backend/requirements.txt"
    "frontend/src/App.js"
    "frontend/package.json"
    "Dockerfile.backend"
    "Dockerfile.frontend"
    "render.yaml"
    "DEPLOYMENT_GUIDE.md"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ Все необходимые файлы найдены"
else
    echo "❌ Отсутствуют файлы:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Пожалуйста, убедитесь что все файлы существуют перед развертыванием."
    exit 1
fi

# Генерация JWT секрета
echo "🔐 Генерация JWT секрета..."
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
echo "✅ JWT Secret сгенерирован: $JWT_SECRET"

# Создание инструкции с персонализированными командами
echo "📝 Создание персонализированной инструкции..."

cat > QUICK_DEPLOY.md << EOL
# Быстрое развертывание - Ваш проект готов! 🎉

## 📋 Чек-лист перед развертыванием

### 1. API Ключи (получите заранее)
- [ ] Google OAuth Client ID и Secret
- [ ] Gemini API Key (рекомендуется)
- [ ] OpenAI API Key (опционально)
- [ ] Anthropic API Key (опционально)

### 2. Render.com настройки

**Backend сервис переменные:**
\`\`\`
JWT_SECRET_KEY=$JWT_SECRET
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
SQLITE_DB_PATH=/app/data/german_ai.db
\`\`\`

**Frontend сервис переменные:**
\`\`\`
REACT_APP_BACKEND_URL=https://your-backend-service.onrender.com
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
\`\`\`

### 3. Git команды для загрузки на GitHub
\`\`\`bash
git init
git add .
git commit -m "Initial commit - German Letter AI Assistant"
git remote add origin https://github.com/YOUR_USERNAME/german-letter-ai.git
git push -u origin main
\`\`\`

## 🔗 Полезные ссылки
- [Подробная инструкция](./DEPLOYMENT_GUIDE.md)
- [Google Cloud Console](https://console.cloud.google.com)
- [Render Dashboard](https://dashboard.render.com)
- [Gemini API](https://ai.google.dev)

Удачи с развертыванием! 🚀
EOL

echo "✅ Файл QUICK_DEPLOY.md создан"

# Финальная проверка
echo ""
echo "🎉 Проект готов к развертыванию!"
echo "================================"
echo ""
echo "📂 Структура проекта проверена"
echo "🔐 JWT секрет сгенерирован"
echo "📝 Инструкции созданы"
echo ""
echo "📖 Следующие шаги:"
echo "1. Прочитайте DEPLOYMENT_GUIDE.md для полной инструкции"
echo "2. Или используйте QUICK_DEPLOY.md для быстрого старта"
echo "3. Получите необходимые API ключи"
echo "4. Загрузите проект на GitHub"
echo "5. Разверните на Render.com"
echo ""
echo "🚀 Удачи с развертыванием!"