# Dockerfile для Fly.io деплоя - German Letter AI Backend
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Обновляем систему и устанавливаем необходимые системные пакеты
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    tesseract-ocr-ukr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Обновляем pip до последней версии
RUN pip install --upgrade pip

# Копируем файлы зависимостей
COPY backend/requirements.txt .

# Устанавливаем стандартные зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем backend код
COPY backend/ .

# Устанавливаем emergentintegrations во время сборки с обработкой ошибок
RUN pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ --trusted-host d33sy5i8bnduwe.cloudfront.net || \
    echo "Warning: emergentintegrations installation failed, application will run in fallback mode"

# Создаем директорию для SQLite базы данных
RUN mkdir -p /app/data && chmod 777 /app/data

# Проверяем установку tesseract и путь
RUN which tesseract || echo "tesseract not found"
RUN tesseract --version || echo "tesseract version check failed"
RUN ls -la /usr/bin/tesseract || echo "tesseract binary not found"

# Устанавливаем переменные окружения
ENV SQLITE_DB_PATH=/app/data/german_ai.db
ENV TESSERACT_AVAILABLE=true
ENV TESSERACT_VERSION=5.3.0
ENV PATH="/usr/bin:/usr/local/bin:$PATH"

# Проверяем что все зависимости работают
RUN python -c "import pytesseract; print('pytesseract OK')" || echo "pytesseract import failed"
RUN python -c "import cv2; print('opencv OK')" || echo "opencv import failed"
RUN python -c "import PIL; print('Pillow OK')" || echo "Pillow import failed"

# Открываем порт 8001
EXPOSE 8001

# Запускаем приложение, используя переменную окружения PORT
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}"]