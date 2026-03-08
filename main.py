import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock


current_dir = os.path.dirname(__file__)
Builder.load_file(os.path.join(current_dir, "pcbuilder.kv"))


class MainGame(Screen):
    money = NumericProperty(1500)
    pc_status = StringProperty("Empty")
    log_message = StringProperty("Welcome to the workshop!")

    installed_cpu = StringProperty("None")
    installed_mb = StringProperty("None")
    installed_psu = StringProperty("None")

    cpu_socket = ""
    mb_socket = ""
    total_wattage = NumericProperty(0)
    psu_limit = 0
    current_value = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.populate_shop)

    def populate_shop(self, dt):
        items = [
            {
                "name": "Core i3 (LGA1700)",
                "price": 300,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 65,
            },
            {
                "name": "Core i5 (LGA1700)",
                "price": 500,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 95,
            },
            {
                "name": "Core i7 (LGA1700)",
                "price": 800,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 125,
            },
            {
                "name": "Core i9 (LGA1700)",
                "price": 1000,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 150,
            },
            {
                "name": "Ryzen 5 5600X (AM4)",
                "price": 200,
                "type": "CPU",
                "socket": "AM4",
                "watt": 65,
            },
            {
                "name": "Ryzen 7 5800X (AM4)",
                "price": 400,
                "type": "CPU",
                "socket": "AM4",
                "watt": 105,
            },
            {
                "name": "Ryzen 9 5900X (AM4)",
                "price": 600,
                "type": "CPU",
                "socket": "AM4",
                "watt": 105,
            },
            {
                "name": "B660 Motherboard (LGA1700)",
                "price": 150,
                "type": "MB",
                "socket": "LGA1700",
            },
            {
                "name": "Z690 Motherboard (LGA1700)",
                "price": 250,
                "type": "MB",
                "socket": "LGA1700",
            },
            {
                "name": "H610 Motherboard (LGA1700)",
                "price": 100,
                "type": "MB",
                "socket": "LGA1700",
            },
            {
                "name": "A520 Motherboard (AM4)",
                "price": 80,
                "type": "MB",
                "socket": "AM4",
            },
            {
                "name": "B450 Motherboard (AM4)",
                "price": 100,
                "type": "MB",
                "socket": "AM4",
            },
            {
                "name": "X570 Motherboard (AM4)",
                "price": 200,
                "type": "MB",
                "socket": "AM4",
            },
            {
                "name": "500W PSU",
                "price": 50,
                "type": "PSU",
                "watt_limit": 500,
            },
            {
                "name": "750W PSU",
                "price": 80,
                "type": "PSU",
                "watt_limit": 750,
            },
        ]


class PCBuilderApp(App):
    def build(self):
        self.title = "PC Builder Tycoon"
        sm = ScreenManager()
        sm.add_widget(MainGame(name="main"))
        return sm


if __name__ == "__main__":
    PCBuilderApp().run()
