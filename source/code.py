# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import os
import board
import displayio
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from digitalio import DigitalInOut, Direction, Pull

from state_machine.state_machine import StateMachine
from state_machine.state_clock import StateClock
from state_machine.state_quote_otd import StateQuoteOTD

from button_state import ButtonState

BLINK = True
DEBUG = True

print("Metro Minimal Clock")
print("Time will be set for {}".format(os.getenv("TIMEZONE")))

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()  # Create a Group
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth

btnUp = DigitalInOut(board.BUTTON_UP)
btnUp.direction = Direction.INPUT
btnUp.pull = Pull.UP
btnUp_prev = btnUp.value

btnDown = DigitalInOut(board.BUTTON_DOWN)
btnDown.direction = Direction.INPUT
btnDown.pull = Pull.UP
btnDown_prev = btnDown.value

color = displayio.Palette(4)  # Create a color palette
color[0] = 0x000000  # black background
color[1] = 0xFF0000  # red
color[2] = 0xCC4000  # amber
color[3] = 0x85FF00  # greenish

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color)
group.append(tile_grid)  # Add the TileGrid to the Group
display.root_group = group

stateMachine = StateMachine()
stateQuote = StateQuoteOTD(display.width, display.height, group, DEBUG)
stateClock = StateClock(display.width, display.height, network, group, DEBUG, BLINK)

buttonUpState = ButtonState(btnUp)
buttonDownState = ButtonState(btnDown)

states = [stateClock, stateQuote]
stateIndex = 0

stateMachine.setState(stateClock)

while True:
    try:
        stateMachine.update()

        # Selects next state if up button was released
        buttonStateChanged, currentButtonValue = buttonUpState.pollButtonState()
        if(buttonStateChanged and currentButtonValue):
           stateIndex = (stateIndex + 1) % len(states)
           stateMachine.setState(states[stateIndex])
        
        # Selects previous state if down button was released
        buttonStateChanged, currentButtonValue = buttonDownState.pollButtonState()
        if(buttonStateChanged and currentButtonValue):
           stateIndex = (stateIndex - 1) % len(states)
           stateMachine.setState(states[stateIndex])
        
    except RuntimeError as e:
        print("Something went wrong -", e)
    
