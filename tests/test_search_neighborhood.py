#!/usr/bin/env python3
"""
Test script to verify search neighborhood functionality
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_graph.data_processor import preprocess_data
from knowledge_graph.graph_builder import build_graph


def test_search_neighborhood():
    """Test the search neighborhood functionality."""
    print("Testing search neighborhood functionality...")

    # Load data
    DATA_PATH = "data/dataset.csv"
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        return False

    diseases, symptoms, relationships = preprocess_data(DATA_PATH)
    graph = build_graph(diseases, symptoms, relationships)

    print(f"Total nodes: {len(graph.nodes)}")
    print(f"Total edges: {len(graph.edges)}")

    # Test search for a disease
    search_term = "diabetes"
    print(f"\nSearching for: '{search_term}'")

    # Find matching diseases
    disease_nodes = [
        n for n, attr in graph.nodes(data=True)
        if attr.get('label') == "Disease"
    ]
    symptom_nodes = [
        n for n, attr in graph.nodes(data=True)
        if attr.get('label') == "Symptom"
    ]

    search_lower = search_term.lower()
    matched_diseases = [n for n in disease_nodes if search_lower in n.lower()]
    matched_symptoms = [n for n in symptom_nodes if search_lower in n.lower()]

    print(f"Matched diseases: {matched_diseases}")
    print(f"Matched symptoms: {matched_symptoms}")

    # Get neighborhood
    neighborhood_nodes = set()
    for node in matched_diseases + matched_symptoms:
        neighborhood_nodes.add(node)
        for neighbor in graph.neighbors(node):
            neighborhood_nodes.add(neighbor)

    print(f"Neighborhood size: {len(neighborhood_nodes)}")

    # Show what's in the neighborhood
    neighborhood_diseases = [
        n for n in disease_nodes if n in neighborhood_nodes
    ]
    neighborhood_symptoms = [
        n for n in symptom_nodes if n in neighborhood_nodes
    ]

    print(f"Neighborhood diseases: {neighborhood_diseases}")
    print(f"Neighborhood symptoms: {neighborhood_symptoms}")

    return True


if __name__ == "__main__":
    test_search_neighborhood()
