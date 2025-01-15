import os
import socket
import zlib


from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from mss import mss, tools
from PIL import Image
import pygame

WIDTH = 900
HEIGHT = 800
MONITOR_NUMBER = 1


class MainApp(App):
    def __del__(self):
        self.soc.close()
        print('Connection Closed')

    def build(self):
        self.connected = False
        self.soc = socket.socket()
        self.soc.bind(('192.168.0.100', 5000))
        self.soc.listen(5)
        print("server started")
        self.screenshot_number = 0
        self.layout = BoxLayout()
        self.start_button = Button(text='Start', pos_hint={'center_x':0.5, 'center_y':0.5})
        self.start_button.bind(on_press=self.start_recording)
        self.end_button = Button(text='End', pos_hint={'center_x':0.5, 'center_y':0.5})
        self.end_button.bind(on_press=self.end_recording)
        self.layout.add_widget(self.start_button)
        return self.layout

    def start_recording(self, instance):
        self.layout.add_widget(self.end_button)
        self.layout.remove_widget(self.start_button)
        self.conn, addr = self.soc.accept()
        print(f"Connected to client : {addr}")
        print('Starting screen recording')
        self.event = Clock.schedule_interval(self.screen_capture, 1/50.)

    def end_recording(self, instance):
        self.event.cancel()
        self.layout.remove_widget(self.end_button)
        self.layout.add_widget(self.start_button)
        print('Screen recording ended')

    def screen_capture(self, dt):
        with mss() as sct:
            file_name = sct.shot(mon=-1, output=f'{self.screenshot_number}.png')
            img = Image.open(f'{self.screenshot_number}.png')
            pixels = img.tobytes('raw', 'RGB')
            pixels = zlib.compress(pixels)
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            self.conn.send(bytes([size_len]))
            size_bytes = size.to_bytes(size_len, 'big')
            self.conn.send(size_bytes)
            self.conn.sendall(pixels)


if __name__ == '__main__':
    MainApp().run()
