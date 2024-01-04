import numpy as np
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.graphics import Color
import sounddevice as sd

class OverdrivePedalApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        with self.layout.canvas.before:
            Color(0, 0, 0, 1)  # Color de fondo negro

        self.distortion_slider = Slider(min=0, max=1, value=0.5)
        devices = sd.query_devices()
        device_names = ['Default'] + [device['name'] for device in devices if 'name' in device]
        self.input_selector = Spinner(text='Select Input', values=device_names)
        self.channel_selector = Spinner(text='Select Channel', values=['1', '2'])

        self.start_button = Button(text='Start', background_color=(0, 1, 0, 1))
        self.start_button.bind(on_press=self.audio_processing)

        self.stop_button = Button(text='Stop', background_color=(1, 0, 0, 1))
        self.stop_button.bind(on_press=self.stop_processing)

        self.layout.add_widget(self.distortion_slider)
        self.layout.add_widget(self.input_selector)
        self.layout.add_widget(self.channel_selector)
        self.layout.add_widget(self.start_button)
        self.layout.add_widget(self.stop_button)

        self.input_buffer = np.array([])  # entrada bufer
        self.output_buffer = np.array([])  # datos al bufer
        self.running = False  # Flag del ciclo

        return self.layout

    def audio_processing(self, instance):
        self.running = True
        self.input_buffer = np.array([])
        self.output_buffer = np.array([])

        device_name = self.input_selector.text
        channel_text = self.channel_selector.text

        if device_name == 'Select Input':
            device_idx = None
        else:
            device_idx = self.input_selector.values.index(device_name)

        if channel_text == 'Select Channel':
            channel = None
        else:
            channel = int(channel_text) - 1

        input_stream = sd.InputStream(device=device_idx, channels=2, callback=self.audio_input_callback)
        output_stream = sd.OutputStream(device=0, channels=2, callback=self.audio_output_callback)

        with input_stream, output_stream:
            while self.running:
                time.sleep(0.01)  # pausa para ahorrar recursos

    def stop_processing(self, instance):
        self.running = False

    def audio_input_callback(self, indata, frames, time, status):
        input_samples = indata[:, 0]
        self.input_buffer = np.concatenate((self.input_buffer, input_samples))

    def audio_output_callback(self, outdata, frames, time, status):
        if len(self.output_buffer) >= frames:
            output_samples = self.output_buffer[:frames]
            self.output_buffer = self.output_buffer[frames:]
        else:
            output_samples = np.zeros(frames)

        outdata[:, 0] = output_samples
        outdata[:, 1] = output_samples  # canales

    def apply_distortion(self, samples, amount):
        return np.tanh(samples * amount)  # distorsion

if __name__ == '__main__':
    OverdrivePedalApp().run()
