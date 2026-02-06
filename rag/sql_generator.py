import logging
from .retriever import Retriever
from .llm import LocalLLM
from .prompt import build_sql_prompt

logger = logging.getLogger(__name__)


class SQLGenerator:
    """
    End-to-end SQL generation pipeline.

    Flow:
        question
            ↓
        Retriever (schema search)
            ↓
        Prompt builder
            ↓
        Local LLM
            ↓
        SQL string
    """

    def __init__(
        self,
        schema_docs: list[str],
        llm_instance: LocalLLM | None = None
    ):
        logger.info("[SQLGenerator] Initializing...")

        # build FAISS + reranker once
        self.retriever = Retriever(schema_docs)

        # load model once (reuse if provided)
        if llm_instance:
            self.llm = llm_instance
        else:
            self.llm = LocalLLM()

        logger.info("[SQLGenerator] Ready.")

    # -------------------------------------------------------

    def generate(self, question: str, sample_data: list[dict] | None = None) -> str:
        """
        Natural language question → SQL query string.
        """

        # 1️⃣ retrieve relevant schema
        docs = self.retriever.retrieve(question, k=10, final_k=3)

        if not docs:
            logger.warning("No schema retrieved for question: %s", question)
            return "-- Unable to generate SQL (no schema context)"

        # 2️⃣ build prompt
        prompt = build_sql_prompt(question, docs, sample_data=sample_data)

        # 3️⃣ generate SQL
        sql = self.llm.generate(prompt, max_tokens=256)

        return sql
