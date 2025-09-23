import displayio

class ColorCycle(object):
    def __init__(self, btnUp, btnDown):
        self._btnUp = btnUp
        self._btnDown = btnDown
        self.color = displayio.Palette(4)  # Create a color palette
        self.color[0] = 0x000000  # black background
        self.color[1] = 0xFF0000  # red
        self.color[2] = 0xCC4000  # amber
        self.color[3] = 0x85FF00  # greenish
        self._minColorIndex = 1
        self._maxColorIndex = 3
        self._colorIndex = self._minColorIndex
        self._btnUp_cur = None
        self._btnUp_prev = None
        self._btnDown_cur = None
        self._btnDown_prev = None

    def update_and_return_color(self):
        self._btnUp_cur = self._btnUp.value
        if self._btnUp_cur != self._btnUp_prev:
            if not self._btnUp_cur:
                print("Button Up is pressed!")
            else:
                print("Button Up is released!")
                self._colorIndex += 1
                if self._colorIndex > self._maxColorIndex:
                    self._colorIndex = self._minColorIndex
            self._btnUp_prev = self._btnUp_cur

        self._btnDown_cur = self._btnDown.value
        if self._btnDown_cur != self._btnDown_prev:
            if not self._btnDown_cur:
                print("Button Down is pressed!")
            else:
                print("Button Down is released!")
                self._colorIndex -= 1
                if self._colorIndex < self._minColorIndex:
                    self._colorIndex = self._maxColorIndex
            self._btnDown_prev = self._btnDown_cur
        
        return self.return_current_color()
    
    def return_current_color(self):        
        return self.color[self._colorIndex]