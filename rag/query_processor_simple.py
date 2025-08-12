import networkx as nx
import numpy as np
from difflib import get_close_matches


class SimpleQueryProcessor:
    """Simplified query processor that doesn't use sentence transformers."""

    def __init__(self, graph):
        self.graph = graph

        # Create dictionaries of nodes by label
        self.disease_nodes = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get('label') == "Disease"
        ]
        self.symptom_nodes = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get('label') == "Symptom"
        ]

    def process_query(self, query):
        """Process a user query and retrieve relevant subgraph using simple text matching."""
        query_terms = query.lower().split()

        matched_entities = set()

        # Check for disease mentions with fuzzy matching
        for disease in self.disease_nodes:
            disease_lower = disease.lower()

            # Direct matching
            if any(term in disease_lower for term in query_terms):
                matched_entities.add(disease)
                continue

            # Fuzzy matching
            for term in query_terms:
                if term in [
                        'symptoms', 'symptom', 'disease', 'condition', 'is',
                        'what', 'are', 'of', 'the', 'for'
                ]:
                    continue  # Skip common words

                # Check if the term is close to the disease name
                if len(term
                       ) > 3:  # Only match terms with more than 3 characters
                    similarity = self._calculate_string_similarity(
                        term, disease_lower)
                    if similarity > 0.7:  # Threshold for similarity
                        matched_entities.add(disease)
                        break

        # Check for symptom mentions
        for symptom in self.symptom_nodes:
            symptom_lower = symptom.lower()
            if any(term in symptom_lower for term in query_terms):
                matched_entities.add(symptom)

        # If no direct matches, try fuzzy matching with all diseases
        if not matched_entities:
            for disease in self.disease_nodes:
                disease_lower = disease.lower()
                for term in query_terms:
                    if len(term) > 3:
                        similarity = self._calculate_string_similarity(
                            term, disease_lower)
                        if similarity > 0.6:  # Lower threshold for broader matching
                            matched_entities.add(disease)
                            break

        # Extract a subgraph centered around these entities
        if not matched_entities:
            return self.graph.subgraph([])

        # Create a subgraph with 1-hop neighborhood of each entity
        subgraph_nodes = set()
        for entity in matched_entities:
            # Add the entity itself
            subgraph_nodes.add(entity)
            # Add immediate neighbors
            subgraph_nodes.update(self.graph.neighbors(entity))

        subgraph = self.graph.subgraph(subgraph_nodes)
        return subgraph

    def _calculate_string_similarity(self, s1, s2):
        """Calculate string similarity using difflib."""
        # Simple wrapper for string similarity
        if s1 in s2 or s2 in s1:
            return 0.9  # High similarity for substrings

        # For very short strings, we need a different approach
        if len(s1) < 4 or len(s2) < 4:
            return 1.0 if s1 == s2 else 0.0

        matches = get_close_matches(s1, [s2], n=1, cutoff=0.0)
        if matches:
            # Return a score between 0 and 1
            return self._string_similarity_score(s1, matches[0])
        return 0.0

    def _string_similarity_score(self, s1, s2):
        """Calculate a similarity score between two strings."""
        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
        # Normalize by the length of the longer string
        return matches / max(len(s1), len(s2))
