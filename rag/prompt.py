def build_sql_prompt(question: str, schema_docs: list[str], sample_data: list[dict] | None = None) -> str:
    """
    Build a strong prompt for SQL generation.

    Inputs:
        question: natural language question
        schema_docs: retrieved relevant schema text
        sample_data: optional sample rows from the table

    Returns:
        prompt string for the LLM
    """

    schema_text = "\n".join(schema_docs)

    # build sample data section
    sample_section = ""
    if sample_data and len(sample_data) > 0:
        cols = list(sample_data[0].keys())
        header = " | ".join(cols)
        rows = "\n".join(
            " | ".join(str(row.get(c, "")) for c in cols)
            for row in sample_data
        )
        sample_section = f"""
====================
SAMPLE DATA (first 3 rows):
====================
{header}
{rows}
"""

    prompt = f"""
You are an expert SQL analyst.

Your job is to write a correct SQL query using ONLY the provided schema.

Follow these rules strictly:
- Return ONLY SQL
- Return EXACTLY one SQL statement
- DO NOT explain anything
- DO NOT add text before or after
- Only use columns listed in the schema
- NEVER invent columns (like id)
- NEVER assume fields
- Use WHERE clauses to filter for specific values when the question asks about a specific item
- Match string values exactly as shown in the sample data
- If unsure, use: SELECT * FROM table LIMIT 5
- For preview queries, NEVER use ORDER BY
- Always prefer LIMIT for first rows

====================
DATABASE SCHEMA:
====================
{schema_text}
{sample_section}
====================
QUESTION:
====================
{question}

====================
SQL:
====================
"""

    return prompt.strip()
