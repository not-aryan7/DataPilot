"""Query execution service."""
from app.core.database import get_connection, execute_query


def validate_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    conn = get_connection()
    try:
        result = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name = ?",
            [table_name]
        ).fetchone()
        return result is not None
    finally:
        conn.close()


def get_table_schema(table_name: str) -> list[dict]:
    """Get the schema for a table."""
    conn = get_connection()
    try:
        result = conn.execute(f"DESCRIBE {table_name}").fetchall()
        return [{"column": row[0], "type": row[1]} for row in result]
    finally:
        conn.close()


def execute_user_query(sql: str) -> list[dict]:
    """
    Execute a SQL query and return results.
    
    Args:
        sql: The SQL query to execute
        
    Returns:
        List of dictionaries representing rows
    """
    return execute_query(sql)
