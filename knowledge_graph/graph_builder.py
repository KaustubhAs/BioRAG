import networkx as nx
import matplotlib.pyplot as plt
from .schema import GraphSchema


def build_graph(diseases, symptoms, relationships):
    """Build a NetworkX graph with diseases and symptoms."""
    G = nx.Graph()

    # Add disease nodes
    for disease in diseases:
        G.add_node(disease, label=GraphSchema.DISEASE)

    # Add symptom nodes
    for symptom in symptoms:
        G.add_node(symptom, label=GraphSchema.SYMPTOM)

    # Add relationships
    for rel in relationships:
        G.add_edge(rel['source'], rel['target'], type=rel['type'])

    return G


def visualize_graph(G, output_path='knowledge_graph.png'):
    """Visualize the graph and save to a file."""
    plt.figure(figsize=(12, 8))

    # Get node positions
    pos = nx.spring_layout(G)

    # Draw disease nodes
    disease_nodes = [
        n for n, attr in G.nodes(data=True)
        if attr.get('label') == GraphSchema.DISEASE
    ]
    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=disease_nodes,
                           node_color='red',
                           node_size=200,
                           alpha=0.8)

    # Draw symptom nodes
    symptom_nodes = [
        n for n, attr in G.nodes(data=True)
        if attr.get('label') == GraphSchema.SYMPTOM
    ]
    nx.draw_networkx_nodes(G,
                           pos,
                           nodelist=symptom_nodes,
                           node_color='blue',
                           node_size=100,
                           alpha=0.6)

    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
