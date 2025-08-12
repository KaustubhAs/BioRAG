"""
Performance and stress tests for Biomedical Assistant
"""
import pytest
import time
import networkx as nx
import pandas as pd
from unittest.mock import Mock, patch

from knowledge_graph.data_processor import preprocess_data
from knowledge_graph.graph_builder import build_graph
from rag.biomedical_rag import BiomedicalRAG

@pytest.mark.performance
class TestSystemPerformance:
    """Performance tests for the system."""
    
    def test_knowledge_graph_construction_performance(self, mock_dataset_path):
        """Test knowledge graph construction performance."""
        start_time = time.time()
        
        diseases, symptoms, relationships = preprocess_data(mock_dataset_path)
        graph = build_graph(diseases, symptoms, relationships)
        
        construction_time = time.time() - start_time
        
        # Graph construction should be fast (< 5 seconds for small dataset)
        assert construction_time < 5.0
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
    
    def test_query_processing_performance(self, sample_graph):
        """Test query processing performance."""
        rag_system = BiomedicalRAG(sample_graph)
        
        queries = [
            "What are diabetes symptoms?",
            "What causes fever?",
            "Tell me about hypertension"
        ]
        
        total_time = 0
        for query in queries:
            start_time = time.time()
            response = rag_system.answer_query(query)
            query_time = time.time() - start_time
            
            total_time += query_time
            
            # Each query should be processed quickly
            assert query_time < 10.0
            assert isinstance(response, str)
            assert len(response) > 0
        
        # Average query time should be reasonable
        avg_time = total_time / len(queries)
        assert avg_time < 5.0
    
    def test_graph_traversal_performance(self, sample_graph):
        """Test graph traversal performance."""
        # Test neighborhood extraction performance
        start_time = time.time()
        
        for node in list(sample_graph.nodes())[:10]:  # Test first 10 nodes
            neighbors = list(sample_graph.neighbors(node))
            # Just ensure it doesn't take too long
            assert len(neighbors) >= 0
        
        traversal_time = time.time() - start_time
        
        # Graph traversal should be very fast
        assert traversal_time < 1.0
    
    def test_memory_usage_optimization(self, sample_graph):
        """Test memory usage optimization."""
        # Skip memory test if psutil not available
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform some operations
            rag_system = BiomedicalRAG(sample_graph)
            for _ in range(10):
                rag_system.answer_query("Test query")
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (< 100MB for small operations)
            assert memory_increase < 100
        except ImportError:
            pytest.skip("psutil not available, skipping memory test")

