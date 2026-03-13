import os
import random
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.core.audio import SoundLoader
from gamedata import CUSTOMER_ORDERS, PARTS_ITEMS

current_dir = os.path.dirname(__file__)
Builder.load_file(os.path.join(current_dir, "pcbuilder.kv"), encoding="utf-8")

class MainMenu(Screen):
    has_started = BooleanProperty(False)
    def on_enter(self):
        # ตรวจสอบไฟล์เซฟเพื่อแสดงปุ่ม CONTINUE
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

class MainGame(Screen):
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
    
    # ส่วนแสดงผลความต้องการของลูกค้า
    required_cpu_display = StringProperty(""); required_gpu_display = StringProperty("")
    required_ram_display = StringProperty(""); required_storage_display = StringProperty("")
    
    # ส่วนแสดงผลอุปกรณ์ที่ติดตั้งแล้ว
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
        Clock.schedule_once(self.init_game)

    def init_game(self, dt):
        if not self.load_game(): 
            self.generate_new_order()
        self.populate_shop(0)

    def play_sfx(self):
        # โหลดและเล่นเสียงคลิก (อ้างอิงระดับเสียงจาก Settings)
        sfx = SoundLoader.load('click.wav')
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
        self.budget_remaining = s["budget"]; self.current_build_cost = 0

    def buy_part(self, item):
        self.play_sfx()
        if self.money < item["price"]:
            self.log_message = "NOT ENOUGH CASH!"; return
        
        part_type = item["type"]
        # เช็คความเข้ากันได้ของ Socket
        if part_type == "CPU" and self.installed_parts["MB"] and item["socket"] != self.installed_parts["MB"]["socket"]:
            self.log_message = "SOCKET MISMATCH!"; return
        if part_type == "MB" and self.installed_parts["CPU"] and item["socket"] != self.installed_parts["CPU"]["socket"]:
            self.log_message = "SOCKET MISMATCH!"; return

        # ถอดของเก่าคืนเงิน
        old = self.installed_parts[part_type]
        if old:
            self.money += old["price"]; self.current_build_cost -= old["price"]
            if "watt" in old: self.total_wattage -= old["watt"]

        # ติดตั้งของใหม่
        self.installed_parts[part_type] = item
        self.money -= item["price"]; self.current_build_cost += item["price"]
        if "watt" in item: self.total_wattage += item["watt"]
        
        self.budget_remaining = self.current_order_specs["budget"] - self.current_build_cost
        setattr(self, f"installed_{part_type.lower()}", item["name"])
        self.log_message = f"Installed {item['name']}"; self.update_status()

    def update_status(self):
        is_complete = all(v is not None for v in self.installed_parts.values())
        if is_complete:
            psu = self.installed_parts["PSU"]
            if self.total_wattage <= (psu["watt_limit"] * 0.8): self.pc_status = "Ready to sell!"
            else: self.pc_status = "Power overload!"
        else: self.pc_status = "Incomplete"

    def on_sell_pc(self):
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

        self.next_day()

    def skip_order(self):
        self.play_sfx()
        for k, v in self.installed_parts.items():
            if v: self.money += v["price"]
        self.reputation = max(0, self.reputation - 5); self.log_message = "Skipped client."; self.next_day()

    def next_day(self):
        def next_day(self):
        # หักค่าเช่าร้านอัตโนมัติ
            self.current_day += 1; self.money -= self.daily_rent
        
        # --- ระบบ Event และ สุ่มลูกค้า ---
        events = [
            "Normal Day. Business as usual.",
            "Tech Expo! +5 Reputation.",
            "Quiet day. Not many people.",
            "Crypto Boom! High PC demand."
        ]
        self.daily_event = random.choice(events)
        if "Tech Expo" in self.daily_event:
            self.reputation = min(100, self.reputation + 5)
            
        self.customers_today = random.randint(1, 3) # สุ่มลูกค้า 1-3 คนต่อวัน
        # -----------------------------
        
        self.clear_bench() # เปลี่ยนไปเรียกฟังก์ชันเคลียร์โต๊ะแทน
        self.generate_new_order(); self.save_game()

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
            self.update_status(); return True
        except: return False

    def reset_game(self):
        self.money = 3000; self.current_day = 1; self.reputation = 50
        self.installed_parts = {k: None for k in ["CPU","MB","GPU","RAM","PSU","Storage","Case"]}
        for p in ["cpu","mb","psu","gpu","ram","storage","case"]: setattr(self, f"installed_{p}", "None")
        self.total_wattage = self.base_system_watt; self.current_build_cost = 0
        self.log_message = "New Game Started!"; self.update_status(); self.generate_new_order(); self.save_game()

class PCBuilderApp(App):
    music_volume = NumericProperty(0.5)
    sfx_volume = NumericProperty(0.8)
    bgm = ObjectProperty(None, allownone=True)

    def build(self):
        self.title = "Neon PC Tycoon"
        # โหลดเพลง BGM อัตโนมัติ (ห้ามลบ .mp3 ออกนะครับ)
        self.bgm = SoundLoader.load('bgm.mp3')
        if self.bgm:
            self.bgm.loop = True
            self.bgm.volume = self.music_volume
            self.bgm.play()
            
        sm = ScreenManager()
        sm.add_widget(MainMenu(name="menu"))
        sm.add_widget(MainGame(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm

    def on_music_volume(self, instance, value):
        if self.bgm: self.bgm.volume = value

if __name__ == "__main__":
    PCBuilderApp().run()