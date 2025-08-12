#!/usr/bin/env python3
"""
Test script for Biomedical Assistant
Run this to verify all components work correctly
"""

import os
import sys
import traceback

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import networkx as nx
        print("✅ networkx imported successfully")
    except ImportError as e:
        print(f"❌ networkx import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        import plotly.graph_objects as go
        print("✅ plotly imported successfully")
    except ImportError as e:
        print(f"❌ plotly import failed: {e}")
        return False
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence_transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence_transformers import failed: {e}")
        return False
    
    return True

def test_data_loading():
    """Test if the dataset can be loaded."""
    print("\n📊 Testing data loading...")
    
    data_path = "data/dataset.csv"
    if not os.path.exists(data_path):
        print(f"❌ Dataset not found at {data_path}")
        return False
    
    try:
        import pandas as pd
        df = pd.read_csv(data_path)
        print(f"✅ Dataset loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        
        if 'Disease' not in df.columns:
            print("❌ 'Disease' column not found in dataset")
            return False
        
        print(f"✅ Found {df['Disease'].nunique()} unique diseases")
        return True
        
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return False

def test_knowledge_graph():
    """Test knowledge graph construction."""
    print("\n🕸️ Testing knowledge graph construction...")
    
    try:
        from knowledge_graph.data_processor import preprocess_data
        from knowledge_graph.graph_builder import build_graph
        
        diseases, symptoms, relationships = preprocess_data("data/dataset.csv")
        print(f"✅ Data preprocessing successful: {len(diseases)} diseases, {len(symptoms)} symptoms, {len(relationships)} relationships")
        
        graph = build_graph(diseases, symptoms, relationships)
        print(f"✅ Graph built successfully: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
        return True
        
    except Exception as e:
        print(f"❌ Error building knowledge graph: {e}")
        traceback.print_exc()
        return False

def test_rag_system():
    """Test RAG system."""
    print("\n🤖 Testing RAG system...")
    
    try:
        from knowledge_graph.data_processor import preprocess_data
        from knowledge_graph.graph_builder import build_graph
        from rag.biomedical_rag import BiomedicalRAG
        
        # Build graph
        diseases, symptoms, relationships = preprocess_data("data/dataset.csv")
        graph = build_graph(diseases, symptoms, relationships)
        
        # Initialize RAG
        rag_system = BiomedicalRAG(graph)
        print("✅ RAG system initialized successfully")
        
        # Test query
        test_query = "What are the symptoms of diabetes?"
        response = rag_system.answer_query(test_query)
        print(f"✅ Test query successful: {len(response)} characters response")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")
        traceback.print_exc()
        return False

def test_ui_components():
    """Test UI components."""
    print("\n🖥️ Testing UI components...")
    
    try:
        # Test if streamlit app can be imported
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.streamlit_app import initialize_system
        print("✅ Streamlit app components imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing UI components: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🏥 Biomedical Assistant - System Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Data Loading", test_data_loading),
        ("Knowledge Graph", test_knowledge_graph),
        ("RAG System", test_rag_system),
        ("UI Components", test_ui_components),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nTo start the UI:")
        print("  python run_ui.py")
        print("\nTo start the CLI:")
        print("  python main.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\nMake sure you have:")
        print("  1. Installed all requirements: pip install -r requirements.txt")
        print("  2. Placed the dataset at data/dataset.csv")
        print("  3. All Python modules are accessible")

if __name__ == "__main__":
    main() 