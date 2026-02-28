import os
from knowledge_graph.data_processor import preprocess_data
from knowledge_graph.embeddings import generate_disease_embeddings, generate_symptom_embeddings
from knowledge_graph.graph_builder import build_graph, visualize_graph

# Define paths
DATA_PATH = "./data/processed/"  # Adjust as needed


def main():
    print("Processing data...")
    diseases, symptoms, relationships = preprocess_data(DATA_PATH)

    print(f"Found {len(diseases)} diseases and {len(symptoms)} symptoms")

    print("Generating embeddings...")
    disease_embeddings = generate_disease_embeddings(diseases)
    symptom_embeddings = generate_symptom_embeddings(symptoms)

    print("Building graph...")
    G = build_graph(diseases, symptoms, relationships)

    print("Visualizing graph...")
    visualize_graph(G)

    print("Knowledge graph built successfully!")


if __name__ == "__main__":
    main()
