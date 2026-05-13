from state_machine.state_machine import StateMachine
import time

class StateCycle:
    def __init__(self, state_machine: StateMachine, cycle_interval: float):
        self.state_machine = state_machine
        self.cycle_interval = cycle_interval
        self.next_cycle_time = time.monotonic() + self.cycle_interval

    def update(self):
        if time.monotonic() > self.next_cycle_time:
            self.next_cycle_time = time.monotonic() + self.cycle_interval
            self.state_machine.nextState()