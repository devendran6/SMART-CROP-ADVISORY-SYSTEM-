import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'database.db')
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')

conn = sqlite3.connect(db_path)
with open(schema_path) as f:
    conn.executescript(f.read())
conn.commit()
conn.close()
print("Database initialized!")
