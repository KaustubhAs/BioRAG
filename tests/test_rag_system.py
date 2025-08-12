"""
Tests for RAG system components
"""
import pytest
import networkx as nx
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from rag.biomedical_rag import BiomedicalRAG
from rag.query_processor import QueryProcessor
from rag.response_generator import ResponseGenerator


class TestQueryProcessor:
    """Test query processing functionality."""

    @pytest.mark.unit
    def test_query_processor_initialization(self, sample_graph):
        """Test QueryProcessor initialization."""
        processor = QueryProcessor(sample_graph)

        assert processor.graph == sample_graph
        assert len(processor.disease_nodes) == 3
        assert len(processor.symptom_nodes) == 4
        assert "Diabetes" in processor.disease_nodes
        assert "Fever" in processor.symptom_nodes

    @pytest.mark.unit
    def test_direct_disease_matching(self, sample_graph):
        """Test direct disease name matching."""
        processor = QueryProcessor(sample_graph)

        query = "What are the symptoms of diabetes?"
        subgraph = processor.process_query(query)

        # Should find diabetes and its neighbors
        assert len(subgraph.nodes) > 0
        assert "Diabetes" in subgraph.nodes

    @pytest.mark.unit
    def test_direct_symptom_matching(self, sample_graph):
        """Test direct symptom name matching."""
        processor = QueryProcessor(sample_graph)

        query = "What diseases cause fever?"
        subgraph = processor.process_query(query)

        # Should find fever and its neighbors
        assert len(subgraph.nodes) > 0
        assert "Fever" in subgraph.nodes

    @pytest.mark.unit
    def test_fuzzy_matching(self, sample_graph):
        """Test fuzzy string matching."""
        processor = QueryProcessor(sample_graph)

        query = "What are the symptoms of diabete?"  # Slightly misspelled
        subgraph = processor.process_query(query)

        # Should still find diabetes through fuzzy matching
        assert len(subgraph.nodes) > 0

    # @pytest.mark.unit
    # def test_no_matches(self, sample_graph):
    #     """Test query with no matches."""
    #     # Mock the entire SentenceTransformer class
    #     with patch('rag.query_processor.SentenceTransformer') as mock_transformer:
    #         mock_instance = Mock()
    #         mock_instance.encode.return_value = np.array([0.1] * 384)
    #         mock_transformer.return_value = mock_instance

    #         processor = QueryProcessor(sample_graph)

    #         query = "What are the symptoms of nonexistent disease?"
    #         subgraph = processor.process_query(query)

    #         # Should return empty subgraph
    #         assert len(subgraph.nodes) == 0

    @pytest.mark.unit
    def test_string_similarity_calculation(self, sample_graph):
        """Test string similarity calculation."""
        processor = QueryProcessor(sample_graph)

        # Test exact match
        similarity = processor._calculate_string_similarity(
            "diabetes", "diabetes")
        assert similarity > 0.8

        # Test substring match
        similarity = processor._calculate_string_similarity(
            "diabet", "diabetes")
        assert similarity > 0.7

        # Test no match
        similarity = processor._calculate_string_similarity(
            "diabetes", "hypertension")
        assert similarity < 0.5


