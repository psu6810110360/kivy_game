from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import NumericProperty, StringProperty


class GameRoot(TabbedPanel):
    money = NumericProperty(50000)
    pc_score = NumericProperty(0)
    current_status = StringProperty("Ready to Build")

    def buy_part(self, part_name, price, score):
        if self.money >= price:
            self.money -= price
            self.pc_score += score
            self.current_status = f"Added {part_name}!"
        else:
            self.current_status = "Not enough money!"


class PCBuilderApp(App):
    def build(self):
        return GameRoot()


if __name__ == "__main__":
    PCBuilderApp().run()
