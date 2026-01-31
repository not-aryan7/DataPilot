"""AI service for SQL generation.

This is a STUB - your friend (AI/RAG side) will replace this with vLLM integration.
"""


def generate_sql(question: str, schema: list[dict], table_name: str) -> str:
    """
    Generate SQL from a natural language question.
    
    STUB IMPLEMENTATION - Returns basic SQL for testing.
    Your friend will integrate this with vLLM/RAG for real SQL generation.
    
    Args:
        question: Natural language question from user
        schema: List of column definitions [{"column": str, "type": str}, ...]
        table_name: Name of the table to query
        
    Returns:
        SQL query string
    """
    # TODO: Replace with vLLM integration (AI/RAG team)
    # For now, return a simple SELECT that works for testing
    return f"SELECT * FROM {table_name} LIMIT 10"


def generate_answer(question: str, data: list[dict]) -> str:
    """
    Generate a natural language answer from query results.
    
    STUB IMPLEMENTATION - Your friend will integrate this with LLM.
    
    Args:
        question: Original question
        data: Query results
        
    Returns:
        Natural language answer
    """
    # TODO: Replace with LLM integration (AI/RAG team)
    row_count = len(data)
    return f"Found {row_count} result(s) for your query."
