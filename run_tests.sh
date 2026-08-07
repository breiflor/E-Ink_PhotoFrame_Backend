#!/bin/bash
set -e

# Run each test file in isolation to avoid mocking bleed-over
echo "Running Configurator tests..."
PYTHONPATH=. python3 -m pytest tests/test_Configurator.py

echo "Running Eink_Panel_Instance tests..."
PYTHONPATH=. python3 -m pytest tests/test_Eink_Panel_Instance.py

echo "Running ImageHandler tests..."
PYTHONPATH=. python3 -m pytest tests/test_ImageHandler.py

echo "Running ImageProcessingPipline tests..."
PYTHONPATH=. python3 -m pytest tests/test_ImageProcessingPipline.py

echo "Running PanelManager tests..."
PYTHONPATH=. python3 -m pytest tests/test_PanelManager.py

echo "Running Uploader tests..."
PYTHONPATH=. python3 -m pytest tests/test_Uploader.py

echo "All tests passed successfully!"
