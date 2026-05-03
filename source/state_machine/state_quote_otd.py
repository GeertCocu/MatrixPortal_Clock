from state_machine.state import State
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_pixels
import terminalio

QUOTE = "Amelia <3"

class StateQuoteOTD(State):
    def __init__(self, displayWidth, displayHeight, displayGroup, font, debug):
        super().__init__("QuoteOTD")
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        self.displayGroup = displayGroup
        self.debug = debug

        if font == None:
            self.font = terminalio.FONT
        else:
            self.font = font

        self.quote_label = label.Label(self.font)
        self.quote_label.anchor_point = (0.5, 0.5)
        self.quote_label.anchored_position = (self.displayWidth / 2, self.displayHeight / 2)

    def load(self):
        super().load()
        self.displayGroup.append(self.quote_label)
        self.quote_label.text = "\n".join(wrap_text_to_pixels(QUOTE, self.displayWidth, self.font))
        self.quote_label.color = 0xCC4000
        print("Loading Quote")
        if self.debug:
            bbx, bby, bbwidth, bbh = self.quote_label.bounding_box
            print("Label box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
            print("Label x: {} y: {}".format(self.quote_label.x, self.quote_label.y))

    def unload(self):
        super().unload()
        self.displayGroup.remove(self.quote_label)
        print("Bye Quote")