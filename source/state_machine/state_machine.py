from state_machine.state import State

class StateMachine(object):
    def __init__(self) -> None:
        self.states = dict()
        self.current_state = None
        self.current_state_id = None
        self.current_state_index = 0
        self.state_order = list()

    def addState(self, state: State):
        if state.state_id not in self.states:
            self.states[state.state_id] = state
            self.state_order.append(state.state_id)
        else:
            print("State already exists for {}", state.state_id)
    
    def removeState(self, state_id):
        if state_id in self.states: 
            self.states.pop(state_id)
            self.state_order.remove(state_id)
        else:
            print("State was not present for {}", state_id)

    def removeState(self, state: State):
        self.removeState(state.state_id)

    def setState(self, state_id):
        if state_id in self.states:
            if(self.current_state != None):
                self.current_state.unload()
            self.current_state = self.states[state_id]
            self.current_state_id = state_id
            self.current_state_index = self.state_order.index(state_id)
            self.current_state.load()
        else:
            print("No state found for {}", state_id)

    def nextState(self):
        next_state_index = (self.current_state_index + 1) % len(self.states)
        self.setState(self.state_order[next_state_index])

    def prevState(self):
        prev_state_index = (self.current_state_index - 1) % len(self.states)
        self.setState(self.state_order[prev_state_index])

    def update(self):
        self.current_state.update()