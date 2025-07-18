#!/bin/bash

# 🚀 Автоматический деплой German Letter AI на Fly.io + Netlify
# Автор: AI Assistant
# Дата: 2025

set -e

echo "🚀 Начинаем автоматический деплой German Letter AI"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка наличия необходимых инструментов
echo -e "${YELLOW}Проверка необходимых инструментов...${NC}"

if ! command -v flyctl &> /dev/null; then
    echo -e "${RED}❌ Fly CLI не установлен. Установите: https://fly.io/docs/hands-on/install-flyctl/${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git не установлен${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Все инструменты доступны${NC}"

# Функция для ввода переменных
read_var() {
    local var_name=$1
    local prompt=$2
    local default_value=$3
    
    if [ -n "$default_value" ]; then
        read -p "$prompt [$default_value]: " value
        echo ${value:-$default_value}
    else
        read -p "$prompt: " value
        echo $value
    fi
}

# Интерактивный ввод переменных
echo -e "${YELLOW}Настройка переменных окружения...${NC}"

APP_NAME=$(read_var "APP_NAME" "Название приложения Fly.io" "german-letter-ai-backend")
REGION=$(read_var "REGION" "Регион Fly.io" "fra")
GOOGLE_CLIENT_SECRET=$(read_var "GOOGLE_CLIENT_SECRET" "Google Client Secret" "")
GEMINI_API_KEY=$(read_var "GEMINI_API_KEY" "Gemini API Key" "")
OPENAI_API_KEY=$(read_var "OPENAI_API_KEY" "OpenAI API Key (optional)" "")
ANTHROPIC_API_KEY=$(read_var "ANTHROPIC_API_KEY" "Anthropic API Key (optional)" "")
ADMIN_PASSWORD=$(read_var "ADMIN_PASSWORD" "Admin Password" "admin123")

echo -e "${GREEN}✅ Переменные настроены${NC}"

# Аутентификация в Fly.io
echo -e "${YELLOW}Аутентификация в Fly.io...${NC}"
flyctl auth login

# Создание приложения
echo -e "${YELLOW}Создание приложения $APP_NAME...${NC}"
flyctl apps create $APP_NAME --org personal || echo "Приложение уже существует"

# Создание volume для базы данных
echo -e "${YELLOW}Создание volume для базы данных...${NC}"
flyctl volumes create german_ai_data --region $REGION --size 1 -a $APP_NAME || echo "Volume уже существует"

# Установка secrets
echo -e "${YELLOW}Настройка переменных окружения...${NC}"
flyctl secrets set -a $APP_NAME \
    JWT_SECRET_KEY="$(openssl rand -base64 32)" \
    GOOGLE_CLIENT_ID="364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com" \
    GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
    GEMINI_API_KEY="$GEMINI_API_KEY" \
    OPENAI_API_KEY="$OPENAI_API_KEY" \
    ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
    ADMIN_PASSWORD="$ADMIN_PASSWORD"

# Обновление fly.toml с корректным именем приложения
echo -e "${YELLOW}Обновление конфигурации...${NC}"
sed -i "s/app = \"german-letter-ai-backend\"/app = \"$APP_NAME\"/g" fly.toml
sed -i "s/primary_region = \"fra\"/primary_region = \"$REGION\"/g" fly.toml

# Деплой backend
echo -e "${YELLOW}Деплой backend на Fly.io...${NC}"
flyctl deploy -a $APP_NAME

# Получение URL приложения
APP_URL=$(flyctl info -a $APP_NAME | grep "Hostname" | awk '{print $2}')
BACKEND_URL="https://$APP_URL"

echo -e "${GREEN}✅ Backend успешно развернут: $BACKEND_URL${NC}"

# Проверка работы backend
echo -e "${YELLOW}Проверка работы backend...${NC}"
sleep 10  # Ждем пока приложение запустится

if curl -s --max-time 30 "$BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend работает корректно${NC}"
else
    echo -e "${RED}❌ Backend не отвечает. Проверьте логи: flyctl logs -a $APP_NAME${NC}"
fi

# Обновление frontend .env
echo -e "${YELLOW}Обновление frontend конфигурации...${NC}"
cat > frontend/.env << EOF
# Frontend Environment Variables - NETLIFY PRODUCTION
REACT_APP_BACKEND_URL=$BACKEND_URL
REACT_APP_GOOGLE_CLIENT_ID=364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com
EOF

echo -e "${GREEN}✅ Frontend .env обновлен${NC}"

# Инструкции для Netlify
echo -e "${YELLOW}=================================================="
echo -e "🎯 СЛЕДУЮЩИЕ ШАГИ ДЛЯ NETLIFY:"
echo -e "=================================================="
echo -e "1. Загрузите код в Git репозиторий:"
echo -e "   ${GREEN}git add .${NC}"
echo -e "   ${GREEN}git commit -m 'Готов к деплою на Fly.io + Netlify'${NC}"
echo -e "   ${GREEN}git push origin main${NC}"
echo -e ""
echo -e "2. Создайте новый сайт на Netlify:"
echo -e "   - Перейдите на https://netlify.com"
echo -e "   - Нажмите 'New site from Git'"
echo -e "   - Выберите ваш репозиторий"
echo -e "   - Настройте деплой:"
echo -e "     ${GREEN}Base directory: frontend${NC}"
echo -e "     ${GREEN}Build command: yarn build${NC}"
echo -e "     ${GREEN}Publish directory: build${NC}"
echo -e ""
echo -e "3. Добавьте environment variables в Netlify:"
echo -e "   ${GREEN}REACT_APP_BACKEND_URL: $BACKEND_URL${NC}"
echo -e "   ${GREEN}REACT_APP_GOOGLE_CLIENT_ID: 364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com${NC}"
echo -e ""
echo -e "4. Обновите Google OAuth настройки:"
echo -e "   - Перейдите в Google Cloud Console"
echo -e "   - Добавьте ваш Netlify URL в Authorized JavaScript origins"
echo -e ""
echo -e "5. Проверьте работу приложения!"
echo -e "=================================================="

echo -e "${GREEN}✅ Деплой backend завершен успешно!${NC}"
echo -e "${GREEN}📝 Backend URL: $BACKEND_URL${NC}"
echo -e "${GREEN}📋 Следуйте инструкциям выше для завершения деплоя frontend${NC}"