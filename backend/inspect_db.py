import sqlite3

conn = sqlite3.connect("skillforge.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables:", [t[0] for t in tables])

for t in tables:
    name = t[0]
    cur.execute(f"PRAGMA table_info({name})")
    cols = cur.fetchall()
    print(f"\nTable: {name}")
    for c in cols:
        print(f"  {c[1]} ({c[2]})")
    cur.execute(f"SELECT count(*) FROM {name}")
    count = cur.fetchone()[0]
    print(f"  --> {count} row(s)")

conn.close()
