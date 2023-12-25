from kivy.app import App
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
import mysql.connector

class OrderApp(App):
    def __init__(self, **kwargs):
        super(OrderApp, self).__init__(**kwargs)
        self.db = None

    def build(self):
        try:
            self.db = mysql.connector.connect(
                host="########",
                user="#########",
                password="##########",
                database="##########"
            )
        except mysql.connector.Error as err:
            # Обработка ошибки подключения к базе данных
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')

        self.client_id = None
        self.driver_phone = None

        # Создание интерфейса для входа и регистрации
        self.login_layout = GridLayout(cols=1, spacing=10, padding=10)
        self.create_login_fields()

        self.login_tab = TabbedPanelItem(text='Вход')
        self.login_tab.add_widget(self.login_layout)

        # Создание основного интерфейса с вкладками
        tab_panel = TabbedPanel(do_default_tab=False)
        main_tab = TabbedPanelItem(text='Главное')
        orders_tab = TabbedPanelItem(text='Заказы')

        Window.clearcolor = (1, 1, 1, 1)

        # Вкладка "Главное"
        main_layout = GridLayout(cols=1, spacing=10, padding=10)
        main_layout.add_widget(Label(text='Адрес места отправления'))
        self.departure_input = TextInput(multiline=False, background_color=(1, 1, 1, 1))
        main_layout.add_widget(self.departure_input)

        main_layout.add_widget(Label(text='Адрес места назначения'))
        self.destination_input = TextInput(multiline=False, background_color=(1, 1, 1, 1))
        main_layout.add_widget(self.destination_input)

        main_layout.add_widget(Label(text='Комментарий'))
        self.comment_input = TextInput(multiline=False, background_color=(1, 1, 1, 1))
        main_layout.add_widget(self.comment_input)

        main_layout.add_widget(Label(text='Стоимость'))
        self.cost_label = Label(text='150 рублей')
        main_layout.add_widget(self.cost_label)

        # Добавляем надпись о номере телефона службы поддержки
        main_layout.add_widget(Label(text='Служба поддержки: 8-800-555-35-35', font_size=12))

        main_layout.add_widget(Button(text='Заказать', on_press=self.place_order))
        main_tab.add_widget(main_layout)

        # Вкладка "Заказы"
        self.orders_layout = GridLayout(cols=1, spacing=10, padding=10)
        # self.orders_label = Label(text='Ваши заказы:')
        # self.orders_layout.add_widget(self.orders_label)
        orders_tab = TabbedPanelItem(text='Заказы')
        orders_tab.add_widget(self.orders_layout)

        # Добавляем вкладки к панели
        tab_panel.add_widget(self.login_tab)
        tab_panel.add_widget(main_tab)
        tab_panel.add_widget(orders_tab)

        tab_panel.bind(current_tab=self.on_tab_switch)

        return tab_panel

    def on_tab_switch(self, instance, value):
        # Проверяем, что переключаемся на вкладку "Заказы"
        if value.text == 'Заказы':
            self.refresh_orders_list()

    def create_login_fields(self):
        self.login_layout.clear_widgets()

        self.login_layout.add_widget(Label(text='Логин'))
        self.login_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.login_input)

        self.login_layout.add_widget(Label(text='Пароль'))
        self.password_input = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.password_input)

        self.login_layout.add_widget(Button(text='Войти', on_press=self.login))
        self.login_layout.add_widget(Button(text='Зарегистрироваться', on_press=self.switch_to_register))

    def create_register_fields(self):
        self.login_layout.clear_widgets()

        self.login_layout.add_widget(Label(text='Логин'))
        self.login_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.login_input)

        self.login_layout.add_widget(Label(text='Пароль'))
        self.password_input = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.password_input)

        self.login_layout.add_widget(Label(text='Повторите пароль'))
        self.repeat_password_input = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.repeat_password_input)

        self.login_layout.add_widget(Label(text='Номер телефона'))
        self.phone_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.phone_input)

        consent_label = Label(text='Нажимая "Зарегистрироваться", \n вы даете согласие на обработку и хранение \n персональных данных.')
        self.login_layout.add_widget(consent_label)

        self.login_layout.add_widget(Button(text='Зарегистрироваться', on_press=self.register))
        self.login_layout.add_widget(Button(text='Войти', on_press=self.switch_to_login))

    def switch_to_register(self, instance):
        self.create_register_fields()

    def switch_to_login(self, instance):
        self.create_login_fields()

    def login(self, instance):

        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        login = self.login_input.text
        password = self.password_input.text

        if not login or not password:
            self.show_popup('Ошибка', 'Введите логин и пароль.')
            return

        client_id = self.authenticate_client(login, password)

        if not client_id:
            self.show_popup('Ошибка', 'Неверный логин или пароль.')
            return

        self.client_id = client_id
        self.login_tab.disabled = True  # Запрещаем доступ к вкладке входа/регистрации
        self.show_popup('Успешно', 'Вход выполнен.')

        self.switch_to_orders_tab()
        self.switch_to_main_tab()

    def switch_to_main_tab(self):
        self.root.switch_to(self.root.tab_list[1])

    def switch_to_orders_tab(self):
        self.refresh_orders_list()
        self.root.switch_to(self.root.tab_list[2])

    def refresh_orders_list(self):
        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        if self.client_id:
            cursor = self.db.cursor()
            query = "SELECT Nomer_zacaza, Mesto_otpravlenia, Mesto_naznacheniya, Stoimost, ID_Voditelya " \
                    "FROM Zakaz WHERE ID_Klienta = %s"
            values = (self.client_id,)
            try:
                cursor.execute(query, values)
                orders = cursor.fetchall()
                cursor.close()

                # Очищаем текущий список заказов
                self.orders_layout.clear_widgets()

                scroll_view = ScrollView()
                scroll_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
                scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

                # Обновляем список заказов
                for order in orders:
                    order_info = f"Заказ №{order[0]}\nМесто отправления: {order[1]}\nМесто назначения: {order[2]}\n" \
                                 f"Стоимость: {order[3]} рублей\n"

                    # Добавляем информацию о водителе, если заказ принят
                    if order[4]:
                        order_info += f"телефон водителя: {self.get_driver_phone(order[4])}\n"
                        order_info += "Заказ принят\n"

                    order_info += '-' * 30

                    order_label = Label(text=order_info, size_hint_y=None, height=dp(110))
                    scroll_layout.add_widget(order_label)

                # Добавляем GridLayout в ScrollView
                scroll_view.add_widget(scroll_layout)

                # Добавляем ScrollView в основной Layout
                self.orders_layout.add_widget(scroll_view)

            except mysql.connector.Error as err:
                print(f"Error in query: {err}")
            finally:
                cursor.close()

    def get_driver_phone(self, driver_id):
        cursor = self.db.cursor()
        query = "SELECT telefon FROM Voditel WHERE ID_voditelya = %s"
        values = (driver_id,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else "Номер не указан"

    def register(self, instance):
        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        login = self.login_input.text
        password = self.password_input.text
        repeat_password = self.repeat_password_input.text
        phone = self.phone_input.text

        if not login or not password or not repeat_password or not phone:
            self.show_popup('Ошибка', 'Заполните все поля.')
            return

        if password != repeat_password:
            self.show_popup('Ошибка', 'Пароли не совпадают.')
            return

        # Проверка наличия логина в базе данных
        if self.check_existing_login(login):
            self.show_popup('Ошибка', 'Пользователь с таким логином уже существует.')
            return

        # Регистрация нового пользователя
        self.register_client(login, password, phone)
        self.show_popup('Успешно', 'Регистрация завершена. Теперь вы можете войти.')
        self.switch_to_main_tab()

    def authenticate_client(self, login, password):
        cursor = self.db.cursor()
        query = "SELECT ID_klienta FROM Klient WHERE login = %s AND parol = %s"
        values = (login, password)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def check_existing_login(self, login):
        cursor = self.db.cursor()
        query = "SELECT ID_klienta FROM Klient WHERE login = %s"
        values = (login,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()
        return True if result else False

    def register_client(self, login, password, phone):
        if self.check_existing_phone(phone):
            self.show_popup('Ошибка', 'Пользователь с таким номером телефона уже существует.')
            return

        cursor = self.db.cursor()
        query = "INSERT INTO Klient (login, parol, telefon) VALUES (%s, %s, %s)"
        values = (login, password, phone)

        try:
            cursor.execute(query, values)
            self.db.commit()
            self.show_popup('Успешно', 'Регистрация завершена. Теперь вы можете войти.')
        except mysql.connector.Error as err:
            self.show_popup('Ошибка', f'Ошибка при выполнении запроса: {err}')
        finally:
            cursor.close()

    def check_existing_phone(self, phone):
        cursor = self.db.cursor()
        query = "SELECT ID_klienta FROM Klient WHERE telefon = %s"
        values = (phone,)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()
        return True if result else False

    def place_order(self, instance):

        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        departure = self.departure_input.text
        destination = self.destination_input.text
        comment = self.comment_input.text

        if not departure or not destination:
            self.show_popup('Ошибка', 'Заполните адреса отправления и назначения.')
            return

        if not self.client_id:
            self.show_popup('Ошибка', 'Вы не авторизованы.')
            return

        # Запись заказа в базу данных с использованием self.client_id
        cursor = self.db.cursor()
        query = "INSERT INTO Zakaz (ID_klienta, Mesto_otpravlenia, Mesto_naznacheniya, Kommentariy, Stoimost) " \
                "VALUES (%s, %s, %s, %s, %s)"
        values = (self.client_id, departure, destination, comment, 150)
        cursor.execute(query, values)
        self.db.commit()
        cursor.close()

        self.show_popup('Успешно', 'Заказ оформлен.')

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()


if __name__ == '__main__':
    OrderApp().run()
