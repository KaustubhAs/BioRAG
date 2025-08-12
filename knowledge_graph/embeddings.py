from sentence_transformers import SentenceTransformer

def generate_embeddings(texts):
    """Generate embeddings for a list of texts."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts)
    return embeddings

def generate_disease_embeddings(diseases, descriptions=None):
    """Generate embeddings for disease entities."""
    if descriptions:
        texts = [f"Disease: {d}. Description: {desc}" for d, desc in zip(diseases, descriptions)]
    else:
        texts = [f"Disease: {d}" for d in diseases]
    return generate_embeddings(texts)

def generate_symptom_embeddings(symptoms):
    """Generate embeddings for symptom entities."""
    texts = [f"Symptom: {s}" for s in symptoms]
    return generate_embeddings(texts)
