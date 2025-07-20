#!/usr/bin/env python3
"""
Тест для проверки OCR функциональности в production
"""
import sys
import os

def test_tesseract():
    """Проверка tesseract OCR"""
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract установлен:", result.stdout.split('\n')[0])
            return True
        else:
            print("❌ Tesseract не найден")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке tesseract: {e}")
        return False

def test_python_ocr():
    """Проверка Python OCR зависимостей"""
    try:
        import pytesseract
        import cv2
        import PIL
        from document_processor import document_processor
        
        print("✅ Все Python OCR зависимости найдены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствует Python зависимость: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при проверке Python OCR: {e}")
        return False

def test_languages():
    """Проверка языковых пакетов"""
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--list-langs'], capture_output=True, text=True)
        if result.returncode == 0:
            langs = result.stdout.strip().split('\n')[1:]
            required = ['rus', 'deu', 'eng', 'ukr']
            missing = [lang for lang in required if lang not in langs]
            
            if not missing:
                print("✅ Все языковые пакеты найдены:", ', '.join(required))
                return True
            else:
                print("❌ Отсутствуют языковые пакеты:", ', '.join(missing))
                return False
        else:
            print("❌ Не удалось получить список языков")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке языков: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тестирование OCR функциональности...")
    
    tests = [
        ("Tesseract OCR", test_tesseract),
        ("Python OCR зависимости", test_python_ocr),
        ("Языковые пакеты", test_languages),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 Тест: {name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ Тест '{name}' провален")
    
    print(f"\n📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! OCR готов к работе.")
        sys.exit(0)
    else:
        print("💥 Есть проблемы с OCR функциональностью!")
        sys.exit(1)