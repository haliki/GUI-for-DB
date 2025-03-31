from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, \
    QWidget, QTabWidget, QHBoxLayout, QMessageBox, QLabel, QLineEdit, QComboBox, QDialog
from PyQt5.QtCore import Qt
import psycopg2
import os
from PyQt5.QtWidgets import QVBoxLayout, QPushButton


os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(__file__),
    'C:/Users/User/PycharmProjects/work/.venv/Lib/site-packages/PyQt5/Qt5/plugins'
)


class MainWindow(QMainWindow):
    def __init__(self, db_connection, username, role):
        super().__init__()
        self.db_connection = db_connection
        self.username = username  # Сохраняем имя пользователя
        self.role = role
        self.setWindowTitle(f"Project management system")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        # Основной макет
        main_layout = QVBoxLayout()

        # Добавляем метку с именем пользователя
        user_label = QLabel(f"Добро пожаловать, {self.username} ({self.role})!", self)
        user_label.setAlignment(Qt.AlignRight)  # Выравнивание по правому краю
        user_label.setStyleSheet("font-size: 14px; color: gray;")  # Стилизация текста
        main_layout.addWidget(user_label)

        # Кнопка для анализа загрузки
        analyze_button = QPushButton("Анализ загрузки", self)
        analyze_button.clicked.connect(self.open_analysis_dialog)
        main_layout.addWidget(analyze_button)

        # Создаем виджет вкладок
        self.tabs = QTabWidget(self)

        # Вкладки для таблиц
        self.projects_tab = self.create_tab("projects")
        self.departments_tab = self.create_tab("departments")
        self.employees_tab = self.create_tab("employees")
        self.departments_employees_tab = self.create_tab("departments_employees")

        # Добавляем вкладки в интерфейс
        self.tabs.addTab(self.projects_tab, "Проекты")
        self.tabs.addTab(self.departments_tab, "Отделы")
        self.tabs.addTab(self.employees_tab, "Служащие")
        self.tabs.addTab(self.departments_employees_tab, "Служащие по отделам")

        main_layout.addWidget(self.tabs)

        # Устанавливаем центральный виджет
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def refresh_all_tabs(self):
        """Обновить данные во всех вкладках."""
        try:
            for i in range(self.tabs.count()):
                table_name = self.tabs.tabText(i).lower()  # Имя таблицы соответствует названию вкладки
                tab_widget = self.tabs.widget(i)
                table = tab_widget.findChild(QTableWidget, table_name)  # Найти таблицу по имени

                if table:
                    self.load_data(table, table_name)  # Перезагрузить данные
            QMessageBox.information(self, "Обновление", "Данные успешно обновлены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить данные: {e}")

    def open_analysis_dialog(self):
        """Открыть окно анализа"""
        self.analysis_dialog = AnalysisDialog(self.db_connection)
        self.analysis_dialog.exec_()

    def create_tab(self, table_name):
        """Создание вкладки для указанной таблицы"""
        tab = QWidget()
        layout = QVBoxLayout()

        if table_name == "projects":
            filters_layout = QHBoxLayout()
            self.departments_filter = QComboBox()
            self.departments_filter.addItem("Все отделы", None)
            self.populate_combobox(self.departments_filter, "departments")
            self.departments_filter.currentIndexChanged.connect(lambda: self.load_data(table, table_name))
            filters_layout.addWidget(QLabel("Фильтр по отделу:"))
            filters_layout.addWidget(self.departments_filter)

            layout.addLayout(filters_layout)

        # Таблица для отображения данных
        table = QTableWidget()
        table.setObjectName(table_name)  # Устанавливаем имя таблицы
        layout.addWidget(table)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Добавить")
        edit_button = QPushButton("Изменить")
        delete_button = QPushButton("Удалить")

        # Отключение кнопок для роли "user"
        if self.role == "user":
            add_button.setEnabled(False)
            edit_button.setEnabled(False)
            delete_button.setEnabled(False)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)

        layout.addLayout(buttons_layout)

        tab.setLayout(layout)

        # Подключаем кнопки к действиям
        add_button.clicked.connect(lambda: self.open_form(table_name, None))
        edit_button.clicked.connect(lambda: self.open_edit_form(table, table_name))
        delete_button.clicked.connect(lambda: self.delete_record(table, table_name))

        # Загружаем данные
        self.load_data(table, table_name)

        return tab

    def populate_combobox(self, combo_box, table_name):
        """Заполнить выпадающий список данными из указанной таблицы"""
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT id, name FROM {table_name}")
        data = cursor.fetchall()

        if not data:
            combo_box.addItem("Нет данных", None)
        else:
            for item_id, item_name in data:
                combo_box.addItem(str(item_name), item_id)


    #чинить
    def load_data(self, table, table_name):
        """Загрузка данных из указанной таблицы"""
        cursor = self.db_connection.cursor()

        if table_name == "projects":
            # Применяем фильтры
            departments_id = self.departments_filter.currentData()

            query = """
                SELECT p.id, p.name, p.cost, p.date_beg, p.date_end, p.date_end_real,
                        COALESCE(d.name, '{Нет данных}') AS department
                FROM projects p
                LEFT JOIN departments d ON p.department_id = d.id
            """
            conditions = []
            params = []

            if departments_id:
                conditions.append("p.departments_id = %s")
                params.append(departments_id)

            if conditions:
                query = query.replace("WHERE", "AND".join(conditions))

            cursor.execute(query, tuple(params))  # Передаем параметры для SQL
        else:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)

        data = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]

        table.setRowCount(len(data))
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        for row_idx, record in enumerate(data):
            for col_idx, value in enumerate(record):
                table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

        # Запрет редактирования таблицы напрямую
        table.setEditTriggers(QTableWidget.NoEditTriggers)

    def open_form(self, table_name, record_id=None):
        """Открыть форму для добавления или редактирования записи"""
        self.form = RecordForm(self.db_connection, table_name, record_id, parent=self)
        self.form.show()

    def open_edit_form(self, table, table_name):
        """Открыть форму для редактирования выбранной записи"""
        try:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
                return

            record_id = table.item(selected_row, 0).text()
            if not record_id.isdigit():
                QMessageBox.warning(self, "Ошибка", "Некорректный идентификатор записи")
                return

            record_id = int(record_id)
            print(f"Редактирование записи с ID: {record_id}")  # Отладочный вывод

            self.open_form(table_name, record_id)

        except Exception as e:
            print(f"Ошибка при открытии формы редактирования: {e}")  # Логирование ошибки
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть форму редактирования: {e}")

    def delete_record(self, table, table_name):
        """Удалить выбранную запись с обработкой триггеров"""
        selected_row = table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления")
            return

        record_id = int(table.item(selected_row, 0).text())
        reply = QMessageBox.question(self, "Подтверждение", f"Удалить запись с ID {record_id}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (record_id,))
                self.db_connection.commit()
                QMessageBox.information(self, "Успех", "Запись успешно удалена!")

                # Обновление текущей таблицы
                self.load_data(table, table_name)

                # Если удалена запись
                if table_name in ["departments"]:
                    people_table = self.tabs.widget(0).findChild(QTableWidget, "projects")
                    self.load_data(people_table, "projects")

            except psycopg2.Error as e:
                self.db_connection.rollback()
                error_message = e.diag.message_primary if e.diag.message_primary else str(e)
                QMessageBox.critical(self, "Ошибка базы данных", f"Удаление невозможно: {error_message}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")


class RecordForm(QWidget):
    def __init__(self, db_connection, table_name, record_id=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Форма записи")
        self.setGeometry(150, 150, 400, 300)

        self.db_connection = db_connection
        self.table_name = table_name
        self.record_id = record_id
        self.init_ui()

        if self.record_id:
            self.load_record()

    #чинить
    def init_ui(self):
        # Устанавливаем центральный фон для всей формы
        self.setStyleSheet("background-color: #e0e0e0;")

        # Создаем контейнер-карточку
        card_container = QWidget(self)
        card_container.setStyleSheet("""
            background-color: #ffffff;
            border: 1px solid #d3d3d3;
        """)
        card_container.setFixedSize(300, 300)

        # Создаем макет для контейнера
        card_layout = QVBoxLayout(card_container)

        # Поля ввода
        self.fields = {}
        if self.table_name == "employees":
            labels = {"Имя": "first_name", "Фамилия": "last_name","Отчество": "father_name", "Должность": "position", "Зарплата": "salary"}
        elif self.table_name == "departments":
            labels = {"Название": "name"}
        elif self.table_name == "departments_employees":
            labels = {"Отдел": "department_id", "Служащий": "employee_id"}
        elif self.table_name == "projects":
            labels = {"Имя": "name", "Стоимость": "cost", "Дата начала": "date_beg", "Дата окончания": "date_end", "Рельаная дата окончания": "date_end_real", "Отдел": "department_id"}

        for label, field_name in labels.items():
            card_layout.addWidget(QLabel(label))

            if field_name in ["department_id", "employee_id"]:
                # Для связанных данных используем QComboBox
                combo_box = QComboBox(card_container)
                if field_name == "department_id":
                    self.populate_combobox(combo_box, "departments")
                elif field_name == "employee_id":
                    self.populate_combobox(combo_box, "employees")
                self.fields[field_name] = combo_box
                card_layout.addWidget(combo_box)
            else:
                field = QLineEdit(card_container)
                self.fields[field_name] = field
                card_layout.addWidget(field)

        # Кнопки
        self.save_button = QPushButton("Сохранить", card_container)
        self.cancel_button = QPushButton("Закрыть", card_container)

        card_layout.addWidget(self.save_button)
        card_layout.addWidget(self.cancel_button)

        # Основной макет формы
        layout = QVBoxLayout(self)
        layout.addWidget(card_container, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        # Подключение событий кнопок
        self.save_button.clicked.connect(self.save_record)
        self.cancel_button.clicked.connect(self.close)

    def populate_combobox(self, combo_box, table_name):
        """Заполнить выпадающий список данными из указанной таблицы"""
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT id, name FROM {table_name}")
        data = cursor.fetchall()

        combo_box.clear()
        for item_id, item_name in data:
            combo_box.addItem(str(item_name), item_id)  # Отображаем имя, но связываем ID

    def load_record(self):
        """Загрузка данных записи для редактирования"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = %s", (self.record_id,))
            record = cursor.fetchone()

            if not record:
                QMessageBox.warning(self, "Ошибка", "Запись не найдена")
                return

            # Пропускаем ID
            for idx, value in enumerate(record[1:]):
                field_name = list(self.fields.keys())[idx]
                field = self.fields[field_name]

                if isinstance(field, QComboBox):
                    index = field.findData(value)  # Используем идентификатор для поиска
                    if index != -1:
                        field.setCurrentIndex(index)
                    else:
                        print(f"Ошибка: Не удалось найти значение {value} в QComboBox {field_name}")
                elif isinstance(field, QLineEdit):
                    field.setText(str(value if value is not None else ""))

        except IndexError as e:
            print(f"Ошибка: Индекс выходит за границы. Проверьте порядок полей. Сообщение: {e}")
            QMessageBox.critical(self, "Ошибка", "Некорректная конфигурация полей в базе.")
        except Exception as e:
            print(f"Ошибка при загрузке записи: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить запись: {e}")

    def save_record(self):
        """Сохранение данных записи с обработкой ошибок"""
        try:
            cursor = self.db_connection.cursor()

            # Получаем данные из полей
            values = []
            for label, field in self.fields.items():
                if isinstance(field, QLineEdit):
                    value = field.text()
                elif isinstance(field, QComboBox):
                    value = field.currentData()
                else:
                    value = None
                values.append(value)

            print(f"Сохранение данных: {values}")  # Отладочный вывод

            if self.record_id:
                # Обновление записи
                placeholders = ", ".join([f'"{col}" = %s' for col in self.fields.keys()])
                query = f'UPDATE "{self.table_name}" SET {placeholders} WHERE id = %s'
                cursor.execute(query, (*values, self.record_id))
            else:
                # Добавление новой записи
                columns = ", ".join([f'"{col}"' for col in self.fields.keys()])
                placeholders = ", ".join(["%s"] * len(self.fields))
                query = f'INSERT INTO "{self.table_name}" ({columns}) VALUES ({placeholders})'
                cursor.execute(query, values)

            self.db_connection.commit()
            QMessageBox.information(self, "Успех", "Запись успешно сохранена!")

            # Обновление таблицы после добавления/изменения
            parent_tab = self.parent()
            table = parent_tab.findChild(QTableWidget, self.table_name)
            parent_tab.load_data(table, self.table_name)

            self.close()

        except psycopg2.IntegrityError as e:
            self.db_connection.rollback()
            print(f"Ошибка целостности: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка целостности данных: {e}")
        except psycopg2.Error as e:
            self.db_connection.rollback()
            error_message = e.diag.message_primary if e.diag else str(e)
            print(f"Ошибка базы данных: {error_message}")
            QMessageBox.critical(self, "Ошибка базы данных", f"Ошибка: {error_message}")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", f"Неизвестная ошибка: {e}")

class AnalysisDialog(QDialog):
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setWindowTitle("Анализ прибыли проектов")
        self.setGeometry(150, 150, 800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Создаем таблицу для отображения данных
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Кнопка обновления данных
        refresh_button = QPushButton("Обновить")
        refresh_button.clicked.connect(self.load_data)
        layout.addWidget(refresh_button)

        # Загрузка данных при открытии
        self.load_data()

    def load_data(self):
        """Получить данные из базы и отобразить в таблице."""
        try:
            cursor = self.db_connection.cursor()
            query = """
                SELECT  p.id AS project_id,
                        p.name AS project_name,
                        p.cost AS project_cost,
                        COALESCE(SUM(e.salary * EXTRACT(MONTH FROM AGE(NOW(), p.date_beg))), 0) AS total_cost,
                        p.cost - COALESCE(SUM(e.salary * EXTRACT(MONTH FROM AGE(NOW(), p.date_beg))), 0) AS profit
                    FROM 
                        projects p
                    LEFT JOIN 
                        departments_employees de ON p.department_id = de.department_id
                    LEFT JOIN 
                        employees e ON de.employee_id = e.id
                    WHERE 
                        p.date_end_real IS NULL AND  -- Проекты не завершены
                        p.date_beg <= NOW()         -- Проекты уже начаты
                    GROUP BY 
                        p.id, p.name, p.cost
                    ORDER BY 
                        profit DESC;

            """

            cursor.execute(query)
            data = cursor.fetchall()

            if not data:
                QMessageBox.warning(self, "Данные отсутствуют", "Нет данных для анализа.")
                return

            # Установка заголовков таблицы
            headers = ["ID","Название проекта", "Стоимость", "Общие зарплаты", "Предполагаемая прибыль"]
            self.table.setRowCount(len(data))
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            # Заполнение таблицы
            for row_idx, row_data in enumerate(data):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

            # Запрет редактирования таблицы напрямую
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Подключение к базе данных
    conn = psycopg2.connect(host="localhost", database="work", user="postgres", password="cruz", port="5432")

    window = MainWindow(conn)
    window.show()

    sys.exit(app.exec_())
