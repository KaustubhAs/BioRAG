#!/usr/bin/env python3
"""
Simple script to test imports and identify issues
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing imports...")

try:
    print("1. Testing basic imports...")
    import pytest
    print("   ✅ pytest imported")
    
    import pandas as pd
    print("   ✅ pandas imported")
    
    import networkx as nx
    print("   ✅ networkx imported")
    
    print("\n2. Testing knowledge_graph imports...")
    from knowledge_graph.schema import GraphSchema
    print("   ✅ GraphSchema imported")
    
    from knowledge_graph.data_processor import preprocess_data
    print("   ✅ preprocess_data imported")
    
    from knowledge_graph.graph_builder import build_graph
    print("   ✅ build_graph imported")
    
    print("\n3. Testing RAG imports...")
    from rag.biomedical_rag import BiomedicalRAG
    print("   ✅ BiomedicalRAG imported")
    
    from rag.query_processor import QueryProcessor
    print("   ✅ QueryProcessor imported")
    
    from rag.response_generator import ResponseGenerator
    print("   ✅ ResponseGenerator imported")
    
    print("\n4. Testing test fixtures...")
    from tests.conftest import sample_data, sample_graph
    print("   ✅ test fixtures imported")
    
    print("\n🎉 All imports successful!")
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
