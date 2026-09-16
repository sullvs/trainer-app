from dotenv import load_dotenv
import psycopg2 
import os
from datetime import date
from werkzeug.security import generate_password_hash
load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute(
    "INSERT INTO users (first_name, last_name, password, email, role, registration_date) VALUES (%s,%s,%s,%s,%s,%s)",
    ('Test', 'Test', generate_password_hash('insert-password', method='pbkdf2:sha256'), 'test@test.com', 'Trainer', date.today())
)
conn.commit()
conn.close()
print("trainer created")