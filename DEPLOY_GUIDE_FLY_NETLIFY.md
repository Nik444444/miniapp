# 🚀 Полное руководство по деплою German Letter AI 

## Развертывание на Fly.io (Backend) + Netlify (Frontend)

### 📋 Предварительные требования

1. **Аккаунт на Fly.io** - [fly.io](https://fly.io)
2. **Аккаунт на Netlify** - [netlify.com](https://netlify.com)
3. **Установленный Fly CLI** - [Инструкция](https://fly.io/docs/hands-on/install-flyctl/)
4. **Git репозиторий** с вашим кодом

---

## 🎯 ЧАСТЬ 1: Развертывание Backend на Fly.io

### Шаг 1: Установка Fly CLI

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Проверка установки
flyctl version
```

### Шаг 2: Аутентификация в Fly.io

```bash
# Войти в аккаунт
flyctl auth login

# Создать новую организацию (если нужно)
flyctl orgs create your-org-name
```

### Шаг 3: Создание приложения на Fly.io

```bash
# Перейти в директорию проекта
cd /path/to/your/project

# Создать приложение (НЕ запускать flyctl launch!)
flyctl apps create german-letter-ai-backend
```

### Шаг 4: Создание Volume для SQLite базы данных

```bash
# Создать persistent volume для базы данных
flyctl volumes create german_ai_data --region fra --size 1
```

### Шаг 5: Настройка environment variables

```bash
# Установить необходимые переменные окружения
flyctl secrets set JWT_SECRET_KEY="your-super-secret-key-change-in-production"
flyctl secrets set GOOGLE_CLIENT_ID="364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com"
flyctl secrets set GOOGLE_CLIENT_SECRET="your-google-client-secret"
flyctl secrets set GEMINI_API_KEY="your-gemini-api-key"
flyctl secrets set OPENAI_API_KEY="your-openai-api-key"
flyctl secrets set ANTHROPIC_API_KEY="your-anthropic-api-key"
flyctl secrets set ADMIN_PASSWORD="admin123"
flyctl secrets set TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
flyctl secrets set OCR_SPACE_API_KEY="your-ocr-space-api-key"
flyctl secrets set AZURE_COMPUTER_VISION_KEY="your-azure-key"
flyctl secrets set AZURE_COMPUTER_VISION_ENDPOINT="your-azure-endpoint"
```

### Шаг 6: Деплой Backend

```bash
# Деплой приложения
flyctl deploy

# Проверка статуса
flyctl status

# Проверка логов
flyctl logs
```

### Шаг 7: Получение URL backend

```bash
# Получить URL вашего приложения
flyctl info
```

**Запишите URL** - он понадобится для настройки frontend!
Обычно это: `https://german-letter-ai-backend.fly.dev`

---

## 🎯 ЧАСТЬ 2: Развертывание Frontend на Netlify

### Шаг 1: Обновление Backend URL

Обновите файл `frontend/.env`:

```env
REACT_APP_BACKEND_URL=https://german-letter-ai-backend.fly.dev
REACT_APP_GOOGLE_CLIENT_ID=364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com
```

**⚠️ ВАЖНО**: Замените `german-letter-ai-backend.fly.dev` на фактический URL вашего backend!

### Шаг 2: Метод 1 - Деплой через Netlify CLI

```bash
# Установить Netlify CLI
npm install -g netlify-cli

# Войти в аккаунт
netlify login

# Перейти в директорию frontend
cd frontend

# Собрать приложение
yarn build

# Деплой
netlify deploy --prod --dir=build
```

### Шаг 3: Метод 2 - Деплой через Git (рекомендуется)

1. **Загрузить код в Git репозиторий**:
   ```bash
   git add .
   git commit -m "Готов к деплою на Fly.io + Netlify"
   git push origin main
   ```

2. **Создать новый сайт на Netlify**:
   - Перейти на [netlify.com](https://netlify.com)
   - Нажать "New site from Git"
   - Выбрать ваш Git репозиторий
   - Настроить деплой:
     - **Base directory**: `frontend`
     - **Build command**: `yarn build`
     - **Publish directory**: `build`

3. **Добавить environment variables в Netlify**:
   - Перейти в "Site settings" → "Environment variables"
   - Добавить:
     - `REACT_APP_BACKEND_URL`: `https://german-letter-ai-backend.fly.dev`
     - `REACT_APP_GOOGLE_CLIENT_ID`: `364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com`

4. **Деплой**:
   - Нажать "Deploy site"
   - Дождаться завершения сборки

---

## 🎯 ЧАСТЬ 3: Настройка Google OAuth

### Шаг 1: Обновление Google Cloud Console

1. Перейти в [Google Cloud Console](https://console.cloud.google.com/)
2. Выбрать проект (или создать новый)
3. Перейти в "APIs & Services" → "Credentials"
4. Найти OAuth 2.0 Client ID: `364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com`
5. В "Authorized JavaScript origins" добавить:
   - `https://your-netlify-site.netlify.app`
   - `https://your-custom-domain.com` (если есть)
6. В "Authorized redirect URIs" добавить:
   - `https://your-netlify-site.netlify.app/`

---

## 🎯 ЧАСТЬ 4: Проверка работы

### Проверка Backend

```bash
# Проверить health endpoint
curl https://german-letter-ai-backend.fly.dev/health

# Проверить API endpoint
curl https://german-letter-ai-backend.fly.dev/api/health
```

### Проверка Frontend

1. Открыть ваш Netlify сайт
2. Проверить авторизацию через Google
3. Загрузить тестовый документ
4. Проверить работу OCR анализа

---

## 🛠️ Troubleshooting

### Проблемы с Backend

```bash
# Проверить логи
flyctl logs -a german-letter-ai-backend

# Проверить статус
flyctl status -a german-letter-ai-backend

# Перезапустить приложение
flyctl restart -a german-letter-ai-backend
```

### Проблемы с Frontend

1. **Проверить Build логи** в Netlify Dashboard
2. **Проверить Environment Variables** в настройках сайта
3. **Проверить Network tab** в браузере на предмет CORS ошибок

### Проблемы с CORS

Если есть CORS ошибки, проверьте:
- Правильность URL в `REACT_APP_BACKEND_URL`
- Что backend действительно доступен по этому URL
- Что в backend правильно настроены CORS headers

---

## 📝 Важные заметки

1. **Первый деплой может занять 5-10 минут**
2. **SQLite база данных будет создана автоматически при первом запуске**
3. **Tesseract OCR будет доступен для анализа документов**
4. **Все зависимости (emergentintegrations) будут установлены автоматически**

---

## 🔧 Команды для обслуживания

### Обновление приложения

```bash
# Backend
flyctl deploy -a german-letter-ai-backend

# Frontend (если используется Git)
git push origin main  # Автоматически передеплоится
```

### Просмотр логов

```bash
# Backend логи
flyctl logs -a german-letter-ai-backend

# Frontend логи
# Доступны в Netlify Dashboard
```

### Управление базой данных

```bash
# Подключиться к приложению
flyctl ssh console -a german-letter-ai-backend

# Внутри контейнера
ls -la /app/data/
sqlite3 /app/data/german_ai.db
```

---

## 🎉 Готово!

После успешного деплоя у вас будет:
- ✅ Backend на Fly.io с полной функциональностью OCR
- ✅ Frontend на Netlify с современным дизайном
- ✅ Автоматическое масштабирование на Fly.io
- ✅ CDN и высокая производительность на Netlify
- ✅ Поддержка Telegram Mini App
- ✅ Полная интеграция с Google OAuth

**Ваши URL:**
- Backend: `https://german-letter-ai-backend.fly.dev`
- Frontend: `https://your-site.netlify.app`

**Финальный чек-лист:**
- [ ] Backend деплой завершен успешно
- [ ] Frontend деплой завершен успешно
- [ ] Google OAuth настроен правильно
- [ ] Тестовый документ успешно анализируется
- [ ] Все API endpoints работают
- [ ] Telegram интеграция функционирует