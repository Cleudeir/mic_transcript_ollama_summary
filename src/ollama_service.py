"""Legacy shim for OllamaService to new services package.

This module re-exports OllamaService from src.services.ollama_service to keep
backward compatibility with existing imports during the refactor.
"""

from src.services.ollama_service import OllamaService

__all__ = ["OllamaService"]
