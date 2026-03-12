import os
import random
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.factory import Factory
from gamedata import CUSTOMER_ORDERS, PARTS_ITEMS

current_dir = os.path.dirname(__file__)
Builder.load_file(os.path.join(current_dir, "pcbuilder.kv"), encoding="utf-8")

class MainMenu(Screen):
    has_started = BooleanProperty(False)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.check_save)
    def check_save(self, dt):
        if os.path.exists(os.path.join(current_dir, "savegame.json")):
            self.has_started = True

class MainGame(Screen):
    money = NumericProperty(3000)
    current_day = NumericProperty(1)
    daily_rent = NumericProperty(100)
    customers_today = NumericProperty(1)
    current_customer_idx = NumericProperty(1)
    pc_status = StringProperty("Empty")
    log_message = StringProperty("Welcome! Build PCs to earn money.")
    reputation = NumericProperty(50)
    current_order = StringProperty("")
    current_build_cost = NumericProperty(0)
    budget_remaining = NumericProperty(0)
    active_event_name = StringProperty("Normal")
    
    required_cpu_display = StringProperty(""); required_gpu_display = StringProperty("")
    required_ram_display = StringProperty(""); required_storage_display = StringProperty("")
    installed_cpu = StringProperty("None"); installed_mb = StringProperty("None")
    installed_psu = StringProperty("None"); installed_gpu = StringProperty("None")
    installed_ram = StringProperty("None"); installed_storage = StringProperty("None")
    installed_case = StringProperty("None")
    total_wattage = NumericProperty(50); base_system_watt = 50

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.installed_parts = {k: None for k in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]}
        self.customer_orders = CUSTOMER_ORDERS
        self.items = PARTS_ITEMS
        self.events = [
            {"name": "Normal", "mult": {}},
            {"name": "Crypto Boom", "mult": {"GPU": 1.5}},
            {"name": "Factory Fire", "mult": {"RAM": 1.3, "Storage": 1.3}},
            {"name": "AMD Sale", "mult": {"CPU": 0.8, "MB": 0.8}}
        ]
        self.current_event = self.events[0]
        Clock.schedule_once(self.init_game)

    def init_game(self, dt):
        if not self.load_game(): self.start_new_day(True)
        self.populate_shop(0)

    def get_price(self, item):
        return int(item["price"] * self.current_event["mult"].get(item["type"], 1.0))

    def populate_shop(self, dt, cat="all"):
        self.ids.shop_list.clear_widgets()
        for i in self.items:
            if cat == "all" or i["type"] == cat:
                p = self.get_price(i)
                btn = Factory.PartButton(text=f"{i['name']} - ${p}")
                btn.part = i; btn.bind(on_release=lambda b: self.buy_part(b.part))
                self.ids.shop_list.add_widget(btn)

    def set_category(self, cat):
        self.populate_shop(0, cat)

    def start_new_day(self, first=False):
        if not first:
            self.current_day += 1
            self.money -= self.daily_rent
            self.log_message = f"Day {self.current_day}: Paid ${self.daily_rent} rent."
        self.current_event = random.choice(self.events) if random.random() < 0.2 else self.events[0]
        self.active_event_name = self.current_event["name"]
        self.customers_today = random.randint(1, 3)
        self.current_customer_idx = 1
        self.populate_shop(0); self.generate_order()

    def generate_order(self):
        pool = [o for o in self.customer_orders if self.reputation >= o["min_rep"]]
        self.current_order_specs = random.choice(pool)
        s = self.current_order_specs
        self.current_order = f"{s['name']} (${s['budget']})"
        self.required_cpu_display = f"CPU: {s['required_cpu']}"; self.required_gpu_display = f"GPU: {s['required_gpu']}"
        self.required_ram_display = f"RAM: {s['required_ram']}"; self.required_storage_display = f"Storage: {s['required_storage']}"
        self.budget_remaining = s["budget"]; self.current_build_cost = 0

    def buy_part(self, i):
        p = self.get_price(i)
        if self.money < p: self.log_message = "No money!"; return
        t = i["type"]
        if t=="CPU" and self.installed_parts["MB"] and i["socket"]!=self.installed_parts["MB"]["socket"]: return
        if t=="MB" and self.installed_parts["CPU"] and i["socket"]!=self.installed_parts["CPU"]["socket"]: return
        if t=="RAM" and self.installed_parts["MB"] and i["ram_type"]!=self.installed_parts["MB"]["ram_type"]: return
        old = self.installed_parts[t]
        if old: 
            self.money += self.get_price(old); self.current_build_cost -= self.get_price(old)
            if "watt" in old: self.total_wattage -= old["watt"]
        self.installed_parts[t] = i; self.money -= p; self.current_build_cost += p
        if "watt" in i: self.total_wattage += i["watt"]
        self.budget_remaining = self.current_order_specs["budget"] - self.current_build_cost
        setattr(self, f"installed_{t.lower()}", i["name"])
        self.log_message = f"Installed {i['name']}"; self.update_status()

    def update_status(self):
        full = all(v is not None for v in self.installed_parts.values())
        if full:
            psu = self.installed_parts["PSU"]
            if self.total_wattage <= (psu["watt_limit"] * 0.8): self.pc_status = "Ready to sell!"
            else: self.pc_status = "Power overload!"
        else: self.pc_status = "Incomplete"

    def on_sell(self):
        if self.pc_status != "Ready to sell!": return
        s = self.current_order_specs
        ok = self.installed_cpu == s["required_cpu"] and self.installed_gpu == s["required_gpu"] and \
             self.installed_ram == s["required_ram"] and self.installed_storage == s["required_storage"]
        if ok:
            price = int(self.current_build_cost * (1.5 + s["reward_multiplier"] + (self.reputation-50)*0.01))
            self.money += price; self.reputation = min(100, self.reputation + 2)
            self.log_message = f"Sold for ${price}!"
        else:
            price = int(self.current_build_cost * 1.1)
            self.money += price; self.reputation = max(0, self.reputation - 5)
            self.log_message = f"Mismatched! Sold for ${price}. Rep -5"
        self.finish_customer()

    def skip_day(self):
        for k, v in self.installed_parts.items():
            if v: self.money += self.get_price(v)
        self.reputation = max(0, self.reputation - 5); self.finish_customer()

    def finish_customer(self):
        self.installed_parts = {k: None for k in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]}
        for p in ["cpu","mb","psu","gpu","ram","storage","case"]: setattr(self, f"installed_{p}", "None")
        self.total_wattage = self.base_system_watt; self.current_build_cost = 0; self.update_status()
        if self.current_customer_idx < self.customers_today:
            self.current_customer_idx += 1; self.generate_order()
        else:
            self.start_new_day()
        self.save_game()

    def save_game(self):
        d = {"money": self.money, "day": self.current_day, "rep": self.reputation, "parts": self.installed_parts, 
             "order": self.current_order_specs, "cost": self.current_build_cost, "today": self.customers_today,
             "idx": self.current_customer_idx, "ev": self.active_event_name}
        with open(os.path.join(current_dir, "savegame.json"), "w", encoding="utf-8") as f: json.dump(d, f, indent=4)

    def load_game(self):
        path = os.path.join(current_dir, "savegame.json")
        if not os.path.exists(path): return False
        try:
            with open(path, "r", encoding="utf-8") as f: d = json.load(f)
            self.money = d["money"]; self.current_day = d["day"]; self.reputation = d["rep"]
            self.active_event_name = d["ev"]; self.current_customer_idx = d["idx"]; self.customers_today = d["today"]
            for ev in self.events:
                if ev["name"] == self.active_event_name: self.current_event = ev; break
            self.installed_parts = d["parts"]; self.current_order_specs = d["order"]; self.current_build_cost = d["cost"]
            if self.current_order_specs:
                s = self.current_order_specs
                self.budget_remaining = s["budget"] - self.current_build_cost
                self.current_order = f"{s['name']} (${s['budget']})"
                self.required_cpu_display = f"CPU: {s['required_cpu']}"; self.required_gpu_display = f"GPU: {s['required_gpu']}"
                self.required_ram_display = f"RAM: {s['required_ram']}"; self.required_storage_display = f"Storage: {s['required_storage']}"
            for p in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]:
                setattr(self, f"installed_{p.lower()}", self.installed_parts[p]["name"] if self.installed_parts[p] else "None")
            self.update_status(); return True
        except: return False

    def reset_game(self):
        self.money = 3000; self.current_day = 0; self.reputation = 50
        self.installed_parts = {k: None for k in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]}
        for p in ["cpu","mb","psu","gpu","ram","storage","case"]: setattr(self, f"installed_{p}", "None")
        self.start_new_day(True); self.save_game()

class PCBuilderApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu")); sm.add_widget(MainGame(name="main"))
        return sm
if __name__ == "__main__": PCBuilderApp().run()