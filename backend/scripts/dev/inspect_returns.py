import os
import pymysql

host = os.getenv("DB_HOST", "127.0.0.1")
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
db = os.getenv("DB_NAME", "jargas_apbn")
port = int(os.getenv("DB_PORT", "3306"))

conn = pymysql.connect(host=host, user=user, password=password, database=db, port=port)
cur = conn.cursor()
cur.execute("SELECT COUNT(*), SUM(project_id IS NULL) FROM returns")
row = cur.fetchone()
print("returns rows:", row)
cur.execute("SELECT id, mandor_id, material_id, quantity_kembali, project_id, is_deleted FROM returns ORDER BY id DESC LIMIT 10")
for r in cur.fetchall():
    print(r)
cur.close(); conn.close(); print('OK')
