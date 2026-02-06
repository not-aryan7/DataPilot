# ai_service.py
import logging
from rag.sql_generator import SQLGenerator
from rag.llm import LocalLLM

logger = logging.getLogger(__name__)

_llm = None
_generators = {}  # cache per dataset


def get_llm():
    global _llm
    if _llm is None:
        logger.info("Loading LocalLLM once...")
        _llm = LocalLLM()
    return _llm


def build_schema_docs(schema: list[dict], table_name: str) -> list[str]:
    cols = ", ".join(c["column"] for c in schema)

    docs = [f"Table {table_name}({cols})"]

    for col in schema:
        docs.append(
            f"Column '{col['column']}' in table '{table_name}' has type {col['type']}"
        )

    return docs


def generate_sql(question: str, schema: list[dict], table_name: str, sample_data: list[dict] | None = None) -> str:
    try:
        if table_name not in _generators:
            logger.info(f"Building retriever ONCE for {table_name}")

            docs = build_schema_docs(schema, table_name)

            _generators[table_name] = SQLGenerator(
                schema_docs=docs,
                llm_instance=get_llm()
            )

        generator = _generators[table_name]

        return generator.generate(question, sample_data=sample_data)

    except Exception as e:
        logger.error(e)
        return f"SELECT * FROM {table_name} LIMIT 5"
