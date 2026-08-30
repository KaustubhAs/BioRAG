import os
import logging
import networkx as nx
from knowledge_graph.schema import GraphSchema
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# Optional Streamlit integration for secrets management
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)


class ResponseGenerator:

    def __init__(self, graph):
        self.graph = graph
        # Initialize Ollama instead of OpenAI
        try:
            self.llm = Ollama(model="llama3.2")
            print("Successfully initialized Ollama model")
        except Exception as e:
            self.llm = None
            print(f"Warning: LLM not initialized. Error: {e}")
            print("Using rule-based responses instead.")

    def extract_context(self, subgraph, query):
        """Extract context from the subgraph for the LLM."""
        if not subgraph or len(subgraph.nodes()) == 0:
            return "No relevant information found in the knowledge base."

        context = []

        # Extract disease nodes from graph
        disease_nodes = [
            n for n, attr in self.graph.nodes(data=True)
            if attr.get('label') == GraphSchema.DISEASE
        ]

        # Search for relevant diseases
        found_diseases = set()
        for disease in disease_nodes:
            if any(term.lower() in query.lower()
                   for term in disease.lower().split()):
                found_diseases.add(disease)
                symptoms = []
                for _, symptom, edge_data in self.graph.edges(disease,
                                                              data=True):
                    if edge_data.get('type') == GraphSchema.HAS_SYMPTOM:
                        symptoms.append(symptom)

                if symptoms:
                    context.append({"disease": disease, "symptoms": symptoms})

        # If no exact matches, extract from subgraph
        if not context:
            diseases = [
                n for n, attr in subgraph.nodes(data=True)
                if attr.get('label') == GraphSchema.DISEASE
            ]

            for disease in diseases:
                symptoms = []
                for _, symptom, edge_data in subgraph.edges(disease,
                                                            data=True):
                    if edge_data.get('type') == GraphSchema.HAS_SYMPTOM:
                        symptoms.append(symptom)

                if symptoms:
                    context.append({"disease": disease, "symptoms": symptoms})

        return context

    def format_context_for_llm(self, context_list):
        """Format the context list into a string for the LLM."""
        if not context_list or isinstance(context_list, str):
            return context_list

        formatted_context = "Knowledge Base Information:\n\n"
        for item in context_list:
            formatted_context += f"Disease: {item['disease']}\n"
            formatted_context += f"Symptoms: {', '.join(item['symptoms'])}\n\n"

        return formatted_context

    def generate_response(self, query, subgraph):
        """Generate a response based on the query and retrieved subgraph.
        
        Multi-tier response generation:
        Tier 1A: Groq API (llama-3.1-8b-instant) if GROQ_API_KEY available
        Tier 1B: Local Ollama (llama3.2) if available
        Tier 2: Rule-based response generation
        """
        context = self.extract_context(subgraph, query)

        # If context is a string, it's an error message
        if isinstance(context, str):
            return context

        # Format context for LLM
        formatted_context = self.format_context_for_llm(context)

        # Dynamically fetch the Groq API key
        current_groq_key = None
        if STREAMLIT_AVAILABLE:
            try:
                current_groq_key = st.secrets.get("GROQ_API_KEY")
            except Exception:
                pass
        if not current_groq_key:
            current_groq_key = os.getenv("GROQ_API_KEY")

        # ========== TIER 1A: Groq API (Zero-cost cloud deployment) ==========
        if current_groq_key:
            try:
                from groq import Groq

                client = Groq(api_key=current_groq_key)

                prompt = f"""You are a helpful medical assistant providing information about diseases and symptoms.
                Use ONLY the information provided in the knowledge base to answer the query.
                If the information is not in the knowledge base, acknowledge that you don't have that information.
                Format your response in a clear, concise manner.
                
                Query: {query}
                
                {formatted_context}
                
                Answer:"""

                logger.info("Attempting Groq API response (Tier 1A)...")
                message = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.2)
                response = message.choices[0].message.content
                logger.info("Successfully generated response using Groq API")
                return response.strip()

            except ImportError:
                logger.warning(
                    "groq library not installed. Skipping Tier 1A (Groq API).")
            except Exception as e:
                logger.warning(
                    f"Groq API call failed (Tier 1A): {e}. Falling back to Tier 1B (Ollama)..."
                )
                print(f"Warning: Groq API error: {e}")

        # ========== TIER 1B: Local Ollama (Fallback to local LLM) ==========
        if self.llm:
            prompt = f"""You are a helpful medical assistant providing information about diseases and symptoms.
            Use ONLY the information provided in the knowledge base to answer the query.
            If the information is not in the knowledge base, acknowledge that you don't have that information.
            Format your response in a clear, concise manner.
            
            Query: {query}
            
            {formatted_context}
            
            Answer:"""

            try:
                logger.info("Attempting Ollama response (Tier 1B)...")
                response = self.llm.invoke(prompt)
                logger.info("Successfully generated response using Ollama")
                return response.strip()
            except Exception as e:
                logger.warning(
                    f"Ollama LLM call failed (Tier 1B): {e}. Falling back to Tier 2 (Rule-based)..."
                )
                print(f"LLM Error: {e}")
                # Fall back to rule-based response if LLM fails
                return self._generate_rule_based_response(context, query)
        else:
            # Fallback to rule-based response if LLM is not available
            logger.info(
                "No LLM available. Using Tier 2 (Rule-based) response...")
            return self._generate_rule_based_response(context, query)

    def _generate_rule_based_response(self, context, query):
        """Generate a rule-based response when LLM is not available."""
        response = f"Here's what I found related to your query:\n\n"

        if not context:
            response += "No relevant information found."
        else:
            for item in context:
                response += f"Disease: {item['disease']}\n"
                response += f"Symptoms: {', '.join(item['symptoms'])}\n\n"

        return response


# import networkx as nx
# from knowledge_graph.schema import GraphSchema

# class ResponseGenerator:
#     def __init__(self, graph):
#         self.graph = graph

#     def extract_context(self, subgraph):
#         """Extract context from the subgraph for the LLM."""
#         if not subgraph:
#             return "No relevant information found."

#         context = []

#         # Extract disease information
#         diseases = [n for n, attr in subgraph.nodes(data=True)
#                    if attr.get('label') == GraphSchema.DISEASE]

#         for disease in diseases:
#             # Get symptoms of this disease
#             symptoms = []
#             for _, symptom, edge_data in subgraph.edges(disease, data=True):
#                 if edge_data.get('type') == GraphSchema.HAS_SYMPTOM:
#                     symptoms.append(symptom)

#             # Create context entry
#             if symptoms:
#                 symptom_list = ", ".join(symptoms)
#                 context.append(f"Disease: {disease}\nSymptoms: {symptom_list}")

#         # If we found no disease-symptom relationships but have nodes
#         if not context and subgraph.nodes():
#             context.append("Found related entities: " +
#                           ", ".join(list(subgraph.nodes())[:10]))

#         return "\n\n".join(context)

#     def generate_response(self, query, subgraph, use_llm=False):
#         """Generate a response based on the query and retrieved subgraph."""
#         context = self.extract_context(subgraph)

#         if use_llm:
#             # In a real implementation, you would call an LLM API here
#             # For demonstration, we'll return a template response
#             response = f"Based on your query '{query}', here's what I found:\n\n{context}"
#         else:
#             # Simple rule-based response
#             response = f"Here's what I found related to your query:\n\n{context}"

#         return response
