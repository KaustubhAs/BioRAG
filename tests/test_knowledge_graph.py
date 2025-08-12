"""
Tests for knowledge graph components
"""
import pytest
import pandas as pd
import networkx as nx
from unittest.mock import patch, Mock

from knowledge_graph.data_processor import preprocess_data
from knowledge_graph.graph_builder import build_graph
from knowledge_graph.schema import GraphSchema


class TestDataProcessor:
    """Test data processing functionality."""

    @pytest.mark.unit
    def test_preprocess_data_success(self, mock_dataset_path):
        """Test successful data preprocessing."""
        diseases, symptoms, relationships = preprocess_data(mock_dataset_path)

        assert len(diseases) == 3
        assert len(
            symptoms
        ) == 7  # 7 unique symptoms (duplicates removed by np.unique)
        assert len(relationships
                   ) == 9  # 9 relationships (3 diseases × 3 symptoms each)

        assert "Diabetes" in diseases
        assert "Fever" in symptoms
        # Check that relationships contain the expected data
        diabetes_fever_rel = next(
            (r for r in relationships
             if r['source'] == 'Diabetes' and r['target'] == 'Fever'), None)
        assert diabetes_fever_rel is not None
        assert diabetes_fever_rel['type'] == 'HAS_SYMPTOM'

    @pytest.mark.unit
    def test_preprocess_data_missing_file(self):
        """Test preprocessing with missing dataset file."""
        with pytest.raises(FileNotFoundError):
            preprocess_data("nonexistent_file.csv")

    @pytest.mark.unit
    def test_preprocess_data_invalid_format(self, tmp_path):
        """Test preprocessing with invalid CSV format."""
        invalid_file = tmp_path / "invalid.csv"
        invalid_file.write_text("Invalid,Data,Format")

        with pytest.raises(KeyError):
            preprocess_data(str(invalid_file))


class TestGraphBuilder:
    """Test graph building functionality."""

    @pytest.mark.unit
    def test_build_graph_success(self, sample_data):
        """Test successful graph construction."""
        graph = build_graph(sample_data['diseases'], sample_data['symptoms'],
                            sample_data['relationships'])

        assert isinstance(graph, nx.Graph)
        assert len(graph.nodes) == 7  # 3 diseases + 4 symptoms
        assert len(graph.edges) == 6

        # Check node attributes
        for disease in sample_data['diseases']:
            assert graph.nodes[disease]['label'] == GraphSchema.DISEASE

        for symptom in sample_data['symptoms']:
            assert graph.nodes[symptom]['label'] == GraphSchema.SYMPTOM

        # Check edge attributes
        for rel in sample_data['relationships']:
            assert graph.has_edge(rel['source'], rel['target'])
            assert graph.edges[
                rel['source'],
                rel['target']]['type'] == GraphSchema.HAS_SYMPTOM

    @pytest.mark.unit
    def test_build_graph_empty_data(self):
        """Test graph construction with empty data."""
        graph = build_graph([], [], [])

        assert isinstance(graph, nx.Graph)
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    @pytest.mark.unit
    def test_build_graph_duplicate_relationships(self, sample_data):
        """Test graph construction with duplicate relationships."""
        # Add duplicate relationship
        relationships_with_duplicates = sample_data['relationships'] + [
            {
                'source': 'Diabetes',
                'target': 'Fever',
                'type': 'HAS_SYMPTOM'
            }  # Duplicate
        ]

        graph = build_graph(sample_data['diseases'], sample_data['symptoms'],
                            relationships_with_duplicates)

        # Should handle duplicates gracefully
        assert len(graph.edges) == 6  # No duplicate edges


class TestGraphOperations:
    """Test graph operations and queries."""

    @pytest.mark.unit
    def test_node_label_filtering(self, sample_graph):
        """Test filtering nodes by label."""
        disease_nodes = [
            n for n, attr in sample_graph.nodes(data=True)
            if attr.get('label') == GraphSchema.DISEASE
        ]
        symptom_nodes = [
            n for n, attr in sample_graph.nodes(data=True)
            if attr.get('label') == GraphSchema.SYMPTOM
        ]

        assert len(disease_nodes) == 3
        assert len(symptom_nodes) == 4
        assert 'Diabetes' in disease_nodes
        assert 'Fever' in symptom_nodes

    @pytest.mark.unit
    def test_neighborhood_extraction(self, sample_graph):
        """Test extracting neighborhood of nodes."""
        # Get 1-hop neighborhood of Diabetes
        diabetes_neighbors = list(sample_graph.neighbors('Diabetes'))

        assert len(diabetes_neighbors) == 2
        assert 'Fever' in diabetes_neighbors
        assert 'Fatigue' in diabetes_neighbors

    @pytest.mark.unit
    def test_subgraph_creation(self, sample_graph):
        """Test creating subgraphs from selected nodes."""
        selected_nodes = ['Diabetes', 'Fever', 'Fatigue']
        subgraph = sample_graph.subgraph(selected_nodes)

        assert len(subgraph.nodes) == 3
        assert len(subgraph.edges) == 2
        assert subgraph.has_edge('Diabetes', 'Fever')
        assert subgraph.has_edge('Diabetes', 'Fatigue')


class TestGraphSchema:
    """Test graph schema constants."""

    @pytest.mark.unit
    def test_schema_constants(self):
        """Test that schema constants are properly defined."""
        assert GraphSchema.DISEASE == "Disease"
        assert GraphSchema.SYMPTOM == "Symptom"
        assert GraphSchema.HAS_SYMPTOM == "HAS_SYMPTOM"
        assert GraphSchema.SYMPTOM_OF == "SYMPTOM_OF"


@pytest.mark.integration
class TestKnowledgeGraphIntegration:
    """Integration tests for knowledge graph components."""

    def test_end_to_end_pipeline(self, mock_dataset_path):
        """Test complete pipeline from data to graph."""
        # Process data
        diseases, symptoms, relationships = preprocess_data(mock_dataset_path)

        # Build graph
        graph = build_graph(diseases, symptoms, relationships)

        # Verify graph properties
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

        # Test basic operations
        disease_nodes = [
            n for n, attr in graph.nodes(data=True)
            if attr.get('label') == GraphSchema.DISEASE
        ]
        assert len(disease_nodes) > 0

        # Test neighborhood extraction
        if disease_nodes:
            first_disease = disease_nodes[0]
            neighbors = list(graph.neighbors(first_disease))
            assert len(neighbors) > 0
