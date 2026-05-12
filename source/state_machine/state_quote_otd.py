from state_machine.state import State
from adafruit_display_text import label, wrap_text_to_pixels
import terminalio

QUOTE = "Amelia <3"

class StateQuoteOTD(State):
    def __init__(self, display_width: int, display_height: int, display_group, font):
        super().__init__("QuoteOTD")
        self.display_width = display_width
        self.display_height = display_height
        self.display_group = display_group

        if font == None:
            self.font = terminalio.FONT
        else:
            self.font = font

        self.quote_label = label.Label(self.font)
        self.quote_label.anchor_point = (0.5, 0.5)
        self.quote_label.anchored_position = (self.display_width / 2, self.display_height / 2)
        self.logMem()

    def load(self):
        super().load()
        print("Loading Quote")
        self.display_group.append(self.quote_label)
        self.quote_label.text = "\n".join(wrap_text_to_pixels(QUOTE, self.display_width, self.font))
        self.quote_label.color = 0xCC4000

    def unload(self):
        super().unload()
        self.display_group.remove(self.quote_label)
        print("Bye Quote")