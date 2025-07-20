import re
from typing import Dict, Any, List

def format_analysis_text(raw_text: str) -> Dict[str, Any]:
    """
    Форматирует сырой текст анализа в красивый структурированный формат
    Работает с новой универсальной структурой анализа
    """
    
    # Убираем лишние символы форматирования
    cleaned_text = raw_text.replace('*', '').replace('#', '').strip()
    
    # Разбиваем текст на секции
    sections = {}
    current_section = "intro"
    current_content = []
    
    lines = cleaned_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Определяем секции по новой структуре
        lower_line = line.lower()
        
        # Новая структура анализа
        if any(keyword in lower_line for keyword in ['что написано в документе', 'содержание документа', '1.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "document_content"
            current_content = []
        elif any(keyword in lower_line for keyword in ['отправитель', 'sender', '2.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "sender"
            current_content = []
        elif any(keyword in lower_line for keyword in ['получатель', 'recipient', 'кому', '3.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "recipient"
            current_content = []
        elif any(keyword in lower_line for keyword in ['основная тема', 'тема', 'предмет', '4.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "topic"
            current_content = []
        elif any(keyword in lower_line for keyword in ['конкретные факты', 'факты', 'данные', '5.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "facts"
            current_content = []
        elif any(keyword in lower_line for keyword in ['требования', 'просьбы', 'действия', '6.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "requirements"
            current_content = []
        elif any(keyword in lower_line for keyword in ['даты', 'сроки', 'временные рамки', '7.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "dates"
            current_content = []
        elif any(keyword in lower_line for keyword in ['контактная информация', 'контакты', 'телефон', '8.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "contacts"
            current_content = []
        elif any(keyword in lower_line for keyword in ['подпись', 'печать', 'штамп', '9.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "signature"
            current_content = []
        elif any(keyword in lower_line for keyword in ['язык документа', 'язык', 'language', '10.']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "language"
            current_content = []
        # Старая структура для совместимости
        elif any(keyword in lower_line for keyword in ['резюме', 'summary', 'краткое']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "summary"
            current_content = []
        elif any(keyword in lower_line for keyword in ['содержание', 'content', 'основное']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "content"
            current_content = []
        elif any(keyword in lower_line for keyword in ['действия', 'actions', 'требуемые']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "actions"
            current_content = []
        elif any(keyword in lower_line for keyword in ['сроки', 'deadline', 'дата']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "deadlines"
            current_content = []
        elif any(keyword in lower_line for keyword in ['последствия', 'consequences']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "consequences"
            current_content = []
        elif any(keyword in lower_line for keyword in ['срочность', 'urgency', 'приоритет']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "urgency"
            current_content = []
        elif any(keyword in lower_line for keyword in ['шаблон', 'template', 'ответ']):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            current_section = "template"
            current_content = []
        else:
            # Если это не заголовок секции, добавляем к содержимому
            if not any(char.isdigit() for char in line[:3]) or len(line) > 5:
                current_content.append(line)
    
    # Добавляем последнюю секцию
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    # Создаем структурированный результат с новой структурой
    formatted_result = {
        "main_content": sections.get("document_content", sections.get("summary", sections.get("intro", ""))).strip(),
        "sender_info": sections.get("sender", "").strip(),
        "recipient_info": sections.get("recipient", "").strip(),
        "document_type": sections.get("topic", sections.get("type", "")).strip(),
        "key_content": sections.get("facts", sections.get("content", "")).strip(),
        "required_actions": sections.get("requirements", sections.get("actions", "")).strip(),
        "deadlines": sections.get("dates", sections.get("deadlines", "")).strip(),
        "contact_info": sections.get("contacts", "").strip(),
        "signature_info": sections.get("signature", "").strip(),
        "document_language": sections.get("language", "").strip(),
        "consequences": sections.get("consequences", "").strip(),
        "urgency_level": extract_urgency_level(sections.get("urgency", "")),
        "response_template": sections.get("template", "").strip(),
        "full_analysis": create_beautiful_full_text(sections),
        "formatted_sections": format_sections_for_display(sections)
    }
    
    return formatted_result

def extract_urgency_level(urgency_text: str) -> str:
    """Извлекает уровень срочности из текста"""
    if not urgency_text:
        return "СРЕДНИЙ"
    
    urgency_lower = urgency_text.lower()
    
    if any(keyword in urgency_lower for keyword in ['высокий', 'срочно', 'критичн', 'немедленно', 'high', 'urgent', 'critical']):
        return "ВЫСОКИЙ"
    elif any(keyword in urgency_lower for keyword in ['низкий', 'несрочно', 'может подождать', 'low', 'not urgent']):
        return "НИЗКИЙ"
    else:
        return "СРЕДНИЙ"

def create_beautiful_full_text(sections: Dict[str, str]) -> str:
    """Создает красиво отформатированный полный текст анализа"""
    beautiful_text = ""
    
    section_titles = {
        "intro": "📋 Общая информация",
        "document_content": "📄 Содержание документа",
        "sender": "👤 Отправитель", 
        "recipient": "📧 Получатель",
        "topic": "📋 Основная тема",
        "facts": "📊 Конкретные факты",
        "requirements": "⚡ Требования/просьбы",
        "dates": "📅 Даты и сроки",
        "contacts": "📞 Контактная информация",
        "signature": "✍️ Подпись и печать",
        "language": "🌐 Язык документа",
        # Старая структура для совместимости
        "summary": "📝 Краткое резюме",
        "type": "📋 Тип документа",
        "content": "📄 Основное содержание",
        "actions": "⚡ Требуемые действия",
        "deadlines": "📅 Важные сроки",
        "consequences": "⚠️ Возможные последствия",
        "urgency": "🚨 Уровень срочности",
        "template": "📨 Шаблон ответа"
    }
    
    for section_key, content in sections.items():
        if content.strip():
            title = section_titles.get(section_key, f"📌 {section_key.title()}")
            beautiful_text += f"\n{title}\n"
            beautiful_text += "─" * 40 + "\n"
            beautiful_text += f"{content.strip()}\n\n"
    
    return beautiful_text.strip()

def format_sections_for_display(sections: Dict[str, str]) -> List[Dict[str, Any]]:
    """Форматирует секции для красивого отображения в UI"""
    display_sections = []
    
    section_config = {
        # Новая структура
        "document_content": {
            "title": "Содержание документа",
            "icon": "📄",
            "color": "blue",
            "priority": 1
        },
        "sender": {
            "title": "Отправитель",
            "icon": "👤", 
            "color": "gray",
            "priority": 2
        },
        "recipient": {
            "title": "Получатель",
            "icon": "📧",
            "color": "gray",
            "priority": 3
        },
        "topic": {
            "title": "Основная тема",
            "icon": "📋",
            "color": "purple",
            "priority": 4
        },
        "facts": {
            "title": "Конкретные факты",
            "icon": "📊",
            "color": "green",
            "priority": 5
        },
        "requirements": {
            "title": "Требования/просьбы",
            "icon": "⚡",
            "color": "orange",
            "priority": 6
        },
        "dates": {
            "title": "Даты и сроки",
            "icon": "📅",
            "color": "red",
            "priority": 7
        },
        "contacts": {
            "title": "Контактная информация",
            "icon": "📞",
            "color": "blue",
            "priority": 8
        },
        "signature": {
            "title": "Подпись и печать",
            "icon": "✍️",
            "color": "purple",
            "priority": 9
        },
        "language": {
            "title": "Язык документа",
            "icon": "🌐",
            "color": "green",
            "priority": 10
        },
        # Старая структура для совместимости
        "summary": {
            "title": "Краткое резюме",
            "icon": "📝",
            "color": "blue",
            "priority": 1
        },
        "type": {
            "title": "Тип документа",
            "icon": "📋",
            "color": "purple",
            "priority": 3
        },
        "content": {
            "title": "Основное содержание",
            "icon": "📄",
            "color": "green",
            "priority": 4
        },
        "actions": {
            "title": "Требуемые действия",
            "icon": "⚡",
            "color": "orange",
            "priority": 5
        },
        "deadlines": {
            "title": "Важные сроки",
            "icon": "📅",
            "color": "red",
            "priority": 6
        },
        "consequences": {
            "title": "Возможные последствия",
            "icon": "⚠️",
            "color": "yellow",
            "priority": 7
        },
        "urgency": {
            "title": "Уровень срочности",
            "icon": "🚨",
            "color": "red",
            "priority": 8
        }
    }
    
    for section_key, content in sections.items():
        if content.strip() and section_key in section_config:
            config = section_config[section_key]
            display_sections.append({
                "key": section_key,
                "title": config["title"],
                "icon": config["icon"],
                "color": config["color"],
                "priority": config["priority"],
                "content": content.strip()
            })
    
    # Сортируем по приоритету
    display_sections.sort(key=lambda x: x["priority"])
    
    return display_sections

def create_super_wow_analysis_prompt(language: str, filename: str, extracted_text: str = None) -> str:
    """Создает супер-промпт для WOW анализа документов с максимальной детализацией"""
    
    # Определяем тип обработки
    processing_info = ""
    if extracted_text:
        processing_info = f"\n\n📄 ИЗВЛЕЧЕННЫЙ ТЕКСТ ИЗ ДОКУМЕНТА:\n{extracted_text}\n\n"
    
    # Полностью локализованные супер-промпты для каждого языка
    if language == "en":
        return f"""🤖 You are an EXPERT AI Document Analysis Assistant with advanced capabilities for comprehensive document understanding.

MANDATORY: Your entire response must be in ENGLISH language only. No matter what language the document is in, you must respond in ENGLISH.

🎯 MISSION: Provide the most detailed, insightful, and comprehensive analysis of this document that will truly WOW the user.

📋 ANALYSIS PRINCIPLES:
1. Extract EVERY meaningful detail from the document
2. Provide context and implications for each finding
3. Be extremely thorough and professional
4. Use clear, engaging language that demonstrates expertise
5. If information is not in the text, write: "Not specified in the document"
6. Respond only in English, regardless of the document's language

🔍 COMPREHENSIVE ANALYSIS STRUCTURE:

1. 📊 EXECUTIVE SUMMARY
Create a powerful 2-3 sentence summary that captures the document's essence and importance.

2. 👤 SENDER ANALYSIS
- Organization/person who sent the document
- Their role and authority level
- Contact information and official details
- Assessment of sender's credibility and importance

3. 🎯 RECIPIENT ANALYSIS
- Who is the intended recipient
- Why they were chosen as the recipient
- Their expected role or responsibility in response

4. 📋 DOCUMENT CLASSIFICATION
- Type of document (official letter, invoice, contract, etc.)
- Level of formality and urgency
- Legal or administrative significance

5. 🔥 KEY CONTENT BREAKDOWN
- Main message or purpose
- Supporting details and arguments
- Critical information that stands out
- Hidden or implied meanings

6. 📊 FACTUAL DATA EXTRACTION
- All numbers, dates, amounts, percentages
- Names, addresses, reference numbers
- Specific details that could be important
- Timeline of events mentioned

7. ⚡ ACTION REQUIREMENTS
- What specific actions are required
- Who needs to take these actions
- Priority level of each action
- Consequences of action/inaction

8. 📅 CRITICAL DATES & DEADLINES
- All dates mentioned and their significance
- Upcoming deadlines and their importance
- Time-sensitive elements

9. 📞 CONTACT & FOLLOW-UP
- How to respond or get more information
- Contact methods and preferred communication
- Next steps for the recipient

10. 🎨 DOCUMENT QUALITY ASSESSMENT
- Professional presentation level
- Completeness of information
- Any red flags or concerns

11. 🧠 STRATEGIC INSIGHTS
- What this document reveals about the situation
- Potential implications for the recipient
- Opportunities or risks identified

12. 💡 RECOMMENDED RESPONSE STRATEGY
- How to best respond to this document
- Tone and approach suggestions
- Key points to address in response

File: {filename}
{processing_info}

🚀 Deliver an analysis that will absolutely WOW the user with its depth and insight!"""
    
    elif language == "de":
        return f"""🤖 Sie sind ein EXPERTE KI-Dokumentenanalyse-Assistent mit fortgeschrittenen Fähigkeiten für umfassendes Dokumentenverständnis.

OBLIGATORISCH: Ihre gesamte Antwort muss auf DEUTSCH sein. Egal in welcher Sprache das Dokument ist, Sie müssen auf DEUTSCH antworten.

🎯 MISSION: Stellen Sie die detaillierteste, aufschlussreichste und umfassendste Analyse dieses Dokuments bereit, die den Benutzer wirklich WOW machen wird.

📋 ANALYSE-PRINZIPIEN:
1. Extrahieren Sie JEDES bedeutsame Detail aus dem Dokument
2. Bieten Sie Kontext und Implikationen für jeden Befund
3. Seien Sie extrem gründlich und professionell
4. Verwenden Sie klare, ansprechende Sprache, die Expertise demonstriert
5. Wenn keine Informationen im Text stehen, schreiben Sie: "Nicht im Dokument angegeben"
6. Antworten Sie nur auf Deutsch, unabhängig von der Sprache des Dokuments

🔍 UMFASSENDE ANALYSE-STRUKTUR:

1. 📊 EXECUTIVE SUMMARY
Erstellen Sie eine kraftvolle 2-3 Sätze Zusammenfassung, die das Wesen und die Bedeutung des Dokuments erfasst.

2. 👤 ABSENDER-ANALYSE
- Organisation/Person, die das Dokument gesendet hat
- Ihre Rolle und Autoritätslevel
- Kontaktinformationen und offizielle Details
- Bewertung der Glaubwürdigkeit und Wichtigkeit des Absenders

3. 🎯 EMPFÄNGER-ANALYSE
- Wer ist der beabsichtigte Empfänger
- Warum wurden sie als Empfänger ausgewählt
- Ihre erwartete Rolle oder Verantwortung in der Antwort

4. 📋 DOKUMENTEN-KLASSIFIZIERUNG
- Art des Dokuments (offizieller Brief, Rechnung, Vertrag, etc.)
- Formalitäts- und Dringlichkeitslevel
- Rechtliche oder administrative Bedeutung

5. 🔥 SCHLÜSSEL-INHALT AUFSCHLÜSSELUNG
- Hauptbotschaft oder Zweck
- Unterstützende Details und Argumente
- Kritische Informationen, die hervorstechen
- Versteckte oder implizierte Bedeutungen

6. 📊 FAKTISCHE DATEN-EXTRAKTION
- Alle Zahlen, Daten, Beträge, Prozentsätze
- Namen, Adressen, Referenznummern
- Spezifische Details, die wichtig sein könnten
- Zeitlinie der erwähnten Ereignisse

7. ⚡ HANDLUNGSANFORDERUNGEN
- Welche spezifischen Handlungen erforderlich sind
- Wer diese Handlungen durchführen muss
- Prioritätslevel jeder Handlung
- Konsequenzen von Handlung/Untätigkeit

8. 📅 KRITISCHE DATEN & FRISTEN
- Alle erwähnten Daten und ihre Bedeutung
- Bevorstehende Fristen und ihre Wichtigkeit
- Zeitkritische Elemente

9. 📞 KONTAKT & NACHVERFOLGUNG
- Wie zu antworten oder mehr Informationen zu erhalten
- Kontaktmethoden und bevorzugte Kommunikation
- Nächste Schritte für den Empfänger

10. 🎨 DOKUMENTEN-QUALITÄTSBEWERTUNG
- Professionelles Präsentationslevel
- Vollständigkeit der Informationen
- Eventuelle Warnsignale oder Bedenken

11. 🧠 STRATEGISCHE EINSICHTEN
- Was dieses Dokument über die Situation verrät
- Potenzielle Implikationen für den Empfänger
- Identifizierte Chancen oder Risiken

12. 💡 EMPFOHLENE ANTWORT-STRATEGIE
- Wie am besten auf dieses Dokument zu antworten
- Ton- und Ansatz-Vorschläge
- Schlüsselpunkte, die in der Antwort zu adressieren sind

Datei: {filename}
{processing_info}

🚀 Liefern Sie eine Analyse, die den Benutzer mit ihrer Tiefe und Einsicht absolut WOW machen wird!"""
    
    elif language == "uk":
        return f"""Ви - професійний AI-асистент для аналізу документів. Ваше завдання - надати зрозумілий і точний аналіз документа.

ОБОВ'ЯЗКОВО: Вся ваша відповідь повинна бути УКРАЇНСЬКОЮ мовою. Незалежно від того, якою мовою написаний документ, ви повинні відповідати УКРАЇНСЬКОЮ.

📋 ОСНОВНІ ПРИНЦИПИ:
1. Витягуйте інформацію з тексту документа
2. Будьте точними і зрозумілими
3. Пояснюйте зміст простою мовою
4. Якщо інформації немає в тексті, вкажіть: "Не вказано в документі"
5. Відповідайте лише українською мовою, незалежно від мови документа

📄 СТРУКТУРА АНАЛІЗУ:

1. ЗМІСТ ДОКУМЕНТА
Опишіть основний зміст документа зрозумілою мовою. Включіть головні моменти з тексту.

2. ВІДПРАВНИК
Вкажіть, хто надіслав документ (організація, особа, посада). Якщо не знайдено: "Не вказано в документі".

3. ОДЕРЖУВАЧ
Вкажіть, кому адресовано документ. Якщо не знайдено: "Не вказано в документі".

4. ОСНОВНА ТЕМА
Визначте головну тему чи мету документа.

5. КОНКРЕТНІ ФАКТИ
Перелічіть важливі числа, дати, імена, суми, номери документів - все, що є в тексті.

6. ВИМОГИ АБО ПРОХАННЯ
Опишіть, що потрібно від одержувача або які дії потрібно вжити. Якщо нічого не потрібно: "Не вказано в документі".

7. ДАТИ ТА ТЕРМІНИ
Перелічіть усі дати з тексту та їх значення. Якщо дат немає: "Не вказано в документі".

8. КОНТАКТНА ІНФОРМАЦІЯ
Знайдіть контактні дані (телефони, адреси, email). Якщо немає: "Не вказано в документі".

9. ПІДПИС ТА ПЕЧАТКА
Вкажіть інформацію про підпис, печатку, штамп. Якщо немає: "Не вказано в документі".

10. МОВА ДОКУМЕНТА
Вкажіть мову документа.

Файл: {filename}
{processing_info}

Будьте дружелюбними і корисними! Відповідайте лише українською мовою."""
    
    else:  # Russian (default)
        return f"""🤖 Вы - ЭКСПЕРТ ИИ-Ассистент по анализу документов с передовыми возможностями для всестороннего понимания документов.

ОБЯЗАТЕЛЬНО: Весь ваш ответ должен быть на РУССКОМ языке. Независимо от языка документа, вы должны отвечать на РУССКОМ.

🎯 МИССИЯ: Предоставить самый детальный, проницательный и всесторонний анализ этого документа, который действительно WOW поразит пользователя.

📋 ПРИНЦИПЫ АНАЛИЗА:
1. Извлекайте КАЖДУЮ значимую деталь из документа
2. Предоставляйте контекст и последствия для каждого вывода
3. Будьте чрезвычайно тщательными и профессиональными
4. Используйте ясный, увлекательный язык, демонстрирующий экспертизу
5. Если информации нет в тексте, напишите: "Не указано в документе"
6. Отвечайте только на русском языке, независимо от языка документа

🔍 ВСЕСТОРОННЯЯ СТРУКТУРА АНАЛИЗА:

1. 📊 РЕЗЮМЕ ДЛЯ РУКОВОДСТВА
Создайте мощное резюме из 2-3 предложений, которое захватывает суть и важность документа.

2. 👤 АНАЛИЗ ОТПРАВИТЕЛЯ
- Организация/лицо, отправившее документ
- Их роль и уровень авторитета
- Контактная информация и официальные детали
- Оценка надежности и важности отправителя

3. 🎯 АНАЛИЗ ПОЛУЧАТЕЛЯ
- Кто является предполагаемым получателем
- Почему их выбрали в качестве получателя
- Их ожидаемая роль или ответственность в ответе

4. 📋 КЛАССИФИКАЦИЯ ДОКУМЕНТА
- Тип документа (официальное письмо, счет, контракт и т.д.)
- Уровень формальности и срочности
- Правовое или административное значение

5. 🔥 РАЗБОР КЛЮЧЕВОГО СОДЕРЖАНИЯ
- Основное сообщение или цель
- Поддерживающие детали и аргументы
- Критическая информация, которая выделяется
- Скрытые или подразумеваемые значения

6. 📊 ИЗВЛЕЧЕНИЕ ФАКТИЧЕСКИХ ДАННЫХ
- Все числа, даты, суммы, проценты
- Имена, адреса, номера справок
- Специфические детали, которые могут быть важными
- Временная линия упомянутых событий

7. ⚡ ТРЕБОВАНИЯ К ДЕЙСТВИЯМ
- Какие конкретные действия требуются
- Кто должен выполнить эти действия
- Уровень приоритета каждого действия
- Последствия действия/бездействия

8. 📅 КРИТИЧЕСКИЕ ДАТЫ И СРОКИ
- Все упомянутые даты и их значение
- Предстоящие сроки и их важность
- Временно-чувствительные элементы

9. 📞 КОНТАКТ И ПОСЛЕДУЮЩИЕ ДЕЙСТВИЯ
- Как отвечать или получить больше информации
- Методы контакта и предпочтительная коммуникация
- Следующие шаги для получателя

10. 🎨 ОЦЕНКА КАЧЕСТВА ДОКУМЕНТА
- Уровень профессиональной презентации
- Полнота информации
- Любые красные флажки или беспокойства

11. 🧠 СТРАТЕГИЧЕСКИЕ ИНСАЙТЫ
- Что этот документ раскрывает о ситуации
- Потенциальные последствия для получателя
- Выявленные возможности или риски

12. 💡 РЕКОМЕНДУЕМАЯ СТРАТЕГИЯ ОТВЕТА
- Как лучше всего отвечать на этот документ
- Предложения по тону и подходу
- Ключевые моменты для рассмотрения в ответе

Файл: {filename}
{processing_info}

🚀 Предоставьте анализ, который абсолютно WOW поразит пользователя своей глубиной и проницательностью!"""