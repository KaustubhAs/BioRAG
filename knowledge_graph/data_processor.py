import pandas as pd
import numpy as np
from knowledge_graph.schema import GraphSchema


def preprocess_data(data_path):
    """Load and preprocess the disease-symptom dataset."""
    import pyarrow.parquet as pq
    
    # Read Parquet directory (will automatically read all partitions)
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    else:
        df = pd.read_parquet(data_path)

    print("Dataset columns:", df.columns.tolist())

    # Extract unique diseases
    diseases = df['Disease'].unique()

    # Extract all symptom columns
    symptom_columns = [col for col in df.columns if col.startswith('Symptom_')]

    # Collect all unique symptoms across all symptom columns
    all_symptoms = []
    for col in symptom_columns:
        # Drop NaN values before adding to the list
        all_symptoms.extend(df[col].dropna().unique())

    # Remove duplicates and NaN values
    symptoms = np.unique(
        [s for s in all_symptoms if isinstance(s, str) and s.strip()])

    # Create relationships
    relationships = []
    for _, row in df.iterrows():
        disease = row['Disease']
        for col in symptom_columns:
            symptom = row[col]
            # Skip if symptom is NaN or empty
            if not isinstance(symptom, pd.Series) and pd.notna(
                    symptom) and str(symptom).strip():
                relationships.append({
                    'source': disease,
                    'target': symptom,
                    'type': GraphSchema.HAS_SYMPTOM
                })

    return diseases, symptoms, relationships
