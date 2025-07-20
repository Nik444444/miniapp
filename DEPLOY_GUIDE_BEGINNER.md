# 📚 Пошаговое руководство для новичков: Деплой German Letter AI

## 🎯 Что мы будем делать:
1. Разместим **backend** (серверную часть) на **Fly.io**
2. Разместим **frontend** (интерфейс) на **Netlify**
3. Настроим все так, чтобы работало идеально!

---

## 📋 Что нужно подготовить:

### 1. Создать аккаунты:
- **Fly.io**: [https://fly.io](https://fly.io) - для backend
- **Netlify**: [https://netlify.com](https://netlify.com) - для frontend
- **GitHub**: [https://github.com](https://github.com) - для хранения кода

### 2. Получить API ключи:
- **Google OAuth**: [https://console.cloud.google.com](https://console.cloud.google.com)
- **Gemini API**: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **OpenAI API** (опционально): [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## 🚀 ШАГИ ДЛЯ ДЕПЛОЯ:

### ШАГ 1: Подготовка кода

1. **Загрузите код в GitHub**:
   ```bash
   git add .
   git commit -m "Готов к деплою"
   git push origin main
   ```

### ШАГ 2: Установка Fly CLI

**Windows:**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### ШАГ 3: Деплой Backend на Fly.io

1. **Войти в Fly.io**:
   ```bash
   flyctl auth login
   ```

2. **Создать приложение**:
   ```bash
   flyctl apps create your-app-name
   ```

3. **Создать хранилище для базы данных**:
   ```bash
   flyctl volumes create german_ai_data --region fra --size 1
   ```

4. **Настроить переменные окружения**:
   ```bash
   flyctl secrets set GOOGLE_CLIENT_SECRET="ваш-google-client-secret"
   flyctl secrets set GEMINI_API_KEY="ваш-gemini-api-key"
   flyctl secrets set ADMIN_PASSWORD="ваш-админ-пароль"
   ```

5. **Деплой**:
   ```bash
   flyctl deploy
   ```

6. **Получить URL**:
   ```bash
   flyctl info
   ```
   **Запишите URL** - например: `https://your-app-name.fly.dev`

### ШАГ 4: Деплой Frontend на Netlify

1. **Перейти на Netlify.com**
2. **Нажать "New site from Git"**
3. **Выбрать ваш GitHub репозиторий**
4. **Настроить деплой**:
   - **Base directory**: `frontend`
   - **Build command**: `yarn build`
   - **Publish directory**: `build`

5. **Добавить переменные окружения**:
   - Перейти в "Site settings" → "Environment variables"
   - Добавить:
     - `REACT_APP_BACKEND_URL`: `https://your-app-name.fly.dev`
     - `REACT_APP_GOOGLE_CLIENT_ID`: `ваш-google-client-id`

6. **Нажать "Deploy site"**

### ШАГ 5: Настройка Google OAuth

1. **Перейти в Google Cloud Console**
2. **Найти ваш OAuth Client ID**
3. **В "Authorized JavaScript origins" добавить**:
   - `https://your-netlify-site.netlify.app`
4. **Сохранить**

### ШАГ 6: Проверка работы

1. **Открыть ваш Netlify сайт**
2. **Попробовать войти через Google**
3. **Загрузить тестовый документ**
4. **Убедиться, что анализ работает**

---

## 🆘 Если что-то не работает:

### Backend проблемы:
```bash
# Проверить логи
flyctl logs

# Проверить статус
flyctl status

# Перезапустить
flyctl restart
```

### Frontend проблемы:
1. **Проверить Build логи** в Netlify Dashboard
2. **Проверить переменные окружения** в настройках сайта
3. **Проверить консоль браузера** на предмет ошибок

### Частые ошибки:
- **CORS ошибки**: Проверьте правильность URL в `REACT_APP_BACKEND_URL`
- **Google OAuth ошибки**: Проверьте настройки в Google Cloud Console
- **API ключи**: Убедитесь, что все ключи введены правильно

---

## 🎉 Готово!

После успешного деплоя у вас будет:
- ✅ Работающий backend на Fly.io
- ✅ Красивый frontend на Netlify
- ✅ Полная функциональность OCR анализа
- ✅ Интеграция с Google OAuth
- ✅ Поддержка Telegram Mini App

**Время деплоя**: 15-30 минут для новичка
**Стоимость**: Бесплатно (в рамках free tier)

---

## 📞 Нужна помощь?

- **Fly.io документация**: [https://fly.io/docs](https://fly.io/docs)
- **Netlify документация**: [https://docs.netlify.com](https://docs.netlify.com)
- **Google OAuth**: [https://developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)

**Удачи с деплоем! 🚀**