#!/bin/bash

echo "🔧 Installing Tesseract OCR..."

# Определяем операционную систему
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📱 Detected macOS"
    
    # Проверяем, установлен ли Homebrew
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "🍺 Installing Tesseract via Homebrew..."
    brew install tesseract
    
    # Проверяем установку
    if command -v tesseract &> /dev/null; then
        echo "✅ Tesseract installed successfully!"
        echo "📍 Location: $(which tesseract)"
        echo "📋 Version: $(tesseract --version | head -n 1)"
    else
        echo "❌ Tesseract installation failed"
        exit 1
    fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Detected Linux"
    
    # Определяем дистрибутив
    if command -v apt-get &> /dev/null; then
        echo "📦 Using apt-get (Ubuntu/Debian)"
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
    elif command -v yum &> /dev/null; then
        echo "📦 Using yum (CentOS/RHEL)"
        sudo yum install -y tesseract
    elif command -v dnf &> /dev/null; then
        echo "📦 Using dnf (Fedora)"
        sudo dnf install -y tesseract
    else
        echo "❌ Unsupported Linux distribution"
        exit 1
    fi
    
    # Проверяем установку
    if command -v tesseract &> /dev/null; then
        echo "✅ Tesseract installed successfully!"
        echo "📍 Location: $(which tesseract)"
        echo "📋 Version: $(tesseract --version | head -n 1)"
    else
        echo "❌ Tesseract installation failed"
        exit 1
    fi

else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "📖 Please install Tesseract manually:"
    echo "   - macOS: brew install tesseract"
    echo "   - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    exit 1
fi

echo ""
echo "🎉 Tesseract installation completed!"
echo "🚀 You can now run: python test_working_ocr.py" 