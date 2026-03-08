import os
import random
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
    reputation = NumericProperty(50)
    current_order = StringProperty("")
    order_reward = NumericProperty(0)
    current_build_cost = NumericProperty(0)
    budget_remaining = NumericProperty(0)

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
    current_order_specs = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.customer_orders = [
            {
                "name": "Budget Gamer",
                "budget": 1200,
                "required_gpu": "GTX 1650",
                "required_cpu": "Ryzen 5 5600X (AM4)",
                "required_ram": "16GB DDR4",
                "reward_multiplier": 0.4,
            },
            {
                "name": "Streaming Workstation",
                "budget": 2000,
                "required_gpu": "RTX 3060",
                "required_cpu": "Core i7 (LGA1700)",
                "required_ram": "32GB DDR4",
                "reward_multiplier": 0.5,
            },
            {
                "name": "High-End Gaming",
                "budget": 2500,
                "required_gpu": "RTX 4070",
                "required_cpu": "Core i9 (LGA1700)",
                "required_ram": "32GB DDR4",
                "reward_multiplier": 0.6,
            },
            {
                "name": "Office Build",
                "budget": 800,
                "required_gpu": "GTX 1650",
                "required_cpu": "Core i3 (LGA1700)",
                "required_ram": "8GB DDR4",
                "reward_multiplier": 0.35,
            },
            {
                "name": "Affordable Gaming",
                "budget": 1500,
                "required_gpu": "RTX 3060",
                "required_cpu": "Ryzen 7 5800X (AM4)",
                "required_ram": "16GB DDR4",
                "reward_multiplier": 0.45,
            },
        ]
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
        Clock.schedule_once(self.generate_new_order)

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

    def generate_new_order(self, dt=0):
        self.current_order_specs = random.choice(self.customer_orders)
        order_name = self.current_order_specs["name"]
        budget = self.current_order_specs["budget"]
        required_cpu = self.current_order_specs["required_cpu"]
        required_gpu = self.current_order_specs["required_gpu"]
        required_ram = self.current_order_specs["required_ram"]
        self.current_order = f"{order_name} - Budget: ${budget}\nRequired CPU: {required_cpu}\nRequired GPU: {required_gpu}\nRequired RAM: {required_ram}"
        self.budget_remaining = budget
        self.current_build_cost = 0
        self.log_message = f"New order: {order_name}"

    def check_order_requirements(self):
        if not self.current_order_specs:
            return False, 0

        specs = self.current_order_specs
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

        # Check if within budget
        if cost > specs["budget"]:
            return False, 0

        # Check component requirements
        cpu_ok = self.installed_cpu == specs["required_cpu"]
        gpu_ok = self.installed_gpu == specs["required_gpu"]
        ram_ok = self.installed_ram == specs["required_ram"]

        if cpu_ok and gpu_ok and ram_ok:
            return True, specs["reward_multiplier"]

        return False, 0

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

            # Check if order requirements are met
            order_met, multiplier = self.check_order_requirements()

            if order_met:
                # Apply reputation multiplier to profit
                base_profit = cost * 0.5
                reputation_bonus = (self.reputation - 50) * 0.01
                sell_price = int(cost * (1.5 + multiplier + reputation_bonus))
                profit = sell_price - cost
                self.money += sell_price
                self.reputation = min(100, self.reputation + 5)
                self.log_message = (
                    f"✓ Order fulfilled! Sold for ${sell_price}! Profit: ${profit}"
                )
            else:
                # Sell without meeting order
                reputation_penalty = 1 - (self.reputation - 50) * 0.01
                sell_price = int(cost * (1.3 * reputation_penalty))
                profit = sell_price - cost
                self.money += sell_price
                self.reputation = max(0, self.reputation - 2)
                self.log_message = f"Order not fulfilled. Sold for ${sell_price}. Rep: {self.reputation}/100"

            # Clear current build
            self.installed_cpu = "None"
            self.installed_mb = "None"
            self.installed_psu = "None"
            self.installed_gpu = "None"
            self.installed_ram = "None"
            self.cpu_socket = ""
            self.mb_socket = ""
            self.total_wattage = 0
            self.update_status()

            # Generate next order
            self.generate_new_order()
        else:
            self.log_message = "PC not ready to sell!"

    def buy_part(self, item):
        if self.money >= item["price"]:
            self.money -= item["price"]
            if item["type"] == "CPU":
                if self.mb_socket and self.mb_socket != item["socket"]:
                    self.log_message = "Socket mismatch!"
                    self.money += item["price"]
                    return
                # Refund old CPU if exists
                if self.installed_cpu != "None":
                    for i in self.items:
                        if i["name"] == self.installed_cpu:
                            self.money += i["price"]
                            self.total_wattage -= i["watt"]
                            self.current_build_cost -= i["price"]
                            break
                self.installed_cpu = item["name"]
                self.cpu_socket = item["socket"]
                self.total_wattage += item["watt"]
                self.current_build_cost += item["price"]
                self.budget_remaining = (
                    self.current_order_specs["budget"] - self.current_build_cost
                    if self.current_order_specs
                    else 0
                )
            elif item["type"] == "MB":
                if self.cpu_socket and self.cpu_socket != item["socket"]:
                    self.log_message = "Socket mismatch!"
                    self.money += item["price"]
                    return
                # Refund old MB if exists
                if self.installed_mb != "None":
                    for i in self.items:
                        if i["name"] == self.installed_mb:
                            self.money += i["price"]
                            self.current_build_cost -= i["price"]
                            break
                self.installed_mb = item["name"]
                self.mb_socket = item["socket"]
                self.current_build_cost += item["price"]
                self.budget_remaining = (
                    self.current_order_specs["budget"] - self.current_build_cost
                    if self.current_order_specs
                    else 0
                )
            elif item["type"] == "PSU":
                # Refund old PSU if exists
                if self.installed_psu != "None":
                    for i in self.items:
                        if i["name"] == self.installed_psu:
                            self.money += i["price"]
                            self.current_build_cost -= i["price"]
                            break
                self.installed_psu = item["name"]
                self.psu_limit = item["watt_limit"]
                self.current_build_cost += item["price"]
                self.budget_remaining = (
                    self.current_order_specs["budget"] - self.current_build_cost
                    if self.current_order_specs
                    else 0
                )
            elif item["type"] == "GPU":
                # Refund old GPU if exists
                if self.installed_gpu != "None":
                    for i in self.items:
                        if i["name"] == self.installed_gpu:
                            self.money += i["price"]
                            self.total_wattage -= i["watt"]
                            self.current_build_cost -= i["price"]
                            break
                self.installed_gpu = item["name"]
                self.total_wattage += item["watt"]
                self.current_build_cost += item["price"]
                self.budget_remaining = (
                    self.current_order_specs["budget"] - self.current_build_cost
                    if self.current_order_specs
                    else 0
                )
            elif item["type"] == "RAM":
                # Refund old RAM if exists
                if self.installed_ram != "None":
                    for i in self.items:
                        if i["name"] == self.installed_ram:
                            self.money += i["price"]
                            self.current_build_cost -= i["price"]
                            break
                self.installed_ram = item["name"]
                self.current_build_cost += item["price"]
                self.budget_remaining = (
                    self.current_order_specs["budget"] - self.current_build_cost
                    if self.current_order_specs
                    else 0
                )
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
        self.reputation = 50
        self.current_build_cost = 0
        self.budget_remaining = 0
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
        self.generate_new_order()


class PCBuilderApp(App):
    def build(self):
        self.title = "PC Builder Tycoon"
        sm = ScreenManager()
        sm.add_widget(MainGame(name="main"))
        return sm


if __name__ == "__main__":
    PCBuilderApp().run()
