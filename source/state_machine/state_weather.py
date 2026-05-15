from state_machine.state import State
import os
import time
import terminalio
import displayio
import math
import gc
from adafruit_matrixportal.network import Network
from adafruit_display_text.label import Label
from adafruit_display_shapes import line
from adafruit_display_shapes import circle

DATA_SOURCE_FORMAT = "https://api.openweathermap.org/data/3.0/onecall?lat={}&lon={}&exclude=minutely,hourly,alerts&appid=" + os.getenv('OPENWEATHER_TOKEN') + "&units=metric"
UPDATE_INTERVAL = 600 # Once every 10 minutes
FAIL_COLOR = 0x430000
BIG_COLOR = 0x434343
SMALL_COLOR = 0x004343

BEAUFORT_COMP = 0.836
BEAUFORT_POW = 2 / 3
COMPASS_RADIUS = 7

NO_DATA_STRING = "--"

WEATHER_ICON_SPREADSHEET = "/icons/weather/weather-icons.bmp"
WEATHER_ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")
ICON_WIDTH = 16
ICON_HEIGHT = 16

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

        self.big_font = big_font if big_font is not None else terminalio.FONT
        self.small_font = small_font if small_font is not None else terminalio.FONT
        
        self.weather_group = displayio.Group()

        # Current Temperature
        self.temp_current_label = Label(self.big_font)
        self.temp_current_label.anchor_point = (0, 0.5)
        self.temp_current_label.anchored_position = (18, 8)
        self.temp_current_label.text = self.temp_current = NO_DATA_STRING
        self.temp_current_label.color = FAIL_COLOR
        self.weather_group.append(self.temp_current_label)
        # Min Temperature
        self.temp_min_label = Label(self.small_font)
        self.temp_min_label.anchor_point = (1, 0.5)
        self.temp_min_label.anchored_position = (64, 8)
        self.temp_min_label.text = self.temp_min = NO_DATA_STRING
        self.temp_min_label.color = FAIL_COLOR
        self.weather_group.append(self.temp_min_label)
        # Max Temperature
        self.temp_max_label = Label(self.small_font)
        self.temp_max_label.anchor_point = (1, 0.5)
        self.temp_max_label.anchored_position = (64, 24)
        self.temp_max_label.text = self.temp_max = NO_DATA_STRING
        self.temp_max_label.color = FAIL_COLOR
        self.weather_group.append(self.temp_max_label)

        # Weather Type Icon
        self.weather_icon_group = displayio.Group()
        self.weather_group.append(self.weather_icon_group)
        self.has_weather_icon_changed = False
        self.weather_icon = ""
        # Load the icon sprite sheet
        self.weather_icons = displayio.OnDiskBitmap(WEATHER_ICON_SPREADSHEET)
        self.weather_icon_sprite = displayio.TileGrid(
            self.weather_icons,
            pixel_shader=self.weather_icons.pixel_shader,
            tile_width=ICON_WIDTH,
            tile_height=ICON_HEIGHT
        )
        self.weather_icon_group.append(self.weather_icon_sprite)

        # Location Icon, based on country
        self.location_icon_group = self.construct_icon_group("/icons/countries/" + flag + ".bmp", 0, 16)
        self.weather_group.append(self.location_icon_group)

        # HighLow format image
        self.high_low_icon_group = self.construct_icon_group("/icons/weather/highlow.bmp", 44, 0)
        self.weather_group.append(self.high_low_icon_group)

        # Wind Direction/Speed
        self.wind_origin = 28, 24
        self.wind_dir_line = None
        self.has_wind_coords_changed = False
        self.wind_coords = None
        self.wind_compass = circle.Circle(self.wind_origin[0], self.wind_origin[1], COMPASS_RADIUS, fill=None, outline=BIG_COLOR)
        self.weather_group.append(self.wind_compass)

        self.logMem()

    def load(self):
        super().load()
        self.display_group.append(self.weather_group)
        print("Hello Weather")

    def unload(self):
        self.display_group.remove(self.weather_group) 
        print("Goodbye Weather")
        return super().unload()

    def update(self):
        super().update()
        has_weather_update = self.next_update_time is None or time.monotonic() > self.next_update_time
        if has_weather_update:
            self.next_update_time = time.monotonic() + UPDATE_INTERVAL
            self.fetch_weather()
            self.update_display()

    def fetch_weather(self):
            print("Fetching Weather...")
            response = self.network.fetch(self.data_source).json()
            print("Weather Fetched")
            self.temp_current = str(round(response['current']['temp']))
            self.temp_min = str(round(response['daily'][0]['temp']['max']))
            self.temp_max = str(round(response['daily'][0]['temp']['min']))

            weather_icon = response['current']['weather'][0]['icon']
            self.has_weather_icon_changed = self.weather_icon != weather_icon
            self.weather_icon = weather_icon

            wind_coords = self.calc_wind_coords(response['current']['wind_deg'], response['current']['wind_speed'], 7, 2, self.wind_origin)
            self.has_wind_coords_changed = self.wind_coords != wind_coords
            self.wind_coords = wind_coords

            # Cleanup
            response = None
            gc.collect()

    def update_display(self):
        self.temp_current_label.color = BIG_COLOR
        self.temp_current_label.text = self.temp_current
        self.temp_min_label.color = SMALL_COLOR
        self.temp_min_label.text = self.temp_min
        self.temp_max_label.color = SMALL_COLOR
        self.temp_max_label.text = self.temp_max
        if self.has_weather_icon_changed: self.set_weather_icon(self.weather_icon)
        if self.has_wind_coords_changed:
            if self.wind_dir_line is not None:
                self.weather_group.remove(self.wind_dir_line)
            self.wind_dir_line = line.Line(self.wind_coords[0], self.wind_coords[1], self.wind_coords[2], self.wind_coords[3],FAIL_COLOR)
            self.weather_group.append(self.wind_dir_line)
    
    def set_weather_icon(self, icon_name):
        print("Set icon to", icon_name)
        if icon_name is not None:
            row = None
            for index, icon in enumerate(WEATHER_ICON_MAP):
                if icon == icon_name[0:2]:
                    row = index
                    break
            column = 1 if icon_name[2] == "n" else 0
            if row is not None:
                self.weather_icon_sprite[0] = (row * 2) + column

    @staticmethod
    def construct_icon_group(file_name: str, x: int, y: int):
        print("Loading icon from ", file_name)
        icon = displayio.OnDiskBitmap(file_name)
        weather_icon = displayio.TileGrid(icon, pixel_shader=icon.pixel_shader)
        print("Icon loaded")
        icon_group = displayio.Group()
        icon_group.x = x
        icon_group.y = y
        icon_group.append(weather_icon)
        return icon_group
    
    @staticmethod
    def calc_wind_coords(wind_angle: float, wind_speed: float, radius: int, wind_scale: int = 1, origin: tuple=(0,0)):
        wind_angle_rad = wind_angle * math.pi / 180
        dir_x = math.sin(wind_angle_rad)
        dir_y = -math.cos(wind_angle_rad) # Negated because screen Y positive is downward

        outer_x = round(dir_x * radius)
        outer_y = round(dir_y * radius)

        scale = StateWeather.calc_beaufort_scale(wind_speed)
        inner_radius = radius - (scale * wind_scale)
        inner_x = round(dir_x * inner_radius)
        inner_y = round(dir_y * inner_radius)

        return origin[0] + inner_x, origin[1] + inner_y, origin[0] + outer_x, origin[1] + outer_y

    @staticmethod
    def calc_beaufort_scale(wind_speed: float):
        beaufort_scale = math.pow((wind_speed / BEAUFORT_COMP), BEAUFORT_POW)
        print(f"Wind Speed was {wind_speed}m/s, bScale is {beaufort_scale}")
        return beaufort_scale


