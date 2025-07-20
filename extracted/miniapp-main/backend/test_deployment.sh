#!/bin/bash

# Простой тест для проверки deployment-ready файлов

echo "=== Test deployment configuration ==="

# Проверяем requirements.txt
echo "Checking requirements.txt..."
if [ -f "requirements.txt" ]; then
    echo "✓ requirements.txt exists"
    
    # Проверяем что emergentintegrations НЕ в requirements.txt
    if grep -q "emergentintegrations" requirements.txt; then
        echo "❌ emergentintegrations found in requirements.txt (should be removed)"
        exit 1
    else
        echo "✓ emergentintegrations not in requirements.txt"
    fi
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Проверяем Dockerfile.backend  
echo "Checking Dockerfile.backend..."
if [ -f "../Dockerfile.backend" ]; then
    echo "✓ Dockerfile.backend exists"
    
    # Проверяем что есть специальная команда для emergentintegrations
    if grep -q "emergentintegrations --extra-index-url" ../Dockerfile.backend; then
        echo "✓ Dockerfile.backend has emergentintegrations installation with extra-index-url"
    else
        echo "❌ Dockerfile.backend missing emergentintegrations installation"
        exit 1
    fi
else
    echo "❌ Dockerfile.backend not found"
    exit 1
fi

# Проверяем start.sh
echo "Checking start.sh..."
if [ -f "start.sh" ]; then
    echo "✓ start.sh exists"
    if [ -x "start.sh" ]; then
        echo "✓ start.sh is executable"
    else
        echo "❌ start.sh is not executable"
        exit 1
    fi
else
    echo "❌ start.sh not found"
    exit 1
fi

# Проверяем что emergentintegrations импортируется корректно
echo "Checking emergentintegrations import..."
if python -c "from emergentintegrations.llm.chat import LlmChat; print('✓ emergentintegrations import successful')" 2>/dev/null; then
    echo "✓ emergentintegrations imports correctly"
else
    echo "❌ emergentintegrations import failed"
    exit 1
fi

# Проверяем что modern_llm_manager работает
echo "Checking modern_llm_manager..."
if python -c "from modern_llm_manager import modern_llm_manager; print('✓ modern_llm_manager import successful')" 2>/dev/null; then
    echo "✓ modern_llm_manager works correctly"
else
    echo "❌ modern_llm_manager import failed"
    exit 1
fi

echo "=== All tests passed! Ready for deployment ==="