# 🎯 КРАТКАЯ ИНСТРУКЦИЯ ПО ДЕПЛОЮ

## 📋 Подготовка (5 минут)

### 1. Аккаунты
- [x] Fly.io (backend)
- [x] Netlify (frontend)
- [x] GitHub (код)

### 2. Инструменты
```bash
# Установите Fly CLI
curl -L https://fly.io/install.sh | sh  # macOS/Linux
# или
iwr https://fly.io/install.ps1 -useb | iex  # Windows
```

### 3. API ключи
- Google Client Secret
- Gemini API Key ([получить](https://aistudio.google.com/apikey))

---

## 🚀 ДЕПЛОЙ (10 минут)

### BACKEND (Fly.io)

```bash
# 1. Логин
flyctl auth login

# 2. Создать приложение
flyctl apps create your-app-name

# 3. Создать volume
flyctl volumes create german_ai_data --region fra --size 1

# 4. Настроить secrets
flyctl secrets set GOOGLE_CLIENT_SECRET="your-secret"
flyctl secrets set GEMINI_API_KEY="your-key"

# 5. Деплой
flyctl deploy

# 6. Получить URL
flyctl info
```

### FRONTEND (Netlify)

```bash
# 1. Обновить .env
echo "REACT_APP_BACKEND_URL=https://your-app.fly.dev" > frontend/.env
echo "REACT_APP_GOOGLE_CLIENT_ID=364877380148-nhlcauaonsvm5j0feh5fltn3qsa6tffm.apps.googleusercontent.com" >> frontend/.env

# 2. Загрузить в GitHub
git add .
git commit -m "Deploy ready"
git push origin main

# 3. Настроить на Netlify.com
# - New site from Git
# - Base directory: frontend
# - Build command: yarn build
# - Publish directory: build
# - Environment variables: как в .env
```

---

## ✅ ПРОВЕРКА

```bash
# Проверить готовность
python check_deployment_ready.py

# Проверить backend
curl https://your-app.fly.dev/health

# Проверить frontend
# Откройте ваш Netlify URL
```

---

## 📚 ДОКУМЕНТАЦИЯ

- 📖 [Подробное руководство](DEPLOY_GUIDE_FLY_NETLIFY.md)
- 📋 [Для новичков](DEPLOY_GUIDE_BEGINNER.md)
- 🤖 [Автоматический деплой](auto_deploy.sh)

---

## 🆘 ПОМОЩЬ

**Проблемы?**
- Fly.io логи: `flyctl logs`
- Netlify: Dashboard → Site logs
- CORS: Проверьте REACT_APP_BACKEND_URL

**Время деплоя:** 15 минут
**Стоимость:** Бесплатно (free tier)

🎉 **Готово!** Ваш AI помощник работает!