from state_machine.state import State
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label

QUOTE = "An appel a day keeps the witch away"

class StateQuoteOTD(State):
    def __init__(self, displayWidth, displayHeight, displayGroup, debug):
        super().__init__("QuoteOTD")
        if not debug:
            self.font = bitmap_font.load_font("/IBMPlexMono-Medium-24_jep.bdf")
        else:
            self.font = terminalio.FONT
        
        self.quote_label = Label(self.font)

        self.displayWidth = displayWidth
        self.displayHeight = displayHeight
        self.displayGroup = displayGroup

        self.debug = debug

    def load(self):
        super().load()
        self.displayGroup.append(self.quote_label)
        print("Loading Quote")

    def unload(self):
        super().unload()
        self.displayGroup.remove(self.quote_label)
        print("Bye Quote")

    def update(self):
        super().update()
        self.quote_label.text = QUOTE
        self.quote_label.color = 0xCC4000
        self.wrap_text(self.quote_label, self.displayWidth)
        bbx, bby, bbwidth, bbh = self.quote_label.bounding_box
        # Center the label
        self.quote_label.x = round(self.displayWidth / 2 - bbwidth / 2)
        self.quote_label.y = self.displayHeight // 2
        if self.debug:
            print("Label box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
            print("Label x: {} y: {}".format(self.quote_label.x, self.quote_label.y)) 
            
    # Function to wrap text based on width
    def wrap_text(self, label, max_width):
        words = label.text.split(' ')
        wrapped_lines = []
        current_line = ""

        print("word Count: {}".format(len(words)))
        for word in words:
            # Check if adding the next word exceeds the max width
            test_line = current_line + (word if current_line == "" else " " + word)
            if label.bounding_box[2] > max_width:  # Check width
                wrapped_lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        wrapped_lines.append(current_line)  # Add the last line
        label.text = "\n".join(wrapped_lines)  # Join lines with newline 