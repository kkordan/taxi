from kivy.app import App
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import mysql.connector

class DriverApp(App):
    def __init__(self, **kwargs):
        super(DriverApp, self).__init__(**kwargs)
        self.db = None

    def build(self):
        try:
            self.db = mysql.connector.connect(
                host="5.183.188.132",
                user="db_stud_dan_usr2",
                password="z0AtWDNnYSRROJWr",
                database="db_stud_dann"
            )
        except mysql.connector.Error as err:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')

        self.driver_id = None

        # Вкладка "Вход/Регистрация" для водителя
        self.login_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.create_driver_login_fields()

        self.login_tab = TabbedPanelItem(text='Вход', content=self.login_layout)

        # Создание основного интерфейса с вкладками
        tab_panel = TabbedPanel(do_default_tab=False)
        main_tab = TabbedPanelItem(text='Главная')
        orders_tab = TabbedPanelItem(text='Заказы')

        Window.clearcolor = (1, 1, 1, 1)

        # Вкладка "Главная" для водителя
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        main_layout.add_widget(Label(text='Информация о заказе'))
        main_layout.add_widget(Label(text='Адрес отправления:'))
        self.departure_label = Label(text='')
        main_layout.add_widget(self.departure_label)
        main_layout.add_widget(Label(text='Адрес назначения:'))
        self.destination_label = Label(text='')
        main_layout.add_widget(self.destination_label)
        main_layout.add_widget(Label(text='Комментарий к заказу:'))
        self.comment_label = Label(text='')
        main_layout.add_widget(self.comment_label)
        main_layout.add_widget(Label(text='Цена заказа:'))
        self.price_label = Label(text='')
        main_layout.add_widget(self.price_label)

        main_tab.add_widget(main_layout)

        self.orders_layout = ScrollView()

        self.orders_container = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.orders_layout.add_widget(self.orders_container)

        orders_tab.add_widget(self.orders_layout)

        tab_panel.add_widget(self.login_tab)
        tab_panel.add_widget(main_tab)
        tab_panel.add_widget(orders_tab)

        tab_panel.bind(current_tab=self.on_tab_switch)

        return tab_panel

    def authenticate_driver(self, login, password):
        cursor = self.db.cursor()
        query = "SELECT ID_Voditelya FROM Voditel WHERE login = %s AND parol = %s"
        values = (login, password)
        cursor.execute(query, values)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None


    def on_tab_switch(self, instance, value):
        if value.text == 'Заказы':
            self.refresh_available_orders()

    def create_driver_login_fields(self):
        self.login_layout.clear_widgets()  # Очищаем виджеты

        self.login_layout.add_widget(Label(text='Логин'))
        self.login_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.login_input)

        self.login_layout.add_widget(Label(text='Пароль'))
        self.password_input = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.password_input)

        if self.driver_id is None:

            self.login_layout.add_widget(Button(text='Войти', on_press=self.login))
            self.login_layout.add_widget(Button(text='Зарегистрироваться', on_press=self.show_registration_fields))

    def show_registration_fields(self, instance):
        # Очищаем текущий layout
        self.login_layout.clear_widgets()

        # Добавляем необходимые поля для регистрации
        self.login_layout.add_widget(Label(text='Логин'))
        self.login_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.login_input)

        self.login_layout.add_widget(Label(text='Пароль'))
        self.password_input = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.password_input)

        self.login_layout.add_widget(Label(text='Серия номер водительского'))
        self.VU = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.VU)

        self.login_layout.add_widget(Label(text='Номер автомобиля'))
        self.avto = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.avto)

        self.login_layout.add_widget(Label(text='Номер телефона'))
        self.phone_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.phone_input)

        # Добавляем надпись о персональных данных
        privacy_label = Label(text='Нажимая "Зарегистрироваться", \n вы даете согласие на обработку и хранение \n персональных данных.')
        self.login_layout.add_widget(privacy_label)

        self.login_layout.add_widget(Button(text='Зарегистрироваться', on_press=self.register))
        self.login_layout.add_widget(Button(text='Войти', on_press=self.show_login_fields))

    def show_login_fields(self, instance):
        # Очищаем текущий layout
        self.login_layout.clear_widgets()

        # Добавляем поля для входа
        self.login_layout.add_widget(Label(text='Логин'))
        self.login_input = TextInput(multiline=False, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.login_input)

        self.login_layout.add_widget(Label(text='Пароль'))
        self.password_input = TextInput(multiline=False, password=True, background_color=(1, 1, 0, 1))
        self.login_layout.add_widget(self.password_input)

        self.login_layout.add_widget(Button(text='Войти', on_press=self.login))
        self.login_layout.add_widget(Button(text='Зарегистрироваться', on_press=self.show_registration_fields))

        # Переключаемся на вкладку "Доступные заказы" после успешного входа
        self.root.switch_to(self.root.tab_list[2])

    def refresh_available_orders(self):
        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        if self.driver_id:
            cursor = self.db.cursor()
            query = "SELECT Nomer_zacaza, Mesto_otpravlenia, Mesto_naznacheniya, Kommentariy, Stoimost FROM Zakaz WHERE ID_Voditelya IS NULL"
            try:
                cursor.execute(query)
                orders = cursor.fetchall()
                cursor.close()

                # Очищаем текущий контейнер с заказами
                self.orders_container.clear_widgets()

                # Обновляем список доступных заказов
                for order in orders:
                    order_info = f"Заказ №{order[0]}\nМесто отправления: {order[1]}\nМесто назначения: {order[2]}\n" \
                                 f"Комментарий: {order[3]}\nСтоимость: {order[4]} рублей\n{'-' * 30}"
                    order_label = Label(text=order_info, size_hint_y=None, height=dp(80))

                    # Добавляем кнопку "Принять заказ" с обработчиком on_press
                    accept_button = Button(text='Принять заказ',
                                           size_hint_y=None,
                                           height=dp(40),
                                           on_press=lambda instance, order_id=order[0]: self.accept_order(order_id))

                    # Делаем кнопку недоступной после принятия заказа
                    if self.is_order_accepted(order[0]):
                        accept_button.disabled = True

                    # Добавляем виджеты в контейнер
                    self.orders_container.add_widget(order_label)
                    self.orders_container.add_widget(accept_button)

                # Устанавливаем высоту контейнера
                self.orders_container.height = self.orders_container.minimum_height

            except mysql.connector.Error as err:
                print(f"Error in query: {err}")
            finally:
                cursor.close()

    def is_order_accepted(self, order_id):
        cursor = self.db.cursor()
        query = "SELECT ID_Voditelya FROM Zakaz WHERE Nomer_zacaza = %s"
        values = (order_id,)
        try:
            cursor.execute(query, values)
            result = cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as err:
            print(f"Error checking if order is accepted: {err}")
        finally:
            cursor.close()

    def accept_order(self, order_id):
        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        if not self.driver_id:
            self.show_popup('Ошибка', 'Вы не авторизованы.')
            return

        # Проверяем, что заказ еще не принят
        if self.is_order_accepted(order_id):
            self.show_popup('Ошибка', 'Этот заказ уже принят.')
            return

        # Обновляем поле ID_Voditelya в заказе
        cursor = self.db.cursor()
        update_query = "UPDATE Zakaz SET ID_Voditelya = %s WHERE Nomer_zacaza = %s"
        update_values = (self.driver_id, order_id)

        try:
            cursor.execute(update_query, update_values)
            self.db.commit()
            cursor.close()

            # Обновляем информацию на вкладке "Главная"
            self.refresh_main_tab_info(order_id)

            # Обновляем список доступных заказов
            self.refresh_available_orders()

        except mysql.connector.Error as err:
            print(f"Error updating order: {err}")
        finally:
            cursor.close()

    def refresh_main_tab_info(self, order_id):
        cursor = self.db.cursor()
        query = "SELECT Mesto_otpravlenia, Mesto_naznacheniya, Kommentariy, Stoimost FROM Zakaz WHERE Nomer_zacaza = %s"
        values = (order_id,)
        try:
            cursor.execute(query, values)
            order_info = cursor.fetchone()
            cursor.close()

            # Обновляем информацию на вкладке "Главная"
            self.departure_label.text = order_info[0]
            self.destination_label.text = order_info[1]
            self.comment_label.text = order_info[2]
            self.price_label.text = f"{order_info[3]} рублей"

            # Отображаем номер телефона пассажира
            passenger_phone = self.get_passenger_phone(order_id)
            if passenger_phone:
                self.comment_label.text += f"\nНомер телефона пассажира: {passenger_phone}"

            # Отображаем номер службы поддержки
            support_phone = "Телефон службы поддержки: 88005553535"
            self.comment_label.text += f"\n{support_phone}"

            # Переключаемся на вкладку "Главная"
            self.root.switch_to(self.root.tab_list[1])

        except mysql.connector.Error as err:
            print(f"Error fetching order info: {err}")
        finally:
            cursor.close()

    def get_passenger_phone(self, order_id):
        cursor = self.db.cursor()
        query = "SELECT Klient.telefon " \
                "FROM Zakaz " \
                "JOIN Klient ON Zakaz.ID_Klienta = Klient.ID_Klienta " \
                "WHERE Zakaz.Nomer_zacaza = %s"
        values = (order_id,)
        try:
            cursor.execute(query, values)
            result = cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as err:
            print(f"Error fetching passenger phone: {err}")
        finally:
            cursor.close()

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()

    def register(self, instance):
        if not self.db:
            self.show_popup('Предупреждение',
                            'Отсутствует подключение к интернету.')
            return

        login = self.login_input.text
        password = self.password_input.text
        VU = self.VU.text
        avto = self.avto.text
        phone = self.phone_input.text

        # Проверяем, что все поля заполнены
        if not login or not password or not VU or not avto or not phone:
            self.show_popup('Ошибка', 'Все поля обязательны для заполнения.')
            return

        cursor = self.db.cursor()
        query = "INSERT INTO Voditel (login, parol, udostoverenie, nomer_avto, telefon) VALUES (%s, %s, %s, %s, %s)"
        values = (login, password, VU, avto, phone)

        try:
            cursor.execute(query, values)
            self.db.commit()
            cursor.close()

            self.show_popup('Успех', 'Регистрация успешна. Теперь вы можете войти в систему.')

        except mysql.connector.Error as err:
            print(f"Error in registration: {err}")
            self.show_popup('Ошибка', 'Не удалось зарегистрироваться. \n Пожалуйста, попробуйте еще раз.')
        finally:
            cursor.close()

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

        driver_id = self.authenticate_driver(login, password)

        if not driver_id:
            self.show_popup('Ошибка', 'Неверный логин или пароль.')
            return

        self.driver_id = driver_id
        self.login_tab.disabled = True  # Запрещаем доступ к вкладке входа/регистрации
        self.show_popup('Успешно', 'Вход выполнен.')

        self.switch_to_available_orders_tab()
        self.root.switch_to(self.root.tab_list[0])

        self.refresh_available_orders()

    def switch_to_available_orders_tab(self):
        self.root.switch_to(self.root.tab_list[2])

if __name__ == '__main__':
    DriverApp().run()
