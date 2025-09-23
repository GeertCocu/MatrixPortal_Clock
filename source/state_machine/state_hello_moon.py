from state_machine.state import State

class StateHelloMoon(State):
    def __init__(self):
        super().__init__("Hello Moon")

    def load(self):
        super().load()
        print("Hello Moon")

    def unload(self):
        super().unload()
        print("Goodbye Moon")

    def update(self):
        super().update()
        print("I See the Moon")