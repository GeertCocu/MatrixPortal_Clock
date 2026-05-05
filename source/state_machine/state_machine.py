from state_machine.state import State

class StateMachine(object):
    def __init__(self) -> None:
        self.states = dict()
        self.currentState = None
        self.currentStateId = None
        self.currentStateIndex = 0
        self.stateOrder = list()

    def addState(self, state: State):
        if state.stateId not in self.states:
            self.states[state.stateId] = state
            self.stateOrder.append(state.stateId)
        else:
            print("State already exists for {}", state.stateId)
    
    def removeState(self, stateId):
        if stateId in self.states: 
            self.states.pop(stateId)
            self.stateOrder.remove(stateId)
        else:
            print("State was not present for {}", stateId)

    def removeState(self, state: State):
        self.removeState(state.stateId)

    def setState(self, stateId):
        if stateId in self.states:
            if(self.currentState != None):
                self.currentState.unload()
            self.currentState = self.states[stateId]
            self.currentStateId = stateId
            self.currentStateIndex = self.stateOrder.index(stateId)
            self.currentState.load()
        else:
            print("No state found for {}", stateId)

    def nextState(self):
        nextStateIndex = (self.currentStateIndex + 1) % len(self.states)
        self.setState(self.stateOrder[nextStateIndex])

    def prevState(self):
        prevStateIndex = (self.currentStateIndex - 1) % len(self.states)
        self.setState(self.stateOrder[prevStateIndex])

    def update(self):
        self.currentState.update()