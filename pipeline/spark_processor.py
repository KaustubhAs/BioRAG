"""
PySpark Data Preprocessing Pipeline for BioRAG.

This module is designed to handle up to 1M records, clean the text, and
export partitioned Parquet files for scalable ingestion by the RAG system.
"""

import os
import argparse
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, regexp_replace, concat_ws, array, lit

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_spark_session(app_name="BioRAG_Preprocessor"):
    """
    Initializes and returns a SparkSession.
    """
    logger.info(f"Initializing SparkSession: {app_name}")
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
        .getOrCreate()
    return spark


def clean_text_column(df, column_name):
    """
    Applies standard text cleaning to a specific column:
    - Trim whitespace
    - Convert to lowercase
    - Remove special characters (keep alphanumeric and spaces/underscores)
    """
    return df.withColumn(
        column_name,
        trim(lower(regexp_replace(col(column_name), r"[^a-zA-Z0-9_\s]", ""))))


def load_data(spark, input_path):
    """
    Loads raw CSV data.
    """
    logger.info(f"Loading data from {input_path}")
    # We assume the CSV has a header
    df = spark.read.csv(input_path, header=True, inferSchema=True)
    return df


def preprocess_data(df):
    """
    Cleans and structures the biomedical dataset.
    The dataset format is assumed to have a 'Disease' column
    and multiple 'Symptom_X' columns.
    """
    logger.info("Starting data preprocessing...")

    # 1. Clean the primary label column (Disease)
    if 'Disease' in df.columns:
        df = clean_text_column(df, 'Disease')
    else:
        logger.warning(
            "Column 'Disease' not found in dataset. Partitioning may fail.")

    # 2. Identify symptom columns
    symptom_cols = [c for c in df.columns if c.lower().startswith('symptom')]

    # 3. Clean symptom columns
    for sc in symptom_cols:
        df = clean_text_column(df, sc)

    logger.info(f"Cleaned {len(symptom_cols)} symptom columns.")

    return df


def write_parquet_spark(df, output_path, partition_col="Disease"):
    """
    Writes the processed Spark DataFrame to Parquet using Spark.
    On Windows this often fails due to HADOOP_HOME/winutils; use write_parquet_pandas as fallback.
    """
    if partition_col in df.columns:
        df.repartition(partition_col) \
          .write \
          .mode("overwrite") \
          .partitionBy(partition_col) \
          .parquet(output_path)
    else:
        df.write.mode("overwrite").parquet(output_path)


def write_parquet_pandas(df, output_path):
    """
    Writes the processed Spark DataFrame to Parquet using Pandas/PyArrow.
    Used on Windows when Spark's write fails (HADOOP_HOME/winutils not set).
    """
    logger.info(
        "Converting to Pandas and writing Parquet (Windows-friendly path)...")
    pdf = df.toPandas()
    os.makedirs(output_path, exist_ok=True)
    # Single file in the directory so pd.read_parquet(output_path) works
    single_path = os.path.join(output_path, "data.parquet")
    pdf.to_parquet(single_path, index=False)
    logger.info(f"Wrote {single_path}")


def main():
    parser = argparse.ArgumentParser(description="BioRAG PySpark Preprocessor")
    parser.add_argument("--input",
                        type=str,
                        default="data/dataset.csv",
                        help="Path to raw CSV dataset")
    parser.add_argument("--output",
                        type=str,
                        default="data/processed/",
                        help="Path to output Parquet directory")
    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return

    spark = create_spark_session()

    try:
        # Load
        df = load_data(spark, args.input)

        # Initial stats
        record_count = df.count()
        logger.info(f"Loaded {record_count} records.")

        # Preprocess
        df_clean = preprocess_data(df)

        # Export: try Spark write first; on Windows (HADOOP_HOME/winutils missing) use Pandas
        try:
            logger.info(f"Writing data to {args.output} (Spark)...")
            write_parquet_spark(df_clean, args.output)
            logger.info("Write operation completed successfully (Spark).")
        except Exception as e:
            from py4j.protocol import Py4JJavaError
            if isinstance(e, Py4JJavaError) or "HADOOP_HOME" in str(
                    e) or "winutils" in str(e).lower():
                logger.warning(
                    "Spark write failed (Windows/HADOOP_HOME). Using Pandas/PyArrow for output."
                )
                write_parquet_pandas(df_clean, args.output)
                logger.info(
                    "Write operation completed successfully (Pandas/PyArrow).")
            else:
                raise

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
    finally:
        logger.info("Stopping SparkSession.")
        spark.stop()


if __name__ == "__main__":
    main()
