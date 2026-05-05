from state_machine.state import State
import os
import time
import terminalio
import displayio
from adafruit_matrixportal.network import Network
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

DATA_SOURCE_FORMAT = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&exclude=minutely,hourly,alerts&appid=" + os.getenv('OPENWEATHER_TOKEN') + "&units=metric"
UPDATE_INTERVAL = 600 # Once every 10 minutes

class StateWeather(State):
    def __init__(self, displayWidth, displayHeight, displayGroup, network, locationkey, bigFont, smallFont):
        super().__init__("Weather")
        self.network = network
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        self.displayGroup = displayGroup

        lat = os.getenv(locationkey+"_LAT")
        lon = os.getenv(locationkey+"_LON")
        flag = os.getenv(locationkey+"_FLAG")
        self.data_source = DATA_SOURCE_FORMAT.format(lat, lon)

        self.has_weather_update = False

        self.response = None
        self.next_update_time = None

        self.fail_color = 0xFF0000
        self.big_color = 0xFFFFFF
        self.small_color = 0x80FFFF
        self.weather_group = displayio.Group()

        if(bigFont == None):
            self.big_font = terminalio.FONT
        else:
            self.big_font = bigFont

        if(smallFont == None):
            self.small_font = terminalio.FONT
        else:
            self.small_font = smallFont
        
        # Current Temperature
        self.cur_temp_label = Label(self.big_font)
        self.cur_temp_label.anchor_point = (0, 0.5)
        self.cur_temp_label.anchored_position = (18, 8)
        self.cur_temp_label.text = "99"
        self.cur_temp_label.color = self.fail_color
        self.weather_group.append(self.cur_temp_label)
        # Max Temperature
        self.high_temp_label = Label(self.small_font)
        self.high_temp_label.anchor_point = (1, 0.5)
        self.high_temp_label.anchored_position = (64, 8)
        self.high_temp_label.text = "99"
        self.high_temp_label.color = self.fail_color
        self.weather_group.append(self.high_temp_label)
        # Min Temperature
        self.low_temp_label = Label(self.small_font)
        self.low_temp_label.anchor_point = (1, 0.5)
        self.low_temp_label.anchored_position = (64, 24)
        self.low_temp_label.text = "99"
        self.low_temp_label.color = self.fail_color
        self.weather_group.append(self.low_temp_label)
        # Weather Type Icon
        self.weather_icon_group = displayio.Group()
        self.weather_group.append(self.weather_icon_group)

        #Location Icon, based on country
        self.location_icon_group = displayio.Group()
        self.location_icon_group.y = 16
        self.weather_group.append(self.location_icon_group)
        StateWeather.set_icon(self.location_icon_group, "/icons/countries/" + flag + ".bmp")

        self.high_low_icon_group = displayio.Group()
        self.high_low_icon_group.x = 44
        self.weather_group.append(self.high_low_icon_group)
        StateWeather.set_icon(self.high_low_icon_group, "/icons/weather/highlow.bmp")
        self.logMem()

    def load(self):
        super().load()
        self.display_weather()
        self.displayGroup.append(self.weather_group)
        print("Hello Weather")

    def unload(self):
        super().unload()
        self.displayGroup.remove(self.weather_group) 
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
            print("Weather Fetched")
    
    def display_weather(self):
        if not self.has_weather_update:
            return
        if self.response is not None:
            self.cur_temp_label.color = self.big_color
            self.cur_temp_label.text = "%d"%(self.response['current']['temp'])
            self.high_temp_label.color = self.small_color
            self.high_temp_label.text = "%d"%(self.response['daily'][0]['temp']['max'])
            self.low_temp_label.color = self.small_color
            self.low_temp_label.text = "%d"%(self.response['daily'][0]['temp']['min'])
            weather_icon = self.response['current']['weather'][0]['icon']
            StateWeather.set_icon(self.weather_icon_group, "/icons/weather/" + weather_icon + ".bmp")
            self.response = None # Free up memory
        else:
            self.cur_temp_label.color = self.fail_color
    
    def set_icon(icon_group, filename):
        print("Set icon to ", filename)
        if icon_group:
            icon_group.pop()

        if not filename:
            return  # we're done, no icon desired

        icon = displayio.OnDiskBitmap(filename)
        weather_icon = displayio.TileGrid(icon, pixel_shader=icon.pixel_shader)

        icon_group.append(weather_icon)