@pytest.mark.stress
class TestStressTests:
    """Stress tests for the system."""
    
    # def test_large_number_of_queries(self, sample_graph):
    #     """Test system with large number of queries."""
    #     rag_system = BiomedicalRAG(sample_graph)
        
    #     # Generate 100 test queries
    #     base_queries = [
    #         "What are diabetes symptoms?",
    #         "What causes fever?",
    #         "Tell me about hypertension",
    #         "What diseases cause headache?",
    #         "Tell me about malaria"
    #     ]
        
    #     queries = []
    #     for i in range(20):  # 20 iterations of 5 queries = 100 total
    #         for query in base_queries:
    #             queries.append(f"{query} (iteration {i})")
        
    #     start_time = time.time()
    #     responses = []
        
    #     for query in queries:
    #         response = rag_system.answer_query(query)
    #         responses.append(response)
        
    #     total_time = time.time() - start_time
        
    #     # All queries should be processed
    #     assert len(responses) == 100
    #     assert all(isinstance(r, str) for r in responses)
    #     assert all(len(r) > 0 for r in responses)
        
    #     # Should handle 100 queries in reasonable time
    #     assert total_time < 60  # 60 seconds max
    
    def test_concurrent_query_processing(self, sample_graph):
        """Test concurrent query processing."""
        import threading
        import queue
        
        rag_system = BiomedicalRAG(sample_graph)
        results_queue = queue.Queue()
        
        def process_query(query):
            """Process a single query."""
            try:
                response = rag_system.answer_query(query)
                results_queue.put(('success', query, response))
            except Exception as e:
                results_queue.put(('error', query, str(e)))
        
        # Start multiple threads
        threads = []
        queries = [
            "What are diabetes symptoms?",
            "What causes fever?",
            "Tell me about hypertension",
            "What diseases cause headache?",
            "Tell me about malaria"
        ]
        
        start_time = time.time()
        
        for query in queries:
            thread = threading.Thread(target=process_query, args=(query,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        # All queries should complete successfully
        assert len(results) == 5
        success_results = [r for r in results if r[0] == 'success']
        assert len(success_results) == 5
        
        # Concurrent processing should be efficient
        assert total_time < 30  # 30 seconds max
    
    def test_large_graph_operations(self):
        """Test operations on larger graphs."""
        # Create a larger test graph
        large_graph = nx.Graph()
        
        # Add 100 diseases and 200 symptoms
        for i in range(100):
            disease = f"Disease_{i}"
            large_graph.add_node(disease, label="Disease")
            
            # Each disease has 2-5 symptoms
            num_symptoms = (i % 4) + 2
            for j in range(num_symptoms):
                symptom = f"Symptom_{i}_{j}"
                large_graph.add_node(symptom, label="Symptom")
                large_graph.add_edge(disease, symptom, type="HAS_SYMPTOM")
        
        # Test RAG system with large graph
        start_time = time.time()
        rag_system = BiomedicalRAG(large_graph)
        init_time = time.time() - start_time
        
        # Initialization should be reasonable
        assert init_time < 5.0
        
        # Test query processing on large graph
        query_start = time.time()
        response = rag_system.answer_query("What are Disease_0 symptoms?")
        query_time = time.time() - query_start
        
        # Query should still be processed in reasonable time
        assert query_time < 10.0
        assert isinstance(response, str)
        assert len(response) > 0

@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for the system."""
    
    def test_query_throughput_benchmark(self, sample_graph):
        """Benchmark query throughput."""
        rag_system = BiomedicalRAG(sample_graph)
        
        # Warm up
        for _ in range(5):
            rag_system.answer_query("Warm up query")
        
        # Benchmark
        start_time = time.time()
        num_queries = 50
        
        for i in range(num_queries):
            query = f"Benchmark query {i}"
            rag_system.answer_query(query)
        
        total_time = time.time() - start_time
        queries_per_second = num_queries / total_time
        
        # Should process at least 10 queries per second
        assert queries_per_second >= 10
        
        print(f"Query throughput: {queries_per_second:.2f} queries/second")
    
    def test_memory_efficiency_benchmark(self, sample_graph):
        """Benchmark memory efficiency."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Measure memory before
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create RAG system
        rag_system = BiomedicalRAG(sample_graph)
        
        # Measure memory after creation
        memory_after_creation = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process some queries
        for _ in range(20):
            rag_system.answer_query("Memory test query")
        
        # Measure memory after queries
        memory_after_queries = process.memory_info().rss / 1024 / 1024  # MB
        
        # Calculate memory metrics
        creation_overhead = memory_after_creation - memory_before
        query_overhead = memory_after_queries - memory_after_creation
        
        # Memory overhead should be reasonable
        assert creation_overhead < 50  # < 50MB for creation
        assert query_overhead < 20   # < 20MB for queries
        
        print(f"Memory overhead - Creation: {creation_overhead:.2f}MB, Queries: {query_overhead:.2f}MB")
    
    def test_response_time_consistency_benchmark(self, sample_graph):
        """Benchmark response time consistency."""
        rag_system = BiomedicalRAG(sample_graph)
        
        response_times = []
        query = "What are diabetes symptoms?"
        
        # Run the same query multiple times
        for _ in range(30):
            start_time = time.time()
            response = rag_system.answer_query(query)
            query_time = time.time() - start_time
            
            response_times.append(query_time)
            assert isinstance(response, str)
            assert len(response) > 0
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        variance = sum((t - avg_time) ** 2 for t in response_times) / len(response_times)
        std_dev = variance ** 0.5
        
        # Response times should be consistent
        assert max_time < 10.0  # Max time < 10 seconds
        assert avg_time < 5.0   # Average time < 5 seconds
        assert std_dev < 2.0    # Reasonable standard deviation
        
        print(f"Response time - Avg: {avg_time:.3f}s, StdDev: {std_dev:.3f}s, Range: {min_time:.3f}s-{max_time:.3f}s")
