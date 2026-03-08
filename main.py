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

    required_cpu_display = StringProperty("")
    required_gpu_display = StringProperty("")
    required_ram_display = StringProperty("")

    installed_cpu = StringProperty("None")
    installed_mb = StringProperty("None")
    installed_psu = StringProperty("None")
    installed_gpu = StringProperty("None")
    installed_ram = StringProperty("None")

    total_wattage = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.installed_parts = {
            "CPU": None,
            "MB": None,
            "GPU": None,
            "RAM": None,
            "PSU": None,
        }
        self.current_order_specs = None

        self.customer_orders = [
            {
                "name": "Office Build",
                "budget": 600,
                "required_gpu": "GTX 1650",
                "required_cpu": "Core i3-12100 (LGA1700)",
                "required_ram": "8GB DDR4",
                "reward_multiplier": 0.3,
                "min_rep": 0,
            },
            {
                "name": "Budget Gamer",
                "budget": 1000,
                "required_gpu": "RX 6600",
                "required_cpu": "Ryzen 5 5500 (AM4)",
                "required_ram": "16GB DDR4",
                "reward_multiplier": 0.4,
                "min_rep": 0,
            },
            {
                "name": "Affordable Gaming",
                "budget": 1400,
                "required_gpu": "RTX 3060",
                "required_cpu": "Ryzen 5 5600X (AM4)",
                "required_ram": "16GB DDR4",
                "reward_multiplier": 0.45,
                "min_rep": 20,
            },
            {
                "name": "Streaming Workstation",
                "budget": 2000,
                "required_gpu": "RTX 4060 Ti",
                "required_cpu": "Core i5-13400 (LGA1700)",
                "required_ram": "32GB DDR4",
                "reward_multiplier": 0.5,
                "min_rep": 40,
            },
            {
                "name": "High-End Gaming",
                "budget": 2800,
                "required_gpu": "RTX 4070 Super",
                "required_cpu": "Ryzen 7 7800X3D (AM5)",
                "required_ram": "32GB DDR5",
                "reward_multiplier": 0.6,
                "min_rep": 60,
            },
            {
                "name": "Enthusiast Build",
                "budget": 4500,
                "required_gpu": "RTX 4090",
                "required_cpu": "Core i9-14900K (LGA1700)",
                "required_ram": "64GB DDR5",
                "reward_multiplier": 0.8,
                "min_rep": 80,
            },
        ]

        self.items = [
            {
                "name": "Core i3-12100 (LGA1700)",
                "price": 120,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 60,
            },
            {
                "name": "Core i5-13400 (LGA1700)",
                "price": 230,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 65,
            },
            {
                "name": "Core i7-14700K (LGA1700)",
                "price": 400,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 125,
            },
            {
                "name": "Core i9-14900K (LGA1700)",
                "price": 580,
                "type": "CPU",
                "socket": "LGA1700",
                "watt": 150,
            },
            {
                "name": "Ryzen 5 5500 (AM4)",
                "price": 90,
                "type": "CPU",
                "socket": "AM4",
                "watt": 65,
            },
            {
                "name": "Ryzen 5 5600X (AM4)",
                "price": 160,
                "type": "CPU",
                "socket": "AM4",
                "watt": 65,
            },
            {
                "name": "Ryzen 7 5800X3D (AM4)",
                "price": 320,
                "type": "CPU",
                "socket": "AM4",
                "watt": 105,
            },
            {
                "name": "Ryzen 5 7600 (AM5)",
                "price": 220,
                "type": "CPU",
                "socket": "AM5",
                "watt": 65,
            },
            {
                "name": "Ryzen 7 7800X3D (AM5)",
                "price": 450,
                "type": "CPU",
                "socket": "AM5",
                "watt": 120,
            },
            {
                "name": "Ryzen 9 7950X (AM5)",
                "price": 550,
                "type": "CPU",
                "socket": "AM5",
                "watt": 170,
            },
            {"name": "H610M (LGA1700)", "price": 80, "type": "MB", "socket": "LGA1700"},
            {
                "name": "B760 Pro (LGA1700)",
                "price": 140,
                "type": "MB",
                "socket": "LGA1700",
            },
            {
                "name": "Z790 Elite (LGA1700)",
                "price": 250,
                "type": "MB",
                "socket": "LGA1700",
            },
            {"name": "A520M (AM4)", "price": 70, "type": "MB", "socket": "AM4"},
            {
                "name": "B550 Steel Legend (AM4)",
                "price": 130,
                "type": "MB",
                "socket": "AM4",
            },
            {"name": "B650 Gaming (AM5)", "price": 180, "type": "MB", "socket": "AM5"},
            {"name": "X670E Taichi (AM5)", "price": 400, "type": "MB", "socket": "AM5"},
            {"name": "GTX 1650", "price": 150, "type": "GPU", "watt": 75},
            {"name": "RTX 3060", "price": 290, "type": "GPU", "watt": 170},
            {"name": "RTX 4060 Ti", "price": 380, "type": "GPU", "watt": 160},
            {"name": "RTX 4070 Super", "price": 600, "type": "GPU", "watt": 220},
            {"name": "RTX 4080 Super", "price": 1000, "type": "GPU", "watt": 320},
            {"name": "RTX 4090", "price": 1800, "type": "GPU", "watt": 450},
            {"name": "RX 6600", "price": 200, "type": "GPU", "watt": 130},
            {"name": "RX 7800 XT", "price": 500, "type": "GPU", "watt": 260},
            {"name": "8GB DDR4", "price": 40, "type": "RAM"},
            {"name": "16GB DDR4", "price": 70, "type": "RAM"},
            {"name": "32GB DDR4", "price": 130, "type": "RAM"},
            {"name": "32GB DDR5", "price": 180, "type": "RAM"},
            {"name": "64GB DDR5", "price": 350, "type": "RAM"},
            {"name": "500W PSU", "price": 50, "type": "PSU", "watt_limit": 500},
            {"name": "750W PSU", "price": 90, "type": "PSU", "watt_limit": 750},
            {"name": "850W PSU", "price": 130, "type": "PSU", "watt_limit": 850},
            {"name": "1000W PSU", "price": 200, "type": "PSU", "watt_limit": 1000},
            {"name": "1200W PSU", "price": 280, "type": "PSU", "watt_limit": 1200},
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
        available_orders = [
            o for o in self.customer_orders if self.reputation >= o["min_rep"]
        ]
        if not available_orders:
            available_orders = [self.customer_orders[0]]
        self.current_order_specs = random.choice(available_orders)

        self.current_order = f"{self.current_order_specs['name']} - Budget: ${self.current_order_specs['budget']}"
        self.required_cpu_display = f"CPU: {self.current_order_specs['required_cpu']}"
        self.required_gpu_display = f"GPU: {self.current_order_specs['required_gpu']}"
        self.required_ram_display = f"RAM: {self.current_order_specs['required_ram']}"
        self.budget_remaining = self.current_order_specs["budget"]
        self.current_build_cost = 0
        self.log_message = f"New order: {self.current_order_specs['name']}"

    def check_order_requirements(self):
        if not self.current_order_specs:
            return False, 0

        cost = self.current_build_cost
        if cost > self.current_order_specs["budget"]:
            return False, 0

        cpu_ok = self.installed_cpu == self.current_order_specs["required_cpu"]
        gpu_ok = self.installed_gpu == self.current_order_specs["required_gpu"]
        ram_ok = self.installed_ram == self.current_order_specs["required_ram"]

        if cpu_ok and gpu_ok and ram_ok:
            return True, self.current_order_specs["reward_multiplier"]

        return False, 0

    def on_sell_pc(self):
        if self.pc_status == "Ready to sell!":
            cost = self.current_build_cost
            order_met, multiplier = self.check_order_requirements()

            if order_met:
                base_profit = cost * 0.5
                reputation_bonus = (self.reputation - 50) * 0.01
                sell_price = int(cost * (1.5 + multiplier + reputation_bonus))
                profit = sell_price - cost
                self.money += sell_price
                self.reputation = min(100, self.reputation + 5)
                self.log_message = (
                    f"Order fulfilled! Sold for ${sell_price}! Profit: ${profit}"
                )
            else:
                reputation_penalty = 1 - (self.reputation - 50) * 0.01
                sell_price = int(cost * (1.3 * reputation_penalty))
                self.money += sell_price
                self.reputation = max(0, self.reputation - 2)
                self.log_message = f"Order not fulfilled. Sold for ${sell_price}. Rep: {self.reputation}/100"

            self.installed_parts = {
                "CPU": None,
                "MB": None,
                "GPU": None,
                "RAM": None,
                "PSU": None,
            }
            self.installed_cpu = "None"
            self.installed_mb = "None"
            self.installed_psu = "None"
            self.installed_gpu = "None"
            self.installed_ram = "None"
            self.total_wattage = 0
            self.current_build_cost = 0

            self.update_status()
            self.generate_new_order()
        else:
            self.log_message = "PC not ready to sell!"

    def buy_part(self, item):
        part_type = item["type"]

        if self.money < item["price"]:
            self.log_message = "Not enough money!"
            return

        if part_type == "CPU" and self.installed_parts["MB"]:
            if item["socket"] != self.installed_parts["MB"]["socket"]:
                self.log_message = "Socket mismatch with Motherboard!"
                return
        if part_type == "MB" and self.installed_parts["CPU"]:
            if item["socket"] != self.installed_parts["CPU"]["socket"]:
                self.log_message = "Socket mismatch with CPU!"
                return

        old_part = self.installed_parts[part_type]
        if old_part:
            self.money += old_part["price"]
            self.current_build_cost -= old_part["price"]
            if "watt" in old_part:
                self.total_wattage -= old_part["watt"]

        self.installed_parts[part_type] = item
        self.money -= item["price"]
        self.current_build_cost += item["price"]

        if self.current_order_specs:
            self.budget_remaining = (
                self.current_order_specs["budget"] - self.current_build_cost
            )

        if "watt" in item:
            self.total_wattage += item["watt"]

        if part_type == "CPU":
            self.installed_cpu = item["name"]
        elif part_type == "MB":
            self.installed_mb = item["name"]
        elif part_type == "GPU":
            self.installed_gpu = item["name"]
        elif part_type == "RAM":
            self.installed_ram = item["name"]
        elif part_type == "PSU":
            self.installed_psu = item["name"]

        self.update_status()

    def update_status(self):
        is_complete = all(v is not None for v in self.installed_parts.values())

        if is_complete:
            psu = self.installed_parts.get("PSU")
            psu_limit = psu["watt_limit"] if psu else 0

            if self.total_wattage <= psu_limit:
                self.pc_status = "Ready to sell!"
            else:
                self.pc_status = "Power overload!"
        else:
            self.pc_status = "Incomplete"

    def reset_game(self):
        self.money = 3000
        self.reputation = 50
        self.current_build_cost = 0
        self.total_wattage = 0
        self.installed_parts = {
            "CPU": None,
            "MB": None,
            "GPU": None,
            "RAM": None,
            "PSU": None,
        }
        self.installed_cpu = "None"
        self.installed_mb = "None"
        self.installed_psu = "None"
        self.installed_gpu = "None"
        self.installed_ram = "None"
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
