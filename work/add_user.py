import bcrypt
import psycopg2

conn = psycopg2.connect(host="localhost", database="work", user="postgres", password="cruz", port="5432")

def add_user(username, password, role):
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                   (username, hashed_password, role))
    conn.commit()
    cursor.close()

add_user("admin", "123", "admin")
conn.close()
