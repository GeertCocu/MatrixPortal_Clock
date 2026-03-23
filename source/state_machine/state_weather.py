from state_machine.state import State
import os
import time
import terminalio
from adafruit_matrixportal.network import Network
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

DATA_SOURCE_FORMAT = "http://api.openweathermap.org/data/2.5/weather?q={}&appid=" + os.getenv('OPENWEATHER_TOKEN') + "&units=metric"
UPDATE_INTERVAL = 30

class StateWeather(State):
    def __init__(self, displayWidth, displayHeight, displayGroup, network, location):
        super().__init__("Weather")
        self.network = network
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        self.displayGroup = displayGroup

        self.data_source = DATA_SOURCE_FORMAT.format(location)
        self.location = location.split(',')[0]

        self.has_weather_update = False

        self.response = None
        self.next_update_time = None

        self.fail_color = 0xFF0000
        self.succes_color = 0x85FF00

        self.temp_label = Label(terminalio.FONT)
        self.temp_label.anchor_point = (0.5, 0.5)
        self.temp_label.anchored_position = (self.displayWidth / 2, self.displayHeight / 2)
        self.temp_label.text = "9999 C"
        self.temp_label.color = self.fail_color


    def load(self):
        super().load()
        self.fetch_weather()
        self.displayGroup.append(self.temp_label)
        print("Hello Weather")

    def unload(self):
        super().unload()
        self.displayGroup.remove(self.temp_label)
        print("Goodbye Weather")

    def update(self):
        super().update()
        self.display_weather()
        self.fetch_weather()

    def fetch_weather(self):
        self.has_weather_update = self.next_update_time is None or time.monotonic() > self.next_update_time
        if self.has_weather_update:
            print("Fetching Weather...")
            self.response = self.network.fetch(self.data_source).json()
            self.next_update_time = time.monotonic() + UPDATE_INTERVAL
            print("Weather Fetched:", self.response)
    
    def display_weather(self):
        if not self.has_weather_update:
            return
        if self.response is not None:
            self.temp_label.color = self.succes_color
            self.temp_label.text = self.location + "\n%d C"%(self.response['main']['temp'])
        else:
            self.temp_label.color = self.fail_color