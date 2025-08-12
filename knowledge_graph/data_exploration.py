import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
dataset_path = "D:\Code\BiomedicalAssistant\data\dataset.csv"  # Adjust path as needed
data = pd.read_csv(dataset_path)

# Display basic information
print("Dataset shape:", data.shape)
print("\nFirst 5 rows:")
print(data.head())

# Summary statistics
print("\nSummary statistics:")
print(data.describe())

# Check for missing values
print("\nMissing values per column:")
print(data.isnull().sum())

# Count of diseases and symptoms
if 'Disease' in data.columns and 'Symptom' in data.columns:
    print(f"\nNumber of unique diseases: {data['Disease'].nunique()}")
    print(f"Number of unique symptoms: {data['Symptom'].nunique()}")
