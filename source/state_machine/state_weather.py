from state_machine.state import State
import os
import time
import terminalio
import displayio
import math
from adafruit_matrixportal.network import Network
from adafruit_display_text.label import Label
from adafruit_display_shapes import line

DATA_SOURCE_FORMAT = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&exclude=minutely,hourly,alerts&appid=" + os.getenv('OPENWEATHER_TOKEN') + "&units=metric"
UPDATE_INTERVAL = 600 # Once every 10 minutes
FAIL_COLOR = 0xFF0000

BEAUFORT_COMP = 0.836
BEAUFORT_POW = 2 / 3

class StateWeather(State):
    def __init__(self, display_width: int, display_height: int, display_group, network: Network, location_key: str, big_font, small_font):
        super().__init__("Weather_{}".format(location_key))
        self.network = network
        self.display_width = display_width
        self.display_height = display_height
        self.display_group = display_group

        lat = os.getenv(location_key+"_LAT")
        lon = os.getenv(location_key+"_LON")
        flag = os.getenv(location_key+"_FLAG")
        self.data_source = DATA_SOURCE_FORMAT.format(lat, lon)

        self.has_weather_update = False

        self.response = None
        self.next_update_time = None

        self.big_color = 0xFFFFFF
        self.small_color = 0x80FFFF
        self.weather_group = displayio.Group()

        if(big_font == None):
            self.big_font = terminalio.FONT
        else:
            self.big_font = big_font

        if(small_font == None):
            self.small_font = terminalio.FONT
        else:
            self.small_font = small_font
        
        # Current Temperature
        self.cur_temp_label = Label(self.big_font)
        self.cur_temp_label.anchor_point = (0, 0.5)
        self.cur_temp_label.anchored_position = (18, 8)
        self.cur_temp_label.text = "--"
        self.cur_temp_label.color = FAIL_COLOR
        self.weather_group.append(self.cur_temp_label)
        # Max Temperature
        self.high_temp_label = Label(self.small_font)
        self.high_temp_label.anchor_point = (1, 0.5)
        self.high_temp_label.anchored_position = (64, 8)
        self.high_temp_label.text = "--"
        self.high_temp_label.color = FAIL_COLOR
        self.weather_group.append(self.high_temp_label)
        # Min Temperature
        self.low_temp_label = Label(self.small_font)
        self.low_temp_label.anchor_point = (1, 0.5)
        self.low_temp_label.anchored_position = (64, 24)
        self.low_temp_label.text = "--"
        self.low_temp_label.color = FAIL_COLOR
        self.weather_group.append(self.low_temp_label)
        # Weather Type Icon
        self.weather_icon_group = displayio.Group()
        self.weather_group.append(self.weather_icon_group)

        # Location Icon, based on country
        self.location_icon_group = displayio.Group()
        self.location_icon_group.y = 16
        self.weather_group.append(self.location_icon_group)
        StateWeather.set_icon(self.location_icon_group, "/icons/countries/" + flag + ".bmp")

        # HighLow format image
        self.high_low_icon_group = displayio.Group()
        self.high_low_icon_group.x = 44
        self.weather_group.append(self.high_low_icon_group)
        StateWeather.set_icon(self.high_low_icon_group, "/icons/weather/highlow.bmp")

        # Wind Direction/Speed
        self.wind_origin = [26, 24]
        self.wind_dir_line = None
        self.wind_strength_origin = [18, 30]
        self.wind_strength_line = None

        self.logMem()

    def load(self):
        super().load()
        self.display_group.append(self.weather_group)
        print("Hello Weather")

    def unload(self):
        super().unload()
        self.display_group.remove(self.weather_group) 
        print("Goodbye Weather")

    def update(self):
        super().update()
        has_weather_update = self.next_update_time is None or time.monotonic() > self.next_update_time
        if has_weather_update:
            self.next_update_time = time.monotonic() + UPDATE_INTERVAL
            data = self.fetch_weather()
            self.display_weather(data)

    def fetch_weather(self):
            print("Fetching Weather...")
            response = self.network.fetch(self.data_source).json()
            print("Weather Fetched")
            return response
    
    def display_weather(self, response):
        if response is None: 
            return
        
        self.cur_temp_label.color = self.big_color
        self.cur_temp_label.text = "%d"%(response['current']['temp'])
        self.high_temp_label.color = self.small_color
        self.high_temp_label.text = "%d"%(response['daily'][0]['temp']['max'])
        self.low_temp_label.color = self.small_color
        self.low_temp_label.text = "%d"%(response['daily'][0]['temp']['min'])
        weather_icon = response['current']['weather'][0]['icon']
        StateWeather.set_icon(self.weather_icon_group, "/icons/weather/" + weather_icon + ".bmp")

        if self.wind_dir_line is not None:
            self.weather_group.remove(self.wind_dir_line)
        wind_end = StateWeather.calc_wind_dir_coords(response['current']['wind_deg'], 7)        
        self.wind_dir_line = line.Line(self.wind_origin[0], self.wind_origin[1], self.wind_origin[0] + wind_end[0], self.wind_origin[1] + wind_end[1], FAIL_COLOR)
        self.weather_group.append(self.wind_dir_line)

        if self.wind_strength_line is not None:
            self.weather_group.remove(self.wind_strength_line)
        wind_line_length = StateWeather.calc_wind_strength_coords(response['current']['wind_speed'], 2)
        self.wind_strength_line = line.Line(self.wind_strength_origin[0], self.wind_strength_origin[1], self.wind_strength_origin[0] + wind_line_length, self.wind_strength_origin[1], self.big_color)
        self.weather_group.append(self.wind_strength_line)
    
    def set_icon(icon_group, file_name):
        print("Set icon to ", file_name)
        if icon_group:
            icon_group.pop()

        if not file_name:
            return  # we're done, no icon desired

        icon = displayio.OnDiskBitmap(file_name)
        weather_icon = displayio.TileGrid(icon, pixel_shader=icon.pixel_shader)

        icon_group.append(weather_icon)
    
    def calc_wind_dir_coords(wind_angle: float, magnitude: int):
        wind_angle_rad = wind_angle * math.pi / 180
        x = round(magnitude * math.sin(wind_angle_rad))
        y = -round(magnitude * math.cos(wind_angle_rad)) # Negated because screen Y positive is downward
        print(f"Wind Angle was {wind_angle}, coords are (x: {x}, y: {y})")
        return [x, y]
    
    def calc_wind_strength_coords(wind_speed: float, scale_multiplier: int):
        beaufort_scale = math.pow((wind_speed / BEAUFORT_COMP), BEAUFORT_POW)
        print(f"Wind Speed was {wind_speed}m/s, bScale is {beaufort_scale}")
        return round(beaufort_scale * scale_multiplier)

