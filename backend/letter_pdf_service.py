"""
Сервис для генерации PDF документов из писем
"""
import logging
import io
import os
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfutils
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

logger = logging.getLogger(__name__)

class LetterPDFService:
    def __init__(self):
        self.setup_fonts()
    
    def setup_fonts(self):
        """Настройка шрифтов для поддержки Unicode"""
        try:
            # Пытаемся зарегистрировать стандартные шрифты для Unicode
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
            from reportlab.pdfbase import pdfmetrics
            
            # Регистрируем Unicode шрифт
            pdfmetrics.registerFont(UnicodeCIDFont('DejaVuSans'))
            logger.info("Unicode шрифты успешно зарегистрированы")
        except Exception as e:
            logger.warning(f"Не удалось настроить Unicode шрифты: {e}. Используется стандартный набор.")
    
    def generate_letter_pdf(
        self, 
        letter_data: Dict[str, Any], 
        sender_info: Dict[str, str],
        recipient_info: Dict[str, str],
        include_translation: bool = False
    ) -> bytes:
        """Генерация PDF документа с письмом"""
        
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Создаем стили
            styles = self._create_styles()
            story = []
            
            # Добавляем заголовок документа
            story.append(Paragraph("Offizielles Schreiben", styles['Title']))
            story.append(Spacer(1, 0.5*cm))
            
            # Добавляем информацию об отправителе
            if sender_info:
                story.extend(self._create_sender_section(sender_info, styles))
            
            # Добавляем информацию о получателе
            if recipient_info:
                story.extend(self._create_recipient_section(recipient_info, styles))
            
            # Добавляем дату
            story.append(Spacer(1, 0.3*cm))
            current_date = datetime.now().strftime("%d.%m.%Y")
            story.append(Paragraph(f"Datum: {current_date}", styles['Normal']))
            story.append(Spacer(1, 0.5*cm))
            
            # Добавляем тему письма
            if letter_data.get('subject'):
                story.append(Paragraph(f"<b>Betreff: {letter_data['subject']}</b>", styles['Subject']))
                story.append(Spacer(1, 0.3*cm))
            
            # Добавляем содержимое письма
            story.extend(self._create_letter_content(letter_data, styles))
            
            # Добавляем перевод если необходимо
            if include_translation and letter_data.get('translation'):
                story.append(Spacer(1, 1*cm))
                story.append(Paragraph("─" * 50, styles['Normal']))
                story.append(Spacer(1, 0.5*cm))
                
                translation_lang = letter_data.get('translation_language', 'Перевод')
                story.append(Paragraph(f"<b>{translation_lang}:</b>", styles['Heading2']))
                story.append(Spacer(1, 0.3*cm))
                
                # Содержимое перевода
                translation_paragraphs = letter_data['translation'].split('\n')
                for para in translation_paragraphs:
                    if para.strip():
                        story.append(Paragraph(para.strip(), styles['Normal']))
                        story.append(Spacer(1, 0.2*cm))
            
            # Добавляем информацию о генерации
            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("─" * 50, styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
            
            generation_info = f"Erstellt mit German Letter AI - {current_date}"
            story.append(Paragraph(generation_info, styles['Footer']))
            
            # Строим PDF
            doc.build(story)
            buffer.seek(0)
            
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Ошибка генерации PDF: {e}")
            return self._generate_fallback_pdf(letter_data, sender_info)
    
    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Создание стилей для PDF"""
        
        styles = getSampleStyleSheet()
        
        # Основной стиль
        styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))
        
        # Стиль заголовка
        styles.add(ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            spaceAfter=12
        ))
        
        # Стиль темы письма
        styles.add(ParagraphStyle(
            name='Subject',
            parent=styles['Normal'],
            fontSize=12,
            leading=15,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            spaceAfter=8
        ))
        
        # Стиль для адресов
        styles.add(ParagraphStyle(
            name='Address',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_LEFT,
            spaceAfter=4
        ))
        
        # Стиль подвала
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.grey
        ))
        
        return styles
    
    def _create_sender_section(self, sender_info: Dict[str, str], styles) -> list:
        """Создание секции отправителя"""
        
        section = []
        section.append(Paragraph("<b>Absender:</b>", styles['Heading3']))
        
        # Формируем адрес отправителя
        sender_lines = []
        if sender_info.get('name'):
            sender_lines.append(sender_info['name'])
        if sender_info.get('address'):
            sender_lines.append(sender_info['address'])
        if sender_info.get('city'):
            city_line = sender_info['city']
            if sender_info.get('postal_code'):
                city_line = f"{sender_info['postal_code']} {city_line}"
            sender_lines.append(city_line)
        if sender_info.get('phone'):
            sender_lines.append(f"Tel: {sender_info['phone']}")
        if sender_info.get('email'):
            sender_lines.append(f"E-Mail: {sender_info['email']}")
        
        for line in sender_lines:
            section.append(Paragraph(line, styles['Address']))
        
        section.append(Spacer(1, 0.5*cm))
        return section
    
    def _create_recipient_section(self, recipient_info: Dict[str, str], styles) -> list:
        """Создание секции получателя"""
        
        section = []
        section.append(Paragraph("<b>Empfänger:</b>", styles['Heading3']))
        
        # Формируем адрес получателя
        recipient_lines = []
        if recipient_info.get('name'):
            recipient_lines.append(recipient_info['name'])
        if recipient_info.get('department'):
            recipient_lines.append(recipient_info['department'])
        if recipient_info.get('address'):
            recipient_lines.append(recipient_info['address'])
        if recipient_info.get('city'):
            city_line = recipient_info['city']
            if recipient_info.get('postal_code'):
                city_line = f"{recipient_info['postal_code']} {city_line}"
            recipient_lines.append(city_line)
        
        for line in recipient_lines:
            section.append(Paragraph(line, styles['Address']))
        
        section.append(Spacer(1, 0.5*cm))
        return section
    
    def _create_letter_content(self, letter_data: Dict[str, Any], styles) -> list:
        """Создание содержимого письма"""
        
        content = []
        letter_text = letter_data.get('content', '')
        
        # Разбиваем письмо на параграфы
        paragraphs = letter_text.split('\n')
        
        for para in paragraphs:
            if para.strip():
                # Обрабатываем специальные форматы
                if para.strip().startswith('Betreff:') or para.strip().startswith('Subject:'):
                    content.append(Paragraph(f"<b>{para.strip()}</b>", styles['Subject']))
                elif para.strip().startswith('Sehr geehrte') or para.strip().startswith('Liebe'):
                    content.append(Paragraph(para.strip(), styles['CustomNormal']))
                elif para.strip().startswith('Mit freundlichen Grüßen') or para.strip().startswith('Hochachtungsvoll'):
                    content.append(Spacer(1, 0.5*cm))
                    content.append(Paragraph(para.strip(), styles['CustomNormal']))
                else:
                    content.append(Paragraph(para.strip(), styles['CustomNormal']))
                
                content.append(Spacer(1, 0.3*cm))
        
        # Добавляем дополнительную информацию если есть
        if letter_data.get('key_points'):
            content.append(Spacer(1, 0.5*cm))
            content.append(Paragraph("<b>Wichtige Punkte:</b>", styles['Heading3']))
            for point in letter_data['key_points']:
                content.append(Paragraph(f"• {point}", styles['CustomNormal']))
        
        return content
    
    def _generate_fallback_pdf(self, letter_data: Dict[str, Any], sender_info: Dict[str, str]) -> bytes:
        """Генерация упрощенного PDF в случае ошибки"""
        
        try:
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Заголовок
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 50, "Offizielles Schreiben")
            
            # Дата
            p.setFont("Helvetica", 12)
            current_date = datetime.now().strftime("%d.%m.%Y")
            p.drawString(50, height - 100, f"Datum: {current_date}")
            
            # Содержимое письма
            y_position = height - 150
            letter_content = letter_data.get('content', 'Inhalt nicht verfügbar')
            
            # Простое разбиение на строки
            lines = letter_content.split('\n')
            for line in lines:
                if y_position < 50:  # Новая страница если нужно
                    p.showPage()
                    y_position = height - 50
                
                p.drawString(50, y_position, line[:80])  # Ограничиваем длину строки
                y_position -= 20
            
            p.save()
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Ошибка генерации fallback PDF: {e}")
            # Возвращаем минимальный PDF с ошибкой
            buffer = io.BytesIO()
            buffer.write(b"PDF generation error")
            return buffer.getvalue()
    
    def validate_letter_for_pdf(self, letter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация данных письма перед генерацией PDF"""
        
        issues = []
        warnings = []
        
        # Проверяем обязательные поля
        if not letter_data.get('content'):
            issues.append("Содержимое письма отсутствует")
        
        if not letter_data.get('subject') and 'Betreff:' not in letter_data.get('content', ''):
            warnings.append("Тема письма не указана")
        
        # Проверяем длину содержимого
        content_length = len(letter_data.get('content', ''))
        if content_length > 10000:
            warnings.append("Письмо очень длинное, возможны проблемы с форматированием")
        elif content_length < 50:
            warnings.append("Письмо очень короткое")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

# Глобальный экземпляр сервиса
letter_pdf_service = LetterPDFService()