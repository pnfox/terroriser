from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from random import random as r
from functools import partial


class StressCanvasApp(App):


    def reset_rects(self, label, wid, *largs):
        label.text = '0'
        wid.canvas.clear()

    def build(self):
        window = BoxLayout(orientation='vertical')
        section_1 = BoxLayout(orientation='vertical')
        section_2 = BoxLayout(orientation='vertical')
        section_3 = BoxLayout(orientation='vertical')
        section_4 = BoxLayout(orientation='vertical')

        window.add_widget(section_1)
        window.add_widget(section_2)
        window.add_widget(section_3)
        window.add_widget(section_4)
        # label = Label(text='0')

        # btn_reset = Button(text='hello',
        #                     on_press=partial(self.reset_rects, label, wid))
        # btn_ok = Button(text='world',
        #                    on_press=partial(self.reset_rects, label, wid))

        # layout = BoxLayout(size_hint=(1, None), height=50)
        # layout.add_widget(btn_reset)
        # layout.add_widget(btn_ok)
        # layout.add_widget(label)

        # layout2 = RelativeLayout()
        #,padding = (10,10), size_hint = (.1,.1)
        btn_1 = Button(text='section 1')
        btn_2 = Button(text='section 2')
        btn_3 = Button(text='section 3')
        btn_4 = Button(text='section 4')
        section_1.add_widget(btn_1)
        section_2.add_widget(btn_2)
        section_3.add_widget(btn_3)
        section_4.add_widget(btn_4)

        # root = BoxLayout(orientation='vertical')
        # root.add_widget(wid)
        # root.add_widget(layout2)
        # root.add_widget(layout)

        return window


if __name__ == '__main__':
    StressCanvasApp().run()