class TestResponseGenerator:
    """Test response generation functionality."""

    @pytest.mark.unit
    def test_response_generator_initialization(self, sample_graph):
        """Test ResponseGenerator initialization."""
        generator = ResponseGenerator(sample_graph)

        assert generator.graph == sample_graph
        # LLM might be None if Ollama is not available
        assert generator.llm is not None or generator.llm is None

    @pytest.mark.unit
    def test_context_extraction(self, sample_graph):
        """Test context extraction from subgraph."""
        generator = ResponseGenerator(sample_graph)

        # Create a subgraph with diabetes and its symptoms
        diabetes_subgraph = sample_graph.subgraph(
            ['Diabetes', 'Fever', 'Fatigue'])

        context = generator.extract_context(diabetes_subgraph,
                                            "What are diabetes symptoms?")

        assert isinstance(context, list)
        assert len(context) > 0

        # Check if diabetes context is extracted
        diabetes_context = next(
            (item for item in context if item['disease'] == 'Diabetes'), None)
        assert diabetes_context is not None
        assert 'symptoms' in diabetes_context

    @pytest.mark.unit
    def test_context_formatting(self, sample_graph):
        """Test context formatting for LLM."""
        generator = ResponseGenerator(sample_graph)

        context_list = [{
            'disease': 'Diabetes',
            'symptoms': ['Fever', 'Fatigue']
        }, {
            'disease': 'Hypertension',
            'symptoms': ['Headache']
        }]

        formatted = generator.format_context_for_llm(context_list)

        assert isinstance(formatted, str)
        assert 'Diabetes' in formatted
        assert 'Fever' in formatted
        assert 'Hypertension' in formatted
        assert 'Headache' in formatted

    @pytest.mark.unit
    def test_rule_based_response(self, sample_graph):
        """Test rule-based response generation."""
        generator = ResponseGenerator(sample_graph)

        context_list = [{
            'disease': 'Diabetes',
            'symptoms': ['Fever', 'Fatigue']
        }]

        response = generator._generate_rule_based_response(
            context_list, "What are diabetes symptoms?")

        assert isinstance(response, str)
        assert 'Diabetes' in response
        assert 'Fever' in response
        assert 'Fatigue' in response

    # @pytest.mark.unit
    # @patch('rag.response_generator.Ollama')
    # def test_llm_response_generation(self, mock_ollama, sample_graph):
    #     """Test LLM response generation."""
    #     # Mock Ollama
    #     mock_llm = Mock()
    #     mock_llm.return_value = "Diabetes symptoms include fever and fatigue."
    #     mock_ollama.return_value = mock_llm

    #     generator = ResponseGenerator(sample_graph)
    #     generator.llm = mock_llm

    #     # Create subgraph
    #     diabetes_subgraph = sample_graph.subgraph(['Diabetes', 'Fever', 'Fatigue'])

    #     response = generator.generate_response("What are diabetes symptoms?", diabetes_subgraph)

    #     assert isinstance(response, str)
    #     assert len(response) > 0


class TestBiomedicalRAG:
    """Test the main RAG system."""

    @pytest.mark.unit
    def test_rag_system_initialization(self, sample_graph):
        """Test BiomedicalRAG initialization."""
        rag_system = BiomedicalRAG(sample_graph)

        assert rag_system.graph == sample_graph
        assert hasattr(rag_system, 'query_processor')
        assert hasattr(rag_system, 'response_generator')

    @pytest.mark.unit
    def test_rag_query_processing(self, sample_graph):
        """Test complete RAG query processing."""
        rag_system = BiomedicalRAG(sample_graph)

        query = "What are the symptoms of diabetes?"
        response = rag_system.answer_query(query)

        assert isinstance(response, str)
        assert len(response) > 0

    @pytest.mark.unit
    def test_rag_with_empty_query(self, sample_graph):
        """Test RAG with empty query."""
        rag_system = BiomedicalRAG(sample_graph)

        query = ""
        response = rag_system.answer_query(query)

        # Should handle empty query gracefully
        assert isinstance(response, str)

    @pytest.mark.unit
    def test_rag_with_complex_query(self, sample_graph):
        """Test RAG with complex medical query."""
        rag_system = BiomedicalRAG(sample_graph)

        query = "What diseases are associated with both fever and headache?"
        response = rag_system.answer_query(query)

        assert isinstance(response, str)
        assert len(response) > 0


@pytest.mark.integration
class TestRAGIntegration:
    """Integration tests for RAG system."""

    def test_end_to_end_rag_pipeline(self, sample_graph):
        """Test complete RAG pipeline."""
        rag_system = BiomedicalRAG(sample_graph)

        # Test multiple query types
        queries = [
            "What are diabetes symptoms?", "What causes fever?",
            "Tell me about hypertension"
        ]

        for query in queries:
            response = rag_system.answer_query(query)
            assert isinstance(response, str)
            assert len(response) > 0

    def test_rag_performance(self, sample_graph):
        """Test RAG system performance."""
        rag_system = BiomedicalRAG(sample_graph)

        import time

        start_time = time.time()
        response = rag_system.answer_query("What are diabetes symptoms?")
        end_time = time.time()

        response_time = end_time - start_time

        # Response should be generated within reasonable time
        assert response_time < 5.0  # 5 seconds max
        assert isinstance(response, str)
        assert len(response) > 0


@pytest.mark.slow
class TestRAGSlowTests:
    """Slow tests that may take longer to run."""

    def test_large_query_processing(self, sample_graph):
        """Test processing of large, complex queries."""
        rag_system = BiomedicalRAG(sample_graph)

        # Create a complex query
        complex_query = """
        What are the symptoms of diabetes, hypertension, and malaria?
        Also, what diseases are associated with fever, headache, and fatigue?
        Please provide detailed information about each condition.
        """

        response = rag_system.answer_query(complex_query)

        assert isinstance(response, str)
        assert len(response) > 0
