from PyQt5.QtWidgets import QMainWindow, QLineEdit, QPushButton, QMessageBox, QLabel
import bcrypt


class RegisterWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Create New User')
        self.setGeometry(100, 100, 300, 300)

        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Username")
        self.username_field.setGeometry(50, 50, 200, 30)

        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Password")
        self.password_field.setGeometry(50, 100, 200, 30)
        self.password_field.setEchoMode(QLineEdit.Password)

        self.role_field = QLineEdit(self)
        self.role_field.setPlaceholderText("Role (user/admin)")
        self.role_field.setGeometry(50, 150, 200, 30)

        create_button = QPushButton("Create", self)
        create_button.setGeometry(100, 200, 100, 30)
        create_button.clicked.connect(self.create_user)

    def create_user(self):
        username = self.username_field.text()
        password = self.password_field.text()
        role = self.role_field.text()

        if not username or not password or role not in ["user", "admin"]:
            QMessageBox.warning(self, "Error", "Заполните все поля корректно!")
            return

        try:
            # Проверка на уникальность имени пользователя
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Error", "Имя пользователя уже занято!")
                return

            # Хеширование пароля
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # Добавление нового пользователя
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, hashed_password, role)
            )
            self.db.commit()

            QMessageBox.information(self, "Success", "Пользователь успешно создан!")
            self.close()  # Закрываем окно регистрации
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Error", str(e))
