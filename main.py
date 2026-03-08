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
        ]


class PCBuilderApp(App):
    def build(self):
        self.title = "PC Builder Tycoon"
        sm = ScreenManager()
        sm.add_widget(MainGame(name="main"))
        return sm


if __name__ == "__main__":
    PCBuilderApp().run()
