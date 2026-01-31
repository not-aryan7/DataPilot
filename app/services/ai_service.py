"""AI service for SQL generation."""
import logging
from app.api.models import ColumnSchema
from rag.sql_generator import SQLGenerator
from rag.llm import LocalLLM

logger = logging.getLogger(__name__)

# Global shared LLM instance to avoid reloading 7GB model
# It will include lazy loading
SHARED_LLM = None

def get_shared_llm():
    """Lazy load the LLM model."""
    global SHARED_LLM
    if SHARED_LLM is None:
        logger.info("[AI Service] Loading Shared LLM (Mistral)...")
        try:
            SHARED_LLM = LocalLLM()
        except Exception as e:
            logger.error(f"Failed to load LocalLLM: {e}")
            raise e
    return SHARED_LLM

def format_schema_for_rag(schema: list[dict], table_name: str) -> list[str]:
    """
    Format schema info into a list of strings for the retriever.
    Expected format by RAG depends on retriever, but usually descriptive text.
    """
    docs = []
    # Main table doc
    docs.append(f"Table: {table_name}")
    
    # Column docs
    for col in schema:
        # col is a dict: {"column": "name", "type": "VARCHAR"}
        # If ColumnSchema pydantic model is passed, convert to dict
        if hasattr(col, "column"):
            col_name = col.column
            col_type = col.type
        else:
            col_name = col.get("column", "unknown")
            col_type = col.get("type", "unknown")
            
        docs.append(f"Column '{col_name}' in table '{table_name}' has type {col_type}")
    
    return docs

def generate_sql(question: str, schema: list[dict], table_name: str) -> str:
    """
    Generate SQL using the RAG pipeline.
    """
    try:
        # 1. Get LLM (reuse loaded instance)
        llm = get_shared_llm()
        
        # 2. Format schema for Retriever
        schema_docs = format_schema_for_rag(schema, table_name)
        
        # 3. Initialize RAG pipeline for this specific dataset
        # We reuse the heavy LLM, but build a light-weight Retriever index for this schema
        rag = SQLGenerator(schema_docs=schema_docs, llm_instance=llm)
        
        # 4. Generate
        logger.info(f"Generating SQL for: {question}")
        sql = rag.generate(question)
        logger.info(f"Generated SQL: {sql}")
        
        return sql
        
    except Exception as e:
        logger.error(f"SQL Generation failed: {e}")
        # Fallback for testing/error cases
        logger.info("Returning fallback SQL due to error")
        return f"SELECT * FROM {table_name} LIMIT 5"


def generate_answer(question: str, data: list[dict]) -> str:
    """
    Generate a natural language answer from query results.
    """
    # For now, keep this simple or hook up LLM here too
    row_count = len(data)
    if row_count == 0:
        return "I found no results matching your query."
        
    return f"I found {row_count} result(s) for your query. Here is the data."
