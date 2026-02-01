"""AI service for SQL generation - calls RAG components directly."""
import logging
from rag.sql_generator import SQLGenerator
from rag.llm import LocalLLM

logger = logging.getLogger(__name__)

# Singleton LLM instance to avoid reloading heavy model
_llm_instance = None


def get_llm():
    """Lazy load the LLM once and reuse."""
    global _llm_instance
    if _llm_instance is None:
        logger.info("[AI Service] Loading LocalLLM...")
        _llm_instance = LocalLLM()
    return _llm_instance


def format_schema_for_rag(schema: list[dict], table_name: str) -> list[str]:
    """
    Format schema info into a list of strings for the RAG retriever.
    """
    docs = []
    
    # Main table doc with all columns
    columns = ", ".join([col.get("column", "unknown") for col in schema])
    docs.append(f"Table {table_name}({columns})")
    
    # Individual column docs for better retrieval
    for col in schema:
        col_name = col.get("column", "unknown")
        col_type = col.get("type", "unknown")
        docs.append(f"Column '{col_name}' in table '{table_name}' has type {col_type}")
    
    return docs


def generate_sql(question: str, schema: list[dict], table_name: str) -> str:
    """
    Generate SQL by using the local SQLGenerator directly.
    
    Flow:
    1. Format schema into schema_docs
    2. Get singleton LLM
    3. Initialize SQLGenerator with specific schema + shared LLM
    4. Generate SQL
    """
    try:
        # Format schema for RAG
        schema_docs = format_schema_for_rag(schema, table_name)
        logger.info(f"[AI Service] Schema docs: {schema_docs}")
        
        # Get shared LLM
        llm = get_llm()
        
        # Create generator for this specific request
        # We create a new SQLGenerator each time to use the specific schema
        # but we pass the shared LLM to avoid reloading weights
        generator = SQLGenerator(schema_docs=schema_docs, llm_instance=llm)
        
        # Generate SQL
        logger.info(f"[AI Service] Generating SQL for question: {question}")
        sql = generator.generate(question)
        
        logger.info(f"[AI Service] Generated SQL: {sql}")
        return sql
        
    except Exception as e:
        logger.error(f"SQL Generation failed: {e}")
        # Fallback for error cases
        return f"SELECT * FROM {table_name} LIMIT 5"


def generate_answer(question: str, data: list[dict]) -> str:
    """
    Generate a natural language answer from query results.
    """
    row_count = len(data)
    if row_count == 0:
        return "I found no results matching your query."
        
    return f"I found {row_count} result(s) for your query. Here is the data."
