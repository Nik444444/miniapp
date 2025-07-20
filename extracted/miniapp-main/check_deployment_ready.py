#!/usr/bin/env python3
"""
🔍 Проверка готовности к деплою German Letter AI
Автор: AI Assistant
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Цвета для вывода
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

def print_colored(text, color):
    print(f"{color}{text}{Colors.NC}")

def check_file_exists(file_path, description):
    """Проверка существования файла"""
    if os.path.exists(file_path):
        print_colored(f"✅ {description}: {file_path}", Colors.GREEN)
        return True
    else:
        print_colored(f"❌ {description}: {file_path} НЕ НАЙДЕН", Colors.RED)
        return False

def check_docker_file(file_path):
    """Проверка содержимого Dockerfile"""
    if not os.path.exists(file_path):
        print_colored(f"❌ Dockerfile не найден: {file_path}", Colors.RED)
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Проверяем ключевые компоненты
    checks = [
        ("tesseract-ocr", "Tesseract OCR"),
        ("python:3.11", "Python 3.11 базовый образ"),
        ("requirements.txt", "Установка зависимостей"),
        ("uvicorn", "Uvicorn сервер"),
        ("EXPOSE 8001", "Порт 8001")
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print_colored(f"  ✅ {description}", Colors.GREEN)
        else:
            print_colored(f"  ❌ {description} отсутствует", Colors.RED)
            all_good = False
    
    return all_good

def check_requirements(file_path):
    """Проверка requirements.txt"""
    if not os.path.exists(file_path):
        print_colored(f"❌ requirements.txt не найден: {file_path}", Colors.RED)
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    required_packages = [
        "fastapi", "uvicorn", "python-dotenv", "pydantic", 
        "pytesseract", "opencv-python", "Pillow", "httpx",
        "google-generativeai", "openai", "anthropic"
    ]
    
    all_good = True
    for package in required_packages:
        if package.lower() in content.lower():
            print_colored(f"  ✅ {package}", Colors.GREEN)
        else:
            print_colored(f"  ❌ {package} отсутствует", Colors.RED)
            all_good = False
    
    return all_good

def check_env_file(file_path):
    """Проверка .env файла"""
    if not os.path.exists(file_path):
        print_colored(f"❌ .env файл не найден: {file_path}", Colors.RED)
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    required_vars = [
        "GOOGLE_CLIENT_ID", "JWT_SECRET_KEY", "SQLITE_DB_PATH",
        "TESSERACT_AVAILABLE", "TESSERACT_VERSION"
    ]
    
    all_good = True
    for var in required_vars:
        if var in content:
            print_colored(f"  ✅ {var}", Colors.GREEN)
        else:
            print_colored(f"  ❌ {var} отсутствует", Colors.RED)
            all_good = False
    
    return all_good

def check_package_json(file_path):
    """Проверка package.json"""
    if not os.path.exists(file_path):
        print_colored(f"❌ package.json не найден: {file_path}", Colors.RED)
        return False
    
    try:
        with open(file_path, 'r') as f:
            package_data = json.load(f)
        
        # Проверяем зависимости
        dependencies = package_data.get('dependencies', {})
        required_deps = ['react', 'react-dom', 'axios', 'react-router-dom']
        
        all_good = True
        for dep in required_deps:
            if dep in dependencies:
                print_colored(f"  ✅ {dep}: {dependencies[dep]}", Colors.GREEN)
            else:
                print_colored(f"  ❌ {dep} отсутствует", Colors.RED)
                all_good = False
        
        # Проверяем скрипты
        scripts = package_data.get('scripts', {})
        if 'build' in scripts:
            print_colored(f"  ✅ build script: {scripts['build']}", Colors.GREEN)
        else:
            print_colored(f"  ❌ build script отсутствует", Colors.RED)
            all_good = False
            
        return all_good
        
    except json.JSONDecodeError:
        print_colored(f"❌ Неверный формат JSON в {file_path}", Colors.RED)
        return False

def main():
    print_colored("🔍 Проверка готовности к деплою German Letter AI", Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    
    # Определяем корневую директорию
    root_dir = Path(__file__).parent
    
    # Счетчики
    total_checks = 0
    passed_checks = 0
    
    # 1. Проверка конфигурационных файлов
    print_colored("\n📋 1. Конфигурационные файлы для деплоя:", Colors.BLUE)
    
    config_files = [
        ("fly.toml", "Конфигурация Fly.io"),
        ("netlify.toml", "Конфигурация Netlify"),
        ("Dockerfile", "Dockerfile для backend"),
        (".dockerignore", "Docker ignore файл"),
        ("auto_deploy.sh", "Скрипт автоматического деплоя")
    ]
    
    for file_name, description in config_files:
        total_checks += 1
        if check_file_exists(root_dir / file_name, description):
            passed_checks += 1
    
    # 2. Проверка Backend файлов
    print_colored("\n🔧 2. Backend файлы:", Colors.BLUE)
    
    backend_dir = root_dir / "backend"
    
    total_checks += 1
    if check_file_exists(backend_dir / "server.py", "Основной сервер"):
        passed_checks += 1
    
    total_checks += 1
    if check_file_exists(backend_dir / "requirements.txt", "Зависимости Python"):
        passed_checks += 1
        print_colored("  📦 Проверка зависимостей:", Colors.YELLOW)
        if check_requirements(backend_dir / "requirements.txt"):
            passed_checks += 1
        total_checks += 1
    
    total_checks += 1
    if check_file_exists(backend_dir / ".env", "Переменные окружения"):
        passed_checks += 1
        print_colored("  🔐 Проверка переменных окружения:", Colors.YELLOW)
        if check_env_file(backend_dir / ".env"):
            passed_checks += 1
        total_checks += 1
    
    # 3. Проверка Frontend файлов
    print_colored("\n🎨 3. Frontend файлы:", Colors.BLUE)
    
    frontend_dir = root_dir / "frontend"
    
    total_checks += 1
    if check_file_exists(frontend_dir / "package.json", "Конфигурация Node.js"):
        passed_checks += 1
        print_colored("  📦 Проверка зависимостей:", Colors.YELLOW)
        if check_package_json(frontend_dir / "package.json"):
            passed_checks += 1
        total_checks += 1
    
    total_checks += 1
    if check_file_exists(frontend_dir / ".env", "Переменные окружения"):
        passed_checks += 1
    
    total_checks += 1
    if check_file_exists(frontend_dir / "public" / "_redirects", "Netlify redirects"):
        passed_checks += 1
    
    # 4. Проверка Docker конфигурации
    print_colored("\n🐳 4. Docker конфигурация:", Colors.BLUE)
    
    total_checks += 1
    if check_file_exists(root_dir / "Dockerfile", "Dockerfile для backend"):
        passed_checks += 1
        print_colored("  🔍 Проверка содержимого Dockerfile:", Colors.YELLOW)
        if check_docker_file(root_dir / "Dockerfile"):
            passed_checks += 1
        total_checks += 1
    
    # 5. Проверка документации
    print_colored("\n📚 5. Документация:", Colors.BLUE)
    
    doc_files = [
        ("DEPLOY_GUIDE_FLY_NETLIFY.md", "Подробное руководство по деплою"),
        ("DEPLOY_GUIDE_BEGINNER.md", "Руководство для новичков"),
        ("fly_secrets.env", "Пример переменных для Fly.io"),
        ("netlify_env.txt", "Пример переменных для Netlify")
    ]
    
    for file_name, description in doc_files:
        total_checks += 1
        if check_file_exists(root_dir / file_name, description):
            passed_checks += 1
    
    # Финальный отчет
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("📊 РЕЗУЛЬТАТ ПРОВЕРКИ:", Colors.WHITE)
    
    success_rate = (passed_checks / total_checks) * 100
    
    if success_rate >= 90:
        print_colored(f"🎉 ОТЛИЧНО! Готовность: {passed_checks}/{total_checks} ({success_rate:.1f}%)", Colors.GREEN)
        print_colored("✅ Проект готов к деплою!", Colors.GREEN)
    elif success_rate >= 70:
        print_colored(f"⚠️  ХОРОШО! Готовность: {passed_checks}/{total_checks} ({success_rate:.1f}%)", Colors.YELLOW)
        print_colored("🔧 Исправьте несколько проблем перед деплоем", Colors.YELLOW)
    else:
        print_colored(f"❌ ВНИМАНИЕ! Готовность: {passed_checks}/{total_checks} ({success_rate:.1f}%)", Colors.RED)
        print_colored("🚨 Необходимо исправить критические проблемы", Colors.RED)
    
    print_colored("\n🚀 Для деплоя выполните:", Colors.CYAN)
    print_colored("1. Прочитайте DEPLOY_GUIDE_FLY_NETLIFY.md", Colors.WHITE)
    print_colored("2. Или запустите: ./auto_deploy.sh", Colors.WHITE)
    print_colored("3. Или следуйте DEPLOY_GUIDE_BEGINNER.md", Colors.WHITE)
    
    return success_rate >= 90

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)