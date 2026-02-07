#!/bin/bash

# Setup script for Document Q&A AI Agent
# This script sets up the environment and dependencies

echo "======================================================================"
echo "Document Q&A AI Agent - Setup Script"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.8+
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

echo "✓ Python version check passed"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "✓ Virtual environment created"
else
    echo "✗ Failed to create virtual environment"
    exit 1
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -eq 0 ]; then
    echo "✓ Virtual environment activated"
else
    echo "✗ Failed to activate virtual environment"
    exit 1
fi
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

if [ $? -eq 0 ]; then
    echo "✓ pip upgraded"
else
    echo "✗ Failed to upgrade pip"
    exit 1
fi
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/pdfs
mkdir -p data/processed
mkdir -p logs

echo "✓ Directories created"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your API keys:"
    echo "   - For OpenAI: Add your OPENAI_API_KEY"
    echo "   - For Google Gemini: Add your GOOGLE_API_KEY"
    echo ""
else
    echo "✓ .env file already exists"
    echo ""
fi

# Run tests (optional)
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Edit the .env file and add your API keys"
echo "2. Add PDF files to the data/pdfs/ directory"
echo "3. Run the application with: python main.py"
echo ""
echo "Optional:"
echo "- Run tests: python -m pytest tests/ -v"
echo "- See examples: python examples/example_usage.py"
echo ""
echo "Documentation:"
echo "- README.md - Getting started guide"
echo "- ARCHITECTURE.md - System architecture"
echo ""
echo "======================================================================"

