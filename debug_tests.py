#!/usr/bin/env python3
"""
Debug script to identify test failures
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import pytest
        print("✅ pytest imported successfully")
    except ImportError as e:
        print(f"❌ pytest import failed: {e}")
        return False
    
    try:
        from knowledge_graph.data_processor import preprocess_data
        print("✅ data_processor imported successfully")
    except ImportError as e:
        print(f"❌ data_processor import failed: {e}")
        return False
    
    try:
        from knowledge_graph.graph_builder import build_graph
        print("✅ graph_builder imported successfully")
    except ImportError as e:
        print(f"❌ graph_builder import failed: {e}")
        return False
    
    try:
        from rag.biomedical_rag import BiomedicalRAG
        print("✅ BiomedicalRAG imported successfully")
    except ImportError as e:
        print(f"❌ BiomedicalRAG import failed: {e}")
        return False
    
    try:
        from rag.query_processor import QueryProcessor
        print("✅ QueryProcessor imported successfully")
    except ImportError as e:
        print(f"❌ QueryProcessor import failed: {e}")
        return False
    
    try:
        from rag.response_generator import ResponseGenerator
        print("✅ ResponseGenerator imported successfully")
    except ImportError as e:
        print(f"❌ ResponseGenerator import failed: {e}")
        return False
    
    return True

def test_fixtures():
    """Test if fixtures can be created."""
    print("\nTesting fixtures...")
    
    try:
        from tests.conftest import sample_data, sample_graph
        print("✅ sample_data fixture created successfully")
        print(f"   - Diseases: {sample_data['diseases']}")
        print(f"   - Symptoms: {sample_data['symptoms']}")
        print(f"   - Relationships: {len(sample_data['relationships'])}")
        
        print("✅ sample_graph fixture created successfully")
        print(f"   - Nodes: {len(sample_graph.nodes)}")
        print(f"   - Edges: {len(sample_graph.edges)}")
        
        return True
    except Exception as e:
        print(f"❌ Fixture creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from tests.conftest import sample_graph
        from rag.biomedical_rag import BiomedicalRAG
        
        rag = BiomedicalRAG(sample_graph)
        print("✅ BiomedicalRAG created successfully")
        
        # Test a simple query
        response = rag.answer_query("What are diabetes symptoms?")
        print(f"✅ Query processed successfully: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Debugging Biomedical Assistant Tests")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_fixtures():
        success = False
    
    if not test_basic_functionality():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    sys.exit(0 if success else 1)
