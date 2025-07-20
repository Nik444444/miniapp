# German Letter AI Assistant - Полное руководство по развертыванию на Render

## 📋 Содержание
1. [Подготовка API ключей](#1-подготовка-api-ключей)
2. [Настройка Google OAuth](#2-настройка-google-oauth)
3. [Развертывание на Render](#3-развертывание-на-render)
4. [Настройка переменных окружения](#4-настройка-переменных-окружения)
5. [Финальная настройка и тестирование](#5-финальная-настройка-и-тестирование)

---

## 1. Подготовка API ключей

### 🔑 Google Gemini API Key (рекомендуется)
1. Перейдите на [ai.google.dev](https://ai.google.dev)
2. Нажмите "Get API key in Google AI Studio"
3. Войдите в свой Google аккаунт
4. Нажмите "Create API key"
5. Выберите проект или создайте новый
6. Скопируйте и сохраните API ключ

### 🔑 OpenAI API Key (опционально)
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Войдите или зарегистрируйтесь
3. Перейдите в раздел "API keys"
4. Нажмите "Create new secret key"
5. Скопируйте и сохраните API ключ
6. **Важно**: Пополните баланс, минимум $5

### 🔑 Anthropic Claude API Key (опционально)
1. Перейдите на [console.anthropic.com](https://console.anthropic.com)
2. Войдите или зарегистрируйтесь
3. Перейдите в раздел "API Keys"
4. Нажмите "Create Key"
5. Скопируйте и сохраните API ключ
6. **Важно**: Пополните баланс, минимум $5

---

## 2. Настройка Google OAuth

### 2.1 Создание проекта в Google Cloud Console
1. Перейдите в [Google Cloud Console](https://console.cloud.google.com)
2. Нажмите на выпадающий список проектов вверху
3. Нажмите "New Project"
4. Введите название: "German Letter AI"
5. Нажмите "Create"

### 2.2 Включение Google+ API
1. В левом меню выберите "APIs & Services" → "Library"
2. Найдите "Google+ API"
3. Нажмите на неё и нажмите "Enable"

### 2.3 Создание OAuth 2.0 credentials
1. В левом меню выберите "APIs & Services" → "Credentials"
2. Нажмите "Create Credentials" → "OAuth 2.0 Client IDs"
3. Если появится запрос о настройке OAuth consent screen:
   - Нажмите "Configure Consent Screen"
   - Выберите "External"
   - Заполните обязательные поля:
     - App name: "German Letter AI Assistant"
     - User support email: ваш email
     - Developer contact information: ваш email
   - Нажмите "Save and Continue" на всех следующих шагах
4. Вернитесь к созданию credentials:
   - Application type: "Web application"
   - Name: "German Letter AI Web Client"
   - Authorized JavaScript origins: 
     - `http://localhost:3000` (для разработки)
     - `https://yourdomain.onrender.com` (замените на ваш домен после деплоя)
   - Authorized redirect URIs:
     - `http://localhost:3000` (для разработки)
     - `https://yourdomain.onrender.com` (замените на ваш домен после деплоя)
5. Нажмите "Create"
6. **Скопируйте Client ID и Client Secret**

---

## 3. Развертывание на Render

### 3.1 Подготовка репозитория
1. Создайте новый репозиторий на GitHub
2. Загрузите все файлы проекта в репозиторий:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - German Letter AI Assistant"
   git remote add origin https://github.com/YOUR_USERNAME/german-letter-ai.git
   git push -u origin main
   ```

### 3.2 Создание аккаунта на Render
1. Перейдите на [render.com](https://render.com)
2. Зарегистрируйтесь используя GitHub аккаунт
3. Подтвердите email если требуется

### 3.3 Развертывание Backend
1. На панели Render нажмите "New" → "Web Service"
2. Подключите ваш GitHub репозиторий
3. Настройте параметры:
   - **Name**: `german-ai-backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.backend`
   - **Docker Context Directory**: `./backend`
   - **Plan**: `Starter` (бесплатный)

### 3.4 Развертывание Frontend
1. Снова нажмите "New" → "Web Service"
2. Выберите тот же репозиторий
3. Настройте параметры:
   - **Name**: `german-ai-frontend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.frontend`
   - **Docker Context Directory**: `./frontend`
   - **Plan**: `Starter` (бесплатный)

---

## 4. Настройка переменных окружения

### 4.1 Backend Environment Variables
В настройках `german-ai-backend` добавьте:

```
JWT_SECRET_KEY=ваш_случайный_секретный_ключ_минимум_32_символа
GOOGLE_CLIENT_ID=ваш_google_client_id_из_шага_2
GOOGLE_CLIENT_SECRET=ваш_google_client_secret_из_шага_2
GEMINI_API_KEY=ваш_gemini_api_key_из_шага_1
OPENAI_API_KEY=ваш_openai_api_key_из_шага_1
ANTHROPIC_API_KEY=ваш_anthropic_api_key_из_шага_1
SQLITE_DB_PATH=/app/data/german_ai.db
```

**Генерация JWT_SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.2 Frontend Environment Variables
В настройках `german-ai-frontend` добавьте:

```
REACT_APP_BACKEND_URL=https://german-ai-backend.onrender.com
REACT_APP_GOOGLE_CLIENT_ID=ваш_google_client_id_из_шага_2
```

**Важно**: Замените `german-ai-backend` на реальное имя вашего backend сервиса.

---

## 5. Финальная настройка и тестирование

### 5.1 Обновление Google OAuth настроек
1. Вернитесь в [Google Cloud Console](https://console.cloud.google.com)
2. Перейдите в "APIs & Services" → "Credentials"
3. Найдите ваш OAuth 2.0 Client ID и нажмите на иконку редактирования
4. Обновите Authorized JavaScript origins и Authorized redirect URIs:
   - Добавьте: `https://ваш-frontend-домен.onrender.com`
   - Пример: `https://german-ai-frontend.onrender.com`
5. Нажмите "Save"

### 5.2 Тестирование приложения
1. Дождитесь завершения развертывания (может занять 5-10 минут)
2. Откройте URL вашего frontend приложения
3. Проверьте:
   - ✅ Загружается страница авторизации
   - ✅ Работает кнопка "Sign in with Google"
   - ✅ После авторизации открывается главная страница
   - ✅ Можно добавить API ключи в профиле
   - ✅ Можно загружать и анализировать файлы

### 5.3 Устранение возможных проблем

**Проблема: "Error 400: redirect_uri_mismatch"**
- Решение: Проверьте что домен правильно добавлен в Google OAuth настройки

**Проблема: "CORS ошибки"**
- Решение: Убедитесь что REACT_APP_BACKEND_URL правильно настроен

**Проблема: "API keys не работают"**
- Решение: Проверьте что все переменные окружения правильно настроены в Render

---

## 6. Дополнительные настройки (опционально)

### 6.1 Настройка собственного домена
1. В настройках сервиса на Render перейдите во вкладку "Settings"
2. В разделе "Custom Domains" нажмите "Add Custom Domain"
3. Введите ваш домен
4. Настройте DNS записи согласно инструкциям Render
5. Обновите Google OAuth настройки с новым доменом

### 6.2 Мониторинг и логи
- Логи можно просматривать во вкладке "Logs" каждого сервиса
- Для мониторинга используйте встроенные метрики Render

---

## 🎉 Поздравляем!

Ваше приложение German Letter AI Assistant теперь развернуто и готово к использованию!

**Полезные ссылки:**
- Frontend: `https://ваш-frontend.onrender.com`
- Backend API: `https://ваш-backend.onrender.com`
- Backend API документация: `https://ваш-backend.onrender.com/docs`

**Возможности приложения:**
- ✅ Анализ PDF документов
- ✅ Анализ изображений писем
- ✅ Поддержка трех AI провайдеров (Gemini, OpenAI, Anthropic)
- ✅ **Быстрое подключение Gemini одним нажатием**
- ✅ История анализов
- ✅ Безопасная аутентификация через Google
- ✅ Современный дизайн интерфейса
- ✅ Мультиязычность (русский, английский, немецкий)

**Новые возможности:**
- 🚀 **Подключение Gemini API одной кнопкой** - упрощенный процесс настройки
- 🎯 **Современная интеграция** - использование latest AI моделей
- 📱 **Улучшенный пользовательский интерфейс** - интуитивная настройка

---

## 📞 Техническая поддержка

Если у вас возникли проблемы:
1. Проверьте логи в Render Dashboard
2. Убедитесь что все переменные окружения настроены правильно
3. Проверьте что Google OAuth настройки корректны
4. Убедитесь что у вас есть API ключи и баланс для AI провайдеров