import os
import random
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.core.audio import SoundLoader
from gamedata import CUSTOMER_ORDERS, PARTS_ITEMS
from kivy.core.window import Window

current_dir = os.path.dirname(__file__)
Builder.load_file(os.path.join(current_dir, "pcbuilder.kv"), encoding="utf-8")

class MainMenu(Screen):
    has_started = BooleanProperty(False)
    def on_enter(self):
        if os.path.exists(os.path.join(current_dir, "savegame.json")):
            self.has_started = True
    
    def play_sfx(self):
        sfx = SoundLoader.load('click.wav')
        if sfx:
            sfx.volume = App.get_running_app().sfx_volume
            sfx.play()

class SettingsScreen(Screen):
    def play_sfx(self):
        sfx = SoundLoader.load('click.wav')
        if sfx:
            sfx.volume = App.get_running_app().sfx_volume
            sfx.play()

    def toggle_fullscreen(self):
        self.play_sfx()
        if Window.fullscreen == False:
            Window.fullscreen = 'auto'
        else:
            Window.fullscreen = False

class MainGame(Screen):
    is_bankrupt = BooleanProperty(False)
    is_winner = BooleanProperty(False) 
    money = NumericProperty(3000)
    current_day = NumericProperty(1)
    daily_rent = NumericProperty(100)
    reputation = NumericProperty(50)
    pc_status = StringProperty("Empty")
    log_message = StringProperty("Neon Workshop Active.")
    current_order = StringProperty("")
    current_build_cost = NumericProperty(0)
    budget_remaining = NumericProperty(0)
    customers_today = NumericProperty(1)
    daily_event = StringProperty("Normal Day")
    event_color = ListProperty([0, 1, 1, 1])
    power_bg_color = ListProperty([0.1, 0.1, 0.15, 0.9])
    log_color = ListProperty([0, 0.4, 0.8, 0.5])
    
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
        self.installed_parts = {k: None for k in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]}
        self.customer_orders = CUSTOMER_ORDERS
        self.items = PARTS_ITEMS
        Clock.schedule_once(self.init_game)

    def init_game(self, dt):
        if not self.load_game(): 
            self.generate_new_order()
        self.populate_shop(0)

    def play_sfx(self):
        sfx = SoundLoader.load('click.wav')
        if sfx:
            sfx.volume = App.get_running_app().sfx_volume
            sfx.play()
    
    def play_error_sfx(self):
        sfx = SoundLoader.load('error.wav')
        if sfx:
            sfx.volume = App.get_running_app().sfx_volume
            sfx.play()

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

    def generate_new_order(self):
        available = [o for o in self.customer_orders if self.reputation >= o["min_rep"]]
        self.current_order_specs = random.choice(available)
        s = self.current_order_specs
        self.current_order = f"{s['name']} (${s['budget']})"
        self.required_cpu_display = f"CPU: {s['required_cpu']}"
        self.required_gpu_display = f"GPU: {s['required_gpu']}"
        self.required_ram_display = f"RAM: {s['required_ram']}"
        self.required_storage_display = f"Storage: {s['required_storage']}"
        self.budget_remaining = s["budget"]
        self.current_build_cost = 0

    def buy_part(self, item):
        if self.is_bankrupt: return

        part_type = item["type"]
        if self.money < item["price"]:
            self.log_message = "NOT ENOUGH CASH!"
            self.log_color = [0.9, 0.1, 0.1, 0.8]
            self.play_error_sfx()
            return
        
        if part_type == "CPU" and self.installed_parts["MB"] and item["socket"] != self.installed_parts["MB"]["socket"]:
            self.log_message = "SOCKET MISMATCH!"
            self.log_color = [0.9, 0.1, 0.1, 0.8]
            self.play_error_sfx()
            return
            
        if part_type == "MB" and self.installed_parts["CPU"] and item["socket"] != self.installed_parts["CPU"]["socket"]:
            self.log_message = "SOCKET MISMATCH!"
            self.log_color = [0.9, 0.1, 0.1, 0.8]
            self.play_error_sfx()
            return
        
        if part_type == "RAM" and self.installed_parts["MB"]:
            if item.get("ram_type") != self.installed_parts["MB"].get("ram_type"):
                self.log_message = f"RAM MISMATCH! Need {self.installed_parts['MB'].get('ram_type')}"
                self.log_color = [0.9, 0.1, 0.1, 0.8]
                self.play_error_sfx()
                return
                
        if part_type == "MB" and self.installed_parts["RAM"]:
            if item.get("ram_type") != self.installed_parts["RAM"].get("ram_type"):
                self.log_message = "RAM MISMATCH! Remove RAM first."
                self.log_color = [0.9, 0.1, 0.1, 0.8]
                self.play_error_sfx()
                return

        self.play_sfx()

        old = self.installed_parts[part_type]
        if old:
            self.money += old["price"]; self.current_build_cost -= old["price"]
            if "watt" in old: self.total_wattage -= old["watt"]

        self.installed_parts[part_type] = item
        self.money -= item["price"]; self.current_build_cost += item["price"]
        if "watt" in item: self.total_wattage += item["watt"]
        
        self.budget_remaining = self.current_order_specs["budget"] - self.current_build_cost
        setattr(self, f"installed_{part_type.lower()}", item["name"])
        
        self.log_message = f"Installed {item['name']}"
        self.log_color = [0, 0.4, 0.8, 0.5] 
        self.update_status()

    def update_status(self):
        is_complete = all(v is not None for v in self.installed_parts.values())
        if is_complete:
            psu = self.installed_parts["PSU"]
            if self.total_wattage <= (psu["watt_limit"] * 0.8): 
                self.pc_status = "Ready to sell!"
                self.power_bg_color = [0.1, 0.4, 0.2, 0.9]
            else: 
                self.pc_status = "Power overload!"
                self.power_bg_color = [0.8, 0.1, 0.1, 0.9]
        else: 
            self.pc_status = "Incomplete"
            self.power_bg_color = [0.1, 0.1, 0.15, 0.9]

    def on_sell_pc(self):
        if self.is_bankrupt: return
        self.play_sfx()
        if self.pc_status != "Ready to sell!": return
        
        s = self.current_order_specs
        correct = (self.installed_cpu == s["required_cpu"] and self.installed_gpu == s["required_gpu"] and 
                   self.installed_ram == s["required_ram"] and self.installed_storage == s["required_storage"])
        
        if correct:
            profit_mult = 1.5 + s["reward_multiplier"] + (self.reputation-50)*0.01
            sell_price = int(self.current_build_cost * profit_mult)
            self.money += sell_price; self.reputation = min(100, self.reputation + 5)
            self.log_message = f"Sold! Profit: ${sell_price - self.current_build_cost}"
        else:
            sell_price = int(self.current_build_cost * 1.1)
            self.money += sell_price; self.reputation = max(0, self.reputation - 5)
            self.log_message = "Order mismatch! Low profit."

        self.check_next_customer()

        if self.money >= 10000:
            self.log_message = "WINNER! You reached $10,000! Tycoon Master!"
            self.log_color = [1, 0.8, 0, 1]
            self.is_winner = True

    def skip_order(self):
        if self.is_bankrupt or self.is_winner: return
        self.play_sfx()
        
        # คืนเงินค่าอะไหล่บนโต๊ะ
        for k, v in self.installed_parts.items():
            if v: self.money += v["price"]
            
        # หักเงินค่าปรับทิ้งงาน และหักชื่อเสียง
        self.money -= 200   # <--- หักเงิน 200 ทุกครั้งที่กด Skip (เอาไว้โชว์อาจารย์)
        self.reputation = max(0, self.reputation - 5)
        self.log_message = "Skipped client. Penalty: -$200"
        self.log_color = [0.9, 0.5, 0.1, 1] # แจ้งเตือนสีส้ม
        
        # ถ้ายอมจ่ายค่าปรับจนเงินติดลบ ให้ล้มละลายทันที!
        if self.money < 0:
            self.daily_event = "BANKRUPT! Out of business."
            self.event_color = [1, 0.2, 0.2, 1]
            self.log_message = "GAME OVER. Please Start New Game."
            self.log_color = [1, 0, 0, 1]
            self.customers_today = 0
            self.is_bankrupt = True
            return

        self.check_next_customer()

    def add_test_money(self):
        if self.is_bankrupt: return
        self.play_sfx()
        self.money += 5000
        self.log_message = "CHEAT: Added $5,000!"
        self.log_color = [0, 0.8, 0, 1]
        
        if self.money >= 10000:
            self.log_message = "WINNER! You reached $10,000! Tycoon Master!"
            self.log_color = [1, 0.8, 0, 1]

    def next_day(self):
        self.current_day += 1
        self.money -= self.daily_rent
        
        event_roll = random.randint(1, 100)
        if event_roll <= 40:
            self.daily_event = "Normal Day. Business as usual."
            self.event_color = [0, 1, 1, 1]
            self.customers_today = random.randint(1, 3)
        elif event_roll <= 55:
            self.daily_event = "Tech Expo! +5 Reputation."
            self.event_color = [0.2, 1, 0.2, 1]
            self.reputation = min(100, self.reputation + 5)
            self.customers_today = random.randint(2, 4)
        elif event_roll <= 70:
            self.daily_event = "Quiet day. Not many people."
            self.event_color = [0, 1, 1, 1]
            self.customers_today = 1
        elif event_roll <= 80:
            self.daily_event = "Crypto Boom! High demand."
            self.event_color = [0, 1, 1, 1]
            self.customers_today = random.randint(3, 5)
        elif event_roll <= 90:
            self.daily_event = "Bad Reviews! -5 Reputation."
            self.event_color = [1, 0.2, 0.2, 1]
            self.reputation = max(0, self.reputation - 5)
            self.customers_today = random.randint(1, 2)
        else:
            self.daily_event = "Extra Bills! Lost $50."
            self.event_color = [1, 0.2, 0.2, 1]
            self.money -= 50
            self.customers_today = random.randint(1, 3)
            
        self.clear_bench()
        self.generate_new_order()
        self.save_game()

        if self.money < 0:
            self.daily_event = "BANKRUPT! Out of business."
            self.event_color = [1, 0.2, 0.2, 1]
            self.log_message = "GAME OVER. Please Start New Game."
            self.log_color = [1, 0, 0, 1]
            self.customers_today = 0
            self.is_bankrupt = True
    
    def clear_bench(self):
        self.installed_parts = {k: None for k in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]}
        for p in ["cpu","mb","psu","gpu","ram","storage","case"]: setattr(self, f"installed_{p}", "None")
        self.total_wattage = self.base_system_watt; self.current_build_cost = 0
        self.update_status()

    def check_next_customer(self):
        self.customers_today -= 1
        if self.customers_today > 0:
            self.clear_bench()
            self.generate_new_order()
            self.save_game()
        else:
            self.next_day()

    def save_game(self):
        data = {"money": self.money, "day": self.current_day, "rep": self.reputation, "parts": self.installed_parts, "order": self.current_order_specs}
        with open(os.path.join(current_dir, "savegame.json"), "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

    def load_game(self):
        path = os.path.join(current_dir, "savegame.json")
        if not os.path.exists(path): return False
        try:
            with open(path, "r", encoding="utf-8") as f: d = json.load(f)
            self.money = d["money"]; self.current_day = d["day"]; self.reputation = d["rep"]
            self.installed_parts = d["parts"]; self.current_order_specs = d["order"]
            if self.current_order_specs:
                s = self.current_order_specs; self.current_order = f"{s['name']} (${s['budget']})"
                self.required_cpu_display = f"CPU: {s['required_cpu']}"; self.required_gpu_display = f"GPU: {s['required_gpu']}"
                self.required_ram_display = f"RAM: {s['required_ram']}"; self.required_storage_display = f"Storage: {s['required_storage']}"
                self.current_build_cost = sum(p["price"] for p in self.installed_parts.values() if p)
                self.budget_remaining = s["budget"] - self.current_build_cost
                self.total_wattage = self.base_system_watt + sum(p.get("watt", 0) for p in self.installed_parts.values() if p)
            for p in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]:
                setattr(self, f"installed_{p.lower()}", self.installed_parts[p]["name"] if self.installed_parts[p] else "None")
            self.update_status()
            
            # โหลดมาแล้วเช็กด้วยว่าเงินติดลบไหม
            if self.money < 0:
                self.is_bankrupt = True
            else:
                self.is_bankrupt = False
                
            return True
        except: return False

    def reset_game(self):
        self.money = 3000; self.current_day = 1; self.reputation = 50
        self.is_bankrupt = False
        self.is_winner = False
        self.clear_bench()
        self.log_message = "New Game Started!"
        self.log_color = [0, 0.4, 0.8, 0.5]
        self.generate_new_order()
        self.save_game()

class PCBuilderApp(App):
    music_volume = NumericProperty(0.5)
    sfx_volume = NumericProperty(0.8)
    bgm = ObjectProperty(None, allownone=True)

    def build(self):
        self.title = "Neon PC Tycoon"
        self.bgm = SoundLoader.load('bgm.mp3')
        if self.bgm:
            self.bgm.loop = True
            self.bgm.volume = self.music_volume
            self.bgm.play()
            
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(MainGame(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        Window.bind(on_keyboard=self.on_keyboard)
        return sm

    def on_music_volume(self, instance, value):
        if self.bgm: self.bgm.volume = value

    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 292: 
            if Window.fullscreen == False:
                Window.fullscreen = 'auto'
            else:
                Window.fullscreen = False
            return True
        return False

if __name__ == "__main__":
    PCBuilderApp().run()