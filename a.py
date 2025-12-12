import sqlite3

def inspect_sqlite(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Inspecting SQLite database: {db_path}\n")

    # list all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found.")
        return

    for (table,) in tables:
        print(f"--- TABLE: {table} ---")

        # get table schema
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()

        for col in columns:
            cid, name, col_type, notnull, default_value, pk = col
            print(f"  {name} | {col_type} | NOT NULL={bool(notnull)} | PK={bool(pk)} | DEFAULT={default_value}")

        print()

    conn.close()


if __name__ == "__main__":
    inspect_sqlite("movies.db")
