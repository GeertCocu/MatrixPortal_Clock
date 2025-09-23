class ButtonState(object):
    def __init__(self, button):
        self._button = button
        self._button_cur = self._button.value
        self._button_prev = self._button.value

    def pollButtonState(self):
        hasStateChanged = False
        self._button_cur = self._button.value
        if self._button_cur != self._button_prev:
            print("State has Changed!")
            hasStateChanged = True
            self._button_prev = self._button_cur

        # button is pressed if self._button_cur = True
        return hasStateChanged, self._button_cur

    def getCurrentState(self):
        return self._button_cur