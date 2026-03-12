import os
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.factory import Factory
from gamedata import CUSTOMER_ORDERS, PARTS_ITEMS

current_dir = os.path.dirname(__file__)
Builder.load_file(os.path.join(current_dir, "pcbuilder.kv"))


class MainMenu(Screen):
    pass


class MainGame(Screen):
    money = NumericProperty(3000)
    current_day = NumericProperty(1)
    daily_rent = NumericProperty(100)
    pc_status = StringProperty("Empty")
    log_message = StringProperty("Welcome to the workshop! Don't go bankrupt!")
    reputation = NumericProperty(50)
    current_order = StringProperty("")
    order_reward = NumericProperty(0)
    current_build_cost = NumericProperty(0)
    budget_remaining = NumericProperty(0)

    required_cpu_display = StringProperty("")
    required_gpu_display = StringProperty("")
    required_ram_display = StringProperty("")
    required_storage_display = StringProperty("")

    installed_cpu = StringProperty("None")
    installed_mb = StringProperty("None")
    installed_psu = StringProperty("None")
    installed_gpu = StringProperty("None")
    installed_ram = StringProperty("None")
    installed_storage = StringProperty("None")
    installed_case = StringProperty("None")

    total_wattage = NumericProperty(50)
    base_system_watt = 50

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.installed_parts = {
            "CPU": None,
            "MB": None,
            "GPU": None,
            "RAM": None,
            "PSU": None,
            "Storage": None,
            "Case": None,
        }
        self.current_order_specs = None
        self.customer_orders = CUSTOMER_ORDERS
        self.items = PARTS_ITEMS

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
        self.required_storage_display = (
            f"Storage: {self.current_order_specs['required_storage']}"
        )
        self.budget_remaining = self.current_order_specs["budget"]
        self.current_build_cost = 0
        self.log_message = (
            f"Day {self.current_day} | New order: {self.current_order_specs['name']}"
        )

    def check_order_requirements(self):
        if not self.current_order_specs:
            return False, 0

        cost = self.current_build_cost
        if cost > self.current_order_specs["budget"]:
            return False, 0

        cpu_ok = self.installed_cpu == self.current_order_specs["required_cpu"]
        gpu_ok = self.installed_gpu == self.current_order_specs["required_gpu"]
        ram_ok = self.installed_ram == self.current_order_specs["required_ram"]
        storage_ok = (
            self.installed_storage == self.current_order_specs["required_storage"]
        )

        if cpu_ok and gpu_ok and ram_ok and storage_ok:
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
                log_txt = f"Sold for ${sell_price}! Profit: ${profit}"
            else:
                reputation_penalty = 1 - (self.reputation - 50) * 0.01
                sell_price = int(cost * (1.3 * reputation_penalty))
                self.money += sell_price
                self.reputation = max(0, self.reputation - 2)
                log_txt = f"Failed order. Sold: ${sell_price}. Rep: {self.reputation}"

            self.current_day += 1
            self.money -= self.daily_rent

            if self.money < 0:
                self.log_message = "BANKRUPT! You are out of money. Please Reset Game."
            else:
                self.log_message = f"{log_txt} | Rent Paid: ${self.daily_rent}"

            self.installed_parts = {
                "CPU": None,
                "MB": None,
                "GPU": None,
                "RAM": None,
                "PSU": None,
                "Storage": None,
                "Case": None,
            }
            self.installed_cpu = "None"
            self.installed_mb = "None"
            self.installed_psu = "None"
            self.installed_gpu = "None"
            self.installed_ram = "None"
            self.installed_storage = "None"
            self.installed_case = "None"
            self.total_wattage = self.base_system_watt
            self.current_build_cost = 0

            self.update_status()
            if self.money >= 0:
                self.generate_new_order()
        else:
            self.log_message = "PC not ready to sell!"

    def skip_day(self):
        if self.money < 0:
            self.log_message = "BANKRUPT! You cannot skip. Reset Game."
            return

        for key, item in self.installed_parts.items():
            if item:
                self.money += item["price"]

        self.current_day += 1
        self.money -= self.daily_rent
        self.reputation = max(0, self.reputation - 5)

        if self.money < 0:
            self.log_message = f"Order skipped. BANKRUPT! Rent Paid: ${self.daily_rent}"
        else:
            self.log_message = f"Order skipped. Day {self.current_day}. Rent paid: ${self.daily_rent}. Rep -5"

        self.installed_parts = {
            "CPU": None,
            "MB": None,
            "GPU": None,
            "RAM": None,
            "PSU": None,
            "Storage": None,
            "Case": None,
        }
        self.installed_cpu = "None"
        self.installed_mb = "None"
        self.installed_psu = "None"
        self.installed_gpu = "None"
        self.installed_ram = "None"
        self.installed_storage = "None"
        self.installed_case = "None"
        self.total_wattage = self.base_system_watt
        self.current_build_cost = 0

        self.update_status()
        if self.money >= 0:
            self.generate_new_order()

    def buy_part(self, item):
        if self.money < 0:
            return

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

        if part_type == "RAM" and self.installed_parts["MB"]:
            if item["ram_type"] != self.installed_parts["MB"]["ram_type"]:
                self.log_message = (
                    f"RAM mismatch! Needs {self.installed_parts['MB']['ram_type']}."
                )
                return
        if part_type == "MB" and self.installed_parts["RAM"]:
            if item["ram_type"] != self.installed_parts["RAM"]["ram_type"]:
                self.log_message = (
                    f"MB mismatch! RAM is {self.installed_parts['RAM']['ram_type']}."
                )
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
        elif part_type == "Storage":
            self.installed_storage = item["name"]
        elif part_type == "Case":
            self.installed_case = item["name"]

        self.update_status()

    def update_status(self):
        is_complete = all(v is not None for v in self.installed_parts.values())

        if is_complete:
            psu = self.installed_parts.get("PSU")
            psu_limit = psu["watt_limit"] if psu else 0
            safe_psu_limit = psu_limit * 0.8

            if self.total_wattage <= safe_psu_limit:
                self.pc_status = "Ready to sell!"
            else:
                self.pc_status = "Power overload!"
        else:
            self.pc_status = "Incomplete"

    def reset_game(self):
        self.money = 3000
        self.current_day = 1
        self.reputation = 50
        self.current_build_cost = 0
        self.total_wattage = self.base_system_watt
        self.installed_parts = {
            "CPU": None,
            "MB": None,
            "GPU": None,
            "RAM": None,
            "PSU": None,
            "Storage": None,
            "Case": None,
        }
        self.installed_cpu = "None"
        self.installed_mb = "None"
        self.installed_psu = "None"
        self.installed_gpu = "None"
        self.installed_ram = "None"
        self.installed_storage = "None"
        self.installed_case = "None"
        self.pc_status = "Empty"
        self.log_message = "Game reset! Good luck!"

        self.ids.shop_list.clear_widgets()
        self.populate_shop(0)
        self.generate_new_order()


class PCBuilderApp(App):
    def build(self):
        self.title = "PC Builder Tycoon"
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(MainGame(name="main"))
        return sm


if __name__ == "__main__":
    PCBuilderApp().run()
