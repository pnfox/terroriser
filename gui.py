from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from random import random as r
from functools import partial


class StressCanvasApp(App):


    def reset_rects(self, label, wid, *largs):
        label.text = '0'
        wid.canvas.clear()

    def build(self):
        wid = Widget()

        label = Label(text='0')

        btn_reset = Button(text='hello',
                            on_press=partial(self.reset_rects, label, wid))
        btn_ok = Button(text='world',
                           on_press=partial(self.reset_rects, label, wid))

        layout = BoxLayout(size_hint=(1, 20), height=50)
        layout.add_widget(btn_reset)
        layout.add_widget(btn_ok)
        layout.add_widget(label)

        root = BoxLayout(orientation='vertical')
        root.add_widget(wid)
        root.add_widget(layout)

        return root


if __name__ == '__main__':
    StressCanvasApp().run()