"""
RAG (Retrieval-Augmented Generation) package for Biomedical Assistant
"""

from .biomedical_rag import BiomedicalRAG
from .response_generator import ResponseGenerator

try:
    from .query_processor import QueryProcessor
except (ImportError, OSError):
    # PyTorch/sentence_transformers not available or DLL load failed (e.g. on Windows)
    from .query_processor_simple import SimpleQueryProcessor as QueryProcessor

__all__ = ['BiomedicalRAG', 'QueryProcessor', 'ResponseGenerator']
