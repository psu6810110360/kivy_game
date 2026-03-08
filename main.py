import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.factory import Factory


current_dir = os.path.dirname(__file__)
Builder.load_file(os.path.join(current_dir, "pcbuilder.kv"))


class MainGame(Screen):
    money = NumericProperty(3000)
    pc_status = StringProperty("Empty")
    log_message = StringProperty("Welcome to the workshop!")

    installed_cpu = StringProperty("None")
    installed_mb = StringProperty("None")
    installed_psu = StringProperty("None")
    installed_gpu = StringProperty("None")
    installed_ram = StringProperty("None")

    cpu_socket = ""
    mb_socket = ""
    total_wattage = NumericProperty(0)
    psu_limit = 0
    current_value = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = [
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
                "name": "GTX 1650",
                "price": 200,
                "type": "GPU",
                "watt": 75,
            },
            {
                "name": "RTX 3060",
                "price": 400,
                "type": "GPU",
                "watt": 170,
            },
            {
                "name": "RTX 4070",
                "price": 600,
                "type": "GPU",
                "watt": 200,
            },
            {
                "name": "8GB DDR4",
                "price": 50,
                "type": "RAM",
            },
            {
                "name": "16GB DDR4",
                "price": 80,
                "type": "RAM",
            },
            {
                "name": "32GB DDR4",
                "price": 150,
                "type": "RAM",
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
        Clock.schedule_once(self.populate_shop)

    def populate_shop(self, dt, category="all"):
        self.ids.shop_list.clear_widgets()
        for item in self.items:
            if category == "all" or item["type"] == category:
                btn = Factory.PartButton(text=f"{item['name']} - ${item['price']}")
                btn.part = item
                btn.bind(on_release=lambda btn: self.buy_part(btn.part))
                self.ids.shop_list.add_widget(btn)

    def set_category(self, cat):
        self.populate_shop(0, cat)

    def on_sell_pc(self):
        if self.pc_status == "Ready to sell!":
            cost = 0
            for item in self.items:
                if item["name"] in [
                    self.installed_cpu,
                    self.installed_mb,
                    self.installed_psu,
                    self.installed_gpu,
                    self.installed_ram,
                ]:
                    cost += item["price"]
            sell_price = int(cost * 1.5)
            self.money += sell_price
            profit = sell_price - cost
            self.log_message = f"PC sold for ${sell_price}! Profit: ${profit}"
            self.installed_cpu = "None"
            self.installed_mb = "None"
            self.installed_psu = "None"
            self.installed_gpu = "None"
            self.installed_ram = "None"
            self.cpu_socket = ""
            self.mb_socket = ""
            self.total_wattage = 0
            self.update_status()
        else:
            self.log_message = "PC not ready to sell!"

    def buy_part(self, item):
        if self.money >= item["price"]:
            self.money -= item["price"]
            if item["type"] == "CPU":
                if self.mb_socket and self.mb_socket != item["socket"]:
                    self.log_message = "Socket mismatch!"
                    return
                self.installed_cpu = item["name"]
                self.cpu_socket = item["socket"]
                self.total_wattage += item["watt"]
            elif item["type"] == "MB":
                if self.cpu_socket and self.cpu_socket != item["socket"]:
                    self.log_message = "Socket mismatch!"
                    return
                self.installed_mb = item["name"]
                self.mb_socket = item["socket"]
            elif item["type"] == "PSU":
                self.installed_psu = item["name"]
                self.psu_limit = item["watt_limit"]
            elif item["type"] == "GPU":
                self.installed_gpu = item["name"]
                self.total_wattage += item["watt"]
            elif item["type"] == "RAM":
                self.installed_ram = item["name"]
            self.update_status()
        else:
            self.log_message = "Not enough money!"

    def update_status(self):
        if (
            self.installed_cpu != "None"
            and self.installed_mb != "None"
            and self.installed_psu != "None"
            and self.installed_gpu != "None"
            and self.installed_ram != "None"
        ):
            if self.total_wattage <= self.psu_limit:
                self.pc_status = "Ready to sell!"
            else:
                self.pc_status = "Power overload!"
        else:
            self.pc_status = "Incomplete"

    def reset_game(self):
        self.money = 3000
        self.installed_cpu = "None"
        self.installed_mb = "None"
        self.installed_psu = "None"
        self.installed_gpu = "None"
        self.installed_ram = "None"
        self.cpu_socket = ""
        self.mb_socket = ""
        self.total_wattage = 0
        self.psu_limit = 0
        self.pc_status = "Empty"
        self.log_message = "Game reset!"
        self.ids.shop_list.clear_widgets()
        self.populate_shop(0)


class PCBuilderApp(App):
    def build(self):
        self.title = "PC Builder Tycoon"
        sm = ScreenManager()
        sm.add_widget(MainGame(name="main"))
        return sm


if __name__ == "__main__":
    PCBuilderApp().run()
