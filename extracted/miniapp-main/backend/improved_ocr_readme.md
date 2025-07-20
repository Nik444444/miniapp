# Improved OCR Service

## Описание

Улучшенный OCR сервис для извлечения текста из изображений и PDF файлов без зависимости от tesseract. Использует современные методы анализа изображений и бесплатные API.

## Поддерживаемые методы (в порядке приоритета):

### 1. LLM Vision (Основной метод)
- **Gemini Pro Vision** - Через Google Gemini API
- **GPT-4V** - Через OpenAI API  
- **Claude 3.5 Sonnet** - Через Anthropic API
- **Преимущества**: Высокая точность, понимание контекста, поддержка многих языков
- **Требования**: API ключи LLM провайдеров (которые уже есть у пользователей)

### 2. OCR.space API (Fallback)
- **Бесплатный лимит**: 25,000 запросов/месяц
- **Языки**: Немецкий, английский, русский
- **Настройка**: Добавить `OCR_SPACE_API_KEY` в .env файл
- **Получить ключ**: https://ocr.space/ocrapi

### 3. Azure Computer Vision (Fallback)
- **Бесплатный лимит**: 5,000 запросов/месяц
- **Языки**: Множество языков включая DE, EN, RU, UK
- **Настройка**: Добавить `AZURE_COMPUTER_VISION_KEY` и `AZURE_COMPUTER_VISION_ENDPOINT` в .env
- **Получить ключи**: https://azure.microsoft.com/en-us/products/cognitive-services/computer-vision

### 4. Прямое извлечение из PDF
- Для PDF файлов с текстовым содержимым
- Не требует внешних API

## Поддерживаемые форматы файлов:

- **Изображения**: JPG, JPEG, PNG, BMP, TIFF, WebP, GIF
- **PDF**: Поддержка как текстовых, так и изображений в PDF
- **Текстовые файлы**: TXT, с поддержкой UTF-8 и CP1252

## Поддерживаемые языки:

- **Немецкий** (основной)
- **Английский**
- **Русский** 
- **Украинский**
- **И другие** (в зависимости от используемого API)

## Установка и настройка:

1. Основные зависимости уже в requirements.txt
2. Для расширенной функциональности добавьте в .env:
   ```
   OCR_SPACE_API_KEY=your_ocr_space_key
   AZURE_COMPUTER_VISION_KEY=your_azure_key
   AZURE_COMPUTER_VISION_ENDPOINT=your_azure_endpoint
   ```

## Использование:

```python
from improved_ocr_service import improved_ocr_service

# Обработка документа
extracted_text, processing_method = await improved_ocr_service.process_document(
    file_path="/path/to/document.pdf",
    file_type="application/pdf",
    user_providers=user_api_keys  # Опционально
)

# Получение статуса сервиса
status = improved_ocr_service.get_service_status()
```

## API Endpoints:

- `GET /api/ocr-status` - Получение статуса OCR сервиса
- `POST /api/analyze-file` - Анализ файла с OCR (уже обновлен)

## Преимущества над tesseract:

✅ **Без системных зависимостей** - Работает в любой среде  
✅ **Высокая точность** - Современные LLM превосходят tesseract  
✅ **Множественные fallback** - Надежность через резервные методы  
✅ **Понимание контекста** - LLM может интерпретировать сложные документы  
✅ **Production ready** - Готов к использованию в production  
✅ **Бесплатные альтернативы** - Не требует платных API  

## Мониторинг:

Сервис логирует каждый этап обработки:
- Какой метод использовался
- Количество извлеченных символов
- Ошибки и fallback переключения
- Время обработки

## Troubleshooting:

- Если LLM Vision не работает - проверьте API ключи пользователей
- Если OCR.space не работает - проверьте OCR_SPACE_API_KEY
- Если Azure не работает - проверьте ключи Azure
- Все методы недоступны - сервис вернет информативное сообщение

## Будущие улучшения:

- Добавление Google Cloud Vision API
- Поддержка Tesseract.js для клиентской обработки
- Кэширование результатов OCR
- Batch обработка множественных файлов