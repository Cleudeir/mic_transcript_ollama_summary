#!/usr/bin/env python3
"""
Test script to verify Ollama URL default population and model loading
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ollama_service import OllamaService

def test_ollama_service():
    """Test the OllamaService functionality"""
    print("Testing OllamaService...")
    
    # Create service instance
    service = OllamaService()
    
    print(f"Default base URL: {service.base_url}")
    print(f"Default model: {service.model_name}")
    
    # Test if service is available
    try:
        is_available = service.is_ollama_available()
        print(f"Ollama service available: {is_available}")
        
        if is_available:
            models = service.get_available_models()
            print(f"Available models: {models}")
        else:
            print("Ollama service not available - models can't be loaded")
            
    except Exception as e:
        print(f"Error testing service: {e}")

if __name__ == "__main__":
    test_ollama_service()
