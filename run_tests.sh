#!/bin/bash
set -e

# Run each test file in isolation to avoid mocking bleed-over
echo "Running Configurator tests..."
PYTHONPATH=. pytest tests/test_Configurator.py

echo "Running Eink_Panel_Instance tests..."
PYTHONPATH=. pytest tests/test_Eink_Panel_Instance.py

echo "Running ImageHandler tests..."
PYTHONPATH=. pytest tests/test_ImageHandler.py

echo "Running ImageProcessingPipline tests..."
PYTHONPATH=. pytest tests/test_ImageProcessingPipline.py

echo "Running PanelManager tests..."
PYTHONPATH=. pytest tests/test_PanelManager.py

echo "Running Uploader tests..."
PYTHONPATH=. pytest tests/test_Uploader.py

echo "All tests passed successfully!"
