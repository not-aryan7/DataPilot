"""Ingestion service: CSV -> DuckDB."""
import uuid
from pathlib import Path
from app.core.database import get_connection

def ingest_csv(file_path: Path, table_name: str = None) -> dict:
    """
    Ingest a CSV file into DuckDB.
    
    Args:
        file_path: Path to the CSV file
        table_name: Optional custom table name, auto-generated if not provided
    
    Returns:
        Dict with dataset_id, table_name, schema info
    """
    if table_name is None:
        table_name = f"dataset_{uuid.uuid4().hex[:8]}"
    
    conn = get_connection()
    try:
        # Create table from CSV
        conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path.as_posix()}')
        """)
        
        # Extract schema
        schema_result = conn.execute(f"DESCRIBE {table_name}").fetchall()
        schema = [
            {"column": row[0], "type": row[1]}
            for row in schema_result
        ]
        
        # Get row count
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        
        return {
            "dataset_id": table_name,
            "table_name": table_name,
            "schema": schema,
            "row_count": row_count
        }
    finally:
        conn.close()
