from rag.sql_generator import SQLGenerator


# fake schema for testing
schema_docs = [
    "Table calls(agent_name, talk_time_sec, call_date, csat_score)",
    "Table agents(agent_name, team, supervisor)",
    "Table tickets(ticket_id, agent_name, status, created_at)",
    "Table sales(order_id, region, revenue, date)"
]


def main():
    print("\n===== SQL Generator Test =====\n")

    generator = SQLGenerator(
        schema_docs=schema_docs
    )

    questions = [
        "average talk time per agent",
        "total revenue by region",
        "count open support tickets",
        "number of calls per team"
    ]

    for q in questions:
        print("\nQuestion:", q)
        sql = generator.generate(q)
        print("SQL:\n", sql)


if __name__ == "__main__":
    main()
