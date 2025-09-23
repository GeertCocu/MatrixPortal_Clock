class StateMachine(object):
    def __init__(self) -> None:
        self.states = None
        self.currentState = None

    def setState(self, state):
        if(self.currentState == state):
            return
        if(self.currentState != None):
            self.currentState.unload()
        self.currentState = state
        self.currentState.load()

    def update(self):
        self.currentState.update()