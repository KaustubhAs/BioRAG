import os
import sys
import argparse
import networkx as nx
from knowledge_graph.data_processor import preprocess_data
from knowledge_graph.graph_builder import build_graph
from rag.biomedical_rag import BiomedicalRAG
from app.cli import CLI

# Define paths
DATA_PATH = "data/dataset.csv"  # Adjust as needed


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Biomedical Assistant")
    parser.add_argument(
        "--mode",
        choices=["cli", "ui"],
        default="cli",
        help="Run mode: cli (command line) or ui (web interface)")
    parser.add_argument("--port",
                        type=int,
                        default=8501,
                        help="Port for web interface (default: 8501)")

    args = parser.parse_args()

    if args.mode == "ui":
        # Launch UI mode
        print("🏥 Starting Biomedical Assistant UI...")
        print("The web interface will open in your browser.")
        print("Press Ctrl+C to stop the server.")

        try:
            import subprocess
            app_path = os.path.join(os.path.dirname(__file__), "app",
                                    "streamlit_app.py")
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", app_path,
                "--server.port",
                str(args.port), "--server.address", "localhost"
            ])
        except KeyboardInterrupt:
            print("\nBiomedical Assistant UI stopped.")
        except Exception as e:
            print(f"Error starting UI: {e}")
            print("Make sure you have installed the requirements:")
            print("pip install -r requirements.txt")
        return

    # CLI mode (original functionality)
    # Check if dataset exists
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        print(
            "Please download the dataset and place it in the correct location."
        )
        return

    print("Loading and processing data...")
    diseases, symptoms, relationships = preprocess_data(DATA_PATH)

    print("Building knowledge graph...")
    graph = build_graph(diseases, symptoms, relationships)

    print("Initializing RAG system...")
    rag_system = BiomedicalRAG(graph)

    print("Starting CLI application...")
    cli = CLI(rag_system)
    cli.run()


if __name__ == "__main__":
    main()
