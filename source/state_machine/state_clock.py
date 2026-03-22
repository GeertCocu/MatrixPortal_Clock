from state_machine.state import State
import terminalio
import displayio
import time
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

class StateClock(State):
    def __init__(self, displayWidth, displayHeight, displayGroup, debug, blink):
        super().__init__("Clock")
        
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        self.displayGroup = displayGroup
        self.debug = debug
        self.blink = blink

        if not debug:
            self.font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
        else:
            self.font = terminalio.FONT
        
        self.clock_label = Label(self.font)
        self.clock_label.anchor_point = (0.5, 0.5)
        self.clock_label.anchored_position = (self.displayWidth / 2, self.displayHeight / 2)

        self.next_blink_time = None

        self.color = displayio.Palette(4)  # Create a color palette
        self.color[0] = 0x000000  # black background
        self.color[1] = 0xFF0000  # red
        self.color[2] = 0xCC4000  # amber
        self.color[3] = 0x85FF00  # greenish


    def load(self):
        super().load()
        self.displayGroup.append(self.clock_label)
        self.update_time(show_colon=True)
        print("Clock Loaded!")

    def unload(self):
        super().unload()
        self.displayGroup.remove(self.clock_label)
        print("Clock Unloaded!")

    def update(self):
        super().update()
        if self.next_blink_time is None or time.monotonic() > self.next_blink_time:
            try:
                self.next_blink_time = time.monotonic() + 1 # Current time + 1 second
                self.update_time()
            except RuntimeError as e:
                print("Some error occured, retrying! -", e)
    
    def update_time(self, *, hours=None, minutes=None, show_colon=False):
        now = time.localtime()  # Get the time values we need
        if hours is None:
            hours = now[3]
        if hours >= 18 or hours < 6:  # evening hours to morning
            self.clock_label.color = self.color[1]
        else:
            self.clock_label.color = self.color[2]  # daylight hours
            
        if minutes is None:
            minutes = now[4]

        if self.blink:
            colon = ":" if show_colon or now[5] % 2 else " "
        else:
            colon = ":"

        self.clock_label.text = "{hours}{colon}{minutes:02d}".format(
            hours=hours, minutes=minutes, colon=colon
        )
        bbx, bby, bbwidth, bbh = self.clock_label.bounding_box
        if self.debug:
            print("bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
            print("Label x: {} y: {}".format(self.clock_label.x, self.clock_label.y)) 