import time
from adafruit_display_text.label import Label

class TimeScreen(object):
    def __init__(self, network, blink, debug, font, color, displayHeight, displayWidth):
        self._network = network
        self._blink = blink
        self._debug = debug
        self._clock_label = Label(font)
        self._clock_label.color = color
        self._displayHeight = displayHeight
        self._displayWidth = displayWidth
        self.last_check = None

    def update_time(self, *, hours=None, minutes=None, show_colon=False):
        now = time.localtime()  # Get the time values we need
        if hours is None:
            hours = now[3]
        if hours > 12:  # Handle times later than 12:59
            hours -= 12
        elif not hours:  # Handle times between 0:00 and 0:59
            hours = 12

        if minutes is None:
            minutes = now[4]

        if self._blink:
            colon = ":" if show_colon or now[5] % 2 else " "
        else:
            colon = ":"

        self.clock_label.text = "{hours}{colon}{minutes:02d}".format(
            hours=hours, minutes=minutes, colon=colon
        )
        bbx, bby, bbwidth, bbh = self.clock_label.bounding_box
        # Center the label
        self.clock_label.x = round(self._displayWidth / 2 - bbwidth / 2)
        self.clock_label.y = self._displayHeight // 2
        if self._debug:
            print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
            print("Label x: {} y: {}".format(self.clock_label.x, self.clock_label.y))

    def set_clock_color(self, color):
        self.clock_label.color = color

    def update_time_at_interval(self, interval):
        if self.last_check is None or time.monotonic() > self.last_check + interval:
            try:
                self.update_time(show_colon=True)  # Make sure a colon is displayed while updating
                self.network.get_local_time()  # Synchronize Board's clock to Internet
                self.last_check = time.monotonic()
            except RuntimeError as e:
                print("Some error occured, retrying! -", e)