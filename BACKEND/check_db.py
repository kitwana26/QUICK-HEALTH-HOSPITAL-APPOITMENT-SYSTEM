import psycopg2

conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='2002',
    database='hospital_db'
)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cur.fetchall()

print('Tables in hospital_db PostgreSQL database:')
for t in tables:
    print(f'  - {t[0]}')

conn.close()
