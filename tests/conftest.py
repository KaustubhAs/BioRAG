"""
Pytest configuration and fixtures for Biomedical Assistant tests
"""
import pytest
import os
import sys
import pandas as pd
import networkx as nx
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def sample_data():
    """Create sample biomedical data for testing."""
    return {
        'diseases': ['Diabetes', 'Hypertension', 'Malaria'],
        'symptoms': ['Fever', 'Headache', 'Fatigue', 'Chest Pain'],
        'relationships': [{
            'source': 'Diabetes',
            'target': 'Fever',
            'type': 'HAS_SYMPTOM'
        }, {
            'source': 'Diabetes',
            'target': 'Fatigue',
            'type': 'HAS_SYMPTOM'
        }, {
            'source': 'Hypertension',
            'target': 'Headache',
            'type': 'HAS_SYMPTOM'
        }, {
            'source': 'Hypertension',
            'target': 'Chest Pain',
            'type': 'HAS_SYMPTOM'
        }, {
            'source': 'Malaria',
            'target': 'Fever',
            'type': 'HAS_SYMPTOM'
        }, {
            'source': 'Malaria',
            'target': 'Headache',
            'type': 'HAS_SYMPTOM'
        }]
    }


@pytest.fixture(scope="session")
def sample_graph(sample_data):
    """Create a sample knowledge graph for testing."""
    graph = nx.Graph()

    # Add disease nodes
    for disease in sample_data['diseases']:
        graph.add_node(disease, label="Disease")

    # Add symptom nodes
    for symptom in sample_data['symptoms']:
        graph.add_node(symptom, label="Symptom")

    # Add relationships
    for rel in sample_data['relationships']:
        graph.add_edge(rel['source'], rel['target'], type="HAS_SYMPTOM")

    return graph


@pytest.fixture(scope="session")
def mock_dataset_path(tmp_path_factory):
    """Create a temporary dataset file for testing."""
    tmp_path = tmp_path_factory.mktemp("data")
    dataset_path = tmp_path / "dataset.csv"

    # Create sample CSV data
    data = {
        'Disease': ['Diabetes', 'Hypertension', 'Malaria'],
        'Symptom_1': ['Fever', 'Headache', 'Fever'],
        'Symptom_2': ['Fatigue', 'Chest Pain', 'Headache'],
        'Symptom_3': ['Thirst', 'Dizziness', 'Nausea']
    }

    df = pd.DataFrame(data)
    df.to_csv(dataset_path, index=False)

    return str(dataset_path)


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without actual Ollama."""
    mock = Mock()
    mock.return_value = "This is a mock response for testing purposes."
    return mock


@pytest.fixture
def mock_sentence_transformer():
    """Mock sentence transformer for testing."""
    with patch('sentence_transformers.SentenceTransformer') as mock:
        mock_instance = Mock()
        mock_instance.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        mock.return_value = mock_instance
        yield mock


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Clean up any existing test artifacts
    yield

    # Cleanup after tests
    pass
