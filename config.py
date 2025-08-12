"""
Configuration file for Biomedical Assistant
"""

import os

# Data paths
DATA_PATH = "data/dataset.csv"
KNOWLEDGE_GRAPH_PATH = "knowledge_graph/"

# LLM Configuration
LLM_MODEL = "llama3.2"  # Ollama model name
LLM_ENABLED = True  # Set to False to disable LLM and use only rule-based responses

# Graph Configuration
GRAPH_LAYOUT_ITERATIONS = 50
GRAPH_SPRING_K = 1.0

# Query Processing
SEMANTIC_SIMILARITY_THRESHOLD = 0.3
FUZZY_MATCH_THRESHOLD = 0.7
MAX_TOP_MATCHES = 3

# UI Configuration
STREAMLIT_PORT = 8501
STREAMLIT_HOST = "localhost"
STREAMLIT_THEME = "light"

# Visualization
NODE_COLORS = {"Disease": "red", "Symptom": "blue"}
NODE_SIZES = {"Disease": 15, "Symptom": 10}

# Response Configuration
MAX_RESPONSE_LENGTH = 1000
INCLUDE_CONFIDENCE_SCORES = True

# Development
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = "INFO"
