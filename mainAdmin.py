import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, \
    QTableWidgetItem, QLineEdit, QInputDialog, QMessageBox
import mysql.connector


class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Панель администратора')
        self.setGeometry(100, 100, 800, 600)

        self.connection = mysql.connector.connect(
            host="#############",
            user="#########",
            password="#############",
            database="##########"
        )
        self.cursor = self.connection.cursor()

        self.table_selector_layout = QHBoxLayout()
        self.zakaz_button = QPushButton('Заказ')
        self.voditel_button = QPushButton('Водитель')
        self.klient_button = QPushButton('Клиент')
        self.table_selector_layout.addWidget(self.zakaz_button)
        self.table_selector_layout.addWidget(self.voditel_button)
        self.table_selector_layout.addWidget(self.klient_button)

        self.table_label = QLabel('Выбранная таблица:')
        self.table_name_label = QLabel()

        self.table_layout = QVBoxLayout()

        self.add_button = QPushButton('Добавить')
        self.edit_button = QPushButton('Изменить')
        self.delete_button = QPushButton('Удалить')

        self.init_table('Zakaz')

        self.add_button.clicked.connect(self.add_record)
        self.edit_button.clicked.connect(self.edit_record)
        self.delete_button.clicked.connect(self.delete_record)

        self.zakaz_button.clicked.connect(lambda: self.init_table('Zakaz'))
        self.voditel_button.clicked.connect(lambda: self.init_table('Voditel'))
        self.klient_button.clicked.connect(lambda: self.init_table('Klient'))

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.table_selector_layout)
        main_layout.addWidget(self.table_label)
        main_layout.addWidget(self.table_name_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(self.table_layout)

        self.setLayout(main_layout)
        self.show()

    def init_table(self, table_name):
        if hasattr(self, 'table'):
            self.table.setParent(None)

        self.current_table = table_name
        self.table_name_label.setText(table_name)
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(self.get_table_columns(table_name)))
        self.table.setHorizontalHeaderLabels(self.get_table_columns(table_name))
        self.refresh_table()
        self.table_layout.addWidget(self.table)

    def refresh_table(self):
        query = f"SELECT * FROM {self.current_table}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        self.table.setRowCount(0)

        for row_num, row_data in enumerate(result):
            self.table.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                if isinstance(col_data, bool):
                    item.setCheckState(col_data)
                self.table.setItem(row_num, col_num, item)

    def get_table_columns(self, table_name):
        query = f"SHOW COLUMNS FROM {table_name}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        columns = [column[0] for column in result]
        return columns

    def add_record(self):
        columns = self.get_table_columns(self.current_table)
        data = []
        for column in columns:
            if column == 'Tip_oplati':
                value, ok = QInputDialog.getInt(self, f"Добавление записи", f"Введите значение для {column}", 0, 0, 1)
            else:
                value, ok = QInputDialog.getText(self, f"Добавление записи", f"Введите значение для {column}")
            if not ok:
                return
            data.append(value)

        try:
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.current_table} VALUES ({placeholders})"
            self.cursor.execute(query, tuple(data))
            self.connection.commit()
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Не удалось добавить запись: {e}')

    def edit_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return

        columns = self.get_table_columns(self.current_table)
        data = []
        for col_num, column in enumerate(columns):
            current_value = self.table.item(selected_row, col_num).text()
            if column == 'Tip_oplati':
                value, ok = QInputDialog.getInt(self, f"Редактирование записи", f"Введите новое значение для {column}",
                                                int(current_value), 0, 1)
            else:
                value, ok = QInputDialog.getText(self, f"Редактирование записи", f"Введите новое значение для {column}",
                                                 text=current_value)
            if not ok:
                return
            data.append(value)

        primary_key_column = columns[0]
        primary_key_value = self.table.item(selected_row, 0).text()
        set_clause = ', '.join([f"{columns[i]} = %s" for i in range(len(columns))])
        query = f"UPDATE {self.current_table} SET {set_clause} WHERE {primary_key_column} = %s"

        try:
            self.cursor.execute(query, tuple(data + [primary_key_value]))
            self.connection.commit()
            self.refresh_table()
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', f'Не удалось изменить запись: {e}')

    def delete_record(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return

        primary_key_column = self.get_table_columns(self.current_table)[0]
        primary_key_value = self.table.item(selected_row, 0).text()
        query = f"DELETE FROM {self.current_table} WHERE {primary_key_column} = %s"
        self.cursor.execute(query, (primary_key_value,))
        self.connection.commit()
        self.refresh_table()

    def closeEvent(self, event):
        self.connection.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    admin_panel = AdminPanel()
    sys.exit(app.exec_())
