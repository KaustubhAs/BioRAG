try:
    from rag.query_processor import QueryProcessor
    QUERY_PROCESSOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Advanced query processor not available: {e}")
    print("Using simple text-based query processor instead.")
    from rag.query_processor_simple import SimpleQueryProcessor as QueryProcessor
    QUERY_PROCESSOR_AVAILABLE = False

from rag.response_generator import ResponseGenerator

class BiomedicalRAG:
    def __init__(self, graph):
        self.graph = graph
        self.query_processor = QueryProcessor(graph)
        self.response_generator = ResponseGenerator(graph)
        
    def answer_query(self, query):
        """Process a query and generate a response."""
        # Retrieve relevant subgraph
        subgraph = self.query_processor.process_query(query)
        
        # Generate response using LLM
        response = self.response_generator.generate_response(query, subgraph)
        
        return response


# from rag.query_processor import QueryProcessor
# from rag.response_generator import ResponseGenerator

# class BiomedicalRAG:
#     def __init__(self, graph):
#         self.graph = graph
#         self.query_processor = QueryProcessor(graph)
#         self.response_generator = ResponseGenerator(graph)
        
#     def answer_query(self, query, use_llm=False):
#         """Process a query and generate a response."""
#         # Retrieve relevant subgraph
#         subgraph = self.query_processor.process_query(query)
        
#         # Generate response
#         response = self.response_generator.generate_response(
#             query, subgraph, use_llm=use_llm
#         )
        
#         return response
