import sqlite3
import glob
import os

print("=== STARHEALERS DATABASE AUDIT ===")
db_files = glob.glob(r"E:\StarHealers\**\*.db", recursive=True)
for p in sorted(db_files):
    try:
        conn = sqlite3.connect(p)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in c.fetchall() if not t[0].startswith('sqlite_')]
        print(f"\nDatabase: {p} (Size: {os.path.getsize(p)} bytes)")
        for t in sorted(tables):
            c.execute(f"SELECT count(*) FROM [{t}]")
            cnt = c.fetchone()[0]
            print(f"  - {t}: {cnt} rows")
        conn.close()
    except Exception as e:
        print(f"\nDatabase: {p} - Error: {e}")
