from dotenv import load_dotenv
import psycopg2, os
load_dotenv()

conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute("UPDATE users SET password = %s WHERE email = %s",
            ('insert-hashed-password', 'test@test.com'))
conn.commit()
conn.close()
print("done")