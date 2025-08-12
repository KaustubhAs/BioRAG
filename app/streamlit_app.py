import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_graph.data_processor import preprocess_data
from knowledge_graph.graph_builder import build_graph
from rag.biomedical_rag import BiomedicalRAG

# Page configuration
st.set_page_config(page_title="Biomedical Assistant",
                   page_icon="🏥",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Initialize session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'graph' not in st.session_state:
    st.session_state.graph = None
if 'query_history' not in st.session_state:
    st.session_state.query_history = []


def initialize_system():
    """Initialize the RAG system and knowledge graph."""
    try:
        with st.spinner("Loading biomedical knowledge base..."):
            # Load and process data
            DATA_PATH = "data/dataset.csv"
            if not os.path.exists(DATA_PATH):
                st.error(f"Dataset not found at {DATA_PATH}")
                return False

            diseases, symptoms, relationships = preprocess_data(DATA_PATH)

            # Build knowledge graph
            graph = build_graph(diseases, symptoms, relationships)

            # Initialize RAG system
            rag_system = BiomedicalRAG(graph)

            # Store in session state
            st.session_state.rag_system = rag_system
            st.session_state.graph = graph

            st.success("System initialized successfully!")
            return True

    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return False


def create_interactive_graph(graph,
                             show_diseases=True,
                             show_symptoms=True,
                             search_term=""):
    """Create an interactive Plotly graph visualization with filtering."""
    if not graph:
        return None

    # Get node positions using spring layout
    pos = nx.spring_layout(graph, k=1, iterations=50)

    # Separate nodes by type
    disease_nodes = [
        n for n, attr in graph.nodes(data=True)
        if attr.get('label') == "Disease"
    ]
    symptom_nodes = [
        n for n, attr in graph.nodes(data=True)
        if attr.get('label') == "Symptom"
    ]

    # Apply filters
    if not show_diseases:
        disease_nodes = []
    if not show_symptoms:
        symptom_nodes = []

    # Apply search filter if provided
    if search_term:
        search_lower = search_term.lower()
        matched_diseases = [
            n for n in disease_nodes if search_lower in n.lower()
        ]
        matched_symptoms = [
            n for n in symptom_nodes if search_lower in n.lower()
        ]

        # Include 1-hop neighborhood of matched nodes
        neighborhood_nodes = set()

        # Add matched nodes and their neighbors
        for node in matched_diseases + matched_symptoms:
            neighborhood_nodes.add(node)
            # Add all neighbors of this node
            for neighbor in graph.neighbors(node):
                neighborhood_nodes.add(neighbor)

        # Filter the original node lists to only include neighborhood nodes
        disease_nodes = [n for n in disease_nodes if n in neighborhood_nodes]
        symptom_nodes = [n for n in symptom_nodes if n in neighborhood_nodes]

        print(
            f"Search matched: {len(matched_diseases)} diseases, {len(matched_symptoms)} symptoms"
        )
        print(
            f"Neighborhood includes: {len(disease_nodes)} diseases, {len(symptom_nodes)} symptoms"
        )

    # Debug information (can be removed in production)
    print(
        f"Filter settings: show_diseases={show_diseases}, show_symptoms={show_symptoms}, search_term='{search_term}'"
    )
    print(
        f"Visible nodes: {len(disease_nodes)} diseases, {len(symptom_nodes)} symptoms"
    )

    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []

    # Get matched nodes for highlighting
    matched_nodes = set()
    if search_term:
        search_lower = search_term.lower()
        matched_diseases = [
            n for n in disease_nodes if search_lower in n.lower()
        ]
        matched_symptoms = [
            n for n in symptom_nodes if search_lower in n.lower()
        ]
        matched_nodes = set(matched_diseases + matched_symptoms)

    # Add disease nodes
    for node in disease_nodes:
        if node in pos:
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(f"Disease: {node}")
            # Highlight searched nodes with darker color and larger size
            if node in matched_nodes:
                node_color.append('darkred')
                node_size.append(20)
            else:
                node_color.append('red')
                node_size.append(15)

    # Add symptom nodes
    for node in symptom_nodes:
        if node in pos:
            node_x.append(pos[node][0])
            node_y.append(pos[node][1])
            node_text.append(f"Symptom: {node}")
            # Highlight searched nodes with darker color and larger size
            if node in matched_nodes:
                node_color.append('darkblue')
                node_size.append(15)
            else:
                node_color.append('blue')
                node_size.append(10)

    # Create edge traces - only show edges between visible nodes
    edge_x = []
    edge_y = []

    visible_nodes = set(disease_nodes + symptom_nodes)
    for edge in graph.edges():
        if edge[0] in pos and edge[1] in pos and edge[
                0] in visible_nodes and edge[1] in visible_nodes:
            edge_x.extend([pos[edge[0]][0], pos[edge[1]][0], None])
            edge_y.extend([pos[edge[0]][1], pos[edge[1]][1], None])

    # Create the figure
    fig = go.Figure()

    # Add edges
    fig.add_trace(
        go.Scatter(x=edge_x,
                   y=edge_y,
                   line=dict(width=0.5, color='gray'),
                   hoverinfo='none',
                   mode='lines',
                   showlegend=False))

    # Add nodes
    fig.add_trace(
        go.Scatter(x=node_x,
                   y=node_y,
                   mode='markers+text',
                   hoverinfo='text',
                   text=node_text,
                   textposition="top center",
                   marker=dict(size=node_size,
                               color=node_color,
                               line=dict(width=2, color='white')),
                   showlegend=False))

    # Update layout
    fig.update_layout(title="Biomedical Knowledge Graph",
                      showlegend=False,
                      hovermode='closest',
                      margin=dict(b=20, l=5, r=5, t=40),
                      xaxis=dict(showgrid=False,
                                 zeroline=False,
                                 showticklabels=False),
                      yaxis=dict(showgrid=False,
                                 zeroline=False,
                                 showticklabels=False),
                      height=600)

    # If no nodes are visible, add a message
    if len(node_x) == 0:
        fig.add_annotation(text="No nodes match the current filters",
                           xref="paper",
                           yref="paper",
                           x=0.5,
                           y=0.5,
                           showarrow=False,
                           font=dict(size=16, color="gray"))

    return fig


def knowledge_graph_page():
    """Knowledge Graph visualization page."""
    st.title("🏥 Biomedical Knowledge Graph")
    st.markdown(
        "Explore the relationships between diseases and symptoms in our knowledge base."
    )

    # Initialize system if not already done
    if st.session_state.graph is None:
        if not initialize_system():
            st.stop()

    # Sidebar controls
    st.sidebar.header("Graph Controls")

    # Node filtering
    st.sidebar.subheader("Filter Nodes")
    show_diseases = st.sidebar.checkbox("Show Diseases", value=True)
    show_symptoms = st.sidebar.checkbox("Show Symptoms", value=True)

    # Search functionality
    st.sidebar.subheader("Search Nodes")
    search_term = st.sidebar.text_input("Search for disease or symptom:")

    # Clear filters button
    if st.sidebar.button("Clear All Filters"):
        st.rerun()

    # Graph statistics
    if st.session_state.graph:
        graph = st.session_state.graph
        disease_count = len([
            n for n, attr in graph.nodes(data=True)
            if attr.get('label') == "Disease"
        ])
        symptom_count = len([
            n for n, attr in graph.nodes(data=True)
            if attr.get('label') == "Symptom"
        ])
        edge_count = len(graph.edges())

        st.sidebar.subheader("Graph Statistics")
        st.sidebar.metric("Diseases", disease_count)
        st.sidebar.metric("Symptoms", symptom_count)
        st.sidebar.metric("Relationships", edge_count)

    # Main graph visualization
    col1, col2 = st.columns([3, 1])

    with col1:
        if st.session_state.graph:
            # Show filter status
            if not show_diseases or not show_symptoms or search_term:
                filter_info = []
                if not show_diseases:
                    filter_info.append("Diseases hidden")
                if not show_symptoms:
                    filter_info.append("Symptoms hidden")
                if search_term:
                    filter_info.append(
                        f"Search: '{search_term}' (showing matched nodes + neighbors)"
                    )
                st.info(f"Filters applied: {', '.join(filter_info)}")

            fig = create_interactive_graph(st.session_state.graph,
                                           show_diseases=show_diseases,
                                           show_symptoms=show_symptoms,
                                           search_term=search_term)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Graph not available")

    with col2:
        st.subheader("Graph Information")
        st.markdown("""
        **Red nodes**: Diseases  
        **Blue nodes**: Symptoms  
        **Gray lines**: Relationships
        
        **Search highlighting:**
        - **Dark red/blue**: Searched nodes
        - **Light red/blue**: Connected neighbors
        
        **Interactions:**
        - Hover over nodes to see details
        - Zoom and pan to explore
        - Use sidebar to filter and search
        - Search shows matched nodes + their connections
        """)

        # Quick stats
        if st.session_state.graph:
            st.subheader("Top Diseases")
            disease_nodes = [
                n for n, attr in st.session_state.graph.nodes(data=True)
                if attr.get('label') == "Disease"
            ]
            for disease in disease_nodes[:10]:
                neighbor_count = len(
                    list(st.session_state.graph.neighbors(disease)))
                st.write(f"• {disease} ({neighbor_count} symptoms)")


def qa_page():
    """Q&A Interface page."""
    st.title("🤖 Biomedical Q&A Assistant")
    st.markdown(
        "Ask questions about diseases and symptoms. Get intelligent responses based on our knowledge base."
    )

    # Initialize system if not already done
    if st.session_state.rag_system is None:
        if not initialize_system():
            st.stop()

    # Main Q&A interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Ask a Question")

        # Question input
        question = st.text_area(
            "Enter your question about diseases or symptoms:",
            placeholder="e.g., What are the symptoms of diabetes?",
            height=100)

        # Ask button
        if st.button("Ask Question", type="primary"):
            if question.strip():
                with st.spinner("Processing your question..."):
                    try:
                        response = st.session_state.rag_system.answer_query(
                            question)

                        # Add to history
                        timestamp = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S")
                        st.session_state.query_history.append({
                            'timestamp':
                            timestamp,
                            'question':
                            question,
                            'response':
                            response
                        })

                        # Display response
                        st.subheader("Answer")
                        st.write(response)

                    except Exception as e:
                        st.error(f"Error processing question: {str(e)}")
            else:
                st.warning("Please enter a question.")

        # Example questions
        st.subheader("Example Questions")
        examples = [
            "What are the symptoms of diabetes?",
            "What diseases cause fever and headache?",
            "Tell me about malaria symptoms",
            "What are the symptoms of hypertension?",
            "What diseases are associated with chest pain?"
        ]

        for example in examples:
            if st.button(example, key=f"example_{example}"):
                st.session_state.example_question = example
                st.rerun()

    with col2:
        st.subheader("Quick Stats")
        if st.session_state.graph:
            disease_count = len([
                n for n, attr in st.session_state.graph.nodes(data=True)
                if attr.get('label') == "Disease"
            ])
            symptom_count = len([
                n for n, attr in st.session_state.graph.nodes(data=True)
                if attr.get('label') == "Symptom"
            ])

            st.metric("Diseases in Database", disease_count)
            st.metric("Symptoms in Database", symptom_count)
            st.metric("Questions Asked", len(st.session_state.query_history))

    # Query History
    st.subheader("📚 Query History")

    if st.session_state.query_history:
        # Filter history
        search_history = st.text_input("Search in history:")

        filtered_history = st.session_state.query_history
        if search_history:
            filtered_history = [
                item for item in st.session_state.query_history
                if search_history.lower() in item['question'].lower()
                or search_history.lower() in item['response'].lower()
            ]

        # Display history
        for i, item in enumerate(reversed(filtered_history)):
            with st.expander(
                    f"Q: {item['question'][:50]}... ({item['timestamp']})"):
                st.write(f"**Question:** {item['question']}")
                st.write(f"**Answer:** {item['response']}")

                # Delete button
                if st.button(f"Delete", key=f"delete_{i}"):
                    st.session_state.query_history.remove(item)
                    st.rerun()
    else:
        st.info("No questions asked yet. Start by asking a question above!")


def main():
    """Main application with navigation."""
    # Sidebar navigation
    st.sidebar.title("Biomedical Assistant")

    # Navigation
    page = st.sidebar.selectbox("Choose a page:",
                                ["Knowledge Graph", "Q&A Interface"])

    # System status
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")

    if st.session_state.rag_system is not None:
        st.sidebar.success("✅ System Ready")
    else:
        st.sidebar.error("❌ System Not Initialized")
        if st.sidebar.button("Initialize System"):
            initialize_system()

    # Page routing
    if page == "Knowledge Graph":
        knowledge_graph_page()
    elif page == "Q&A Interface":
        qa_page()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Biomedical Assistant v1.0**")
    st.sidebar.markdown("Powered by RAG + Knowledge Graph")


if __name__ == "__main__":
    main()
