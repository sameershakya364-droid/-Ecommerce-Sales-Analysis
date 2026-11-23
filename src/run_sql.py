import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DB = ROOT / "data" / "processed" / "olist_sales.db"
SQL_FILE = ROOT / "sql" / "analysis.sql"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

# Read SQL file
sql = SQL_FILE.read_text(encoding="utf-8")

# Remove comment lines
sql_lines = []

for line in sql.splitlines():
    if not line.strip().startswith("--"):
        sql_lines.append(line)

clean_sql = "\n".join(sql_lines)

# Split queries
queries = [
    q.strip()
    for q in clean_sql.split(";")
    if q.strip()
]

# Execute queries
for i, query in enumerate(queries, start=1):

    print("\n" + "=" * 50)
    print("QUERY", i)
    print("=" * 50)

    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    print(" | ".join(columns))
    print("-" * 70)

    for row in rows:
        print(" | ".join(str(value) for value in row))

conn.close()

print("\nAll SQL queries executed successfully!")