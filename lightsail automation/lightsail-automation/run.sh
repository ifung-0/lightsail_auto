#!/bin/bash

echo "=========================================="
echo "LightSail Automation Bot"
echo "=========================================="
echo ""
echo "Choose version:"
echo "1. FREE Version (Recommended)"
echo "2. OpenAI Version (Requires API key)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "Starting FREE version..."
    python3 lightsail_bot_free_ai.py
elif [ "$choice" = "2" ]; then
    echo ""
    echo "Starting OpenAI version..."
    python3 lightsail_bot.py
else
    echo "Invalid choice. Please run again."
    exit 1
fi

read -p "Press Enter to exit..."
