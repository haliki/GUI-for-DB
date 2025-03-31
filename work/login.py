from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QMessageBox
from database import connect
import bcrypt
from register_window import RegisterWindow  # Импорт формы регистрации
from main_window import MainWindow  # Импорт главного окна


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = connect()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Login to Management')
        self.setGeometry(100, 100, 300, 250)

        self.username_field = QLineEdit(self)
        self.username_field.setPlaceholderText("Username")
        self.username_field.setGeometry(50, 50, 200, 30)

        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Password")
        self.password_field.setGeometry(50, 100, 200, 30)
        self.password_field.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login", self)
        login_button.setGeometry(50, 150, 90, 30)
        login_button.clicked.connect(self.authenticate)

        register_button = QPushButton("Create User", self)
        register_button.setGeometry(160, 150, 90, 30)
        register_button.clicked.connect(self.open_register_window)  # Переход к форме регистрации

    def authenticate(self):
        username = self.username_field.text()
        password = self.password_field.text()

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT password_hash, role FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                stored_hash, role = result
                if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                    QMessageBox.information(self, "Success", f"Успешный вход, роль: {role}")

                    # Открываем главное окно с передачей роли
                    self.main_window = MainWindow(self.db, username, role)
                    self.main_window.show()

                    self.close()  # Закрываем окно входа
                else:
                    QMessageBox.warning(self, "Error", "Неверный пароль")
            else:
                QMessageBox.warning(self, "Error", "Пользователь не найден")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_register_window(self):
        """Открыть форму регистрации нового пользователя."""
        self.register_window = RegisterWindow(self.db)
        self.register_window.show()


# Для тестирования окна входа
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
