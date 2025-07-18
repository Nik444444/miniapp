# 🚀 German Letter AI - Telegram Mini App

[![Deployment Status](https://img.shields.io/badge/Deployment-Ready-brightgreen)](https://github.com/yourusername/german-letter-ai)
[![Backend](https://img.shields.io/badge/Backend-Fly.io-purple)](https://fly.io)
[![Frontend](https://img.shields.io/badge/Frontend-Netlify-blue)](https://netlify.com)
[![OCR](https://img.shields.io/badge/OCR-Tesseract%205.3.0-orange)](https://github.com/tesseract-ocr/tesseract)
[![AI](https://img.shields.io/badge/AI-Gemini%20%7C%20OpenAI%20%7C%20Claude-lightblue)](https://ai.google.dev)

## 📋 Описание

**German Letter AI** - это мощное приложение для анализа немецких документов с использованием OCR и искусственного интеллекта. Поддерживает как веб-интерфейс, так и Telegram Mini App.

### 🎯 Основные возможности

- **🔍 OCR анализ** - Распознавание текста с помощью Tesseract 5.3.0
- **🤖 AI анализ** - Интеллектуальный анализ документов с помощью Gemini, OpenAI, Claude
- **📱 Telegram Mini App** - Полная поддержка Telegram Web App
- **🌐 Веб-интерфейс** - Современный дизайн с Tailwind CSS
- **🔐 OAuth авторизация** - Безопасная авторизация через Google и Telegram
- **📊 Аналитика** - Детальный анализ документов с рекомендациями
- **🗞️ Telegram новости** - Интеграция с Telegram каналами
- **👨‍💼 Админ панель** - Управление текстами приложения

### 🛠️ Технологии

**Backend:**
- FastAPI (Python 3.11)
- SQLite база данных
- Tesseract OCR 5.3.0
- Google OAuth 2.0
- Современные LLM (Gemini, OpenAI, Claude)
- emergentintegrations

**Frontend:**
- React 19
- Tailwind CSS
- React Router Dom 7.5.1
- Google OAuth
- Telegram Web App SDK

---

## 🚀 Быстрый старт

### Вариант 1: Автоматический деплой

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/german-letter-ai.git
cd german-letter-ai

# Проверьте готовность к деплою
python check_deployment_ready.py

# Запустите автоматический деплой
./auto_deploy.sh
```

### Вариант 2: Ручной деплой

1. **Подготовьте аккаунты:**
   - [Fly.io](https://fly.io) - для backend
   - [Netlify](https://netlify.com) - для frontend

2. **Получите API ключи:**
   - [Google OAuth](https://console.cloud.google.com)
   - [Gemini API](https://aistudio.google.com/apikey)

3. **Следуйте руководству:**
   - 📚 [Подробное руководство](DEPLOY_GUIDE_FLY_NETLIFY.md)
   - 📖 [Руководство для новичков](DEPLOY_GUIDE_BEGINNER.md)

---

## 📁 Структура проекта

```
german-letter-ai/
├── backend/                  # FastAPI сервер
│   ├── server.py            # Основной сервер
│   ├── requirements.txt     # Python зависимости
│   ├── database.py          # SQLite база данных
│   ├── llm_manager.py       # Менеджер LLM
│   ├── improved_ocr_service.py  # OCR сервис
│   └── .env                 # Переменные окружения
├── frontend/                # React приложение
│   ├── src/
│   │   ├── components/      # React компоненты
│   │   ├── context/         # Context API
│   │   └── utils/           # Утилиты
│   ├── public/
│   │   └── _redirects       # Netlify redirects
│   ├── package.json         # Node.js зависимости
│   └── .env                 # Переменные окружения
├── fly.toml                 # Конфигурация Fly.io
├── netlify.toml             # Конфигурация Netlify
├── Dockerfile               # Docker для backend
├── auto_deploy.sh           # Автоматический деплой
├── check_deployment_ready.py # Проверка готовности
└── README.md               # Этот файл
```

---

## 🔧 Локальная разработка

### Требования

- Python 3.11+
- Node.js 20+
- Yarn
- Tesseract OCR

### Запуск backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Запуск frontend

```bash
cd frontend
yarn install
yarn start
```

### Переменные окружения

**Backend (.env):**
```env
JWT_SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GEMINI_API_KEY=your-gemini-api-key
SQLITE_DB_PATH=/app/data/german_ai.db
TESSERACT_AVAILABLE=true
TESSERACT_VERSION=5.3.0
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

---

## 📊 Деплой статистика

### Платформы деплоя

- **Backend**: Fly.io
  - Регион: Frankfurt (fra)
  - Память: 1GB
  - Persistent storage: 1GB volume
  - Автоматическое масштабирование

- **Frontend**: Netlify
  - CDN: Global
  - Сборка: Node.js 20
  - Автоматический деплой из Git

### Время деплоя

- **Первый деплой**: 10-15 минут
- **Обновления**: 3-5 минут
- **Проверка готовности**: 30 секунд

---

## 🛡️ Безопасность

- **OAuth 2.0** - Безопасная авторизация
- **JWT токены** - Защищенные сессии
- **HTTPS** - Шифрование трафика
- **CORS** - Защита от межсайтовых атак
- **Secrets management** - Безопасное хранение ключей

---

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

---

## 📞 Поддержка

- **Документация**: [Руководства по деплою](DEPLOY_GUIDE_FLY_NETLIFY.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/german-letter-ai/issues)
- **Email**: support@german-letter-ai.com

---

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

---

## 🎉 Благодарности

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR движок
- [FastAPI](https://fastapi.tiangolo.com/) - Backend фреймворк
- [React](https://reactjs.org/) - Frontend фреймворк
- [Fly.io](https://fly.io) - Хостинг backend
- [Netlify](https://netlify.com) - Хостинг frontend

---

**Сделано с ❤️ для анализа немецких документов**
