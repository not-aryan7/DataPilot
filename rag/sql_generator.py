import logging
from .retriever import Retriever
from .llm import LocalLLM
from .prompt import build_sql_prompt

logger = logging.getLogger(__name__)

class SQLGenerator:
    """
    RAG Pipeline for SQL Generation:
    1. Retrieve relevant schema context
    2. Build prompt
    3. Generate SQL using Local LLM
    """

    def __init__(self, schema_docs: list[str], model_name: str = None, llm_instance: LocalLLM = None):
        """
        Args:
            schema_docs: List of strings describing tables/columns for the retriever index
            model_name: Optional custom model name (defaults to Mistral in LocalLLM)
            llm_instance: Pre-loaded LocalLLM instance (recommended to save memory)
        """
        logger.info("[SQLGenerator] Initializing RAG pipeline...")
        
        # 1. Initialize Retriever (builds FAISS index)
        self.retriever = Retriever(schema_docs)
        
        # 2. Initialize LLM (loads model to GPU/CPU)
        if llm_instance:
             self.llm = llm_instance
        elif model_name:
            self.llm = LocalLLM(model_name=model_name)
        else:
            self.llm = LocalLLM()
            
        logger.info("[SQLGenerator] Pipeline ready.")

    def generate(self, question: str) -> str:
        """
        Generate SQL for a given natural language question.
        """
        # 1. Retrieve relevant schema context
        # k=10 candidates, final_k=3 best matches after reranking
        relevant_docs = self.retriever.retrieve(question, k=10, final_k=3)
        
        if not relevant_docs:
            logger.warning("No relevant schema found for question: %s", question)
            # Fallback: maybe use all schema if small, or return empty
            # For now, let's assume if nothing found, we can't generate good SQL
        
        # 2. Build Prompt
        prompt = build_sql_prompt(question, relevant_docs)
        
        # 3. Generate
        # max_tokens=256 is usually enough for SQL
        sql = self.llm.generate(prompt, max_tokens=256)
        
        return sql
