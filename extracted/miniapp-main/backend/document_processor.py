import os
import logging
import tempfile
import shutil
from typing import Optional, Tuple, Union
import PyPDF2
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import io
import base64

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Класс для обработки различных типов документов"""
    
    def __init__(self):
        # Проверяем доступность tesseract
        self.tesseract_available = self._check_tesseract()
        
        # Настройка pytesseract для украинского, русского, немецкого и английского языков
        # Использование лучших параметров OCR для различных типов документов
        self.tesseract_config = '--oem 3 --psm 6 -l ukr+rus+deu+eng'
        self.tesseract_config_document = '--oem 3 --psm 4 -l ukr+rus+deu+eng'  # Для документов
        self.tesseract_config_single_block = '--oem 3 --psm 6 -l ukr+rus+deu+eng'  # Для одного блока текста
        
    def _check_tesseract(self):
        """Проверка доступности tesseract с fallback режимом"""
        try:
            # Проверяем переменную окружения
            tesseract_available = os.environ.get('TESSERACT_AVAILABLE', 'true').lower()
            if tesseract_available == 'false':
                logger.warning("TESSERACT_AVAILABLE=false - OCR functionality disabled")
                return False
            
            # Логируем системную информацию
            logger.info("=== TESSERACT DIAGNOSTIC START ===")
            
            # Проверяем PATH
            import subprocess
            which_result = subprocess.run(['which', 'tesseract'], capture_output=True, text=True)
            if which_result.returncode == 0:
                logger.info(f"Tesseract found at: {which_result.stdout.strip()}")
            else:
                logger.error(f"Tesseract not found in PATH: {which_result.stderr}")
                logger.warning("Running in fallback mode without tesseract")
                return False
            
            # Проверяем версию через subprocess
            version_result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
            if version_result.returncode == 0:
                logger.info(f"Tesseract version (subprocess): {version_result.stdout.strip()}")
            else:
                logger.error(f"Failed to get tesseract version: {version_result.stderr}")
                logger.warning("Running in fallback mode without tesseract")
                return False
            
            # Проверяем языки через subprocess
            langs_result = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True)
            if langs_result.returncode == 0:
                logger.info(f"Available languages (subprocess): {langs_result.stdout.strip()}")
            else:
                logger.error(f"Failed to get tesseract languages: {langs_result.stderr}")
                logger.warning("Running in fallback mode without tesseract")
                return False
            
            # Проверяем pytesseract
            try:
                version = pytesseract.get_tesseract_version()
                logger.info(f"Tesseract version (pytesseract): {version}")
                
                # Проверяем доступные языки
                languages = pytesseract.get_languages()
                logger.info(f"Available languages (pytesseract): {languages}")
                
                # Проверяем наличие необходимых языков
                required_langs = ['rus', 'deu', 'eng', 'ukr']
                missing_langs = [lang for lang in required_langs if lang not in languages]
                
                if missing_langs:
                    logger.warning(f"Missing language packs: {missing_langs}")
                    # Используем только доступные языки
                    available_langs = [lang for lang in required_langs if lang in languages]
                    if available_langs:
                        self.tesseract_config = f'--oem 3 --psm 6 -l {"+".join(available_langs)}'
                        self.tesseract_config_document = f'--oem 3 --psm 4 -l {"+".join(available_langs)}'
                        self.tesseract_config_single_block = f'--oem 3 --psm 6 -l {"+".join(available_langs)}'
                        logger.info(f"Using available languages: {available_langs}")
                    else:
                        # Fallback to English only
                        self.tesseract_config = '--oem 3 --psm 6 -l eng'
                        self.tesseract_config_document = '--oem 3 --psm 4 -l eng'
                        self.tesseract_config_single_block = '--oem 3 --psm 6 -l eng'
                        logger.warning("Fallback to English only OCR")
                else:
                    logger.info("All required language packs are available")
                    
                logger.info("=== TESSERACT DIAGNOSTIC SUCCESS ===")
                return True
                
            except Exception as pytesseract_error:
                logger.error(f"Pytesseract error: {pytesseract_error}")
                return False
                
        except Exception as e:
            logger.error(f"Tesseract check failed: {e}")
            logger.warning("Tesseract OCR is not available - OCR functionality will be limited")
            logger.info("=== TESSERACT DIAGNOSTIC FAILED ===")
            return False
    
    def _safe_tesseract_call(self, image, config):
        """Безопасный вызов tesseract с обработкой ошибок"""
        try:
            if not self.tesseract_available:
                logger.warning("Tesseract not available for OCR call")
                return ""
                
            result = pytesseract.image_to_string(image, config=config)
            return result.strip() if result else ""
        except Exception as e:
            logger.warning(f"Tesseract call failed with config '{config}': {e}")
            return ""
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Извлечение текста из PDF файла"""
        try:
            extracted_text = ""
            
            # Сначала пробуем извлечь текст напрямую
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
            
            # Если текст не извлечен, конвертируем PDF в изображения и используем OCR
            logger.info("Direct text extraction failed, trying OCR...")
            return self._extract_text_from_pdf_with_ocr(pdf_path)
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # Пробуем OCR как fallback
            return self._extract_text_from_pdf_with_ocr(pdf_path)
    
    def _extract_text_from_pdf_with_ocr(self, pdf_path: str) -> str:
        """Извлечение текста из PDF с помощью OCR"""
        try:
            # Конвертируем PDF в изображения
            images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=5)  # Ограничиваем 5 страницами
            
            extracted_text = ""
            for i, image in enumerate(images):
                # Улучшаем качество изображения для OCR
                enhanced_image = self._enhance_image_for_ocr(image)
                
                # Извлекаем текст с помощью OCR (пробуем разные конфигурации)
                text_results = []
                
                # Конфигурация для документов
                try:
                    text1 = self._safe_tesseract_call(enhanced_image, self.tesseract_config_document)
                    if text1:
                        text_results.append(text1)
                except Exception as e:
                    logger.warning(f"OCR document config failed for page {i+1}: {e}")
                
                # Стандартная конфигурация
                try:
                    text2 = self._safe_tesseract_call(enhanced_image, self.tesseract_config)
                    if text2:
                        text_results.append(text2)
                except Exception as e:
                    logger.warning(f"OCR standard config failed for page {i+1}: {e}")
                
                # Выбираем наиболее длинный результат
                if text_results:
                    best_text = max(text_results, key=len)
                    extracted_text += f"--- Страница {i+1} ---\n{best_text}\n\n"
            
            logger.info(f"Extracted text from PDF with OCR: {len(extracted_text)} characters")
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF with OCR: {e}")
            return "Ошибка при извлечении текста из PDF файла"
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Улучшенное извлечение текста из изображения с помощью OCR"""
        try:
            # Проверяем доступность tesseract
            if not self.tesseract_available:
                logger.warning("Tesseract OCR is not available - cannot extract text from image")
                return "OCR не доступен - не удалось извлечь текст из изображения"
            
            # Открываем изображение
            image = Image.open(image_path)
            
            # Улучшаем качество изображения для OCR
            enhanced_image = self._enhance_image_for_ocr(image)
            
            # Пробуем разные конфигурации OCR
            text_results = []
            
            # Конфигурация для документов
            try:
                text1 = self._safe_tesseract_call(enhanced_image, self.tesseract_config_document)
                if text1:
                    text_results.append(text1)
            except Exception as e:
                logger.warning(f"OCR document config failed: {e}")
            
            # Конфигурация для одного блока
            try:
                text2 = self._safe_tesseract_call(enhanced_image, self.tesseract_config_single_block)
                if text2:
                    text_results.append(text2)
            except Exception as e:
                logger.warning(f"OCR single block config failed: {e}")
            
            # Стандартная конфигурация
            try:
                text3 = self._safe_tesseract_call(enhanced_image, self.tesseract_config)
                if text3:
                    text_results.append(text3)
            except Exception as e:
                logger.warning(f"OCR standard config failed: {e}")
            
            # Выбираем наиболее длинный результат
            if text_results:
                best_text = max(text_results, key=len)
                logger.info(f"Extracted text from image: {len(best_text)} characters")
                return best_text
            else:
                logger.warning("No text extracted from image")
                return "Текст не был извлечен из изображения"
                
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return "Ошибка при извлечении текста из изображения"
    
    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """Продвинутое улучшение изображения для супер-качественного OCR"""
        try:
            # Конвертируем в numpy array
            img_array = np.array(image)
            
            # Если изображение цветное, конвертируем в серый
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Продвинутое улучшение качества
            # 1. Адаптивная гауссова фильтрация для удаления шума
            img_array = cv2.GaussianBlur(img_array, (3, 3), 0)
            
            # 2. Улучшение контраста с помощью CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img_array = clahe.apply(img_array)
            
            # 3. Морфологические операции для очистки текста
            kernel = np.ones((2,2), np.uint8)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            img_array = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, kernel)
            
            # 4. Адаптивная пороговая обработка
            img_array = cv2.adaptiveThreshold(img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 5. Дополнительное увеличение размера для лучшего OCR
            height, width = img_array.shape
            if width < 1500:  # Увеличиваем целевой размер
                scale_factor = 1500 / width
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # 6. Дополнительное повышение резкости
            kernel_sharpen = np.array([[-1,-1,-1], 
                                     [-1, 9,-1], 
                                     [-1,-1,-1]])
            img_array = cv2.filter2D(img_array, -1, kernel_sharpen)
            
            # Конвертируем обратно в PIL Image
            enhanced_image = Image.fromarray(img_array)
            
            return enhanced_image
            
        except Exception as e:
            logger.error(f"Error enhancing image: {e}")
            return image  # Возвращаем оригинальное изображение в случае ошибки
    
    def process_document(self, file_path: str, file_type: str) -> Tuple[str, str]:
        """Обработка документа - извлечение текста и определение типа обработки"""
        try:
            extracted_text = ""
            processing_method = "unknown"
            
            if file_type.lower() == 'pdf' or file_path.lower().endswith('.pdf'):
                extracted_text = self.extract_text_from_pdf(file_path)
                processing_method = "pdf_extraction"
            elif file_type.startswith('image/') or any(file_path.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']):
                extracted_text = self.extract_text_from_image(file_path)
                processing_method = "image_ocr"
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

# Глобальный экземпляр процессора документов
document_processor = DocumentProcessor()