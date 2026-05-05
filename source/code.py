# SPDX-FileCopyrightText: 2020 John Park for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import os
import board
import displayio
import terminalio
import gc
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text.label import Label

from state_machine.state_machine import StateMachine
from state_machine.state_clock import StateClock
from state_machine.state_quote_otd import StateQuoteOTD
from state_machine.state_weather import StateWeather

from font_junction_regular_10 import FONT as JUN_10
from font_junction_regular_18 import FONT as JUN_18

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

display.root_group = group

gc.collect()
cur_mem = gc.mem_free()
print("Available memory pre-wifi: {} bytes".format(cur_mem))

# Display to the user the wifi is connecting
network_label = Label(terminalio.FONT)
network_label.anchor_point = (0.5, 0.5)
network_label.anchored_position = (display.width / 2, display.height / 2)
network_label.color = 0x888888
network_label.text = "Wifi..."
group.append(network_label)
network.connect() # Connecting to the internet
network_label.text = "Time..."
network.get_local_time()  # Synchronize Board's clock to Internet
group.remove(network_label)

gc.collect()
cur_mem = gc.mem_free()
print("Available memory pre-statemachine: {} bytes".format(cur_mem))

stateMachine = StateMachine()
stateMachine.addState(StateQuoteOTD(display.width, display.height, group, JUN_10, DEBUG))
stateMachine.addState(StateClock(display.width, display.height, group, DEBUG, BLINK))
stateMachine.addState(StateWeather(display.width, display.height, group, network, "OPENWEATHER_LOCATION_1", JUN_18, JUN_10))
stateMachine.addState(StateWeather(display.width, display.height, group, network, "OPENWEATHER_LOCATION_2", JUN_18, JUN_10))
stateMachine.setState(StateClock.clockId)

buttonUpState = ButtonState(btnUp)
buttonDownState = ButtonState(btnDown)

while True:
    try:
        stateMachine.update()

        # Selects next state if up button was released
        buttonStateChanged, currentButtonValue = buttonUpState.pollButtonState()
        if(buttonStateChanged and currentButtonValue):
           stateMachine.nextState()
        
        # Selects previous state if down button was released
        buttonStateChanged, currentButtonValue = buttonDownState.pollButtonState()
        if(buttonStateChanged and currentButtonValue):
           stateMachine.prevState()
        
    except RuntimeError as e:
        print("Something went wrong -", e)
    
