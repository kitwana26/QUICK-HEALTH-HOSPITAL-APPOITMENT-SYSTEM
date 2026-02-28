import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='2002'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("CREATE DATABASE hospital_db")
    print('Database hospital_db created successfully!')
    cur.close()
    conn.close()
except psycopg2.errors.DuplicateDatabase:
    print('Database hospital_db already exists!')
except Exception as e:
    print(f'Error: {e}')
