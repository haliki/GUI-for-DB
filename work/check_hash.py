import bcrypt
import psycopg2

conn = psycopg2.connect(host="localhost", database="work", user="postgres", password="cruz", port="5432")

# Проверка пароля
def authenticate_user(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        stored_hash, role = result
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            print(f"Успешный вход, роль: {role}")
        else:
            print("Неверный пароль")
    else:
        print("Пользователь не найден")


# Пример
authenticate_user("admin", "123")
