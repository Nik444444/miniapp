import os
import logging
import tempfile
from typing import Optional, Tuple
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
import asyncio
from datetime import datetime
import pytesseract
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class SimpleTesseractOCR:
    """
    Упрощенный и быстрый OCR сервис ТОЛЬКО с Tesseract
    - Убраны все остальные методы OCR (LLM Vision, OCR.space, Azure Vision)
    - Оптимизирован для максимальной скорости
    - Мгновенное извлечение текста из фото
    """
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract_availability()
        
        # Оптимизированные конфигурации для быстрого OCR
        self.tesseract_config = '--oem 3 --psm 6 -l ukr+rus+deu+eng'
        self.tesseract_fast_config = '--oem 3 --psm 8 -l ukr+rus+deu+eng'  # Быстрый режим
        
        logger.info(f"Simple Tesseract OCR Service initialized")
        logger.info(f"Tesseract available: {self.tesseract_available}")
    
    def _check_tesseract_availability(self) -> bool:
        """Проверка доступности Tesseract OCR"""
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            
            # Проверяем доступные языки
            languages = pytesseract.get_languages()
            logger.info(f"Available languages: {languages}")
            
            return True
        except Exception as e:
            logger.error(f"Tesseract check failed: {e}")
            return False
    
    def _safe_tesseract_call(self, image, config):
        """Безопасный вызов tesseract с обработкой ошибок"""
        try:
            if not self.tesseract_available:
                logger.error("Tesseract not available")
                return ""
                
            result = pytesseract.image_to_string(image, config=config)
            return result.strip() if result else ""
        except Exception as e:
            logger.error(f"Tesseract call failed: {e}")
            return ""
    
    def _enhance_image_fast(self, image: Image.Image) -> Image.Image:
        """Быстрое улучшение изображения для OCR"""
        try:
            # Конвертируем в numpy array
            img_array = np.array(image)
            
            # Если изображение цветное, конвертируем в серый
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Простое улучшение для скорости
            # 1. Увеличиваем размер для лучшего OCR
            height, width = img_array.shape
            if width < 1000:
                scale_factor = 1000 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 2. Простая пороговая обработка
            _, img_array = cv2.threshold(img_array, 127, 255, cv2.THRESH_BINARY)
            
            # Конвертируем обратно в PIL Image
            enhanced_image = Image.fromarray(img_array)
            
            return enhanced_image
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image
    
    async def extract_text_with_tesseract(self, image_path: str) -> str:
        """
        Быстрое извлечение текста с помощью Tesseract OCR
        """
        try:
            if not self.tesseract_available:
                logger.error("Tesseract OCR is not available")
                return ""
            
            # Открываем изображение
            image = Image.open(image_path)
            
            # Быстрое улучшение изображения
            enhanced_image = self._enhance_image_fast(image)
            
            # Попробуем быструю конфигурацию сначала
            text = self._safe_tesseract_call(enhanced_image, self.tesseract_fast_config)
            
            # Если не получили достаточно текста, попробуем стандартную конфигурацию
            if not text or len(text.strip()) < 10:
                text = self._safe_tesseract_call(enhanced_image, self.tesseract_config)
            
            if text:
                logger.info(f"Tesseract OCR extracted {len(text)} characters")
                return text
            else:
                logger.warning("No text extracted with Tesseract")
                return ""
                
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return ""
    
    async def extract_text_from_image(self, file_path: str) -> str:
        """
        СУПЕР-БЫСТРОЕ извлечение текста из изображения - без сложной обработки
        """
        try:
            logger.info(f"Starting fast image OCR for: {file_path}")
            
            if not self.tesseract_available:
                logger.error("Tesseract OCR is not available")
                return "Tesseract OCR недоступен"
            
            # Открываем изображение
            image = Image.open(file_path)
            
            # Минимальная оптимизация изображения
            if image.mode != 'L':
                image = image.convert('L')  # Только в серый, без других улучшений
            
            # Только один быстрый вызов tesseract
            try:
                # Используем самую простую и быструю конфигурацию
                text = pytesseract.image_to_string(image, config='--oem 3 --psm 6')
                
                if text and len(text.strip()) > 5:
                    logger.info(f"✅ Fast image OCR successful: {len(text)} characters")
                    return text.strip()
                else:
                    logger.info("Fast OCR returned minimal text")
                    return "Текст не найден в изображении"
                    
            except Exception as e:
                logger.error(f"Fast tesseract call failed: {e}")
                return "Ошибка при обработке изображения"
                
        except Exception as e:
            logger.error(f"Fast image OCR failed: {e}")
            return "Ошибка при обработке изображения"
    
    def extract_text_from_pdf_direct(self, pdf_path: str) -> str:
        """Прямое извлечение текста из PDF"""
        try:
            extracted_text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        extracted_text += text + "\n"
            
            if extracted_text.strip():
                logger.info(f"Direct PDF extraction: {len(extracted_text)} characters")
                return extracted_text.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Direct PDF extraction failed: {e}")
            return ""
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        БЫСТРОЕ извлечение текста из PDF - только прямое извлечение, без OCR
        """
        try:
            logger.info(f"Starting fast PDF processing for: {pdf_path}")
            
            # Пробуем прямое извлечение текста из PDF
            direct_text = self.extract_text_from_pdf_direct(pdf_path)
            if direct_text and len(direct_text.strip()) > 20:
                logger.info("✅ Direct PDF text extraction successful")
                return direct_text
            
            logger.info("❌ PDF contains no extractable text (probably images)")
            return "PDF файл содержит изображения. Для анализа изображений в PDF используйте другой формат."
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            return "Ошибка при обработке PDF файла"
    
    async def process_document(self, file_path: str, file_type: str) -> Tuple[str, str]:
        """
        Быстрый метод обработки документов ТОЛЬКО с Tesseract
        """
        try:
            logger.info(f"Processing document: {file_path}, type: {file_type}")
            
            extracted_text = ""
            processing_method = "unknown"
            
            # Определяем тип файла и выбираем метод обработки
            if file_type.lower() == 'pdf' or file_path.lower().endswith('.pdf'):
                extracted_text = await self.extract_text_from_pdf(file_path)
                processing_method = "simple_tesseract_pdf"
                
            elif file_type.startswith('image/') or any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']):
                extracted_text = await self.extract_text_from_image(file_path)
                processing_method = "simple_tesseract_image"
                
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
                        processing_method = "text_file_cp1252"
                    except Exception as e:
                        logger.error(f"Text file reading failed: {e}")
                        extracted_text = "Не удалось распознать тип файла или извлечь текст"
                        processing_method = "error"
            
            # Проверяем качество извлеченного текста
            if extracted_text and len(extracted_text.strip()) > 10:
                logger.info(f"✅ Document processing successful: {processing_method}, {len(extracted_text)} characters")
            else:
                logger.warning(f"⚠️ Document processing returned minimal text: {processing_method}")
            
            return extracted_text, processing_method
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return "Ошибка при обработке документа", "error"
    
    def get_service_status(self) -> dict:
        """Получение статуса сервиса"""
        return {
            "service_name": "Simple Tesseract OCR Service",
            "methods": {
                "tesseract_ocr": {
                    "available": self.tesseract_available,
                    "description": "Tesseract OCR (единственный метод) - быстрый и эффективный"
                },
                "direct_pdf": {
                    "available": True,
                    "description": "Прямое извлечение текста из PDF"
                }
            },
            "primary_method": "tesseract_ocr",
            "tesseract_dependency": True,
            "tesseract_version": "5.3.0" if self.tesseract_available else "not_installed",
            "production_ready": True,
            "optimized_for_speed": True
        }

# Глобальный экземпляр упрощенного OCR сервиса
simple_tesseract_ocr = SimpleTesseractOCR()