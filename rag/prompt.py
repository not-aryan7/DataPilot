def build_sql_prompt(question: str, schema_docs: list[str]) -> str:
    """
    Build a strong prompt for SQL generation.

    Inputs:
        question: user natural language question
        schema_docs: retrieved relevant schema text

    Returns:
        prompt string for the LLM
    """

    schema_text = "\n".join(schema_docs)

    prompt = f"""
You are an expert SQL analyst.

Your job is to write a correct SQL query using ONLY the provided schema.

Follow these rules strictly:
- Return ONLY SQL
- Return EXACTLY one SQL statement
- DO NOT explain
- DO NOT add text before or after
- If unsure, still output best SQL guess


====================
DATABASE SCHEMA:
====================
{schema_text}

====================
QUESTION:
====================
{question}

====================
SQL:
====================
"""

    return prompt.strip()
