import os
import logging
import tempfile
import base64
from typing import Optional, Tuple
import io
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
import requests
import json

logger = logging.getLogger(__name__)

class AlternativeOCRService:
    """Альтернативный OCR сервис с Google Vision API и fallback к простому text extraction"""
    
    def __init__(self):
        self.google_vision_available = self._check_google_vision_api()
        
    def _check_google_vision_api(self):
        """Проверка доступности Google Vision API"""
        try:
            api_key = os.environ.get('GOOGLE_VISION_API_KEY')
            if not api_key:
                logger.info("Google Vision API key not found in environment")
                return False
            
            # Простой тест API
            test_url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
            logger.info("Google Vision API key found and configured")
            return True
            
        except Exception as e:
            logger.error(f"Error checking Google Vision API: {e}")
            return False
    
    def extract_text_with_google_vision(self, image_content: bytes, languages: list = None) -> str:
        """Извлечение текста с помощью Google Vision API"""
        try:
            api_key = os.environ.get('GOOGLE_VISION_API_KEY')
            if not api_key:
                raise Exception("Google Vision API key not found")
            
            url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
            
            # Конвертируем в base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Создаем запрос к API
            request_data = {
                "requests": [{
                    "image": {
                        "content": image_base64
                    },
                    "features": [{
                        "type": "DOCUMENT_TEXT_DETECTION"
                    }]
                }]
            }
            
            # Добавляем языковые hints если указаны
            if languages:
                request_data["requests"][0]["imageContext"] = {
                    "languageHints": languages
                }
            
            # Отправляем запрос
            response = requests.post(url, json=request_data)
            response.raise_for_status()
            
            result = response.json()
            
            # Извлекаем текст
            if "responses" in result and len(result["responses"]) > 0:
                response_data = result["responses"][0]
                if "fullTextAnnotation" in response_data:
                    extracted_text = response_data["fullTextAnnotation"]["text"]
                    logger.info(f"Google Vision API extracted {len(extracted_text)} characters")
                    return extracted_text
                elif "textAnnotations" in response_data and len(response_data["textAnnotations"]) > 0:
                    extracted_text = response_data["textAnnotations"][0]["description"]
                    logger.info(f"Google Vision API extracted {len(extracted_text)} characters")
                    return extracted_text
            
            logger.warning("No text found by Google Vision API")
            return ""
            
        except Exception as e:
            logger.error(f"Google Vision API error: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Извлечение текста из PDF файла"""
        try:
            extracted_text = ""
            
            # Сначала пробуем извлечь текст напрямую из PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        extracted_text += text + "\n"
            
            # Если текст извлечен успешно, возвращаем его
            if extracted_text.strip():
                logger.info(f"Extracted text directly from PDF: {len(extracted_text)} characters")
                return extracted_text.strip()
            
            # Если текст не извлечен, пробуем OCR с Google Vision
            if self.google_vision_available:
                logger.info("Direct PDF text extraction failed, trying OCR with Google Vision...")
                return self._extract_text_from_pdf_with_google_vision(pdf_path)
            
            logger.warning("No text extraction method available for PDF")
            return "PDF содержит изображения, но OCR не доступен"
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return "Ошибка при извлечении текста из PDF файла"
    
    def _extract_text_from_pdf_with_google_vision(self, pdf_path: str) -> str:
        """Извлечение текста из PDF с помощью Google Vision API"""
        try:
            # Конвертируем PDF в изображения
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=5)
            
            extracted_text = ""
            for i, image in enumerate(images):
                # Конвертируем изображение в bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Извлекаем текст с помощью Google Vision
                try:
                    page_text = self.extract_text_with_google_vision(img_byte_arr, ['de', 'en', 'ru', 'uk'])
                    if page_text:
                        extracted_text += f"--- Страница {i+1} ---\n{page_text}\n\n"
                except Exception as e:
                    logger.warning(f"Google Vision failed for page {i+1}: {e}")
                    continue
            
            logger.info(f"Extracted text from PDF with Google Vision: {len(extracted_text)} characters")
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF with Google Vision: {e}")
            return "Ошибка при извлечении текста из PDF с помощью OCR"
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Извлечение текста из изображения"""
        try:
            # Читаем изображение как bytes
            with open(image_path, 'rb') as f:
                image_content = f.read()
            
            # Если доступен Google Vision API, используем его
            if self.google_vision_available:
                try:
                    text = self.extract_text_with_google_vision(image_content, ['de', 'en', 'ru', 'uk'])
                    if text:
                        logger.info(f"Google Vision extracted {len(text)} characters from image")
                        return text
                except Exception as e:
                    logger.warning(f"Google Vision failed, no fallback available: {e}")
            
            # Если Google Vision не доступен
            logger.warning("Google Vision API not available and no local OCR - cannot extract text from image")
            return "OCR не доступен - не удалось извлечь текст из изображения"
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return "Ошибка при извлечении текста из изображения"
    
    def process_document(self, file_path: str, file_type: str) -> Tuple[str, str]:
        """Обработка документа - извлечение текста и определение типа обработки"""
        try:
            extracted_text = ""
            processing_method = "unknown"
            
            if file_type.lower() == 'pdf' or file_path.lower().endswith('.pdf'):
                extracted_text = self.extract_text_from_pdf(file_path)
                processing_method = "pdf_extraction" if not self.google_vision_available else "pdf_google_vision"
            elif file_type.startswith('image/') or any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']):
                extracted_text = self.extract_text_from_image(file_path)
                processing_method = "google_vision_ocr" if self.google_vision_available else "no_ocr"
            else:
                # Пробуем как текстовый файл
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        extracted_text = f.read()
                    processing_method = "text_file"
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='cp1252') as f:
                            extracted_text = f.read()
                        processing_method = "text_file"
                    except:
                        extracted_text = "Не удалось распознать тип файла или извлечь текст"
                        processing_method = "error"
            
            logger.info(f"Processed document: {processing_method}, extracted {len(extracted_text)} characters")
            return extracted_text, processing_method
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return "Ошибка при обработке документа", "error"
    
    def is_text_meaningful(self, text: str) -> bool:
        """Проверка, содержит ли текст осмысленную информацию"""
        if not text or len(text.strip()) < 10:
            return False
        
        # Проверяем, есть ли в тексте читаемые слова
        words = text.split()
        meaningful_words = [word for word in words if len(word) > 2 and word.isalpha()]
        
        return len(meaningful_words) > 3

# Глобальный экземпляр альтернативного OCR сервиса
alternative_ocr_service = AlternativeOCRService()