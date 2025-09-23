from state_machine.state import State

class StateHelloWorld(State):
    def __init__(self):
        super().__init__("Hello World")

    def load(self):
        super().load()
        print("Hello World")

    def unload(self):
        super().unload()
        print("Goodbye world")

    def update(self):
        super().update()
        print("I See the world")