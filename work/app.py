from PyQt5.QtWidgets import QApplication
from login import LoginWindow
import os
from PyQt5.QtCore import QCoreApplication

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(__file__),
    'D:/projects/PycharmProjects/work/.venv/Lib/site-packages/PyQt5/Qt5/plugins'
)
QCoreApplication.setAttribute(2)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Запуск окна авторизации
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec_())
