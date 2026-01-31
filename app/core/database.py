"""DuckDB connection management."""
import duckdb
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent.parent.parent / "data" / "datapilot.db"

def get_connection() -> duckdb.DuckDBPyConnection:
    """Get a connection to the DuckDB database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))

def execute_query(sql: str) -> list[dict]:
    """Execute a SQL query and return results as list of dicts."""
    conn = get_connection()
    try:
        result = conn.execute(sql).fetchdf()
        return result.to_dict(orient="records")
    finally:
        conn.close()
