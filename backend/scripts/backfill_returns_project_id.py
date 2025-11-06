import os
import pymysql

host = os.getenv("DB_HOST", "127.0.0.1")
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
db = os.getenv("DB_NAME", "jargas_apbn")
port = int(os.getenv("DB_PORT", "3306"))

conn = pymysql.connect(host=host, user=user, password=password, database=db, port=port)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM returns WHERE project_id IS NULL")
null_count = cur.fetchone()[0]
print(f"returns with NULL project_id: {null_count}")
if null_count > 0:
    cur.execute("UPDATE returns SET project_id = 1 WHERE project_id IS NULL")
    conn.commit()
    print(f"Updated {cur.rowcount} returns rows to project_id=1")
else:
    print("No NULL project_id rows to update")
cur.close(); conn.close(); print('OK')
