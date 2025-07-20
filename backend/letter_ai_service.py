"""
AI сервис для генерации и улучшения писем
"""
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
import re
from modern_llm_manager import modern_llm_manager

logger = logging.getLogger(__name__)

class LetterAIService:
    def __init__(self):
        self.supported_languages = {
            'de': 'Немецкий',
            'ru': 'Русский', 
            'uk': 'Украинский'
        }

    async def generate_letter_from_request(
        self, 
        user_request: str,
        recipient_type: str,
        user_language: str,
        user_providers: List[tuple]
    ) -> Dict[str, Any]:
        """Генерация письма на основе запроса пользователя"""
        
        try:
            # Создаем промпт для генерации письма
            prompt = self._create_letter_generation_prompt(
                user_request, recipient_type, user_language
            )
            
            # Используем AI для генерации
            response = await self._call_ai_service(prompt, user_providers)
            
            if not response:
                raise Exception("AI сервис не доступен")
            
            # Парсим ответ
            letter_data = self._parse_ai_response(response)
            
            # Добавляем перевод если нужно
            if user_language != 'de':
                translation = await self._translate_letter(
                    letter_data['content'], 'de', user_language, user_providers
                )
                letter_data['translation'] = translation
                letter_data['translation_language'] = self.supported_languages.get(user_language, user_language)
            
            return {
                "status": "success",
                "letter": letter_data,
                "generation_method": "ai_custom"
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации письма: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_available": True
            }

    async def generate_letter_from_template(
        self,
        template_content: str,
        user_data: Dict[str, str],
        user_language: str,
        user_providers: List[tuple]
    ) -> Dict[str, Any]:
        """Генерация письма на основе шаблона"""
        
        try:
            # Заполняем шаблон данными пользователя
            filled_template = self._fill_template(template_content, user_data)
            
            # Улучшаем письмо с помощью AI
            improved_letter = await self._improve_letter_with_ai(
                filled_template, user_language, user_providers
            )
            
            # Проверяем грамматику
            grammar_check = await self._check_german_grammar(
                improved_letter, user_providers
            )
            
            # Добавляем перевод если нужно
            translation = None
            if user_language != 'de':
                translation = await self._translate_letter(
                    improved_letter, 'de', user_language, user_providers
                )
            
            return {
                "status": "success",
                "letter": {
                    "content": improved_letter,
                    "translation": translation,
                    "translation_language": self.supported_languages.get(user_language, user_language),
                    "grammar_check": grammar_check,
                    "generated_from": "template"
                },
                "generation_method": "template_based"
            }
            
        except Exception as e:
            logger.error(f"Ошибка генерации письма из шаблона: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_content": self._fill_template(template_content, user_data)
            }

    async def improve_existing_letter(
        self,
        letter_content: str,
        improvement_type: str,
        user_language: str,
        user_providers: List[tuple]
    ) -> Dict[str, Any]:
        """Улучшение существующего письма"""
        
        try:
            improvement_prompt = self._create_improvement_prompt(
                letter_content, improvement_type, user_language
            )
            
            response = await self._call_ai_service(improvement_prompt, user_providers)
            
            if not response:
                raise Exception("AI сервис не доступен")
            
            # Парсим улучшенное письмо
            improved_data = self._parse_improvement_response(response)
            
            return {
                "status": "success",
                "original": letter_content,
                "improved": improved_data['content'],
                "improvements": improved_data.get('improvements', []),
                "grammar_fixes": improved_data.get('grammar_fixes', [])
            }
            
        except Exception as e:
            logger.error(f"Ошибка улучшения письма: {e}")
            return {
                "status": "error",
                "error": str(e),
                "original": letter_content
            }

    def _create_letter_generation_prompt(
        self, user_request: str, recipient_type: str, user_language: str
    ) -> str:
        """Создание промпта для генерации письма"""
        
        prompt = f"""Du bist ein Experte für deutsche Amtssprache und offizielle Korrespondenz. 
        
Erstelle ein professionelles deutsches Schreiben basierend auf folgender Anfrage:

Anfrage: {user_request}
Empfänger-Typ: {recipient_type}
Benutzersprache: {user_language}

WICHTIGE ANFORDERUNGEN:
1. Das Schreiben muss auf DEUTSCH verfasst sein
2. Verwende die korrekte deutsche Amtssprache und Höflichkeitsformen
3. Strukturiere das Schreiben professionell (Anrede, Hauptteil, Schluss)
4. Verwende angemessene Formulierungen für den jeweiligen Empfänger
5. Achte auf korrekte deutsche Grammatik und Rechtschreibung

STRUKTUR:
- Betreff (falls relevant)
- Anrede
- Hauptteil mit klarer Darstellung des Anliegens
- Höfliche Schlussformel
- Grußformel

Bitte antworte in folgendem JSON-Format:
{{
    "subject": "Betreff des Schreibens",
    "content": "Vollständiges deutsches Schreiben",
    "letter_type": "Art des Schreibens",
    "formality_level": "formell/semi-formell",
    "key_points": ["Wichtige Punkte des Schreibens"],
    "suggestions": ["Zusätzliche Empfehlungen oder Hinweise"]
}}"""

        return prompt

    def _create_improvement_prompt(
        self, letter_content: str, improvement_type: str, user_language: str
    ) -> str:
        """Создание промпта для улучшения письма"""
        
        improvements_map = {
            "grammar": "Grammatik und Rechtschreibung",
            "style": "Stil und Formulierungen",
            "formality": "Förmlichkeit und Höflichkeit",
            "structure": "Struktur und Aufbau",
            "clarity": "Klarheit und Verständlichkeit"
        }
        
        improvement_focus = improvements_map.get(improvement_type, "allgemeine Verbesserung")
        
        prompt = f"""Du bist ein Experte für deutsche Amtssprache und Korrespondenz.

Verbessere das folgende deutsche Schreiben mit Fokus auf: {improvement_focus}

Original-Schreiben:
{letter_content}

VERBESSERUNGSAUFGABEN:
1. Korrigiere alle Grammatik- und Rechtschreibfehler
2. Verbessere den Stil und die Formulierungen
3. Stelle sicher, dass die Höflichkeitsformen korrekt sind
4. Optimiere die Struktur und den Aufbau
5. Erhöhe die Klarheit und Verständlichkeit

Bitte antworte in folgendem JSON-Format:
{{
    "content": "Verbessertes deutsches Schreiben",
    "improvements": ["Liste der vorgenommenen Verbesserungen"],
    "grammar_fixes": ["Grammatik- und Rechtschreibkorrekturen"],
    "style_changes": ["Stilistische Änderungen"],
    "structure_improvements": ["Strukturelle Verbesserungen"]
}}"""

        return prompt

    async def _call_ai_service(self, prompt: str, user_providers: List[tuple]) -> str:
        """Вызов AI сервиса"""
        
        try:
            # Пытаемся использовать пользовательские провайдеры
            for provider_name, model_name, api_key in user_providers:
                try:
                    logger.info(f"Trying user provider {provider_name} with model {model_name}")
                    response = await modern_llm_manager.generate_content(
                        prompt=prompt,
                        provider=provider_name,
                        model=model_name,
                        api_key=api_key,
                        max_tokens=2000,
                        temperature=0.3
                    )
                    if response and "AI сервис недоступен" not in response:
                        logger.info(f"Successfully generated content with user provider {provider_name}")
                        return response
                    else:
                        logger.warning(f"User provider {provider_name} returned error or no response")
                        continue
                except Exception as e:
                    logger.warning(f"Ошибка с пользовательским провайдером {provider_name}: {e}")
                    continue
            
            # Если пользовательские провайдеры не работают, пробуем системные
            logger.info("Falling back to system providers")
            system_response = await modern_llm_manager.generate_content(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            if system_response and "недоступен" not in system_response:
                logger.info("System provider successful")
                return system_response
            
            logger.error("All providers failed")
            return None
            
        except Exception as e:
            logger.error(f"Все AI провайдеры недоступны: {e}")
            return None

    async def _translate_letter(
        self, letter_content: str, from_lang: str, to_lang: str, user_providers: List[tuple]
    ) -> str:
        """Перевод письма"""
        
        lang_names = {'de': 'немецкий', 'ru': 'русский', 'uk': 'украинский'}
        
        translation_prompt = f"""Переведи следующее официальное письмо с {lang_names.get(from_lang, from_lang)} языка на {lang_names.get(to_lang, to_lang)} язык.

Сохраняй официальный стиль и структуру документа.

Оригинальное письмо:
{letter_content}

Переведи только содержимое письма, сохранив его структуру и формальный тон."""

        try:
            translation = await self._call_ai_service(translation_prompt, user_providers)
            return translation if translation else "Перевод недоступен"
        except Exception as e:
            logger.error(f"Ошибка перевода: {e}")
            return "Ошибка перевода"

    async def _check_german_grammar(
        self, letter_content: str, user_providers: List[tuple]
    ) -> Dict[str, Any]:
        """Проверка немецкой грамматики"""
        
        grammar_prompt = f"""Prüfe das folgende deutsche Schreiben auf Grammatik- und Rechtschreibfehler.

Text:
{letter_content}

Bitte antworte in folgendem JSON-Format:
{{
    "errors_found": true/false,
    "error_count": Anzahl der Fehler,
    "errors": [
        {{
            "type": "Grammatik/Rechtschreibung",
            "error": "gefundener Fehler",
            "correction": "Korrektur",
            "position": "Position im Text"
        }}
    ],
    "overall_quality": "sehr gut/gut/befriedigend/verbesserungswürdig",
    "suggestions": ["Allgemeine Verbesserungsvorschläge"]
}}"""

        try:
            response = await self._call_ai_service(grammar_prompt, user_providers)
            if response:
                return self._parse_grammar_response(response)
            return {"errors_found": False, "message": "Grammatikprüfung nicht verfügbar"}
        except Exception as e:
            logger.error(f"Ошибка проверки грамматики: {e}")
            return {"errors_found": False, "error": str(e)}

    async def _improve_letter_with_ai(
        self, letter_content: str, user_language: str, user_providers: List[tuple]
    ) -> str:
        """Улучшение письма с помощью AI"""
        
        improvement_prompt = f"""Verbessere das folgende deutsche Schreiben, um es professioneller und korrekter zu machen:

{letter_content}

VERBESSERUNGSAUFGABEN:
1. Korrigiere alle Fehler
2. Verbessere die Formulierungen
3. Stelle sicher, dass der Stil angemessen förmlich ist
4. Optimiere die Struktur

Gib nur das verbesserte Schreiben zurück, keine zusätzlichen Erklärungen."""

        try:
            improved = await self._call_ai_service(improvement_prompt, user_providers)
            return improved if improved else letter_content
        except Exception as e:
            logger.error(f"Ошибка улучшения письма: {e}")
            return letter_content

    def _fill_template(self, template: str, user_data: Dict[str, str]) -> str:
        """Заполнение шаблона данными пользователя"""
        
        filled_template = template
        for key, value in user_data.items():
            placeholder = f"{{{key}}}"
            if value:
                filled_template = filled_template.replace(placeholder, str(value))
        
        # Убираем оставшиеся пустые плейсхолдеры
        filled_template = re.sub(r'\{[^}]+\}', '[Bitte ausfüllen]', filled_template)
        
        return filled_template

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа от AI"""
        
        try:
            # Пытаемся найти JSON в ответе
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return {
                    "content": json_data.get("content", response),
                    "subject": json_data.get("subject", ""),
                    "letter_type": json_data.get("letter_type", ""),
                    "formality_level": json_data.get("formality_level", ""),
                    "key_points": json_data.get("key_points", []),
                    "suggestions": json_data.get("suggestions", [])
                }
            else:
                # Если JSON не найден, возвращаем весь ответ как содержимое
                return {
                    "content": response,
                    "subject": "",
                    "letter_type": "Стандартное письмо",
                    "formality_level": "formell",
                    "key_points": [],
                    "suggestions": []
                }
        except Exception as e:
            logger.warning(f"Ошибка парсинга AI ответа: {e}")
            return {
                "content": response,
                "subject": "",
                "letter_type": "Стандартное письмо",
                "formality_level": "formell",
                "key_points": [],
                "suggestions": []
            }

    def _parse_improvement_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа улучшения"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group())
                return json_data
            else:
                return {"content": response, "improvements": [], "grammar_fixes": []}
        except Exception as e:
            logger.warning(f"Ошибка парсинга улучшения: {e}")
            return {"content": response, "improvements": [], "grammar_fixes": []}

    def _parse_grammar_response(self, response: str) -> Dict[str, Any]:
        """Парсинг ответа проверки грамматики"""
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"errors_found": False, "message": "Ответ в неверном формате"}
        except Exception as e:
            logger.warning(f"Ошибка парсинга грамматики: {e}")
            return {"errors_found": False, "error": str(e)}

# Глобальный экземпляр сервиса
letter_ai_service = LetterAIService()