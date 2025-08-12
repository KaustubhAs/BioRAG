# 🏥 Biomedical Assistant

A Retrieval-Augmented Generation (RAG) system for biomedical information that combines a knowledge graph with natural language processing to answer questions about diseases and symptoms.

## Features

- **Knowledge Graph**: Interactive visualization of disease-symptom relationships
- **Q&A Interface**: Natural language questions about medical conditions
- **Dual Interface**: Both command-line (CLI) and web-based (UI) interfaces
- **Query History**: Track and search through previous questions
- **Intelligent Responses**: Powered by RAG system with fallback to rule-based responses

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd BiomedicalAssistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the dataset**:
   - Place your disease-symptom dataset as `data/dataset.csv`
   - The dataset should have columns: `Disease`, `Symptom_1`, `Symptom_2`, etc.

## Usage

### Web Interface (Recommended)

Launch the interactive web interface:

```bash
# Method 1: Using the launcher script
python run_ui.py

# Method 2: Using main.py
python main.py --mode ui

# Method 3: Direct Streamlit command
streamlit run app/streamlit_app.py
```

The web interface will open at `http://localhost:8501` with two main pages:

#### 🏥 Knowledge Graph Page
- Interactive network visualization
- Zoom, pan, and search functionality
- Filter diseases and symptoms
- View graph statistics
- Explore relationships

#### 🤖 Q&A Interface Page
- Ask questions about diseases and symptoms
- Get intelligent responses
- View query history
- Search through previous questions
- Example questions provided

### Command Line Interface

For traditional command-line usage:

```bash
python main.py --mode cli
```

Or simply:
```bash
python main.py
```

## Example Questions

Try these example questions in the Q&A interface:

- "What are the symptoms of diabetes?"
- "What diseases cause fever and headache?"
- "Tell me about malaria symptoms"
- "What are the symptoms of hypertension?"
- "What diseases are associated with chest pain?"

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Query Processor │───▶│ Response Generator│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Knowledge Graph │    │   LLM/LLaMA     │
                       │   (NetworkX)    │    │   (Ollama)      │
                       └─────────────────┘    └─────────────────┘
```

## Technical Stack

- **Python**: Core language
- **Streamlit**: Web interface
- **NetworkX**: Graph operations
- **Plotly**: Interactive visualizations
- **Sentence Transformers**: Semantic embeddings
- **Ollama**: Local LLM integration
- **Pandas**: Data processing

## Project Structure

```
BiomedicalAssistant/
├── app/
│   ├── cli.py              # Command-line interface
│   └── streamlit_app.py    # Web interface
├── knowledge_graph/
│   ├── data_processor.py   # Data preprocessing
│   ├── graph_builder.py    # Graph construction
│   ├── embeddings.py       # Vector embeddings
│   ├── neo4j_builder.py    # Neo4j integration
│   └── schema.py          # Graph schema
├── rag/
│   ├── biomedical_rag.py   # Main RAG system
│   ├── query_processor.py  # Query processing
│   └── response_generator.py # Response generation
├── data/
│   └── dataset.csv        # Disease-symptom dataset
├── main.py                # Main entry point
├── run_ui.py             # UI launcher
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## Configuration

### LLM Setup (Optional)

For enhanced responses, install Ollama and the llama3.2 model:

```bash
# Install Ollama (follow instructions at https://ollama.ai)
# Then pull the model:
ollama pull llama3.2
```

The system will work without Ollama using rule-based responses.

### Custom Dataset

To use your own dataset:

1. Format your CSV with columns: `Disease`, `Symptom_1`, `Symptom_2`, etc.
2. Place it as `data/dataset.csv`
3. Restart the application

## Troubleshooting

### Common Issues

1. **Dataset not found**: Ensure `data/dataset.csv` exists
2. **Import errors**: Install requirements with `pip install -r requirements.txt`
3. **LLM not working**: The system works without LLM using rule-based responses
4. **Port already in use**: Use `--port` argument to specify a different port

### Performance Tips

- The system caches the knowledge graph in memory
- First query may take longer due to model loading
- Large datasets may require more memory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is a research/educational tool and should not be used for medical diagnosis or treatment decisions. Always consult with qualified healthcare professionals for medical advice. 